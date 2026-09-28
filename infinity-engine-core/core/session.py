"""Browser session persistence: open tabs + login state (cookies & localStorage).

A "session" is captured when a profile's browser shuts down and restored when
it launches again — including on a different device via cloud sync.  The disk
HTTP cache itself is not synced (it is transient and not needed for login), but
cookies + localStorage cover the actual login state, and the tab list restores
the same pages.

File layout: data/sessions/<profile_id>.json
    {
      "saved_at": <epoch seconds>,
      "tabs":     [{"url": "...", "title": "..."}, ...],
      "storage":  <Playwright context.storage_state() output: cookies + origins/localStorage>
    }
"""

import json
import time
from pathlib import Path

from .profile import DATA_DIR, DEFAULT_START_URL

SESSIONS_DIR = DATA_DIR / "sessions"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"

MAX_RESTORE_TABS = 10
MAX_SNAPSHOT_BYTES = 300_000


def session_file(profile_id: str) -> Path:
    return SESSIONS_DIR / f"{profile_id}.json"


def load_session(profile_id: str) -> dict | None:
    f = session_file(profile_id)
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_session(profile_id: str, session: dict) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    f = session_file(profile_id)
    f.write_text(json.dumps(session, ensure_ascii=False), encoding="utf-8")
    return f


def saved_at(profile_id: str) -> float:
    s = load_session(profile_id)
    return float(s.get("saved_at", 0)) if s else 0.0


def snapshot_file(profile_id: str) -> Path:
    return SNAPSHOTS_DIR / f"{profile_id}.json"


def load_snapshots(profile_id: str) -> dict:
    f = snapshot_file(profile_id)
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_snapshots(profile_id: str, snapshots: dict) -> Path:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    f = snapshot_file(profile_id)
    f.write_text(json.dumps(snapshots, ensure_ascii=False), encoding="utf-8")
    return f


def _session_tabs(context) -> list:
    try:
        tabs = []
        for p in context.pages:
            url = (p.url or "").strip()
            if not url or url == "about:blank":
                continue
            tabs.append({"url": url, "title": (p.title() or "")[:200]})
        return tabs
    except Exception:
        return []


def capture(context, profile_id: str, saved_at_ts: float | None = None) -> dict:
    """Snapshot the running context into a session dict and write it to disk.

    Also writes a local-only HTML snapshot of each open tab so a later restore
    can paint the pages instantly instead of blank tabs. Snapshots stay on the
    device (they are not uploaded to the cloud sync server).
    """
    state = context.storage_state()
    session = {
        "saved_at": saved_at_ts if saved_at_ts is not None else time.time(),
        "tabs": _session_tabs(context),
        "storage": state,
    }
    save_session(profile_id, session)
    try:
        pages = []
        for p in context.pages:
            url = (p.url or "").strip()
            if not url or url == "about:blank":
                continue
            try:
                html = p.content()
                if len(html) > MAX_SNAPSHOT_BYTES:
                    html = html[:MAX_SNAPSHOT_BYTES]
            except Exception:
                html = ""
            pages.append({"url": url, "html": html})
        save_snapshots(profile_id, {"saved_at": session["saved_at"], "pages": pages})
    except Exception as e:
        print(f"[launcher] snapshot capture failed: {e}", flush=True)
    return session


def restore(context, profile_id: str, start_url: str) -> None:
    """Apply a saved session to a freshly-created context:
    cookies + localStorage first, then reopen the saved tabs."""
    session = load_session(profile_id)
    storage = (session or {}).get("storage") or {}

    cookies = storage.get("cookies") or []
    if cookies:
        try:
            context.add_cookies(cookies)
        except Exception as e:
            print(f"[launcher] session cookie restore failed: {e}", flush=True)

    origins = storage.get("origins") or []
    storage_map = {}
    for o in origins:
        kv = o.get("localStorage") or []
        if kv and o.get("origin"):
            storage_map[o["origin"]] = {item["name"]: item["value"] for item in kv}

    tabs = (session or {}).get("tabs") or []
    urls = [t["url"] for t in tabs if isinstance(t, dict) and (t.get("url") or "").startswith(("http://", "https://"))]
    if not urls:
        urls = [start_url or DEFAULT_START_URL]
    urls = urls[:MAX_RESTORE_TABS]

    snap = load_snapshots(profile_id)
    html_by_url = {pg["url"]: pg["html"] for pg in snap.get("pages", []) if pg.get("html")}

    pages = context.pages
    # Drop any pages Firefox auto-restored from a previous (possibly unclean)
    # shutdown so our session restore doesn't stack extra windows/tabs on top.
    for extra in pages[1:]:
        try:
            extra.close()
        except Exception:
            pass
    first = context.pages[0] if context.pages else context.new_page()
    _restore_into(first, urls[0], html_by_url.get(urls[0]))
    _apply_storage(first, storage_map)
    for u in urls[1:]:
        try:
            page = _open_tab(context, first, u)
            _restore_into(page, u, html_by_url.get(u))
            _apply_storage(page, storage_map)
        except Exception as e:
            print(f"[launcher] tab restore failed: {e}", flush=True)


def _apply_storage(page, storage_map: dict) -> None:
    """Write the saved localStorage for the page's origin once, after load.
    (An init script would re-apply the snapshot on every navigation and
    clobber values the user changed during the session.)"""
    if not storage_map:
        return
    try:
        page.evaluate(
            "((MAP) => {"
            "  const kv = MAP[location.origin];"
            "  if (kv) { for (const k in kv) { try { localStorage.setItem(k, kv[k]); } catch (e) {} } }"
            "})(" + json.dumps(storage_map) + ")"
        )
    except Exception:
        pass


def _open_tab(context, opener, url: str):
    """Open a new tab in the opener's window (not a separate window).

    Firefox routes window.open('_blank') to a tab in the current window when
    the browser.link.open_newwindow prefs are set; new_page() would open a
    brand-new window on a real display. Falls back to new_page() if the popup
    is blocked.
    """
    page = None
    try:
        with context.expect_page(timeout=3000) as pinfo:
            ok = opener.evaluate(
                "(u) => { try { const w = window.open(u, '_blank'); return !!w; } catch (e) { return false; } }",
                url)
            if ok:
                page = pinfo.value
    except Exception:
        page = None
    if page is None:
        page = context.new_page()
    return page


def _restore_into(page, url: str, html: str | None) -> None:
    """Paint the last-seen HTML snapshot instantly, then load the live page."""
    if html:
        try:
            page.set_content(html, wait_until="commit", timeout=15000)
        except Exception as e:
            print(f"[launcher] snapshot show failed: {e}", flush=True)
    _goto(page, url)


def _goto(page, url: str) -> None:
    try:
        page.goto(url, timeout=30000, wait_until="commit")
    except Exception as e:
        print(f"[launcher] goto {url} failed: {e}", flush=True)
