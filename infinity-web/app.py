#!/usr/bin/env python3
"""infinity-web — Web UI to launch & remote-control fingerprinted browsers
(Camoufox via the Infinity Lines core) as browser TABS, over noVNC.

Security model:
  * App binds 127.0.0.1 only; nginx (TLS) is the only public gateway.
  * Every route starts with /browser/<INFINITY_WEB_TOKEN>/ …; without the
    exact token, requests return 404 (the browser never learns it is there).
  * noVNC websocket goes through nginx under /browser/<TOK>/ws/<PORT>/ ->
      proxy_pass http://127.0.0.1:<PORT>; so no extra security-group ports.

Env:
  INFINITY_WEB_TOKEN  required (same value as systemd)
  INFINITY_WEB_ROOT   dir containing main.py + core/ (Infinity Lines repo)
  INFINITY_WEB_DATA   working dir for Xvfb/logs/cookies
  INFINITY_WEB_MAX_R  max concurrent browser instances (default 2)
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

TOKEN = os.environ.get("INFINITY_WEB_TOKEN", "").strip()
ROOT = Path(os.environ.get("INFINITY_WEB_ROOT", "/home/ubuntu/infinity-lines"))
DATA = Path(os.environ.get("INFINITY_WEB_DATA", "/home/ubuntu/infinity-web-data"))
MAX_R = int(os.environ.get("INFINITY_WEB_MAX_R", "2"))
STATIC = Path(__file__).resolve().parent / "static"
NOVNC = Path("/usr/share/novnc")
PORT = int(os.environ.get("PORT", "9001"))

if not TOKEN:
    print("FATAL: INFINITY_WEB_TOKEN not set", file=sys.stderr)
    sys.exit(1)
DATA.mkdir(parents=True, exist_ok=True)
(DATA / "cookies").mkdir(exist_ok=True)

BASE_X = 90        # Xvfb display numbers start here
BASE_WS = 6100     # websockify ports; slot i => BASE_WS + i
SLOTS = list(range(int(MAX_R)))

sessions = {}      # profile -> {"slot": n, "x": d, "ws": port, "procs": []}
lock = threading.Lock()


def acquire_slot():
    with lock:
        used = {s["slot"] for s in sessions.values()}
        for slot in SLOTS:
            if slot not in used:
                return slot
    return None


def launch(profile: str) -> dict:
    if not profile or "/" in profile or len(profile) > 64:
        return {"ok": False, "error": "invalid profile"}
    slot = acquire_slot()
    if slot is None:
        return {"ok": False, "error": f"all {MAX_R} slots busy — stop a browser first"}
    x = BASE_X + slot
    ws_port = BASE_WS + slot
    rfb = 5900 + slot  # Xvfb rfb port

    procs = []
    try:
        rfbpath = DATA / f"X{slot}-rfbUnix"
        if rfbpath.exists():
            rfbpath.unlink()
        xvfb = subprocess.Popen(
            ["Xvfb", f":{x}", "-screen", "0", "1440x900x24",
             "-nolisten", "tcp", "-rfbport", str(rfb)],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
        )
        time.sleep(0.4)
        webify = subprocess.Popen(
            ["websockify", "127.0.0.1:" + str(ws_port), "127.0.0.1:" + str(rfb)],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
        )
        procs += [xvfb, webify]
        time.sleep(0.4)

        env = os.environ.copy()
        env["DISPLAY"] = f":{x}"
        main_py = ROOT / "main.py"
        if not main_py.exists():
            return {"ok": False, "error": "Infinity Lines main.py not found"}
        browser = subprocess.Popen(
            [str(ROOT / ".venv" / "bin" / "python"), str(main_py), "--launch-profile", profile],
            cwd=str(ROOT), env=env,
            stdout=open(DATA / f"{profile}.log", "ab"),
            stderr=subprocess.STDOUT,
        )
        procs.append(browser)
    except Exception as e:
        for p in procs:
            try: p.kill()
            except Exception: pass
        return {"ok": False, "error": str(e)}

    with lock:
        sessions[profile] = {"slot": slot, "x": x, "ws": ws_port, "rfb": rfb, "procs": procs}
    return {"ok": True, "ws": ws_port, "display": x}


def stop(profile: str) -> dict:
    with lock:
        s = sessions.pop(profile, None)
    if not s:
        return {"ok": True, "not_running": True}
    pgids = []
    for p in s["procs"]:
        try: os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            try: p.terminate()
            except Exception: pass
    time.sleep(1.5)
    for p in s["procs"]:
        try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            try: p.kill()
            except Exception: pass
    f = Path(f"/tmp/.X11-unix/X{s['x']}")
    if f.exists():
        try: f.unlink()
        except Exception: pass
    return {"ok": True}


def cookie_path(profile):
    folder = DATA / "cookies"
    folder.mkdir(exist_ok=True)
    safe = "".join(c for c in profile if c.isalnum() or c in "-_")
    return folder / f"{safe}.json"


def send_json(h, code, obj):
    b = json.dumps(obj).encode()
    h.send_response(code)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(b)))
    h.send_header("Cache-Control", "no-store")
    h.end_headers()
    h.wfile.write(b)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *a):
        pass

    def _token_path(self):
        """Return the sub-path after /browser/<TOKEN>/ or None (404s out)."""
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        if len(parts) >= 2 and parts[0] == "browser" and parts[1] == TOKEN:
            return "/".join(parts[2:])
        return None

    def _send_bytes(self, data, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        sub = self._token_path()
        if sub is None:
            return self.send_error(404)

        if sub in ("", "index.html"):
            return self._file(STATIC / "index.html", "text/html; charset=utf-8")
        if sub == "health":
            prof = {k: {"display": v["x"], "ws": v["ws"]} for k, v in sessions.items()}
            return send_json(self, 200, {"ok": True, "sessions": prof})

        if sub.startswith("vnc/"):
            rel = sub[len("vnc/"):].split("?")[0].split("#")[0] or "vnc.html"
            f = NOVNC / rel
            if not f.is_file():
                return self.send_error(404)
            ctype = {"html": "text/html; charset=utf-8",
                     "js": "text/javascript", "css": "text/css",
                     "ico": "image/x-icon"}.get(rel.rsplit(".", 1)[-1],
                                                  "application/octet-stream")
            return self._send_bytes(f.read_bytes(), ctype)

        if sub.startswith("ws/") and sub[3:].strip("/").isdigit():
            port = int(sub[3:].strip("/"))
            if BASE_WS <= port < BASE_WS + MAX_R:
                # nginx upgrades to websocket against 127.0.0.1:<port>
                return self.proxy_ws(port)
        return self.send_error(404)

    def proxy_ws(self, port):
        # nginx handles the WebSocket upgrade itself; this app never sees it.
        # Kept for completeness in case someone binds this route on TTL tests.
        return self.send_error(501)

    def do_POST(self):
        sub = self._token_path()
        if sub is None:
            return self.send_error(404)
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = {}
        if length:
            try: body = json.loads(self.rfile.read(length))
            except Exception: return self.send_error(400)

        if sub == "api/launch":
            return send_json(self, 200,
                             launch(str(body.get("profile", ""))[:64]))
        if sub == "api/stop":
            return send_json(self, 200, stop(str(body.get("profile", ""))))
        if sub == "cookies/export":
            p = DATA / "cookies" / f"{str(body.get('profile',''))[:64]}.json"
            if not p.exists():
                return send_json(self, 404, {"error": "no cookies saved"})
            try:
                return send_json(self, 200, json.loads(p.read_text()))
            except Exception:
                return send_json(self, 500, {"error": "unreadable cookie file"})
        if sub == "cookies/import":
            prof = str(body.get("profile", ""))[:64]
            jar = body.get("cookies")
            if prof and isinstance(jar, (dict, list)):
                (DATA / "cookies").mkdir(exist_ok=True)
                (DATA / "cookies" / ("".join(
                    c for c in prof if c.isalnum() or c in "-_") + ".json")
                 ).write_text(json.dumps(jar))
                return send_json(self, 200, {"ok": True})
            return send_json(self, 400, {"error": "profile/cookies required"})
        if sub == "sessions":
            return send_json(self, 200, {k: {"display": v["x"], "ws": v["ws"]}
                                          for k, v in sessions.items()})
        self.send_error(404)

    def _file(self, f, ctype):
        if not f or not f.is_file():
            return self.send_error(404)
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print(f"infinity-web listening on 127.0.0.1:{PORT} (token len={len(TOKEN)})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
