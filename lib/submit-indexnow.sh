#!/usr/bin/env bash
# submit-indexnow.sh — push sitemap URLs to IndexNow (Bing/Yandex pickup in hours).
set -e
cd /home/ubuntu/gochina
KEY=$(ls site/*.txt 2>/dev/null | head -1 | xargs cat)
URLS=$(mktemp)
curl -s https://gochina.events/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' > "$URLS"
python3 - "$KEY" "$URLS" <<'PY'
import json, sys, subprocess
key, urls_f = sys.argv[1], sys.argv[2]
urls = [l.strip() for l in open(urls_f) if l.strip()]
body = json.dumps({"host": "gochina.events", "key": key, "urlList": urls[:200]})
r = subprocess.run(["curl","-s","-X","POST","https://api.indexnow.org/indexnow","-H","Content-Type: application/json; charset=utf-8","-d",body,"-o","/tmp/in.txt","-w","%{http_code}"],capture_output=True,text=True)
print("indexnow:", r.stdout, open("/tmp/in.txt").read()[:100])
PY
date -u >> data/leads/indexnow.log
