"""Team cloud sync client.

Protocol (see server/app.py):
    GET  /api/profiles                  -> all profiles + lock info
    PUT  /api/profiles/<id>             -> upsert one profile  {data, user}
    DELETE /api/profiles/<id>           -> tombstone (delete everywhere)
    GET/PUT /api/cookies/<id>
    GET/PUT /api/sessions/<id>      -> browsing session (tabs + login state)
    GET  /api/proxies                   -> all proxies
    PUT/DELETE /api/proxies/<id>
    POST /api/lock   {profile_id, user, device}  -> acquire exclusive lock
    POST /api/unlock {profile_id, user}
    GET  /api/changes?since=<ts>        -> incremental changes since ts
    GET/PUT /api/sync                   -> whole bundle (backward compatible)

Merge rule: last-writer-wins *per item* by the `updated` timestamp, so a
team member pushing one profile never overwrites someone else's edits to a
different profile (or the same one made later).
"""

import getpass
import json
import os
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from .cookies import load_cookies, save_cookies
from .profile import DATA_DIR, ProfileManager
from .proxies import ProxyPool
from .session import load_session, saved_at, save_session

SETTINGS_FILE = DATA_DIR / "settings.json"


class SyncError(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _epoch() -> float:
    return datetime.now(timezone.utc).timestamp()


def get_settings() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"sync_url": "", "sync_token": "", "user_name": "",
            "device_name": "", "auto_sync": True, "last_sync_at": 0.0}


def save_settings(**kw) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    s = get_settings()
    s.update(kw)
    SETTINGS_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def user_name() -> str:
    return get_settings().get("user_name") or getpass.getuser()


def device_name() -> str:
    return get_settings().get("device_name") or socket.gethostname()


def _request(method: str, url: str, payload=None, token: str = "",
             ok_statuses=()):
    req = urllib.request.Request(url, method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if e.code in ok_statuses:
            try:
                return json.loads(body) if body else {}
            except Exception:
                return {}
        raise SyncError(f"server returned {e.code}: {body[:300]}")
    except urllib.error.URLError as e:
        raise SyncError(f"cannot reach server: {e.reason}")


def _api(path: str) -> str:
    s = get_settings()
    if not s.get("sync_url"):
        raise SyncError("sync URL is not configured (set it in the Sync tab)")
    base = s["sync_url"].rstrip("/") + "/"
    return urljoin(base, path.lstrip("/"))


def _token() -> str:
    return get_settings().get("sync_token", "")


def is_configured() -> bool:
    return bool(get_settings().get("sync_url"))


# ---------------------------------------------------------------------------
# per-item push
# ---------------------------------------------------------------------------
def push_profile(profile_id: str) -> None:
    mgr = ProfileManager()
    p = mgr.get(profile_id)
    if p is None:
        return
    _request("PUT", _api(f"api/profiles/{profile_id}"),
             {"data": p, "user": user_name()}, _token())


def delete_profile(profile_id: str) -> None:
    _request("DELETE", _api(f"api/profiles/{profile_id}"), token=_token())


def push_cookies(profile_id: str) -> None:
    cs = load_cookies(profile_id)
    _request("PUT", _api(f"api/cookies/{profile_id}"),
             {"cookies": cs, "updated_at": _epoch()}, _token())


def push_session(profile_id: str) -> None:
    """Upload the profile's saved browsing session (tabs + login state)."""
    s = load_session(profile_id)
    if not s:
        return
    updated = float(s.get("saved_at") or _epoch())
    _request("PUT", _api(f"api/sessions/{profile_id}"),
             {"session": s, "updated_at": updated}, _token())


def pull_session(profile_id: str) -> bool:
    """Fetch the latest remote session for one profile and apply it locally
    if it is newer than what we already have. Returns True if applied."""
    try:
        res = _request("GET", _api(f"api/sessions/{profile_id}"), token=_token())
    except SyncError:
        raise
    except Exception:
        return False
    data = res.get("session")
    updated = float(res.get("updated_at") or 0)
    if data and updated > saved_at(profile_id):
        save_session(profile_id, data)
        return True
    return False


def _apply_remote_sessions(sessions: dict) -> int:
    """Merge remote sessions {pid: {data, updated_at}} into local storage."""
    count = 0
    for pid, sdata in (sessions or {}).items():
        data = sdata.get("data") if isinstance(sdata, dict) else sdata
        ts = float((sdata.get("updated_at") if isinstance(sdata, dict) else 0) or 0)
        if data and ts > saved_at(pid):
            save_session(pid, data)
            count += 1
    return count


def push_proxy(proxy_id: str) -> None:
    p = ProxyPool().get(proxy_id)
    if p is None:
        return
    _request("PUT", _api(f"api/proxies/{proxy_id}"), {"data": p}, _token())


def delete_proxy(proxy_id: str) -> None:
    _request("DELETE", _api(f"api/proxies/{proxy_id}"), token=_token())


# ---------------------------------------------------------------------------
# locks
# ---------------------------------------------------------------------------
def acquire_lock(profile_id: str) -> dict:
    """Try to exclusively lock a profile. Returns {ok:bool, locked_by, locked_device}.
    If ok is False, another team member currently has it open."""
    try:
        res = _request("POST", _api("api/lock"),
                       {"profile_id": profile_id,
                        "user": user_name(), "device": device_name()},
                       _token(), ok_statuses=(409,))
        if isinstance(res, dict) and res.get("ok"):
            return {"ok": True}
        return {"ok": False,
                "locked_by": (res or {}).get("locked_by", "another user"),
                "locked_device": (res or {}).get("locked_device", "another device")}
    except SyncError as e:
        raise e
    except Exception:
        return {"ok": True}  # if server unreachable, don't block local work


def release_lock(profile_id: str) -> None:
    try:
        _request("POST", _api("api/unlock"),
                 {"profile_id": profile_id, "user": user_name()}, _token())
    except Exception:
        pass


# ---------------------------------------------------------------------------
# full push / pull (manual buttons + after edits)
# ---------------------------------------------------------------------------
def push_all() -> dict:
    """Push every local profile, its cookies, and the whole proxy pool."""
    mgr = ProfileManager()
    profiles = mgr.list_profiles()
    for p in profiles:
        push_profile(p["id"])
        push_cookies(p["id"])
        push_session(p["id"])
    for pr in ProxyPool().list():
        push_proxy(pr["id"])
    return {"profiles": len(profiles), "cookies": len(profiles)}


def pull_all() -> dict:
    """Fetch the whole bundle and merge locally (per-item last-writer-wins).
    Returns counts of created/updated profiles and loaded cookie files."""
    s = get_settings()
    bundle = _request("GET", _api("api/sync"), token=_token())
    remote_profiles = bundle.get("profiles", []) or []
    remote_cookies = bundle.get("cookies", {}) or {}
    remote_proxies = bundle.get("proxies", []) or []
    remote_sessions = bundle.get("sessions", {}) or {}

    mgr = ProfileManager()
    local = {p["id"]: p for p in mgr.list_profiles()}
    created = updated = 0
    for rp in remote_profiles:
        pid = rp.get("id")
        if not pid:
            continue
        rp = dict(rp)
        rp.pop("id", None)
        rp.pop("updated_by", None)
        local_p = local.get(pid)
        if local_p is None or (rp.get("updated") or "") > (local_p.get("updated") or ""):
            mgr.upsert({"id": pid, **rp})
            created += local_p is None
            updated += local_p is not None
        cs = remote_cookies.get(pid)
        if cs:
            save_cookies(pid, cs)

    pool = ProxyPool()
    for rp in remote_proxies:
        if rp.get("id"):
            pool.upsert(rp)

    sessions = _apply_remote_sessions(remote_sessions)

    save_settings(last_sync_at=_epoch())
    return {"created": created, "updated": updated,
            "cookies": len(remote_cookies), "proxies": len(remote_proxies),
            "sessions": sessions}


# ---------------------------------------------------------------------------
# incremental auto-sync
# ---------------------------------------------------------------------------
def pull_changes() -> dict:
    """GET /api/changes since the last sync and apply them locally.
    Returns what changed: {created, updated, deleted, cookies, lock_changes}."""
    since = get_settings().get("last_sync_at") or 0.0
    try:
        bundle = _request("GET", _api(f"api/changes?since={since}"), token=_token())
    except SyncError:
        raise
    except Exception:
        return {"created": 0, "updated": 0, "deleted": 0,
                "cookies": 0, "sessions": 0, "locks": {}}

    mgr = ProfileManager()
    local = {p["id"]: p for p in mgr.list_profiles()}
    created = updated = deleted = 0

    for rp in bundle.get("profiles", []) or []:
        pid = rp.get("id")
        if not pid:
            continue
        if rp.get("deleted"):
            if pid in local:
                mgr.delete(pid)
                deleted += 1
            continue
        rp = dict(rp)
        rp.pop("id", None)
        for k in ("deleted", "updated_by"):
            rp.pop(k, None)
        local_p = local.get(pid)
        if local_p is None or (rp.get("updated") or "") > (local_p.get("updated") or ""):
            mgr.upsert({"id": pid, **rp})
            created += local_p is None
            updated += local_p is not None

    for pid, cs in (bundle.get("cookies", {}) or {}).items():
        data = cs.get("data") if isinstance(cs, dict) else cs
        if data:
            save_cookies(pid, data)

    sessions = _apply_remote_sessions(bundle.get("sessions", {}) or {})

    pool = ProxyPool()
    for rp in bundle.get("proxies", []) or []:
        if rp.get("id"):
            pool.upsert(rp)

    save_settings(last_sync_at=_epoch())

    locks = {}
    for p in bundle.get("profiles", []) or []:
        if p.get("deleted"):
            continue
        lb = p.get("locked_by")
        if isinstance(lb, dict) and lb.get("user"):
            locks[p["id"]] = {"locked_by": lb["user"],
                              "locked_device": lb.get("device", "")}
    return {"created": created, "updated": updated, "deleted": deleted,
            "cookies": len(bundle.get("cookies", {}) or {}),
            "sessions": sessions,
            "locks": locks}


def fetch_locks() -> dict:
    """Current lock state for every profile (for list badges and takeover
    detection). Returns {profile_id: {"locked_by", "locked_device"}}."""
    try:
        data = _request("GET", _api("api/profiles"), token=_token())
    except Exception:
        return {}
    locks = {}
    for p in data.get("profiles", []) or []:
        lb = p.get("locked_by")
        if isinstance(lb, dict) and lb.get("user"):
            locks[p["id"]] = {"locked_by": lb["user"],
                              "locked_device": lb.get("device", "")}
    return locks


# backward-compatible aliases
def push() -> dict:
    return push_all()


def pull() -> dict:
    return pull_all()
