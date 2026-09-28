#!/usr/bin/env bash
# weekly-shop-report.sh — prints a simple funnel report from server analytics + lead files.
# Usage on server: bash weekly-report.sh
cd "$(dirname "$0")"
THIRTY=$(date -u -d '-30 days' +%Y-%m-%dT%H)
{
echo "== Last 30 days =="
python3 - val <<PY
import json, glob, datetime, collections, sys
d0 = "$(date -u -d '-30 days' +%Y-%m-%d)"
# analytics
views={}; refs={}; visitors=set(); conv=0
try:
    for line in open("data/leads/analytics.jsonl"):
        r=json.loads(line)
        if r["ts"][:10] < d0: continue
        if r.get("bot"): continue
        p=r["p"]; views[p]=views.get(p,0)+1
        if r.get("r"):
            ref=json.loads('"'+r["r"]+'"') if isinstance(r["r"],str) else r["r"]
            refs[ref]=refs.get(ref,0)+1
        visitors.add(r.get("h"))
except FileNotFoundError: pass
print(f"Human page views: {sum(views.values())}, unique visitors: {len(visitors)}")
for p,n in sorted(views.items(),key=lambda x:-x[1])[:12]: print(f"  {p}: {n}")
drop=[r for r in refs if "google" in r or "bing" in r or "baidu" in r]
if refs: print("Top referrers:", sorted(refs.items(),key=lambda x:-x[1])[:5])
# leads
leads=0; byday={}
for f in glob.glob("data/leads/buyer.jsonl"):
    for line in open(f):
        r=json.loads(line); byday[r["ts"][:10]]=byday.get(r["ts"][:10],0)+1
print("Buyer inquiries:",len(byday))
PY
} 2>/dev/null
echo "== AI crawler hits (last 7d from nginx, by UA) =="
sudo grep -oE "(GPTBot|OAI-SearchBot|ChatGPT-User|PerplexityBot|ClaudeBot|Claude-Web|anthropic-ai|Google-Extended|Bytespider|Applebot|Bingbot|YandexBot)" /var/log/nginx/access.log 2>/dev/null | sort | uniq -c | sort -rn
