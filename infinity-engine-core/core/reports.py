"""Google Ads spend aggregation for the Infinity Lines dashboard.

Imports the account-level "Performance report" CSVs that are downloaded into
each profile's downloads folder, accumulates monthly MTD snapshots, and
derives per-account spend (today / this month / all-time), the owning MCC
(extracted from the report's "Direct manager" columns), and computes remaining
credit against user-provided per-MCC EUR credit lines (converted to USD with a
daily exchange rate).

Report layout (tab-separated, usually UTF-16 LE with BOM):

    Performance report
    "August 1, 2026 - August 12, 2026"
    Account Status	Account name	Account external customer ID	... Cost	Cost (Converted currency) ...	Converted currency code
    Active	MEI-0713-7	576-909-9795	... 11966.35	10371.84	...	EUR
    Total: ...  (skip)

Aggregation rules (MTD reports only, as agreed with the user):
  * 当月 (this month)  = the latest snapshot whose period falls in the
    current calendar month.
  * 当日 (today)       = difference between the two most recent snapshots of
    the current month (re-downloading the MTD report daily makes this the
    day's spend). None when only one snapshot exists.
  * 历史 (all-time)    = one value per calendar month (that month's latest MTD
    snapshot), summed over every recorded month.
"""

import csv
import hashlib
import io
import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, date
from pathlib import Path

from .profile import BASE_DIR, DATA_DIR

REPORTS_FILE = DATA_DIR / "reports.json"
CREDIT_FILE = DATA_DIR / "credit_lines.json"
RATE_FILE = DATA_DIR / "rate.json"

FRANKFURTER_URL = "https://api.frankfurter.app/latest?from=EUR&to=USD"
ER_API_URL = "https://open.er-api.com/v6/latest/EUR"

# tried in order; first reachable source wins (frankfurter is often blocked
# behind a CDN redirect in some regions, so fall back to er-api).
_RATE_SOURCES = [("frankfurter", FRANKFURTER_URL), ("er-api", ER_API_URL)]


def _fetch_json(url: str, timeout: int = 8) -> dict:
    """GET a JSON payload, tolerating the macOS Python SSL-CA gap by using
    certifi's bundle when present and falling back to an unverified context
    (rate lookups are non-sensitive)."""
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
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
    if last is not None:
        raise last
    raise ConnectionError(f"no TLS context for {url}")

# date fragments allowed on the report's period line
_DATE_PATTERNS = [
    re.compile(r"([A-Za-z]+) (\d{1,2}), (\d{4})"),   # August 1, 2026
    re.compile(r"(\d{1,2}) ([A-Za-z]+) (\d{4})"),    # 1 August 2026
    re.compile(r"(\d{4})-(\d{2})-(\d{2})"),          # 2026-08-01
]
_MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}
_MONTHS.update({"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10,
                "nov": 11, "dec": 12})

_TSV_HEADER_FIELDS = [
    "Account Status", "Account name", "Account external customer ID",
    "Optimization score", "Optimisation score", "Direct manager name",
    "Direct manager customer ID", "Account type", "Clicks", "Impr.", "CTR",
    "Currency code", "Avg. CPC", "Avg. CPC (Converted currency)", "Cost",
    "Cost (Converted currency)", "Conversions", "Conv. rate",
    "Account labels", "Converted currency code",
]


def _read_text(path: Path) -> str:
    """Decode a Google Ads CSV regardless of UTF-16 LE BOM / UTF-8."""
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def _to_float(value: str) -> float:
    if value is None:
        return 0.0
    s = value.strip().replace(",", "").replace("€", "").replace("$", "")
    if not s or s in ("--", "—"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _split(line: str, delim: str) -> list[str]:
    """Split a report line by tab, or by comma (CSV) handling quoted fields."""
    if delim == "\t":
        return line.split("\t")
    try:
        return next(csv.reader(io.StringIO(line)))
    except Exception:
        return line.split(",")


def _parse_dates(line: str):
    """Return (start, end) as datetime.date from the report's period line."""
    if not line:
        return None, None
    stripped = line.strip().strip('"')
    found = []
    # US: "August 1, 2026"
    for mon, day, yr in re.findall(r"([A-Za-z]+) (\d{1,2}), (\d{4})", stripped):
        if mon.lower() in _MONTHS:
            found.append(date(int(yr), _MONTHS[mon.lower()], int(day)))
    # EU: "1 August 2026"
    for day, mon, yr in re.findall(r"(\d{1,2}) ([A-Za-z]+) (\d{4})", stripped):
        if mon.lower() in _MONTHS:
            found.append(date(int(yr), _MONTHS[mon.lower()], int(day)))
    # ISO: "2026-08-01"
    for yr, mo, day in re.findall(r"(\d{4})-(\d{2})-(\d{2})", stripped):
        found.append(date(int(yr), int(mo), int(day)))
    found = sorted(set(found))
    if not found:
        return None, None
    return found[0], found[-1]


def parse_report(path: Path) -> dict | None:
    """Parse one downloaded report into a snapshot dict, or None if the file
    is not a supported Google Ads performance report."""
    try:
        text = _read_text(path)
    except OSError:
        return None
    lines = text.splitlines()
    if len(lines) < 3:
        return None
    start, end = _parse_dates(lines[1] if len(lines) > 1 else "")
    header_line = lines[2]
    delim = "\t" if "\t" in header_line else ","
    header = [c.strip() for c in _split(header_line, delim)]
    idx = {name: i for i, name in enumerate(header) if name}
    if "Account external customer ID" not in idx:
        return None
    has_converted = "Cost (Converted currency)" in idx
    accounts = []
    for line in lines[3:]:
        if not line.strip() or line.strip().lower().startswith("total"):
            continue
        cols = _split(line, delim)
        def col(name):
            i = idx.get(name)
            return cols[i].strip() if i is not None and i < len(cols) else ""
        account_id = col("Account external customer ID").replace("-", "")
        if not account_id:
            continue
        currency = col("Currency code") or ""
        if has_converted:
            cost_eur = _to_float(col("Cost (Converted currency)"))
            converted = col("Converted currency code") or "EUR"
        else:
            # 报表未带换算列时, 用账户币种金额兜底 (按 1:1 计入)
            cost_eur = _to_float(col("Cost"))
            converted = currency or "EUR"
        accounts.append({
            "name": col("Account name") or account_id,
            "id": account_id,
            "mcc_name": col("Direct manager name") or "",
            "mcc_id": col("Direct manager customer ID").replace("-", "") or "",
            "cost": _to_float(col("Cost")),
            "cost_eur": cost_eur,
            "currency": currency,
            "converted_currency": converted,
        })
    if not accounts:
        return None
    raw = path.read_bytes()
    return {
        "hash": hashlib.sha256(raw).hexdigest(),
        "file": path.name,
        "source": str(path),
        "imported_at": datetime.now().isoformat(timespec="seconds"),
        "period_start": start.isoformat() if start else None,
        "period_end": end.isoformat() if end else None,
        "accounts": accounts,
    }


def _now():
    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# exchange rate
# ---------------------------------------------------------------------------
class RateProvider:
    """Daily EUR->USD rate, cached in DATA_DIR/rate.json. Auto-fetches once a
    day from frankfurter.app; a manual override (GUI) wins until changed."""

    def __init__(self, file: Path = RATE_FILE):
        self.file = file
        self.data = self._load()

    def _load(self) -> dict:
        try:
            return json.loads(self.file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(self.data, indent=2, ensure_ascii=False),
                             encoding="utf-8")

    def rate(self, force_refresh: bool = False) -> tuple[float, str]:
        """Return (rate, label). label describes the source/date so the UI can
        show whether the rate is live, cached, or manual."""
        today = date.today().isoformat()
        manual = self.data.get("manual")
        if manual and manual.get("date") == today:
            return float(manual["rate"]), f"手动 {manual['date']}"
        if not force_refresh and self.data.get("date") == today and self.data.get("rate"):
            return float(self.data["rate"]), f"{self.data['source']} {today}"
        for source, url in _RATE_SOURCES:
            try:
                body = _fetch_json(url)
                rate = float(body["rates"]["USD"])
            except Exception:
                continue
            self.data.update({"date": today, "rate": rate, "source": source})
            self._save()
            return rate, f"{source} {today}"
        if self.data.get("rate"):
            return float(self.data["rate"]), f"缓存 {self.data.get('date', '?')}"
        return 0.0, "无汇率(离线)"

    def set_manual(self, rate: float) -> None:
        self.data["manual"] = {"rate": rate, "date": date.today().isoformat()}
        self._save()

    def clear_manual(self) -> None:
        self.data.pop("manual", None)
        self._save()

    def to_eur(self, currency: str) -> float:
        """Convert an amount's rate factor from `currency` to EUR (1.0 if the
        currency is already EUR). Cached daily; falls back to cache or 1.0."""
        ccy = (currency or "EUR").upper()
        if ccy in ("EUR", ""):
            return 1.0
        today = date.today().isoformat()
        cached = self.data.get("ccy", {}).get(ccy)
        if cached and cached.get("date") == today:
            return float(cached["rate"])
        try:
            body = _fetch_json(
                f"https://api.frankfurter.app/latest?from={ccy}&to=EUR")
            rate = float(body["rates"]["EUR"])
        except Exception:
            if cached:
                return float(cached["rate"])
            return 1.0
        self.data.setdefault("ccy", {})[ccy] = {
            "rate": rate, "date": today, "source": "frankfurter"}
        self._save()
        return rate


# ---------------------------------------------------------------------------
# credit lines (MCC -> EUR total)
# ---------------------------------------------------------------------------
class CreditLines:
    def __init__(self, file: Path = CREDIT_FILE):
        self.file = file
        self.data = self._load()

    def _load(self) -> dict:
        try:
            return json.loads(self.file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(self.data, indent=2, ensure_ascii=False),
                             encoding="utf-8")

    def _key(self, mcc_id: str, mcc_name: str) -> str:
        return mcc_id or (mcc_name.strip() or "?")

    def get(self, mcc_id: str, mcc_name: str) -> float | None:
        entry = self.data.get(self._key(mcc_id, mcc_name))
        if entry:
            try:
                return float(entry.get("eur_limit", 0))
            except (TypeError, ValueError):
                return None
        return None

    def set(self, mcc_id: str, mcc_name: str, eur: float) -> None:
        key = self._key(mcc_id, mcc_name)
        existing = self.data.get(key, {})
        existing.update({"name": mcc_name or existing.get("name", ""),
                         "mcc_id": mcc_id or existing.get("mcc_id", ""),
                         "eur_limit": eur, "updated_at": _now()})
        self.data[key] = existing
        self._save()

    def delete(self, mcc_id: str, mcc_name: str) -> None:
        self.data.pop(self._key(mcc_id, mcc_name), None)
        self._save()

    def all(self) -> list[dict]:
        return sorted(self.data.values(), key=lambda e: e.get("name", "").lower())


# ---------------------------------------------------------------------------
# report store + aggregation
# ---------------------------------------------------------------------------
class ReportStore:
    def __init__(self, file: Path = REPORTS_FILE):
        self.file = file
        self.data = self._load()

    def _load(self) -> dict:
        try:
            d = json.loads(self.file.read_text(encoding="utf-8"))
        except Exception:
            d = {}
        d.setdefault("snapshots", [])
        return d

    def _save(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(self.data, indent=2, ensure_ascii=False),
                             encoding="utf-8")

    def _downloads_dirs(self) -> list[Path]:
        root = DATA_DIR / "profiles"
        if not root.is_dir():
            return []
        return [d for d in root.glob("*/downloads") if d.is_dir()]

    def _snap_key(self, snap: dict):
        """Identity for period-replacement: same range AND same set of MCCs,
        so a re-downloaded report for one MCC replaces its own older snapshot
        without colliding with other MCCs reporting the same dates."""
        mccs = tuple(sorted({a.get("mcc_id") or (a.get("mcc_name") or "?")
                             for a in snap.get("accounts", [])}))
        return (snap.get("period_start"), snap.get("period_end"), mccs)

    def import_file(self, path: Path) -> str:
        snap = parse_report(path)
        if snap is None:
            return f"跳过(无法解析): {path.name}"
        existing = {s["hash"] for s in self.data["snapshots"]}
        if snap["hash"] in existing:
            return f"跳过(已导入): {path.name}"
        return self.import_snapshot(snap)

    def import_snapshot(self, snap: dict) -> str:
        """Store a snapshot dict directly (no file), replacing an older
        snapshot for the same (period, MCC set). Used by the Google Sheets
        source so re-pulling the same data never double-counts."""
        key = self._snap_key(snap)
        for i, s in enumerate(self.data["snapshots"]):
            if self._snap_key(s) == key:
                self.data["snapshots"][i] = snap
                self._save()
                return f"更新: {snap['period_start']} → {snap['period_end']}"
        self.data["snapshots"].append(snap)
        self._save()
        return f"导入: {snap['period_start']} → {snap['period_end']}"

    def months(self) -> list[str]:
        """Sorted (newest first) list of 'YYYY-MM' months present in data."""
        seen = set()
        for s in self.data["snapshots"]:
            pm = _period_month(s.get("period_end"))
            if pm[0] is not None:
                seen.add(f"{pm[0]:04d}-{pm[1]:02d}")
        return sorted(seen, reverse=True)

    def scan_downloads(self) -> list[str]:
        log = []
        for d in self._downloads_dirs():
            for f in sorted(d.glob("*.csv")):
                try:
                    log.append(self.import_file(f))
                except Exception as e:
                    log.append(f"失败: {f.name}: {e}")
        return log

    def _account_snapshots(self, account_id: str) -> list[dict]:
        snaps = []
        for s in self.data["snapshots"]:
            for acc in s.get("accounts", []):
                if acc["id"] == account_id:
                    snaps.append({**acc, "period_start": s.get("period_start"),
                                  "period_end": s.get("period_end"),
                                  "imported_at": s.get("imported_at")})
        snaps.sort(key=lambda a: a.get("period_end") or "")
        return snaps

    def _month_total(self, snaps: list[dict], year: int, month: int) -> float:
        in_month = [a for a in snaps
                    if _period_month(a.get("period_end")) == (year, month)]
        if not in_month:
            return 0.0
        last = in_month[-1]
        return last.get("cost_eur", 0.0)

    def _today_24h_eur(self, snaps: list[dict]) -> float:
        """最新快照里记录的 today_24h_eur 字段 (滚动 24h 消耗, EUR)。"""
        if not snaps:
            return 0.0
        return snaps[-1].get("today_24h_eur", 0.0) or 0.0

    def _historical_eur(self, snaps: list[dict]) -> float:
        months = {_period_month(a.get("period_end")) for a in snaps}
        months.discard((None, None))
        return sum(self._month_total(snaps, y, m) for y, m in months)

    def _current_month(self):
        today = date.today()
        return today.year, today.month

    def aggregate(self, eur_usd: float, year: int | None = None,
                  month: int | None = None) -> dict:
        """Return the dashboard dataset.

        {accounts, mccs, totals, rate, rate_label} — same shape as before.
        `year`/`month` select the "current" month shown in the 当月 column
        (defaults to the actual current month).
        """
        if year is None or month is None:
            cur_y, cur_m = self._current_month()
        else:
            cur_y, cur_m = year, month
        last_y, last_m = self._prior_month(cur_y, cur_m)
        account_ids = sorted({a["id"]
                              for s in self.data["snapshots"]
                              for a in s.get("accounts", [])})
        rows = []
        for aid in account_ids:
            snaps = self._account_snapshots(aid)
            if not snaps:
                continue
            last = snaps[-1]
            name = last["name"]
            mcc_name = last.get("mcc_name") or ""
            mcc_id = last.get("mcc_id") or ""
            month_eur = self._month_total(snaps, cur_y, cur_m)
            today_24h_eur = self._today_24h_eur(snaps)
            last_month_eur = self._month_total(snaps, last_y, last_m)
            hist_eur = self._historical_eur(snaps)
            rows.append({
                "account": name, "account_id": aid, "mcc": mcc_name,
                "mcc_id": mcc_id,
                "today_24h_eur": today_24h_eur,
                "month_eur": month_eur,
                "last_month_eur": last_month_eur,
                "hist_eur": hist_eur,
                "today_24h_usd": today_24h_eur * eur_usd,
                "month_usd": month_eur * eur_usd,
                "last_month_usd": last_month_eur * eur_usd,
                "hist_usd": hist_eur * eur_usd,
            })
        rows.sort(key=lambda r: (r["mcc"].lower(), r["account"].lower()))
        return rows

    @staticmethod
    def _prior_month(year: int, month: int) -> tuple[int, int]:
        m = month - 1
        y = year
        if m < 1:
            m = 12
            y -= 1
        return y, m

    def mccs(self) -> list[dict]:
        by_id = {}
        for s in self.data["snapshots"]:
            for acc in s.get("accounts", []):
                mid = acc.get("mcc_id") or ""
                key = mid or (acc.get("mcc_name") or "").strip() or "?"
                entry = by_id.setdefault(key, {"mcc_id": mid,
                                               "name": acc.get("mcc_name") or ""})
        return list(by_id.values())


def _period_month(iso: str | None):
    if not iso:
        return (None, None)
    try:
        d = datetime.fromisoformat(iso).date()
    except ValueError:
        try:
            d = datetime.strptime(iso, "%Y-%m-%d").date()
        except ValueError:
            return (None, None)
    return (d.year, d.month)


def build_dashboard(store: ReportStore, credit: CreditLines,
                    rate_provider: RateProvider,
                    force_rate: bool = False, year=None, month=None):
    eur_usd, rate_label = rate_provider.rate(force_refresh=force_rate)
    rate_ok = bool(eur_usd and eur_usd > 0)
    if not rate_ok:
        # never blank the figures: fall back to showing EUR amounts in the
        # USD columns, clearly labelled, instead of $0.00.
        eur_usd = 1.0
        rate_label = "无汇率(离线): 金额暂按 EUR 显示"
    rows = store.aggregate(eur_usd, year, month)
    # latest data-update time across all snapshots that contributed
    data_updated_at = max((s.get("imported_at") or s.get("file") or "")
                          for s in store.data.get("snapshots", [])) or None
    # attach credit / remaining per account
    by_mcc_limit = {}
    for r in rows:
        lim = credit.get(r["mcc_id"], r["mcc"])
        r["limit_eur"] = lim
        r["limit_usd"] = None if lim is None else lim * eur_usd
        r["remaining_usd"] = (None if lim is None
                              else lim * eur_usd - r["last_month_usd"] - r["month_usd"])
        by_mcc_limit[(r["mcc_id"], r["mcc"])] = lim
    # MCC summaries
    mcc_map = {}
    for r in rows:
        key = (r["mcc_id"], r["mcc"])
        m = mcc_map.setdefault(key, {"mcc_id": r["mcc_id"], "name": r["mcc"],
                                     "count": 0, "month_eur": 0.0,
                                     "last_month_eur": 0.0,
                                     "today_24h_eur": 0.0,
                                     "hist_eur": 0.0})
        m["count"] += 1
        m["month_eur"] += r["month_eur"]
        m["last_month_eur"] += r["last_month_eur"]
        m["today_24h_eur"] += r["today_24h_eur"]
        m["hist_eur"] += r["hist_eur"]
    mccs = []
    for key, m in mcc_map.items():
        lim = by_mcc_limit.get(key)
        m["limit_eur"] = lim
        m["limit_usd"] = None if lim is None else lim * eur_usd
        m["today_24h_usd"] = m["today_24h_eur"] * eur_usd
        m["month_usd"] = m["month_eur"] * eur_usd
        m["last_month_usd"] = m["last_month_eur"] * eur_usd
        m["hist_usd"] = m["hist_eur"] * eur_usd
        m["remaining_usd"] = (None if lim is None
                               else lim * eur_usd - m["last_month_usd"] - m["month_usd"])
        mccs.append(m)
    mccs.sort(key=lambda m: m["name"].lower())
    totals = {
        "today_24h_usd": sum(r["today_24h_usd"] for r in rows),
        "month_usd": sum(r["month_usd"] for r in rows),
        "last_month_usd": sum(r["last_month_usd"] for r in rows),
        "hist_usd": sum(r["hist_usd"] for r in rows),
    }
    return {"accounts": rows, "mccs": mccs, "totals": totals,
            "rate": eur_usd, "rate_ok": rate_ok, "rate_label": rate_label,
            "data_updated_at": data_updated_at}
