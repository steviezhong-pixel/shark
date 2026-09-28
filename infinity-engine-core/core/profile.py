"""Profile management: create, update, delete, and store profiles as JSON."""

import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path.home() / "Library" / "Application Support" / "MultiAccountBrowser"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROFILES_DIR = DATA_DIR / "profiles"
CONFIG_FILE = DATA_DIR / "profiles.json"
LOGS_DIR = DATA_DIR / "logs"

DEFAULT_START_URL = "https://ads.google.com/aw"

SEED_FILES = ("profiles.json", "proxies.json", "settings.json",
              "report_sources.json", "credit_lines.json",
              "rate.json", "reports.json")

SEED_DIRS = ("cookies",)


def _seed_dir() -> Path | None:
    """Locate the bundled seed data (Resources/seed_data) in a PyInstaller
    bundle. sys._MEIPASS points at Contents/Frameworks in onedir mode while
    the seed is copied to Contents/Resources, so walk up like
    core.browser._bundle_resources does."""
    if not getattr(sys, "frozen", False):
        return None
    d = Path(sys._MEIPASS)
    for _ in range(6):
        for cand in (d / "Resources", d):
            if (cand / "seed_data" / "profiles.json").is_file():
                return cand / "seed_data"
        d = d.parent
    return None


def bootstrap_seed() -> bool:
    """First-run import: when the app data dir is empty, copy the bundled
    profiles / proxies / cloud-sync settings so a fresh install works out of
    the box. No-op in dev mode or when data already exists."""
    if CONFIG_FILE.exists():
        return False
    seed = _seed_dir()
    if seed is None:
        return False
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in SEED_FILES:
        src = seed / name
        if src.is_file():
            try:
                shutil.copy2(src, DATA_DIR / name)
                copied += 1
            except OSError:
                pass
    if copied:
        print(f"[bootstrap] imported seed data ({copied} files)", flush=True)
    # 复制子目录(如 cookies/*.json),保留登录态
    for sub in SEED_DIRS:
        src = seed / sub
        if src.is_dir():
            dst_dir = DATA_DIR / sub
            try:
                shutil.rmtree(dst_dir, ignore_errors=True)
                shutil.copytree(src, dst_dir)
                print(f"[bootstrap] imported {sub}/ ({len(list(src.glob('*')))} items)", flush=True)
            except OSError as e:
                print(f"[bootstrap] {sub} copy failed: {e}", flush=True)
    return copied > 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_proxy() -> dict:
    return {
        "enabled": False,
        "type": "http",
        "host": "",
        "port": 0,
        "username": "",
        "password": "",
    }


class ProfileManager:
    def __init__(self, config_file=None):
        self.config_file = Path(config_file) if config_file else CONFIG_FILE
        bootstrap_seed()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self._save({})

    def _load(self) -> dict:
        return json.loads(self.config_file.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.config_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def list_profiles(self) -> list:
        data = self._load()
        return sorted(data.values(), key=lambda p: p.get("created", ""))

    def get(self, profile_id: str):
        return self._load().get(profile_id)

    def create(self, name: str, fingerprint: dict, start_url=None, proxy=None,
               proxy_id="", extra=None) -> dict:
        profile_id = str(uuid.uuid4())
        data = self._load()
        data[profile_id] = {
            "id": profile_id,
            "name": name,
            "start_url": start_url or DEFAULT_START_URL,
            "proxy": proxy or _default_proxy(),
            "proxy_id": proxy_id,
            "fingerprint": fingerprint,
            "fp_source": "auto",
            "created": _now(),
            "updated": _now(),
        }
        if extra:
            data[profile_id].update(extra)
        self._save(data)
        return data[profile_id]

    def update(self, profile_id: str, fields: dict):
        data = self._load()
        if profile_id in data:
            data[profile_id].update(fields)
            data[profile_id]["updated"] = _now()
            self._save(data)
            return data[profile_id]
        return None

    def delete(self, profile_id: str) -> bool:
        data = self._load()
        if profile_id in data:
            del data[profile_id]
            self._save(data)
            profile_dir = PROFILES_DIR / profile_id
            if profile_dir.exists():
                shutil.rmtree(profile_dir, ignore_errors=True)
            return True
        return False

    def upsert(self, profile: dict) -> str:
        """Store a full profile object as-is (preserving its id and `updated`
        timestamp). Used by import and cloud-sync so ids stay stable across
        devices and last-writer-wins merges work correctly."""
        data = self._load()
        pid = profile["id"]
        if not profile.get("updated"):
            profile["updated"] = _now()
        data[pid] = profile
        self._save(data)
        return pid

    def profile_dir(self, profile_id: str) -> Path:
        return PROFILES_DIR / profile_id
