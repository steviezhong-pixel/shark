#!/bin/bash
# 粘贴到网页终端。一次效果：清理 /browser/ 误留 location，纯净地放到主443块。
set -e
sudo cp /etc/nginx/sites-available/gochina /etc/nginx/sites-available/gochina.bk.$(date +%s)
sudo python3 - <<'PYEOF'
import re
p = "/etc/nginx/sites-available/gochina"
t = open(p).read()
# 无论现在是否有 location /browser/，先清理：
t = re.sub(r"    [lL]ocation \^~ /browser.*?\n    \}\n", "", t, flags=re.S)
block = '''    # ---- infinityweb ----
    location ^~ /browser/1aa0618a8ccaed2513508689/ {
        proxy_pass http://127.0.0.1:9001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400s;
    }
    location ^~ /browser-ws/6100/ {
        proxy_pass http://127.0.0.1:6100/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
    location ^~ /browser-ws/6101/ {
        proxy_pass http://127.0.0.1:6101/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
    # -------------
'''
t = t.replace("    location / {\n        try_files $uri $uri/ =404;\n    }",
    block + "\n    location / {\n        try_files $uri $uri/ =404;\n    }")
open(p, "w").write(t)
PYEOF
sudo nginx -t 2>&1 | tail -1
sudo systemctl reload nginx
curl -s -o /dev/null -w "browser-ui:%{http_code}\n" --max-time 20 "https://gochina.events/browser/1aa0618a8ccaed2513508689/"
curl -s -o /dev/null -w "site-home:%{http_code}\n" --max-time 10 https://gochina.events/
