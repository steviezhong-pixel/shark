"""In-app self-update.

Flow:  check the sync server for a newer build -> download the .app zip ->
verify sha256 -> write a detached helper that swaps the running app bundle
for the new one and relaunches.  Requires the packaged (PyInstaller) app;
no-ops in dev mode.
"""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

from .profile import BASE_DIR
from .sync import _request, _token

APP_NAME = "Infinity Lines"
UPDATES_DIR = BASE_DIR / "updates"


class UpdateError(Exception):
    pass


def current_version() -> str:
    """Version shown to the user (read from the bundle's Info.plist)."""
    if getattr(sys, "frozen", False):
        try:
            import plistlib
            info = Path(sys.executable).resolve().parent.parent / "Info.plist"
            with open(info, "rb") as f:
                v = plistlib.load(f).get("CFBundleShortVersionString")
            if v:
                return str(v)
        except Exception:
            pass
    from .version import VERSION
    return VERSION


def app_bundle_path() -> Path:
    """Absolute path to the running .app bundle (Contents/MacOS/<exe> -> .app)."""
    if not getattr(sys, "frozen", False):
        raise UpdateError("update only works in the packaged app")
    return Path(sys.executable).resolve().parent.parent.parent


def _update_base() -> str:
    from .sync import get_settings, is_configured
    if not is_configured():
        raise UpdateError("cloud sync is not configured (set the server URL first)")
    return get_settings()["sync_url"].rstrip("/") + "/api/update"


def fetch_latest() -> dict | None:
    """Query the server for the newest build metadata.
    Returns {version, url, sha256, notes} or None if none is published."""
    try:
        res = _request("GET", _update_base() + "/latest", token=_token())
    except Exception:
        return None
    if not isinstance(res, dict) or not res.get("version"):
        return None
    return res


def _download(url: str, dest: Path, token: str) -> None:
    import urllib.request
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=120) as resp:
        with open(dest, "wb") as f:
            shutil.copyfileobj(resp, f, length=1024 * 1024)


def download_update(meta: dict) -> Path:
    """Download the app zip for `meta` and verify its sha256. Returns the path."""
    from urllib.parse import urljoin
    url = urljoin(_update_base() + "/", meta.get("url") or "")
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPDATES_DIR / f"update-{meta.get('version')}.zip"
    _download(url, dest, _token())
    sha = (meta.get("sha256") or "").lower()
    if sha:
        h = hashlib.sha256()
        with open(dest, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        if h.hexdigest() != sha:
            dest.unlink(missing_ok=True)
            raise UpdateError("download checksum mismatch - update aborted")
    return dest


def prepare_install(zip_path: Path) -> Path:
    """Write the detached swap helper scripts; returns the entry helper path.

    install_update.sh (user level) tries the swap directly, then falls back to
    osascript with administrator privileges (prompts once), then relaunches.
    """
    app_dir = app_bundle_path()
    dest_dir = app_dir.parent
    app_name = app_dir.name
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)

    root_helper = UPDATES_DIR / "install_root.sh"
    root_helper.write_text(
        '#!/bin/bash\n'
        'set -e\n'
        f'APP_DIR="{app_dir}"\n'
        'TMP="/tmp/InfinityLinesUpdate.$$"\n'
        'rm -rf "$TMP"\n'
        'mkdir -p "$TMP"\n'
        f'ditto -x -k "{zip_path}" "$TMP"\n'
        'rm -rf "$APP_DIR"\n'
        f'cp -R "$TMP/{app_name}" "{dest_dir}/"\n'
        'rm -rf "$TMP"\n',
        encoding="utf-8",
    )
    root_helper.chmod(0o755)

    entry = UPDATES_DIR / "install_update.sh"
    entry.write_text(
        '#!/bin/bash\n'
        'sleep 2\n'
        f'APP_DIR="{app_dir}"\n'
        'TMP="/tmp/InfinityLinesUpdate.$$"\n'
        'rm -rf "$TMP"\n'
        'mkdir -p "$TMP"\n'
        f'ditto -x -k "{zip_path}" "$TMP"\n'
        f'NEW="$TMP/{app_name}"\n'
        'if rm -rf "$APP_DIR" 2>/dev/null && cp -R "$NEW" "{dest_dir}/" 2>/dev/null; then\n'
        '  :\n'
        'else\n'
        f'  osascript -e "do shell script \\"bash \'{root_helper}\'\\" with administrator privileges"\n'
        'fi\n'
        'xattr -dr com.apple.quarantine "$APP_DIR" 2>/dev/null || true\n'
        'rm -rf "$TMP"\n'
        f'open -a "{app_name[:-4]}"\n',
        encoding="utf-8",
    )
    entry.chmod(0o755)
    return entry


def spawn_install(entry: Path) -> None:
    """Detach the helper so it survives the app quitting, then let the GUI exit."""
    subprocess.Popen(
        ["/bin/bash", str(entry)],
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
