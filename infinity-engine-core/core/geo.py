"""Detect a proxy's egress country and align timezone / language with it.

At launch time the proxy's public IP is geolocated via a free API
(ip-api.com). The result is used to override the profile fingerprint's
timezone and language so they match the proxy country. If the API is
unreachable, falls back to a static country -> timezone/language map
(also usable with the profile's stored proxy_country / proxy custom name).
"""

import json
import subprocess
from urllib.parse import quote, urlparse

# Country code -> primary language + timezone (used when the API is unavailable)
COUNTRY_INFO = {
    "IT": ("it-IT", ["it-IT", "it"], "Europe/Rome"),
    "CA": ("en-CA", ["en-CA", "en"], "America/Toronto"),
    "DK": ("da-DK", ["da-DK", "da"], "Europe/Copenhagen"),
    "GB": ("en-GB", ["en-GB", "en"], "Europe/London"),
    "FR": ("fr-FR", ["fr-FR", "fr"], "Europe/Paris"),
    "AU": ("en-AU", ["en-AU", "en"], "Australia/Sydney"),
    "DE": ("de-DE", ["de-DE", "de"], "Europe/Berlin"),
    "ES": ("es-ES", ["es-ES", "es"], "Europe/Madrid"),
    "NL": ("nl-NL", ["nl-NL", "nl"], "Europe/Amsterdam"),
    "US": ("en-US", ["en-US", "en"], "America/New_York"),
    "BE": ("nl-BE", ["nl-BE", "nl"], "Europe/Brussels"),
    "AT": ("de-AT", ["de-AT", "de"], "Europe/Vienna"),
    "CH": ("de-CH", ["de-CH", "de"], "Europe/Zurich"),
    "IE": ("en-IE", ["en-IE", "en"], "Europe/Dublin"),
    "PT": ("pt-PT", ["pt-PT", "pt"], "Europe/Lisbon"),
    "SE": ("sv-SE", ["sv-SE", "sv"], "Europe/Stockholm"),
    "NO": ("nb-NO", ["nb-NO", "nb"], "Europe/Oslo"),
    "FI": ("fi-FI", ["fi-FI", "fi"], "Europe/Helsinki"),
    "PL": ("pl-PL", ["pl-PL", "pl"], "Europe/Warsaw"),
    "CZ": ("cs-CZ", ["cs-CZ", "cs"], "Europe/Prague"),
    "RO": ("ro-RO", ["ro-RO", "ro"], "Europe/Bucharest"),
    "HU": ("hu-HU", ["hu-HU", "hu"], "Europe/Budapest"),
    "GR": ("el-GR", ["el-GR", "el"], "Europe/Athens"),
    "RU": ("ru-RU", ["ru-RU", "ru"], "Europe/Moscow"),
    "UA": ("uk-UA", ["uk-UA", "uk"], "Europe/Kyiv"),
    "TR": ("tr-TR", ["tr-TR", "tr"], "Europe/Istanbul"),
    "IL": ("he-IL", ["he-IL", "he"], "Asia/Jerusalem"),
    "IN": ("hi-IN", ["hi-IN", "hi"], "Asia/Kolkata"),
    "SG": ("en-SG", ["en-SG", "en"], "Asia/Singapore"),
    "JP": ("ja-JP", ["ja-JP", "ja"], "Asia/Tokyo"),
    "KR": ("ko-KR", ["ko-KR", "ko"], "Asia/Seoul"),
    "TW": ("zh-TW", ["zh-TW", "zh"], "Asia/Taipei"),
    "HK": ("zh-HK", ["zh-HK", "zh"], "Asia/Hong_Kong"),
    "CN": ("zh-CN", ["zh-CN", "zh"], "Asia/Shanghai"),
    "TH": ("th-TH", ["th-TH", "th"], "Asia/Bangkok"),
    "VN": ("vi-VN", ["vi-VN", "vi"], "Asia/Ho_Chi_Minh"),
    "ID": ("id-ID", ["id-ID", "id"], "Asia/Jakarta"),
    "MY": ("ms-MY", ["ms-MY", "ms"], "Asia/Kuala_Lumpur"),
    "PH": ("fil-PH", ["fil-PH", "fil"], "Asia/Manila"),
    "MX": ("es-MX", ["es-MX", "es"], "America/Mexico_City"),
    "BR": ("pt-BR", ["pt-BR", "pt"], "America/Sao_Paulo"),
    "AR": ("es-AR", ["es-AR", "es"], "America/Argentina/Buenos_Aires"),
    "CL": ("es-CL", ["es-CL", "es"], "America/Santiago"),
    "CO": ("es-CO", ["es-CO", "es"], "America/Bogota"),
    "ZA": ("en-ZA", ["en-ZA", "en"], "Africa/Johannesburg"),
    "NG": ("en-NG", ["en-NG", "en"], "Africa/Lagos"),
    "EG": ("ar-EG", ["ar-EG", "ar"], "Africa/Cairo"),
    "AE": ("ar-AE", ["ar-AE", "ar"], "Asia/Dubai"),
    "SA": ("ar-SA", ["ar-SA", "ar"], "Asia/Riyadh"),
}

COUNTRY_NAME_TO_CODE = {
    "italy": "IT", "canada": "CA", "denmark": "DK", "united kingdom": "GB",
    "uk": "GB", "britain": "GB", "france": "FR", "australia": "AU",
    "germany": "DE", "spain": "ES", "netherlands": "NL", "holland": "NL",
    "united states": "US", "usa": "US", "america": "US", "belgium": "BE",
    "austria": "AT", "switzerland": "CH", "ireland": "IE", "portugal": "PT",
    "sweden": "SE", "norway": "NO", "finland": "FI", "poland": "PL",
    "czech": "CZ", "czech republic": "CZ", "romania": "RO", "hungary": "HU",
    "greece": "GR", "russia": "RU", "ukraine": "UA", "turkey": "TR",
    "israel": "IL", "india": "IN", "singapore": "SG", "japan": "JP",
    "korea": "KR", "south korea": "KR", "taiwan": "TW", "hong kong": "HK",
    "china": "CN", "thailand": "TH", "vietnam": "VN", "indonesia": "ID",
    "malaysia": "MY", "philippines": "PH", "mexico": "MX", "brazil": "BR",
    "argentina": "AR", "chile": "CL", "colombia": "CO", "south africa": "ZA",
    "nigeria": "NG", "egypt": "EG", "uae": "AE", "united arab emirates": "AE",
    "saudi arabia": "SA",
}


def country_to_code(value: str) -> str:
    """Best-effort: 'IT', 'Italy', 'United Kingdom', 'Italy - 2' -> ISO code."""
    if not value:
        return ""
    v = value.strip()
    code = v.upper()
    if code in COUNTRY_INFO:
        return code
    lowered = v.lower()
    if lowered in COUNTRY_NAME_TO_CODE:
        return COUNTRY_NAME_TO_CODE[lowered]
    # handle names with suffixes like "Italy - 2", "US 3", "New York (1)"
    tokens = [t for t in lowered.replace("-", " ").replace("_", " ")
              .replace("(", " ").replace(")", " ").split()
              if not t.isdigit()]
    for end in range(len(tokens), 0, -1):
        candidate = " ".join(tokens[:end])
        if candidate in COUNTRY_NAME_TO_CODE:
            return COUNTRY_NAME_TO_CODE[candidate]
    return ""


def _curl_proxy_arg(proxy: dict) -> str:
    """Build a curl -x URL from a Playwright proxy dict."""
    u = urlparse(proxy["server"])
    if proxy.get("username"):
        auth = f"{quote(proxy['username'])}:{quote(proxy.get('password', ''))}@"
    else:
        auth = ""
    return f"{u.scheme}://{auth}{u.hostname}:{u.port}"


def detect_proxy_geo(proxy: dict) -> dict:
    """Geolocate the proxy's egress IP via ip-api.com through the proxy.

    Returns {"country": "IT", "timezone": "Europe/Rome"} or {} on failure.
    """
    if not proxy:
        return {}
    url = ("http://ip-api.com/json/?fields=status,countryCode,timezone,query")
    cmd = ["curl", "-s", "--max-time", "15", "-x", _curl_proxy_arg(proxy), url]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        data = json.loads(out.stdout)
        if data.get("status") == "success":
            return {
                "country": data.get("countryCode", ""),
                "timezone": data.get("timezone", ""),
            }
    except Exception:
        pass
    return {}


def apply_geo(fingerprint: dict, geo: dict, proxy_country: str = "") -> dict:
    """Return a copy of the fingerprint with timezone/language aligned to a country.

    geo: {"country": "IT", "timezone": "Europe/Rome"} from the API (may be empty).
    proxy_country: fallback country hint stored on the profile (code or name).
    """
    fp = dict(fingerprint)
    country = geo.get("country") or country_to_code(proxy_country)
    info = COUNTRY_INFO.get(country)

    if geo.get("timezone"):
        fp["timezone"] = geo["timezone"]
    elif info:
        fp["timezone"] = info[2]

    if info:
        fp["language"] = info[0]
        fp["languages"] = info[1]

    fp["_geo_country"] = country
    return fp
