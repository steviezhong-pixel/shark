#!/usr/bin/env node
// gochina.events — static site + lead API (zero-dependency Node).
import { createServer } from "node:http";
import { createReadStream, existsSync, statSync, appendFileSync, mkdirSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { randomUUID, createHash } from "node:crypto";
import { fileURLToPath } from "node:url";

const PORT = process.env.PORT || 8787;
const HERE = fileURLToPath(new URL(".", import.meta.url));
const SITE = join(HERE, "site");
const LEADS = join(HERE, "data", "leads");
mkdirSync(LEADS, { recursive: true });

const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".webp": "image/webp", ".svg": "image/svg+xml", ".ico": "image/x-icon", ".pdf": "application/pdf",
  ".xml": "application/xml", ".txt": "text/plain; charset=utf-8",
};

const FILES = {
  "api/lead": "buyer.jsonl",
  "api/meetup": "meetup-interest.jsonl",
  "api/partner/supplier": "partner-supplier.jsonl",
  "api/partner/local-service": "partner-local-service.jsonl",
  "api/partner/sponsorship": "sponsorship.jsonl",
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const WA_RE = /^\+?[()\d][\d()\s-]{6,}$/;

function alert(msg) {
  try {
    appendFileSync(join(LEADS, "errors.log"), `${new Date().toISOString()} ${msg}\n`);
  } catch { /* never throw from alerting */ }
  if (process.env.ALERT_WEBHOOK) {
    fetch(process.env.ALERT_WEBHOOK, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service: "gochina-events", message: msg }),
    }).catch(() => {});
  }
}

// simple per-IP rate limit
const hits = new Map();
const WINDOW = 60_000, MAX = 6;
function rateLimited(ip) {
  const now = Date.now();
  const arr = (hits.get(ip) || []).filter((t) => now - t < WINDOW);
  arr.push(now);
  hits.set(ip, arr);
  if (hits.size > 5000) hits.clear(); // bound memory
  return arr.length > MAX;
}

const readBody = (req) =>
  new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (c) => { data += c; if (data.length > 1e6) { reject(new Error("too large")); req.destroy(); } });
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });

const parseForm = (raw) => {
  const out = {};
  for (const pair of raw.split("&")) {
    if (!pair) continue;
    const i = pair.indexOf("=");
    const k = i < 0 ? pair : pair.slice(0, i);
    const v = i < 0 ? "" : pair.slice(i + 1);
    out[decodeURIComponent(k.replace(/\+/g, " "))] = decodeURIComponent(v.replace(/\+/g, " ")).trim();
  }
  return out;
};

function contactValid(p) {
  const c = p.contact || p.email || "";
  return EMAIL_RE.test(c) || WA_RE.test(c);
}

async function api(req, res, path, ip) {
  let p;
  try { p = parseForm(await readBody(req)); }
  catch { return sendJson(res, 413, { error: "Body too large or unreadable." }); }

  // honeypot field: act successful so bots don't retry
  if (p["company_website"]) return sendJson(res, 200, { ok: true, message: "Thank you — inquiry received." });

  const missing = [];
  if (!p.name) missing.push("name");
  if (!contactValid(p)) missing.push("a valid email or WhatsApp number");
  if (path.startsWith("api/partner/") && !p.company) missing.push("company name");
  if (path === "api/meetup" && !p.attendee_type) missing.push("attendee type");
  if (path === "api/partner/sponsorship" && p.consent !== "yes") missing.push("confirmation checkbox");
  if (missing.length) return sendJson(res, 400, { error: `Please complete: ${missing.join(", ")}.` });

  const record = { id: randomUUID(), ts: new Date().toISOString(), type: path, payload: p };
  try {
    appendFileSync(join(LEADS, FILES[path] || "other.jsonl"), JSON.stringify(record) + "\n");
    alert(`NEW_LEAD type=${path} id=${record.id} name=${p.name}`);
    // email push notification (iCloud SMTP via notify.py; credentials from systemd env file)
    if (process.env.NOTIFY_TO && process.env.SMTP_PASS) {
      const { spawn } = await import("node:child_process");
      const child = spawn("python3", [join(HERE, "lib", "notify.py"), "inquiry"], { env: process.env });
      child.stdin.write(JSON.stringify(record));
      child.stdin.end();
      child.on("error", (e) => alert(`NOTIFY_FAILED err=${e.message}`));
      child.on("exit", (c) => { if (c !== 0) alert(`NOTIFY_EXIT code=${c} lead=${record.id}`); });
    }
  } catch (e) {
    alert(`STORE_FAILED type=${path} err=${(e && e.message) || "?"}`);
    return sendJson(res, 500, { error: "Could not record your inquiry server-side. Please retry shortly." });
  }

  const msg =
    path === "api/meetup"
      ? "Thank you — interest recorded. We only write back when a real event matches your profile."
      : p.lang === "zh"
        ? "提交成功，已收到您的资料，通常一个工作日内联系您。"
        : "Thank you — inquiry received. We reply within one business day.";
  sendJson(res, 200, { ok: true, id: record.id, message: msg });
}

const sendJson = (res, status, obj) => {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" });
  res.end(JSON.stringify(obj));
};

function serveStatic(res, rel) {
  const p = join(SITE, rel);
  if (!p.startsWith(SITE) || !existsSync(p) || statSync(p).isDirectory()) return send404(res);
  res.writeHead(200, { "content-type": MIME[extname(p)] || "application/octet-stream", "cache-control": "public, max-age=3600" });
  createReadStream(p).pipe(res);
}
function send404(res) {
  const f = join(SITE, "404.html");
  res.writeHead(404, { "content-type": "text/html; charset=utf-8" });
  if (existsSync(f)) createReadStream(f).pipe(res); else res.end("404 Not Found");
}

const server = createServer(async (req, res) => {
  let url = decodeURIComponent(new URL(req.url, "http://x").pathname);
  url = normalize(url).replace(/^(\.\.[/\\])+/, "");

  if (req.method === "POST" && url === "/api/track") {
    try {
      const raw = await readBody(req);
      const d = JSON.parse(raw || "{}");
      const ip = (req.headers["x-real-ip"] || "").toString();
      const h = createHash("sha256").update(ip + "salt-gc").digest("hex").slice(0, 16);
      const ua = (req.headers["user-agent"] || "").toString();
      const isBot = /bot|crawl|spider|slurp|ChatGPT|OAI|Perplexity/i.test(ua);
      appendFileSync(join(LEADS, "analytics.jsonl"), JSON.stringify({
        ts: new Date().toISOString(), p: String(d.p||"/").slice(0,120), r: String(d.r||"").slice(0,220),
        h, bot: isBot, lang: String(d.l||"").slice(0,10), w: String(d.w||"").slice(0,6)
      }) + "\n");
      res.writeHead(204); return res.end();
    } catch { res.writeHead(400); return res.end(); }
  }
  if (req.method === "POST" && url.startsWith("/api/")) {
    const ip = (req.headers["x-real-ip"] || req.socket.remoteAddress || "").toString();
    if (rateLimited(ip)) {
      alert(`RATE_LIMITED ip=${ip}`);
      return sendJson(res, 429, { error: "Too many submissions — please wait a minute." });
    }
    try { return await api(req, res, url.replace(/^\//, "").replace(/\/$/, ""), ip); }
    catch (e) {
      alert(`HANDLER_FAILED ${url} err=${(e && e.message) || "?"}`);
      return sendJson(res, 500, { error: "Internal error — please retry." });
    }
  }
  if (req.method !== "GET" && req.method !== "HEAD") { res.writeHead(405); return res.end(); }

  if (url !== "/" && !url.endsWith("/") && !extname(url)) { res.writeHead(301, { location: url + "/" }); return res.end(); }
  const direct = url.replace(/^\//, "").replace(/\/$/, "");
  if (extname(direct)) return serveStatic(res, direct);
  if (direct) return serveStatic(res, `${direct}/index.html`);
  return serveStatic(res, "index.html");
});

server.listen(PORT, () => console.log(`gochina.events app on :${PORT}`));
