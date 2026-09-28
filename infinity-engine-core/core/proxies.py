"""Proxy pool management: a reusable list of proxies profiles can reference."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .profile import DATA_DIR

PROXIES_FILE = DATA_DIR / "proxies.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProxyPool:
    def __init__(self, file=None):
        self.file = Path(file) if file else PROXIES_FILE
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.file.exists():
            self._save([])

    def _load(self) -> list:
        return json.loads(self.file.read_text(encoding="utf-8"))

    def _save(self, data: list) -> None:
        self.file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def list(self) -> list:
        return self._load()

    def get(self, proxy_id: str):
        for p in self._load():
            if p["id"] == proxy_id:
                return p
        return None

    def add(self, name: str, type_: str, host: str, port: int,
            username: str = "", password: str = "", extra: dict = None) -> dict:
        proxies = self._load()
        proxy = {
            "id": str(uuid.uuid4()),
            "name": name,
            "type": type_,
            "host": host,
            "port": int(port),
            "username": username,
            "password": password,
            "updated": _now(),
        }
        if extra:
            proxy.update(extra)
        proxies.append(proxy)
        self._save(proxies)
        return proxy

    def update(self, proxy_id: str, fields: dict):
        proxies = self._load()
        for p in proxies:
            if p["id"] == proxy_id:
                fields = dict(fields)
                fields.setdefault("updated", _now())
                p.update(fields)
                self._save(proxies)
                return p
        return None

    def upsert(self, proxy: dict) -> bool:
        """Store a proxy as-is (preserving its id and `updated` timestamp).
        Used by cloud-sync so ids stay stable and merges are last-writer-wins."""
        proxies = self._load()
        for p in proxies:
            if p["id"] == proxy.get("id"):
                if not proxy.get("updated") or (p.get("updated") or "") >= proxy["updated"]:
                    return False
                p.update(proxy)
                self._save(proxies)
                return True
        if not proxy.get("updated"):
            proxy["updated"] = _now()
        proxies.append(proxy)
        self._save(proxies)
        return True

    def delete(self, proxy_id: str) -> bool:
        proxies = self._load()
        remaining = [p for p in proxies if p["id"] != proxy_id]
        if len(remaining) != len(proxies):
            self._save(remaining)
            return True
        return False

    def find_duplicate(self, server: str, username: str, password: str):
        for p in self._load():
            if p.get("server") == server and p.get("username") == username \
                    and p.get("password") == password:
                return p
        return None

    def resolve(self, profile) -> dict:
        """Resolve a profile's effective proxy config for Playwright.

        Priority: profile.proxy_id (pool) -> profile.proxy (inline) -> None.
        Returns a Playwright proxy dict or None.
        """
        proxy_id = profile.get("proxy_id") or ""
        if proxy_id:
            pool = self.get(proxy_id)
            if pool:
                return self._to_playwright(pool)
        inline = profile.get("proxy") or {}
        if inline.get("enabled") and inline.get("host"):
            return self._to_playwright(inline)
        return None

    @staticmethod
    def _to_playwright(p: dict) -> dict:
        cfg = {
            "server": f"{p.get('type', 'http')}://{p['host']}:{p['port']}",
        }
        if p.get("username"):
            cfg["username"] = p["username"]
            cfg["password"] = p.get("password", "")
        return cfg
