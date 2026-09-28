"""Launch a headed Camoufox (patched Firefox) browser for a single profile.

The fingerprint is applied natively by the Camoufox engine (via Firefox
preferences + a launch config delivered through the environment), mirroring
how GoLogin's Orbita engine works. There is no CDP / JS init-script spoofing;
the engine patches navigator.*, screen, timezone, locale, fonts, canvas and
audio noise at the browser level.

A tiny local HTTP server exposes the live persistent context for cookie
export / import while the browser is running (replaces the old CDP port).
"""

import hashlib
import json
import os
import signal
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from camoufox.sync_api import NewBrowser
from playwright.sync_api import sync_playwright

from .cookies import save_cookies
from .geo import apply_geo, detect_proxy_geo
from .passkey import PasskeyManager, install as install_passkey
from .totp import TOTPManager, install as install_totp
from .profile import DEFAULT_START_URL, ProfileManager
from .proxies import ProxyPool
from .session import capture, restore
from .sync import is_configured, push_session

CONTROL_PORT_BASE = 9200
CONTROL_PORT_RANGE = 1000


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def control_port_for(profile_id: str) -> int:
    """Deterministic localhost port for the profile's cookie control server."""
    digest = int(hashlib.md5(profile_id.encode()).hexdigest(), 16)
    port = CONTROL_PORT_BASE + (digest % CONTROL_PORT_RANGE)
    for _ in range(CONTROL_PORT_RANGE):
        if _port_free(port):
            return port
        port = CONTROL_PORT_BASE + (port - CONTROL_PORT_BASE + 1) % CONTROL_PORT_RANGE
    return CONTROL_PORT_BASE


def _bundle_resources() -> Path | None:
    """Locate the directory holding the bundled Camoufox.app inside a
    PyInstaller bundle. sys._MEIPASS points at Contents/Frameworks in
    onedir mode, while the browser is copied to Contents/Resources."""
    d = Path(sys._MEIPASS)
    for _ in range(6):
        for cand in (d / "Resources", d):
            if (cand / "Camoufox.app").is_dir():
                return cand
        d = d.parent
    return None


def _os_for(fp: dict) -> str:
    p = (fp.get("platform") or "").lower()
    if "mac" in p:
        return "macos"
    if "win" in p:
        return "windows"
    if "linux" in p or "x11" in p:
        return "linux"
    return "windows"


def _screen_config(fp: dict) -> dict:
    """Pin the JS-visible screen / window geometry to the stored fingerprint.

    The Camoufox engine fills in everything else (UA, fonts, canvas/audio
    noise, WebGL) natively; we only override the dimensions so a profile
    reports the same screen every launch, like GoLogin.
    """
    w = int(fp.get("screen_width") or 1920)
    h = int(fp.get("screen_height") or 1080)
    depth = int(fp.get("color_depth") or 24)
    scale = float(fp.get("device_scale_factor") or 1.0)
    win_w = min(w, 1366)
    win_h = min(h, 850)
    return {
        "timezone": fp.get("timezone") or "UTC",
        "screen.width": w,
        "screen.availWidth": w,
        "screen.height": h,
        "screen.availHeight": max(h - 33, 1),
        "screen.colorDepth": depth,
        "screen.pixelDepth": depth,
        "window.devicePixelRatio": scale,
        "window.outerWidth": win_w,
        "window.outerHeight": win_h,
        "window.screenX": (w - win_w) // 2,
        "window.screenY": (h - win_h) // 2,
    }


def _camoufox_options(fp: dict, proxy: dict | None, user_data_dir: str,
                      downloads_dir: Path) -> dict:
    """Build launch_options() kwargs for a profile fingerprint.

    Pinning the screen/window/timezone/locale ourselves is intentional
    (GoLogin-style stable per-profile fingerprint), so the Camoufox
    LeakWarnings are silenced via i_know_what_im_doing.
    """
    from camoufox.sync_api import launch_options

    locale = fp.get("languages") or [fp.get("language") or "en-US"]
    kwargs = {
        "os": _os_for(fp),
        "locale": locale,
        "config": _screen_config(fp),
        "humanize": True,
        "headless": False,
        "user_data_dir": user_data_dir,
        "i_know_what_im_doing": True,
        # Capture every download so we can persist it to the profile's own
        # downloads folder with the original filename (Playwright's default
        # would write to a temp dir that is wiped when the browser closes).
        "accept_downloads": True,
        # Session restore behaviour:
        #  - never let Firefox auto-restore a previous (unclean) session, our
        #    own session restore is the single source of truth
        #  - route "open in new window" links / window.open to new tabs so the
        #    restored tabs stay in one window instead of spawning new ones
        "firefox_user_prefs": {
            "browser.sessionstore.resume_from_crash": False,
            "browser.sessionstore.resume_session_once": False,
            "browser.sessionstore.resume_restore_on_new_window": False,
            "browser.link.open_newwindow": 3,
            "browser.link.open_newwindow.restriction": 0,
            "browser.tabs.allowTabDetach": False,
            # if the engine ever hands a download back to Firefox instead of
            # Playwright, still land it in the profile's downloads folder
            "browser.download.folderList": 2,
            "browser.download.dir": str(downloads_dir),
            "browser.download.useDownloadDir": True,
            "browser.download.manager.showWhenStarting": True,
        },
    }
    if proxy:
        kwargs["proxy"] = proxy

    if getattr(sys, "frozen", False):
        # Bundled build: point the engine at the Camoufox.app inside Resources,
        # use the bundled uBlock Origin addon, and pin the engine version so no
        # Camoufox install/cache lookup is needed on the target machine.
        from camoufox.addons import DefaultAddons

        kwargs["exclude_addons"] = [DefaultAddons.UBO]
        kwargs["ff_version"] = 152
        resources = _bundle_resources()
        if resources is not None:
            addon_dir = resources / "addons" / "UBO"
            if addon_dir.is_dir():
                kwargs["addons"] = [str(addon_dir)]
            from camoufox.utils import launch_path

            try:
                kwargs["executable_path"] = launch_path(resources)
                print(f"[launcher] bundled engine: {kwargs['executable_path']}", flush=True)
            except Exception as e:
                print(f"[launcher] bundled engine lookup failed: {e}", flush=True)
        else:
            print("[launcher] warning: bundled Camoufox.app not found", flush=True)

    # Build the full launch options (engine config, env, prefs, executable).
    # i_know_what_im_doing is only a launcher flag - strip it so Playwright
    # never receives it via from_options.
    from_options = launch_options(**kwargs)
    from_options.pop("i_know_what_im_doing", None)
    return from_options


class _CookieRPC:
    """Marshals cookie requests from the HTTP server thread to the Playwright
    thread. Playwright's sync API is not thread-safe, so the control server
    only queues requests; the launcher's main loop executes them."""

    def __init__(self):
        self._lock = threading.Lock()
        self._context = None
        self._queue = []
        self._results = {}
        self._seq = 0
        self._closed = False
        self._stop = False

    def set_context(self, context) -> None:
        self._context = context

    @property
    def stop_requested(self) -> bool:
        with self._lock:
            return self._stop or self._closed

    def request_stop(self) -> None:
        with self._lock:
            self._stop = True

    def request(self, op: str, payload):
        with self._lock:
            if self._closed:
                raise RuntimeError("browser is shutting down")
            self._seq += 1
            rid = self._seq
            ev = threading.Event()
            self._queue.append((rid, op, payload, ev))
            self._results[rid] = None
        ev.wait(timeout=15)
        with self._lock:
            res, err = self._results.pop(rid)
        if err:
            raise err
        return res

    def pump(self) -> None:
        """Called from the main (Playwright) thread."""
        with self._lock:
            items = list(self._queue)
            self._queue.clear()
        for rid, op, payload, ev in items:
            res, err = None, None
            try:
                ctx = self._context
                if op == "export":
                    res = ctx.cookies() if ctx else []
                elif op == "import":
                    if ctx:
                        ctx.add_cookies(payload)
                    res = True
                elif op == "stop":
                    self._stop = True
                    res = True
            except Exception as e:  # pragma: no cover - defensive
                err = e
            with self._lock:
                self._results[rid] = (res, err)
            ev.set()

    def close(self) -> None:
        with self._lock:
            self._closed = True
            pending = list(self._queue)
            self._queue.clear()
        for rid, op, payload, ev in pending:
            with self._lock:
                self._results[rid] = (None, RuntimeError("browser closed"))
            ev.set()


class _ControlHandler(BaseHTTPRequestHandler):
    rpc = None

    def _json(self, status: int, body: dict | list):
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.rstrip("/") == "/cookies":
            try:
                self._json(200, self.rpc.request("export", None))
            except Exception as e:
                self._json(503, {"error": str(e)})
        else:
            self._json(404, {"error": "not found"})

    def do_PUT(self):
        if self.path.rstrip("/") == "/cookies":
            length = int(self.headers.get("Content-Length") or 0)
            try:
                cookies = json.loads(self.rfile.read(length) or b"[]")
                self.rpc.request("import", cookies)
                self._json(200, {"ok": True})
            except Exception as e:
                self._json(400, {"error": str(e)})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") == "/stop":
            self.rpc.request_stop()
            self._json(200, {"ok": True})
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *args):
        pass


class _ControlServer:
    def __init__(self, port: int):
        self.rpc = _CookieRPC()
        handler = type("Handler", (_ControlHandler,), {"rpc": self.rpc})
        self.httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def shutdown(self) -> None:
        self.rpc.close()
        self.httpd.shutdown()
        self.httpd.server_close()


def _profile_title_prefix(profile: dict) -> str:
    name = (profile.get("name") or "").strip()
    if not name:
        name = profile.get("id", "profile")[:8]
    return f"{name} · "


def _tag_title(page, prefix: str) -> None:
    """Prefix the page title with the profile name so macOS Dock window
    thumbnails / hover tooltips identify each running profile."""
    try:
        page.evaluate(
            "(P) => { const t = document.title;"
            " if (t && !t.startsWith(P)) document.title = P + t; }",
            prefix,
        )
    except Exception:
        pass


def _watch_page_titles(context, prefix: str, page) -> None:
    def _on_frame(f):
        if f == page.main_frame:
            _tag_title(page, prefix)
    try:
        page.on("framenavigated", _on_frame)
        page.on("load", _on_frame)
    except Exception:
        pass


def launch(profile_id: str) -> None:
    mgr = ProfileManager()
    profile = mgr.get(profile_id)
    if not profile:
        print(f"[launcher] profile not found: {profile_id}", flush=True)
        sys.exit(1)

    fp = dict(profile["fingerprint"])
    proxy = ProxyPool().resolve(profile)
    geo = detect_proxy_geo(proxy)
    fp = apply_geo(fp, geo, profile.get("proxy_country", ""))
    if fp.get("_geo_country"):
        print(f"[launcher] geo-aligned: country={fp['_geo_country']} "
              f"timezone={fp['timezone']} language={fp['language']}", flush=True)

    port = profile.get("control_port") or profile.get("cdp_port") or 0
    if not port or not _port_free(port):
        # stored port is stale / taken by another process -> pick a free one
        port = control_port_for(profile_id)
    mgr.update(profile_id, {"control_port": port, "launch_pid": os.getpid()})

    user_data_dir = str(mgr.profile_dir(profile_id) / "context")
    downloads_dir = mgr.profile_dir(profile_id) / "downloads"
    os.makedirs(downloads_dir, exist_ok=True)
    options = _camoufox_options(fp, proxy, user_data_dir, downloads_dir)

    control = _ControlServer(port)
    control.start()

    def _signal_handler(signum, frame):
        # Playwright sync calls can't be interrupted mid-flight, so set a
        # flag instead; the main loop exits on the next tick.
        control.rpc.request_stop()
        print(f"[launcher] signal {signum}: stopping", flush=True)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    with sync_playwright() as p:
        context = None
        try:
            print(f"[launcher] engine: Camoufox (Firefox) control port={port}", flush=True)
            context = NewBrowser(p, persistent_context=True, from_options=options)
            control.rpc.set_context(context)

            if PasskeyManager.is_enabled(profile):
                install_passkey(context, profile_id)
            if TOTPManager.is_enabled(profile):
                install_totp(context, profile_id)

            pending_downloads = []

            def _on_download(d):
                pending_downloads.append(d)

            try:
                context.on("download", _on_download)
            except Exception:
                pass

            restore(context, profile_id,
                    profile.get("start_url") or DEFAULT_START_URL)

            title_prefix = _profile_title_prefix(profile)
            for pg in context.pages:
                _tag_title(pg, title_prefix)
                _watch_page_titles(context, title_prefix, pg)
            try:
                context.on("page", lambda p: (
                    _tag_title(p, title_prefix),
                    _watch_page_titles(context, title_prefix, p),
                ))
            except Exception:
                pass

            page = context.pages[0] if context.pages else context.new_page()
            try:
                print("[launcher] browser timezone="
                      f"{page.evaluate('Intl.DateTimeFormat().resolvedOptions().timeZone')} "
                      f"language={page.evaluate('navigator.language')} "
                      f"screen={page.evaluate('screen.width')}x"
                      f"{page.evaluate('screen.height')} "
                      f"dpr={page.evaluate('devicePixelRatio')}", flush=True)
            except Exception:
                pass

            browser = context.browser
            last_save = time.time()
            last_tag = time.time()
            while browser and browser.is_connected() and not control.rpc.stop_requested:
                time.sleep(0.2)
                control.rpc.pump()
                if time.time() - last_tag > 5:
                    for pg in context.pages:
                        _tag_title(pg, title_prefix)
                    last_tag = time.time()
                if time.time() - last_save > 30:
                    try:
                        cookies = context.cookies()
                        if cookies:
                            save_cookies(profile_id, cookies)
                    except Exception:
                        pass
                    last_save = time.time()
                if pending_downloads:
                    d = pending_downloads.pop(0)
                    try:
                        fname = os.path.basename(d.suggested_filename or "download")
                        stem = Path(fname).stem or "download"
                        ext = Path(fname).suffix
                        dest = downloads_dir / fname
                        n = 1
                        while dest.exists():
                            dest = downloads_dir / f"{stem} ({n}){ext}"
                            n += 1
                        d.save_as(str(dest))
                        print(f"[launcher] download saved: {dest}", flush=True)
                    except Exception as e:
                        print(f"[launcher] download save failed: {e}", flush=True)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"[launcher] error: {e}", flush=True)
        finally:
            control.rpc.pump()
            if context is not None:
                try:
                    capture(context, profile_id)
                    print("[launcher] session captured", flush=True)
                except Exception as e:
                    print(f"[launcher] session capture failed: {e}", flush=True)
                try:
                    context.close()
                except Exception:
                    pass
            mgr.update(profile_id, {"launch_pid": None})

    control.shutdown()

    if is_configured():
        try:
            push_session(profile_id)
            print("[launcher] session pushed to cloud", flush=True)
        except Exception as e:
            print(f"[launcher] session push failed: {e}", flush=True)
    print("[launcher] browser closed", flush=True)


if __name__ == "__main__":
    launch(sys.argv[1])
