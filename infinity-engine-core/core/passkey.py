"""Software passkey authenticator injected into Camoufox profiles.

Camoufox is an ad-hoc-signed Firefox build, so the macOS platform
authenticator (iCloud Keychain / system passkey sheet) is unavailable: that
UI requires the restricted `com.apple.developer.web-browser.public-key-credential`
entitlement which only properly-signed browsers ship with.  This module gives
every profile its own *software* WebAuthn authenticator instead, the same way
password managers (1Password / Bitwarden …) provide software passkeys.

The emulator runs as a document-start init script that shadows
`navigator.credentials.create/get` inside the browser, generates real P-256
credentials with WebCrypto, maintains a proper incrementing sign-counter and
consistent UP/UV flags (the two things Google's risk engine checks), and asks
for an explicit in-page confirmation so a ceremony can never fire silently.

Each profile has its own credential store, so no authenticator identity is
shared across accounts.  Keys are software (exportable) and stored with
0600 perms in the profile directory.

Usage:
    mgr = PasskeyManager(profile_id)
    mgr.enable()                 # one-off per profile
    context.expose_binding("__mabPasskey", mgr.bridge)
    context.add_init_script(EMULATOR_JS)
"""

import json
import os
import time
from pathlib import Path

from .profile import ProfileManager

FLAG = "passkey_enabled"

EMULATOR_JS = r"""
(() => {
  const DEBUG = true;
  const log = (...a) => { console.log("[mab-passkey]", ...a); };

  const b64u = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf)))
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const fromB64u = (s) => {
    const b = s.replace(/-/g, "+").replace(/_/g, "/");
    const pad = b.length % 4 ? "=".repeat(4 - (b.length % 4)) : "";
    return Uint8Array.from(atob(b + pad), (c) => c.charCodeAt(0));
  };
  const concat = (parts) => {
    const n = parts.reduce((s, p) => s + p.length, 0);
    const out = new Uint8Array(n);
    let o = 0;
    for (const p of parts) { out.set(p, o); o += p.length; }
    return out;
  };
  const sha256 = async (data) =>
      new Uint8Array(await crypto.subtle.digest("SHA-256", data));

  // ---- minimal CBOR for the pieces WebAuthn needs ----
  const u8Int = (n) => {
    if (n < 24) return new Uint8Array([n]);
    if (n <= 0xff) return new Uint8Array([0x18, n]);
    if (n <= 0xffff) { const b = new Uint8Array(3); b[0] = 0x19;
      new DataView(b.buffer).setUint16(1, n, false); return b; }
    const b = new Uint8Array(5); b[0] = 0x1a;
    new DataView(b.buffer).setUint32(1, n, false); return b;
  };
  const cborInt = (n) => {
    const neg = n < 0;
    const v = neg ? -1 - n : n;
    const h = u8Int(v);
    h[0] = (neg ? 0x20 : 0x00) | (h[0] & 0x1f);
    return h;
  };
  const cborBytes = (u) => { const h = u8Int(u.length); h[0] = 0x40 | (h[0] & 0x1f);
    return concat([h, u]); };
  const cborText = (s) => { const u = new TextEncoder().encode(s);
    const h = u8Int(u.length); h[0] = 0x60 | (h[0] & 0x1f); return concat([h, u]); };
  const cborMap = (pairs) => { const h = u8Int(pairs.length);
    h[0] = 0xa0 | (h[0] & 0x1f); const parts = [h];
    for (const [k, v] of pairs) parts.push(k, v); return concat(parts); };

  // ---- per-profile credential store (bridged to Python) ----
  const store = {
    creds: null,
    async ensure() {
      if (this.creds) return this.creds;
      try {
        const raw = await window.__mabPasskey("load");
        this.creds = raw ? JSON.parse(raw) : [];
      } catch (e) { log("load failed", e); this.creds = []; }
      return this.creds;
    },
    async save() {
      try { await window.__mabPasskey("save", JSON.stringify(this.creds)); }
      catch (e) { log("save failed", e); }
    },
    async find(rpId, allowed) {
      const creds = await this.ensure();
      return creds.filter((c) => c.rpId === rpId &&
          (!allowed || allowed.length === 0 || allowed.includes(c.credentialId)));
    },
  };

  // ---- explicit user confirmation (the "tap" of a security key) ----
  function confirmUI(kind, rpId) {
    return new Promise((resolve) => {
      let done = false;
      const wrap = document.createElement("div");
      wrap.style.cssText =
        "position:fixed;top:24px;left:50%;transform:translateX(-50%);" +
        "z-index:2147483647;background:#1d1d1f;color:#fff;padding:14px 18px;" +
        "border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,.35);" +
        "font-family:-apple-system,'PingFang SC',sans-serif;font-size:14px;" +
        "max-width:420px;text-align:center;user-select:none;";
      const title = document.createElement("div");
      title.style.cssText = "font-weight:600;margin-bottom:4px;";
      title.textContent = "Passkey 确认 · Confirm";
      const sub = document.createElement("div");
      sub.style.cssText = "opacity:.75;margin-bottom:12px;word-break:break-all;";
      sub.textContent = `${kind === "create" ? "注册 Create" : "使用 Use"} · ${rpId}`;
      const row = document.createElement("div");
      row.style.cssText = "display:flex;gap:10px;justify-content:center;";
      const deny = document.createElement("button");
      deny.id = "mab-passkey-deny";
      deny.textContent = "拒绝 Deny";
      deny.style.cssText = "background:#cb6964;color:#fff;border:0;border-radius:6px;" +
        "padding:6px 16px;cursor:pointer;font-size:14px;";
      const allow = document.createElement("button");
      allow.id = "mab-passkey-allow";
      allow.textContent = "允许 Allow";
      allow.style.cssText = "background:#59a26b;color:#fff;border:0;border-radius:6px;" +
        "padding:6px 16px;cursor:pointer;font-size:14px;font-weight:600;";
      const finish = (ok) => { if (done) return; done = true; wrap.remove(); resolve(ok); };
      allow.onclick = () => finish(true);
      deny.onclick = () => finish(false);
      row.append(deny, allow);
      wrap.append(title, sub, row);
      document.documentElement.appendChild(wrap);
    });
  }

  // ---- WebAuthn data construction ----
  const buildCose = (x, y) => cborMap([
    [cborInt(1), cborInt(2)],    // kty = EC2
    [cborInt(3), cborInt(-7)],   // alg = ES256
    [cborInt(-1), cborInt(1)],   // crv = P-256
    [cborInt(-2), cborBytes(x)],
    [cborInt(-3), cborBytes(y)],
  ]);



  async function makeCredential(publicKey) {
    const rpId = publicKey.rp.id;
    const user = publicKey.user || { id: new TextEncoder().encode("user") };
    const attFmt = publicKey.attestation || "none";
    const clientDataJSON = JSON.stringify({
      type: "webauthn.create",
      challenge: b64u(publicKey.challenge),
      origin: location.origin,
      crossOrigin: false,
    });
    const clientDataHash = await sha256(new TextEncoder().encode(clientDataJSON));
    const keypair = await crypto.subtle.generateKey(
        { name: "ECDSA", namedCurve: "P-256" }, true, ["sign"]);
    const jwk = await crypto.subtle.exportKey("jwk", keypair.privateKey);
    const rpIdHash = await sha256(new TextEncoder().encode(rpId));
    const credIdRaw = crypto.getRandomValues(new Uint8Array(32));
    const credentialId = b64u(credIdRaw);
    const userHandle = b64u(user.id);

    const flags = 0x01 | 0x04 | 0x40 | 0x08 | 0x10; // UP|UV|AT|BE|BS
    let authData = new Uint8Array(rpIdHash.length + 1 + 4);
    authData.set(rpIdHash, 0);
    authData[32] = flags;
    new DataView(authData.buffer).setUint32(33, 0, false); // signCount
    const len = new Uint8Array(2);
    new DataView(len.buffer).setUint16(0, credIdRaw.length, false);
    // TouchID AAGUID (platform authenticator on macOS)
    const AAGUID = new Uint8Array([
      0x08, 0x98, 0x70, 0x58, 0xca, 0xdc, 0x4b, 0x81,
      0xb6, 0xe1, 0x30, 0xde, 0x50, 0xdc, 0xbe, 0x96]);
    const att = concat([AAGUID, len, credIdRaw,
                        buildCose(fromB64u(jwk.x), fromB64u(jwk.y))]);
    authData = concat([authData, att]);

    const sigInput = concat([authData, clientDataHash]);
    const signature = new Uint8Array(await crypto.subtle.sign(
        { name: "ECDSA", hash: "SHA-256" }, keypair.privateKey, sigInput));

    let attStmt;
    let fmt;
    if (attFmt === "direct" || attFmt === "indirect") {
      try {
        fmt = "packed";
        attStmt = cborMap([
          [cborInt(1), cborInt(-7)],          // alg = ES256
          [cborInt(2), cborBytes(signature)],  // sig over authData || clientDataHash
        ]);
        log("packed self-attestation built, sig.len:", signature.length);
      } catch (e) {
        log("packed self-attestation failed, falling back to none:", e.message);
        fmt = "none";
        attStmt = cborMap([]);
      }
    } else {
      fmt = "none";
      attStmt = cborMap([]);
    }

    const attestationObject = cborMap([
      [cborInt(1), cborText(fmt)],
      [cborInt(2), attStmt],
      [cborInt(3), cborBytes(authData)],
    ]);

    const pubKey = await crypto.subtle.importKey(
        "jwk", { kty: "EC", crv: "P-256", x: jwk.x, y: jwk.y, ext: true },
        { name: "ECDSA", namedCurve: "P-256" }, true, []);
    const pubKeySpki = await crypto.subtle.exportKey("spki", pubKey);

    await store.ensure();
    store.creds.push({ rpId, credentialId, userHandle, jwk,
                       signCount: 0, createdAt: Date.now() });
    await store.save();
    log("created passkey", rpId, credentialId, "fmt:", fmt);

    const u8toAB = (u) => {
      if (u instanceof ArrayBuffer) return u;
      if (u && u.buffer instanceof ArrayBuffer)
        return u.buffer.slice(u.byteOffset, u.byteOffset + u.byteLength);
      return new Uint8Array(u || []).buffer;
    };
    const resp = Object.create(AuthenticatorAttestationResponse.prototype, {
      clientDataJSON:     { value: u8toAB(new TextEncoder().encode(clientDataJSON)) },
      attestationObject:  { value: u8toAB(attestationObject) },
    });
    Object.defineProperties(resp, {
      getTransports:          { value: () => ["internal"] },
      getPublicKey:           { value: () => u8toAB(pubKeySpki) },
      getPublicKeyAlgorithm:  { value: () => -7 },
      getAuthenticatorData:   { value: () => u8toAB(authData) },
    });

    const obj = Object.create(PublicKeyCredential.prototype);
    Object.defineProperties(obj, {
      type:         { value: "public-key", writable: false },
      id:           { value: credentialId, writable: false },
      rawId:        { value: u8toAB(credIdRaw), writable: false },
      authenticatorAttachment: { value: "platform", writable: false },
      response:     { value: resp, writable: false },
      getClientExtensionResults: {
        value: () => ({ credProps: { rk: true } }), writable: false },
    });
    return obj;
  }

  async function getAssertion(publicKey) {
    const rpId = publicKey.rpId;
    const allowed = publicKey.allowCredentials
        ? publicKey.allowCredentials.map((c) => b64u(c.id)) : [];
    const creds = await store.find(rpId, allowed);
    if (!creds.length) {
      throw new DOMException("no passkey for this site", "NotAllowedError");
    }
    const cred = creds[0];
    const clientDataJSON = JSON.stringify({
      type: "webauthn.get",
      challenge: b64u(publicKey.challenge),
      origin: location.origin,
      crossOrigin: false,
    });
    const clientDataHash = await sha256(new TextEncoder().encode(clientDataJSON));
    const rpIdHash = await sha256(new TextEncoder().encode(rpId));
    cred.signCount = (cred.signCount || 0) + 1;
    const flags = 0x01 | 0x04 | 0x08 | 0x10; // UP|UV|BE|BS
    const authData = new Uint8Array(37);
    authData.set(rpIdHash, 0);
    authData[32] = flags;
    new DataView(authData.buffer).setUint32(33, cred.signCount, false);
    const sigInput = concat([authData, clientDataHash]);
    const signingKey = await crypto.subtle.importKey(
        "jwk", cred.jwk, { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"]);
    const signature = new Uint8Array(await crypto.subtle.sign(
        { name: "ECDSA", hash: "SHA-256" }, signingKey, sigInput));
    await store.save();
    log("asserted", rpId, cred.credentialId, "count", cred.signCount);

    const u8toAB2 = (u) => {
      if (u instanceof ArrayBuffer) return u;
      if (u && u.buffer instanceof ArrayBuffer)
        return u.buffer.slice(u.byteOffset, u.byteOffset + u.byteLength);
      return new Uint8Array(u || []).buffer;
    };
    const resp = Object.create(AuthenticatorAssertionResponse.prototype, {
      clientDataJSON:     { value: u8toAB2(new TextEncoder().encode(clientDataJSON)) },
      authenticatorData:  { value: u8toAB2(authData) },
      signature:          { value: u8toAB2(signature) },
      userHandle:         { value: u8toAB2(fromB64u(cred.userHandle)) },
    });
    Object.defineProperties(resp, {
      getAuthenticatorData: { value: () => u8toAB2(authData) },
    });

    const obj = Object.create(PublicKeyCredential.prototype);
    Object.defineProperties(obj, {
      type:         { value: "public-key", writable: false },
      id:           { value: cred.credentialId, writable: false },
      rawId:        { value: u8toAB2(fromB64u(cred.credentialId)), writable: false },
      authenticatorAttachment: { value: "platform", writable: false },
      response:     { value: resp, writable: false },
      getClientExtensionResults: {
        value: () => ({}), writable: false },
    });
    return obj;
  }

  // ---- capture helpers ----
  const capLog = (obj) => { try { window.__mabPasskey("log", JSON.stringify(obj)); } catch(e){} };
  const u8Hex = (buf) => buf ? Array.from(new Uint8Array(buf instanceof ArrayBuffer ? buf : buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength))).map(b => b.toString(16).padStart(2, "0")).join("") : null;
  const u8B64 = (buf) => buf ? btoa(String.fromCharCode(...new Uint8Array(buf instanceof ArrayBuffer ? buf : buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength)))) : null;

  // ---- intercept fetch + XHR for Google submission capture ----
  const _origFetch = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const [url, opts] = args;
    if (opts && opts.method === "POST" && opts.body) {
      try {
        const body = typeof opts.body === "string" ? opts.body : await opts.body.text();
        if (body.includes("attestationObject") || body.includes("clientDataJSON") || body.includes("rawId")) {
          try {
            capLog({ t: "FETCH_SUBMIT", url: String(url).slice(0, 400), body: JSON.parse(body) });
          } catch(e) {
            capLog({ t: "FETCH_SUBMIT_RAW", url: String(url).slice(0, 400), body: body.slice(0, 8000) });
          }
        }
      } catch(e) {}
    }
    const resp = await _origFetch(...args);
    if (opts && opts.method === "POST") {
      try {
        const clone = resp.clone();
        const text = await clone.text();
        capLog({ t: "FETCH_RESP", url: String(url).slice(0, 400), status: resp.status,
                 bodyLen: text.length, preview: text.slice(0, 2000) });
      } catch(e) {}
    }
    return resp;
  };

  const _origXhrOpen = XMLHttpRequest.prototype.open;
  const _origXhrSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this.__capM = method; this.__capU = String(url);
    return _origXhrOpen.call(this, method, url, ...rest);
  };
  XMLHttpRequest.prototype.send = function(body) {
    if (this.__capM === "POST" && body) {
      try {
        const b = typeof body === "string" ? body : String(body);
        if (b.includes("attestationObject") || b.includes("clientDataJSON") || b.includes("rawId")) {
          try { capLog({ t: "XHR_SUBMIT", url: this.__capU.slice(0, 400), body: JSON.parse(b) }); }
          catch(e) { capLog({ t: "XHR_SUBMIT_RAW", url: this.__capU.slice(0, 400), body: b.slice(0, 8000) }); }
        }
      } catch(e) {}
    }
    this.addEventListener("load", () => {
      try { capLog({ t: "XHR_RESP", url: this.__capU.slice(0, 400), status: this.status,
                     body: this.responseText.slice(0, 2000) }); } catch(e) {}
    });
    return _origXhrSend.call(this, body);
  };

  // ---- shadow navigator.credentials ----
  const nativeCreate = navigator.credentials.create.bind(navigator.credentials);
  const nativeGet = navigator.credentials.get.bind(navigator.credentials);

  navigator.credentials.create = async (options) => {
    if (options && options.publicKey) {
      const pk = options.publicKey;
      log("create() called, rp.id:", pk.rp.id, "origin:", location.origin);
      capLog({ t: "CREATE_OPTS", origin: location.origin,
               rpId: pk.rp && pk.rp.id, rpName: pk.rp && pk.rp.name,
               userName: pk.user && pk.user.name,
               userDisplayName: pk.user && pk.user.displayName,
               userIdHex: u8Hex(pk.user && pk.user.id),
               challengeHex: u8Hex(pk.challenge),
               challengeB64: u8B64(pk.challenge),
               timeout: pk.timeout, attestation: pk.attestation,
               authenticatorSelection: pk.authenticatorSelection,
               pubKeyCredParams: pk.pubKeyCredParams,
               extensions: pk.extensions });
      if (!(await confirmUI("create", pk.rp.id))) {
        throw new DOMException("cancelled by user", "NotAllowedError");
      }
      const cred = await makeCredential(pk);
      log("create() returning cred, id:", cred.id);
      capLog({ t: "CREATE_RESULT", credId: cred.id, rawIdLen: cred.rawId.byteLength,
               rawIdHex: u8Hex(cred.rawId), type: cred.type,
               authnAttachment: cred.authenticatorAttachment,
               clientDataJSONStr: new TextDecoder().decode(cred.response.clientDataJSON),
               attObjB64: u8B64(cred.response.attestationObject),
               transports: cred.response.getTransports(),
               pubKeyAlg: cred.response.getPublicKeyAlgorithm(),
               authDataLen: cred.response.getAuthenticatorData().byteLength });
      return cred;
    }
    return nativeCreate(options);
  };

  navigator.credentials.get = async (options) => {
    if (options && options.publicKey) {
      if (!(await confirmUI("get", options.publicKey.rpId))) {
        throw new DOMException("cancelled by user", "NotAllowedError");
      }
      return getAssertion(options.publicKey);
    }
    return nativeGet(options);
  };

  if (window.PublicKeyCredential) {
    Object.defineProperty(window.PublicKeyCredential,
        "isUserVerifyingPlatformAuthenticatorAvailable", { configurable: true,
          value: () => Promise.resolve(true) });
    Object.defineProperty(window.PublicKeyCredential,
        "isConditionalMediationAvailable", { configurable: true,
          value: () => Promise.resolve(false) });
  }
})();
"""


class PasskeyManager:
    """Per-profile software-passkey store + Playwright bridge handler."""

    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        self.dir = ProfileManager().profile_dir(profile_id) / "passkey"
        self.dir.mkdir(parents=True, exist_ok=True)

    # ---- enable / disable ----
    @staticmethod
    def is_enabled(profile: dict) -> bool:
        return bool(profile.get(FLAG))

    def enable(self, on: bool = True) -> None:
        ProfileManager().update(self.profile_id, {FLAG: bool(on)})

    # ---- storage ----
    @property
    def store_file(self) -> Path:
        return self.dir / "credentials.json"

    def _load(self) -> list:
        try:
            return json.loads(self.store_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []

    def _save(self, creds: list) -> None:
        try:
            self.store_file.write_text(
                json.dumps(creds, indent=2, ensure_ascii=False),
                encoding="utf-8")
            os.chmod(self.store_file, 0o600)
        except OSError as e:
            print(f"[passkey] save failed: {e}", flush=True)

    def list(self) -> list:
        return sorted(self._load(), key=lambda c: c.get("createdAt", 0))

    def delete(self, credential_id: str) -> bool:
        creds = self._load()
        nxt = [c for c in creds if c.get("credentialId") != credential_id]
        if len(nxt) == len(creds):
            return False
        self._save(nxt)
        return True

    def clear(self) -> None:
        self._save([])

    # ---- Playwright binding ----
    @property
    def capture_file(self) -> Path:
        return self.dir / "capture.jsonl"

    def _capture(self, entry: dict) -> str:
        """Append a diagnostic entry to the capture log."""
        try:
            with open(self.capture_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return "ok"
        except OSError as e:
            return f"err:{e}"

    def bridge(self, source, op: str, payload: str = ""):
        """Handler for context.expose_binding('__mabPasskey', ...)."""
        try:
            if op == "load":
                return json.dumps(self._load())
            if op == "save":
                self._save(json.loads(payload or "[]"))
                return "ok"
            if op == "log":
                self._capture(json.loads(payload or "{}"))
                return "ok"
            if op == "clear_log":
                try:
                    self.capture_file.unlink(missing_ok=True)
                except Exception:
                    pass
                return "ok"
            return "err:unknown-op"
        except Exception as e:
            return f"err:{e}"


def install(context, profile_id: str) -> None:
    """Wire the software passkey authenticator into a Camoufox context.

    Call right after the context is created and before any navigation.
    Idempotent per process (the persistent context owns a single store).
    """
    mgr = PasskeyManager(profile_id)
    try:
        mgr.capture_file.unlink(missing_ok=True)
    except Exception:
        pass
    try:
        context.expose_binding("__mabPasskey", mgr.bridge)
    except Exception as e:
        print(f"[passkey] expose_binding failed: {e}", flush=True)
    try:
        context.add_init_script(EMULATOR_JS)
    except Exception as e:
        print(f"[passkey] add_init_script failed: {e}", flush=True)
    print(f"[passkey] software authenticator installed for {profile_id}", flush=True)
