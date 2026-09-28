#!/usr/bin/env python3
# Alert + customer acknowledgment sender for gochina.events leads.
# notify.py inquiry|error  < lead.json          (lead JSON on stdin)
# notify.py customer                        (lead JSON on stdin)
# Credentials from env: SMTP_USER / SMTP_PASS / NOTIFY_TO (systemd mail.conf)
import email.utils, json, os, re, smtplib, ssl, sys
from email.mime.text import MIMEText

USER = os.environ.get("SMTP_USER", "steviezhong@icloud.com")
PWD = os.environ.get("SMTP_PASS", "")
TO = os.environ.get("NOTIFY_TO", "contact@gochina.events")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def body(kind, lead):
    p = lead.get("payload", {})
    fields = [("ID", lead.get("id")), ("Time", lead.get("ts")),
              ("Name", p.get("name")), ("Contact", p.get("contact") or p.get("email")),
              ("Service", p.get("service")), ("Dates/Show", p.get("dates") or p.get("show")),
              ("Category/City", p.get("category") or p.get("city_show")),
              ("Quantity", p.get("quantity")), ("Budget", p.get("budget")),
              ("Role/Type", p.get("role") or p.get("attendee_type")),
              ("Country", p.get("country")), ("Message", p.get("message")),
              ("Source page", p.get("source_page")),
              ("UTM", " ".join(f"{k}={v}" for k, v in p.items() if k.startswith("utm")) or "—")]
    extra = ""
    if kind == "error":
        extra = "<p style='color:#a00'><b>SYSTEM ALERT</b> — one of the inquiry channels failed. Check errors.log on the server.</p>"
    rows = "".join(f"<tr><td><b>{k}</b></td><td style='white-space:pre-wrap'>{v or '—'}</td></tr>"
                   for k, v in fields)
    return f"""<html><body style='font-family:-apple-system,Segoe UI,sans-serif'>
<h2 style='color:#0f5c56'>New {kind}</h2>{extra}
<table border=1 cellpadding=6 style='border-collapse:collapse;border-color:#ccc'>{rows}</table>
<p style='color:#888;font-size:12px'>Sender is the site's alert mailbox, not a client.</p>
</body></html>"""

def send(to, subject, html):
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = USER
    msg["To"] = to
    msg["Date"] = email.utils.formatdate()
    ctx = ssl.create_default_context()
    s = smtplib.SMTP("smtp.mail.me.com", 587, timeout=30)
    s.starttls(context=ctx)
    s.login(USER, PWD)
    s.send_message(msg)
    s.quit()

def customer_ack(lead):
    p = lead.get("payload", {})
    zh = p.get("lang") == "zh" or any(ord(c) > 0x2e80 for c in (p.get("message") or ""))
    html = CUSTOMER_ADMIN_REPLY_ZH if zh else CUSTOMER_ADMIN_REPLY_EN
    head = "您的合作申请已收到" if zh else "Inquiry received — goChina Events"
    return ("[goChina Events] " + head, html)

CUSTOMER_ADMIN_REPLY_EN = """<p>Thank you — your inquiry has been received.</p>
<p>We reply within <b>one business day</b> (Mon–Sun 8:30–19:00, China Standard Time). No payment or documents are needed at this stage.</p>
<p>Prefer WhatsApp? Message us anytime at <b>+86 182 2441 6343</b>.</p>
<p style='color:#888'>goChina Events — independent trip & sourcing support in Guangzhou–Foshan and Shanghai. This is an automated acknowledgment.</p>"""

CUSTOMER_ADMIN_REPLY_ZH = """<p>您好，您的申请/询价已收到。</p>
<p>我们通常在 <b>一个工作日内</b>（周一至周日 8:30–19:00 中国时间）联系您。此阶段无需合同或付款信息。</p>
<p style='color:#888'>goChina Events · 本邮件为自动确认，无需直接回复。</p>"""

def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "inquiry"
    lead = json.load(sys.stdin)
    if not PWD:
        print("SMTP_PASS missing — notify skipped", file=sys.stderr); sys.exit(0)
    # 1) internal alert to operator
    head = "NEW INQUIRY" if kind == "inquiry" else "SYSTEM ALERT"
    name = lead.get("payload", {}).get("name", "?")
    send(TO, f"[goChina Events] {head} — {lead.get('payload', {}).get('name', '?')}", body(kind, lead))
    # 2) customer acknowledgment (only when a real email was provided and allowed kind)
    if kind == "inquiry":
        p = lead.get("payload", {})
        c = p.get("contact") or p.get("email") or ""
        if EMAIL_RE.match(c):
            subject, html = customer_ack(lead)
            send(c, subject, html)

if __name__ == "__main__":
    main()
