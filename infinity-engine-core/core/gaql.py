"""Google Ads 数据源: GAQL.app (TrueClicks)。

支持多个 GAQL token（每个对应一组 Google Ads 账号），
可用自定义日期范围拉取消耗数据。

接口（来自 @trueclicks/google-ads-mcp-js 源码）:

    GET  https://api.gaql.app/api/gpt/google-ads/get-accounts?gptToken=<tok>
    POST https://api.gaql.app/api/gpt/google-ads/execute-query?gptToken=<tok>
         body: {"query", "customerId", "loginCustomerId", "reportAggregation"}

返回列名是 Google Ads API 驼峰形式，如 customer.descriptiveName、
customer.currencyCode、metrics.costMicros、segments.date。
花费单位 micros（÷ 1_000_000 = 账号币种金额）。
"""

import json
import ssl
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

from .profile import DATA_DIR
from .reports import RateProvider, ReportStore

API_BASE = "https://api.gaql.app"
USER_AGENT = "qaql-tool-client/1.0"
MICROS = 1_000_000

SOURCES_FILE = DATA_DIR / "report_sources.json"


class GaqlError(Exception):
    pass


# ---------------------------------------------------------------------------
# 多 token 存取
# ---------------------------------------------------------------------------
def load_tokens() -> list[dict]:
    """[{label, token, mcc_id, mcc_name}] — 所有配置过的 GAQL token。"""
    try:
        data = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
        out = []
        for t in data.get("gaql_tokens") or []:
            if isinstance(t, dict) and t.get("token"):
                out.append(t)
        return out
    except (json.JSONDecodeError, OSError):
        return []


def save_tokens(tokens: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {}
    try:
        data = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    data["gaql_tokens"] = [
        {"label": (t.get("label") or ""),
         "token": (t.get("token") or "").strip(),
         "mcc_id": t.get("mcc_id") or "",
         "mcc_name": t.get("mcc_name") or ""}
        for t in tokens if t.get("token")]
    SOURCES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                            encoding="utf-8")


def add_token(label: str, token: str, mcc_id: str = "",
              mcc_name: str = "") -> list[dict]:
    tokens = load_tokens()
    tokens.append({"label": (label or "").strip(),
                   "token": (token or "").strip(),
                   "mcc_id": mcc_id, "mcc_name": mcc_name})
    save_tokens(tokens)
    return tokens


def update_token(index: int, **fields) -> list[dict]:
    tokens = load_tokens()
    if 0 <= index < len(tokens):
        for k, v in fields.items():
            if k in ("label", "token", "mcc_id", "mcc_name"):
                tokens[index][k] = v
        save_tokens(tokens)
    return tokens


def remove_token(index: int) -> list[dict]:
    tokens = load_tokens()
    if 0 <= index < len(tokens):
        del tokens[index]
        save_tokens(tokens)
    return tokens


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
def _urlopen(req, timeout: int = 60):
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
            return urllib.request.urlopen(req, timeout=timeout, context=ctx)
        except Exception as e:
            last = e
    if last is not None:
        raise last
    raise ConnectionError(f"no TLS context for {req.full_url}")


def _request(method: str, path: str, token: str, payload: dict | None = None) -> dict:
    url = f"{API_BASE}{path}?gptToken={urllib.parse.quote(token)}"
    req = urllib.request.Request(url, method=method,
                                 headers={"User-Agent": USER_AGENT})
    if payload is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(payload).encode("utf-8")
    with _urlopen(req) as r:
        data = json.loads(r.read().decode("utf-8"))
    if not data.get("isSuccessful"):
        notif = data.get("notification") or {}
        errs = notif.get("errors") or []
        raise GaqlError("; ".join(errs) or f"GAQL request failed: {path}")
    return data


def _row_map(cols, row):
    return {c: v for c, v in zip(cols, row)} if row else {}


def _micros(value) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(value) / MICROS
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------------------
# 数据读取
# ---------------------------------------------------------------------------
def fetch_accounts(token: str) -> list[dict]:
    """所有可访问账号: {customer_id, login_customer_id, name}。"""
    data = _request("GET", "/api/gpt/google-ads/get-accounts", token)
    out = []
    for a in data.get("result") or []:
        out.append({
            "customer_id": str(a.get("customerId")),
            "login_customer_id": str(a.get("loginCustomerId")),
            "name": a.get("name") or "",
        })
    return out


def fetch_mcc_name(token: str, login_customer_id: str) -> str:
    cid = int(login_customer_id)
    data = _request("POST", "/api/gpt/google-ads/execute-query", token, {
        "query": "SELECT customer.id, customer.descriptive_name FROM customer",
        "customerId": cid, "loginCustomerId": cid,
        "reportAggregation": "daily",
    })
    res = data.get("result") or {}
    cols, rows = res.get("columns") or [], res.get("data") or []
    if not rows:
        return ""
    return _row_map(cols, rows[0]).get("customer.descriptiveName") or ""


def fetch_daily_costs(token: str, customer_id: str, login_customer_id: str,
                      start: date, end: date) -> tuple[list[tuple[str, float]], str]:
    """[(date_str, cost_in_currency)], currency_code。"""
    q = (f"SELECT segments.date, customer.id, customer.descriptive_name, "
         f"customer.currency_code, metrics.cost_micros FROM customer "
         f"WHERE segments.date >= '{start.isoformat()}' "
         f"AND segments.date <= '{end.isoformat()}'")
    data = _request("POST", "/api/gpt/google-ads/execute-query", token, {
        "query": q, "customerId": int(customer_id),
        "loginCustomerId": int(login_customer_id),
        "reportAggregation": "daily",
    })
    res = data.get("result") or {}
    cols, rows = res.get("columns") or [], res.get("data") or []
    currency = ""
    daily = []
    for row in rows:
        m = _row_map(cols, row)
        if not currency:
            currency = m.get("customer.currencyCode") or ""
        daily.append((m.get("segments.date") or "",
                      _micros(m.get("metrics.costMicros"))))
    daily.sort(key=lambda x: x[0])
    return daily, currency


def fetch_rolling_24h(token: str, customer_id: str,
                     login_customer_id: str) -> float:
    """滚动 24 小时的账号累计消耗（账号币种金额）。

    查询 segments.date 维度 = 昨天+今天，按 segments.hour 拆分，
    合并后取倒数 24 个小时点求和。"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    q = (f"SELECT segments.date, segments.hour, metrics.cost_micros "
         f"FROM campaign WHERE segments.date >= '{yesterday.isoformat()}' "
         f"AND segments.date <= '{today.isoformat()}'")
    try:
        data = _request("POST", "/api/gpt/google-ads/execute-query", token, {
            "query": q, "customerId": int(customer_id),
            "loginCustomerId": int(login_customer_id),
            "reportAggregation": "hourly",
        })
    except GaqlError:
        return 0.0
    res = data.get("result") or {}
    cols, rows = res.get("columns") or [], res.get("data") or []
    points: list[tuple[str, int, float]] = []
    for row in rows:
        m = _row_map(cols, row)
        d = m.get("segments.date") or ""
        h = m.get("segments.hour")
        try:
            hi = int(h) if h not in (None, "") else -1
        except (TypeError, ValueError):
            hi = -1
        points.append((d, hi, _micros(m.get("metrics.costMicros"))))
    points.sort(key=lambda p: (p[0], p[1]))
    return sum(c for _, _, c in points[-24:])


# ---------------------------------------------------------------------------
# 广告查询 & 素材库
# ---------------------------------------------------------------------------
def fetch_ad_details(token: str, customer_id: str, login_customer_id: str,
                     ad_id: str, start: date, end: date) -> dict:
    """单条广告 ID 的消耗详情。

    返回 {id, type, status,
          cost, impressions, clicks, conversions, ctr, average_cpc,
          cost_micros}（金额为账号币种）。
    """
    q = (f"SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status, "
         f"metrics.cost_micros, metrics.impressions, metrics.clicks, "
         f"metrics.conversions, metrics.ctr, metrics.average_cpc "
         f"FROM ad_group_ad "
         f"WHERE segments.date >= '{start.isoformat()}' "
         f"AND segments.date <= '{end.isoformat()}' "
         f"AND ad_group_ad.ad.id = {int(ad_id)}")
    data = _request("POST", "/api/gpt/google-ads/execute-query", token, {
        "query": q, "customerId": int(customer_id),
        "loginCustomerId": int(login_customer_id),
        "reportAggregation": "summary",
    })
    res = data.get("result") or {}
    cols, rows = res.get("columns") or [], res.get("data") or []
    if not rows:
        return {}
    m = _row_map(cols, rows[0])
    return {
        "id": ad_id,
        "type": m.get("adGroupAd.ad.type") or "",
        "status": m.get("adGroupAd.status") or "",
        "cost": _micros(m.get("metrics.costMicros")),
        "impressions": float(m.get("metrics.impressions") or 0),
        "clicks": float(m.get("metrics.clicks") or 0),
        "conversions": float(m.get("metrics.conversions") or 0),
        "ctr": float(m.get("metrics.ctr") or 0),
        "average_cpc": _micros(m.get("metrics.averageCpc")),
    }


def fetch_account_assets(token: str, customer_id: str,
                         login_customer_id: str) -> dict:
    """拉取整个账户的素材库,返回 {images, youtube, texts}。

    images: [{id, name, url, width, height}]
    youtube: [{id, video_id}]
    texts: [{id, text}]
    """
    out = {"images": [], "youtube": [], "texts": []}
    # 图片
    try:
        data = _request("POST", "/api/gpt/google-ads/execute-query", token, {
            "query": ("SELECT asset.id, asset.name, asset.type, "
                      "asset.image_asset.full_size.url, "
                      "asset.image_asset.full_size.width_pixels, "
                      "asset.image_asset.full_size.height_pixels "
                      "FROM asset WHERE asset.type = 'IMAGE'"),
            "customerId": int(customer_id),
            "loginCustomerId": int(login_customer_id),
            "reportAggregation": "summary",
        })
        res = data.get("result") or {}
        cols, rows = res.get("columns") or [], res.get("data") or []
        for row in rows:
            m = _row_map(cols, row)
            out["images"].append({
                "id": m.get("asset.id") or "",
                "name": m.get("asset.name") or "",
                "url": m.get("asset.imageAsset.fullSize.url") or "",
                "width": m.get("asset.imageAsset.fullSize.widthPixels") or "",
                "height": m.get("asset.imageAsset.fullSize.heightPixels") or "",
            })
    except GaqlError:
        pass
    # YouTube
    try:
        data = _request("POST", "/api/gpt/google-ads/execute-query", token, {
            "query": ("SELECT asset.id, asset.youtube_video_asset.youtube_video_id "
                      "FROM asset WHERE asset.type = 'YOUTUBE_VIDEO'"),
            "customerId": int(customer_id),
            "loginCustomerId": int(login_customer_id),
            "reportAggregation": "summary",
        })
        res = data.get("result") or {}
        cols, rows = res.get("columns") or [], res.get("data") or []
        for row in rows:
            m = _row_map(cols, row)
            vid = m.get("asset.youtubeVideoAsset.youtubeVideoId") or ""
            out["youtube"].append({
                "id": m.get("asset.id") or "",
                "video_id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}" if vid else "",
            })
    except GaqlError:
        pass
    # TEXT
    try:
        data = _request("POST", "/api/gpt/google-ads/execute-query", token, {
            "query": ("SELECT asset.id, asset.text_asset.text "
                      "FROM asset WHERE asset.type = 'TEXT'"),
            "customerId": int(customer_id),
            "loginCustomerId": int(login_customer_id),
            "reportAggregation": "summary",
        })
        res = data.get("result") or {}
        cols, rows = res.get("columns") or [], res.get("data") or []
        for row in rows:
            m = _row_map(cols, row)
            out["texts"].append({
                "id": m.get("asset.id") or "",
                "text": m.get("asset.textAsset.text") or "",
            })
    except GaqlError:
        pass
    return out


# ---------------------------------------------------------------------------
# 快照构建（迭代所有 token）
# ---------------------------------------------------------------------------
def _account_dict(acc, mcc_id, mcc_name, currency, cost, today_24h, cost_eur):
    return {
        "name": acc["name"] or acc["customer_id"],
        "id": acc["customer_id"],
        "mcc_name": mcc_name,
        "mcc_id": mcc_id,
        "cost": cost,
        "cost_eur": cost_eur,
        "currency": currency,
        "converted_currency": "EUR",
        "today_24h": today_24h,
        "today_24h_eur": 0.0,
    }


def build_snapshots(tokens: list[dict], rate: RateProvider,
                    start: date, end: date) -> tuple[list[dict], list[str]]:
    """拉取所有 token 对应的账号数据，构建 [start..end] 的逐日累计快照，
    并附加每账号的滚动 24h 消耗。

    返回 (snapshots, log)。"""
    log = []
    snapshots: list[dict] = []
    now = datetime.now().isoformat(timespec="seconds")

    for tinfo in tokens:
        token = tinfo["token"]
        label = tinfo.get("label") or "?"
        try:
            accounts = fetch_accounts(token)
        except GaqlError as e:
            log.append(f"[{label}] 获取账号失败: {e}")
            continue
        if not accounts:
            log.append(f"[{label}] 无可访问账号")
            continue
        by_mcc: dict[str, list[dict]] = {}
        for a in accounts:
            by_mcc.setdefault(a["login_customer_id"], []).append(a)
        for mcc_id, accs in by_mcc.items():
            try:
                mcc_name = fetch_mcc_name(token, mcc_id)
            except GaqlError as e:
                log.append(f"[{label}] MCC {mcc_id} 名字失败: {e}")
                mcc_name = ""
            per_acc: dict[str, list[tuple[str, float]]] = {}
            per_acc_today: dict[str, float] = {}
            currencies: dict[str, str] = {}
            for acc in accs:
                try:
                    daily, ccy = fetch_daily_costs(token, acc["customer_id"],
                                                   mcc_id, start, end)
                except GaqlError as e:
                    log.append(f"[{label}] 账号 {acc['customer_id']}: {e}")
                    continue
                per_acc[acc["customer_id"]] = daily
                currencies[acc["customer_id"]] = ccy
                try:
                    per_acc_today[acc["customer_id"]] = fetch_rolling_24h(
                        token, acc["customer_id"], mcc_id)
                except GaqlError as e:
                    log.append(f"[{label}] 账号 {acc['customer_id']} 24h: {e}")
                    per_acc_today[acc["customer_id"]] = 0.0
            if not per_acc:
                continue
            # 找出该 MCC 所有天
            all_days = sorted({d for dl in per_acc.values() for d, _ in dl})
            for d in all_days:
                accounts_out = []
                for acc in accs:
                    cid = acc["customer_id"]
                    cum = sum(c for dd, c in per_acc.get(cid, []) if dd <= d)
                    t24 = per_acc_today.get(cid, 0.0)
                    ccy = currencies.get(cid, "")
                    ccy_rate = rate.to_eur(ccy) if ccy else 1.0
                    accounts_out.append(_account_dict(
                        acc, mcc_id, mcc_name, ccy, round(cum, 2),
                        round(t24, 2), round(cum * ccy_rate, 2)))
                    accounts_out[-1]["today_24h_eur"] = round(t24 * ccy_rate, 2)
                snapshots.append({
                    "hash": None, "file": "gaql", "source": f"gaql:{mcc_id}",
                    "imported_at": now,
                    "period_start": start.isoformat(),
                    "period_end": d,
                    "accounts": accounts_out,
                })
            log.append(f"[{label}] MCC {mcc_name or mcc_id}: "
                       f"{len(accs)} 账号, {len(all_days)} 天快照")
    return snapshots, log


def import_gaql(store: ReportStore, rate: RateProvider,
                tokens: list[dict], start: date, end: date) -> list[str]:
    """拉取所有 token 数据并灌入 ReportStore。"""
    snapshots, log = build_snapshots(tokens, rate, start, end)
    for snap in snapshots:
        msg = store.import_snapshot(snap)
        log.append(f"  {msg} · {snap['period_end']} · "
                   f"{len(snap['accounts'])} 账号")
    return log