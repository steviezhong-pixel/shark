"""Per-profile TOTP (2FA) code generator + browser auto-fill.

Stores a TOTP secret per profile (the same secret you'd put in Google
Authenticator) and injects a document-start init script that:
  - detects 2FA input fields on the page (Google Authenticator code,
    generic OTP inputs)
  - generates the current 6-digit code via the binding
  - auto-fills the field and copies the code to the clipboard
  - shows a small floating "TOTP" button so the user can re-copy the code

Usage:
    mgr = TOTPManager(profile_id)
    mgr.set_secret("JBSWY3DPEHPK3PXP")   # base32 secret
    mgr.enable()
    context.expose_binding("__mabTotp", mgr.bridge)
    context.add_init_script(TOTP_AUTOFILL_JS)
"""

import base64
import hashlib
import hmac
import json
import os
import struct
import time
from pathlib import Path

from .profile import ProfileManager

FLAG = "totp_enabled"

TOTP_AUTOFILL_JS = r"""
(() => {
  const DEBUG = true;
  const log = (...a) => { if (DEBUG) console.log("[mab-totp]", ...a); };

  let lastCode = "";
  let lastFill = 0;

  async function getCode() {
    try {
      return await window.__mabTotp("code");
    } catch (e) {
      log("binding failed", e);
      return null;
    }
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      // fallback: execCommand
      try {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
        return true;
      } catch (e2) { return false; }
    }
  }

  let btn = null;
  function ensureButton() {
    if (btn && document.body.contains(btn)) return btn;
    if (!document.body) return null;
    btn = document.createElement("div");
    btn.id = "mab-totp-btn";
    btn.style.cssText =
      "position:fixed;top:64px;right:24px;z-index:2147483646;" +
      "background:#1d1d1f;color:#fff;padding:7px 14px;border-radius:8px;" +
      "box-shadow:0 4px 16px rgba(0,0,0,.3);font-family:monospace;" +
      "font-size:13px;cursor:pointer;user-select:none;display:none;";
    btn.title = "Click to re-copy the TOTP code";
    btn.onclick = async () => {
      const code = await getCode();
      if (code) { await copyText(code); flash("Copied " + code); }
    };
    document.body.appendChild(btn);
    return btn;
  }

  function flash(msg) {
    const b = ensureButton();
    if (!b) return;
    const old = b.textContent;
    b.textContent = msg;
    b.style.background = "#59a26b";
    setTimeout(() => {
      b.textContent = old;
      b.style.background = "#1d1d1f";
    }, 1500);
  }

  function setButton(code) {
    const b = ensureButton();
    if (!b) return;
    b.textContent = code || "------";
    b.style.display = code ? "block" : "none";
  }

  // ---- field detection ----
  const isTotpInput = (el) => {
    if (!el || el.tagName !== "INPUT") return false;
    if (el.disabled || el.readOnly) return false;
    const name = (el.name || "").toLowerCase();
    const id = (el.id || "").toLowerCase();
    const ac = (el.autocomplete || "").toLowerCase();
    const jl = (el.getAttribute("jsname") || "").toLowerCase();
    const ph = (el.placeholder || "").toLowerCase();
    const t = (el.type || "").toLowerCase();
    // Google Authenticator challenge page uses jsname="jFxqbc" / name="totpPin"
    if (jl.includes("jfxqbc") || name.includes("totppin")) return true;
    if (ac === "one-time-code" || ac === "otp") return true;
    if (name.match(/otp|totp|code|verify|pin|token/) && el.maxLength <= 8 && el.maxLength >= 4) return true;
    if (id.match(/otp|totp|code|verify/) && el.maxLength <= 8 && el.maxLength >= 4) return true;
    if (ph.match(/\d{6}|code|otp|totp|verify/) && el.maxLength <= 8) return true;
    // common: 6 separate single-digit inputs
    if (t === "tel" && el.maxLength >= 4 && el.maxLength <= 8
        && (name.includes("pin") || ph.match(/code|otp|\d{6}/))) return true;
    return false;
  };

  function findTotpInputs() {
    const all = document.querySelectorAll("input");
    const hits = [];
    for (const el of all) { if (isTotpInput(el)) hits.push(el); }
    return hits;
  }

  function fillInputs(code) {
    const inputs = findTotpInputs();
    for (const el of inputs) {
      try {
        el.focus();
        // use native setter so React/Angular listeners fire
        const proto = Object.getPrototypeOf(el);
        const setter = Object.getOwnPropertyDescriptor(proto, "value");
        if (setter && setter.set) setter.set.call(el, code);
        else el.value = code;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
        if (el.tagName) el.dispatchEvent(new KeyboardEvent("keydown", { bubbles: true, key: "Enter" }));
      } catch (e) { log("fill error", e); }
    }
    return inputs.length;
  }

  async function tryAutofill() {
    if (Date.now() - lastFill < 1500) return;   // throttle
    const code = await getCode();
    if (!code) { setButton(""); return; }
    setButton(code);
    const inputs = findTotpInputs();
    if (inputs.length === 0) return;
    lastFill = Date.now();
    const n = fillInputs(code);
    if (n > 0) {
      await copyText(code);
      flash("Copied " + code);
      log("filled", n, "fields with", code);
    }
  }

  // observer + polling
  let observer = null;
  function hookObserver() {
    if (observer || !document.body) return;
    observer = new MutationObserver(() => { tryAutofill(); });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  let pollHandle = null;
  function startPolling() {
    if (pollHandle) clearInterval(pollHandle);
    pollHandle = setInterval(tryAutofill, 3000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => { hookObserver(); startPolling(); });
  } else { hookObserver(); startPolling(); }
  // also try immediately
  setTimeout(tryAutofill, 500);
  setTimeout(tryAutofill, 2000);

  log("TOTP auto-fill init script loaded");
})();
"""


# ---- Python TOTP (RFC 6238) ----

def generate_totp(secret: str, timestamp: float | None = None,
                  period: int = 30, digits: int = 6) -> str:
    """Generate a TOTP code from a base32 secret."""
    key = _b32_decode(secret)
    t = int(timestamp or time.time()) // period
    msg = struct.pack(">Q", t)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    code = (struct.unpack(">I", h[offset:offset + 4])[0] & 0x7FFFFFFF)
    code = code % (10 ** digits)
    return str(code).zfill(digits)


def _b32_decode(secret: str) -> bytes:
    s = secret.strip().replace(" ", "").upper()
    pad = (8 - len(s) % 8) % 8
    s = s + "=" * pad
    try:
        return base64.b32decode(s)
    except Exception as e:
        raise ValueError(f"invalid base32 TOTP secret: {e}")


class TOTPManager:
    """Per-profile TOTP secret store + binding callback."""

    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        self.dir = ProfileManager().profile_dir(profile_id) / "totp"
        self.dir.mkdir(parents=True, exist_ok=True)

    @property
    def secret_file(self) -> Path:
        return self.dir / "secret.json"

    @staticmethod
    def is_enabled(profile: dict) -> bool:
        return bool(profile.get(FLAG))

    def enable(self, on: bool = True) -> None:
        ProfileManager().update(self.profile_id, {FLAG: bool(on)})

    def set_secret(self, secret: str) -> None:
        data = {"secret": secret.strip().replace(" ", ""),
                "updated": time.time()}
        self.secret_file.write_text(json.dumps(data, indent=2),
                                    encoding="utf-8")
        os.chmod(self.secret_file, 0o600)

    def get_secret(self) -> str | None:
        if not self.secret_file.exists():
            return None
        try:
            d = json.loads(self.secret_file.read_text(encoding="utf-8"))
            return d.get("secret")
        except Exception:
            return None

    def clear(self) -> None:
        self.secret_file.unlink(missing_ok=True)

    # ---- Playwright binding ----
    def bridge(self, source, op: str = ""):
        try:
            if op == "code":
                secret = self.get_secret()
                if not secret:
                    return ""
                return generate_totp(secret)
            if op == "secret":
                return self.get_secret() or ""
            return ""
        except Exception as e:
            return f"err:{e}"


def install(context, profile_id: str) -> None:
    mgr = TOTPManager(profile_id)
    try:
        context.expose_binding("__mabTotp", mgr.bridge)
    except Exception as e:
        print(f"[totp] expose_binding failed: {e}", flush=True)
    try:
        context.add_init_script(TOTP_AUTOFILL_JS)
    except Exception as e:
        print(f"[totp] add_init_script failed: {e}", flush=True)
    print(f"[totp] auto-fill installed for {profile_id}", flush=True)