"""Google Ads 报表来源: 读取 Google Ads 脚本写入的共享表格。

每个 MCC 里安装一个 Google Ads 脚本 (tools/google_ads_report_script.js)，
脚本把该 MCC 下所有账号的花费快照写入一张 Google 表格；表格发布到网页后，
本模块通过发布链接把 CSV 拉下来，转成与 parse_report 相同结构的 snapshot
灌进 ReportStore，复用报表页已有的聚合逻辑。

表格列 (脚本 HEADER):
    period_start, period_end, mcc_id, mcc_name,
    account_id, account_name, currency, cost
cost 为该账号自身货币下的花费；导入时按账号货币换算成 EUR (rate.to_eur)。
"""

import csv
import io
import json
import re
import ssl
import urllib.request
from datetime import datetime
from pathlib import Path

from .profile import DATA_DIR
from .reports import RateProvider, ReportStore

SOURCES_FILE = DATA_DIR / "report_sources.json"

_HEADER = ["period_start", "period_end", "mcc_id", "mcc_name",
           "account_id", "account_name", "currency", "cost"]


def load_sources() -> list[str]:
    try:
        data = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
        return [u for u in data.get("sheets", []) if u]
    except (json.JSONDecodeError, OSError):
        return []


def save_sources(urls: list[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    seen, clean = set(), []
    for u in urls:
        u = (u or "").strip()
        if u and u not in seen:
            seen.add(u)
            clean.append(u)
    SOURCES_FILE.write_text(json.dumps({"sheets": clean}, indent=2,
                                       ensure_ascii=False), encoding="utf-8")


def add_source(url: str) -> list[str]:
    urls = load_sources()
    if url not in urls:
        urls.append(url)
        save_sources(urls)
    return urls


def remove_source(url: str) -> list[str]:
    urls = [u for u in load_sources() if u != url]
    save_sources(urls)
    return urls


def _export_url(url: str) -> str:
    """Normalize any docs.google.com/spreadsheets/... link to a published
    CSV export URL (requires the sheet to be published to the web)."""
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_-]+)", url)
    if m:
        return (f"https://docs.google.com/spreadsheets/d/{m.group(1)}"
                f"/export?format=csv")
    return url


def _fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    last = None
    contexts = []
    try:
        import certifi
        contexts.append(ssl.create_default_context(cafile=certifi.where()))
    except Exception:
        pass
    try:
        contexts.append(ssl.create_default_context())
    except Exception:
        pass
    for ctx in contexts:
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read()
        except Exception as e:
            last = e
    if last is not None:
        raise last
    raise ConnectionError(f"no TLS context for {url}")


def _to_float(value) -> float:
    if value is None:
        return 0.0
    s = str(value).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_sheet_csv(data: bytes) -> list[list[str]]:
    text = data.decode("utf-8-sig", "replace")
    rows = list(csv.reader(io.StringIO(text)))
    # locate header by content, tolerate extra/missing columns
    head_idx = 0
    for i, r in enumerate(rows[:5]):
        if r and r[0].strip().lower() == "period_start":
            head_idx = i
            break
    header = [h.strip() for h in rows[head_idx]]
    col = {name: header.index(name) for name in _HEADER if name in header}
    out = []
    for r in rows[head_idx + 1:]:
        if not r or not r[0].strip():
            continue
        def g(name):
            i = col.get(name)
            return r[i].strip() if i is not None and i < len(r) else ""
        if not g("account_id"):
            continue
        out.append({
            "period_start": g("period_start"),
            "period_end": g("period_end"),
            "mcc_id": g("mcc_id").replace("-", ""),
            "mcc_name": g("mcc_name"),
            "account_id": g("account_id").replace("-", ""),
            "account_name": g("account_name") or g("account_id"),
            "currency": g("currency") or "EUR",
            "cost": _to_float(g("cost")),
        })
    return out


def fetch_sheet(url: str, rate: RateProvider) -> list[dict]:
    """Download a published sheet and convert its rows into snapshot dicts
    matching parse_report()'s output (cost converted to EUR)."""
    raw = _fetch_bytes(_export_url(url))
    rows = parse_sheet_csv(raw)
    snapshots: dict[tuple, dict] = {}
    for r in rows:
        key = (r["period_start"], r["period_end"])
        snap = snapshots.setdefault(key, {
            "hash": None,
            "file": "sheet",
            "source": f"sheet:{url}",
            "imported_at": datetime.now().isoformat(timespec="seconds"),
            "period_start": r["period_start"],
            "period_end": r["period_end"],
            "accounts": [],
        })
        snap["accounts"].append({
            "name": r["account_name"],
            "id": r["account_id"],
            "mcc_name": r["mcc_name"],
            "mcc_id": r["mcc_id"],
            "cost": r["cost"],
            "cost_eur": r["cost"] * rate.to_eur(r["currency"]),
            "currency": r["currency"],
            "converted_currency": "EUR",
        })
    return list(snapshots.values())


def import_sources(store: ReportStore, rate: RateProvider,
                   urls: list[str] | None = None) -> list[str]:
    """Fetch every configured source and import into the report store.
    Returns human-readable log lines (also suitable for the GUI)."""
    urls = urls if urls is not None else load_sources()
    log = []
    if not urls:
        log.append("未配置报表来源: 先在左侧粘贴 Google 表格发布链接")
        return log
    for url in urls:
        try:
            snaps = fetch_sheet(url, rate)
        except Exception as e:
            log.append(f"拉取失败 {url[:70]}: {e}")
            continue
        if not snaps:
            log.append(f"来源无数据 (发布格式或链接对吗?): {url[:70]}")
            continue
        for snap in snaps:
            log.append(f"  导入: {snap['period_start']} → "
                       f"{snap['period_end']} · {len(snap['accounts'])} 账号")
            store.import_snapshot(snap)
    return log
