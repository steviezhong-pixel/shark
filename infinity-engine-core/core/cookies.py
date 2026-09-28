"""Cookie export / import. Cookies are stored as JSON per profile and
auto-imported on browser launch / auto-exported on close.

While the browser is running, the launcher exposes a small local HTTP server
(on the profile's control port) that proxies cookie reads / writes to the live
persistent context.
"""

import json
import urllib.request
from pathlib import Path

from .profile import DATA_DIR

COOKIES_DIR = DATA_DIR / "cookies"


def cookies_file(profile_id: str) -> Path:
    return COOKIES_DIR / f"{profile_id}.json"


def load_cookies(profile_id: str) -> list:
    f = cookies_file(profile_id)
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_cookies(profile_id: str, cookies: list) -> Path:
    COOKIES_DIR.mkdir(parents=True, exist_ok=True)
    f = cookies_file(profile_id)
    f.write_text(json.dumps(cookies, indent=2, ensure_ascii=False), encoding="utf-8")
    return f


def _request(port: int, method: str, payload: list | None = None) -> list:
    url = f"http://127.0.0.1:{port}/cookies"
    data = json.dumps(payload or []).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def export_from_running(port: int) -> list:
    """Read cookies from the running browser via its control server.
    Does NOT close the browser."""
    return _request(port, "GET")


def import_to_running(port: int, cookies: list) -> None:
    """Inject cookies into the running browser via its control server.
    Does NOT close the browser."""
    _request(port, "PUT", cookies)
