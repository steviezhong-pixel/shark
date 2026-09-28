#!/usr/bin/env bash
# Run inside /home/ubuntu via Tencent Web console (VNC / OrcaTerm).
# One-shot: installs deps, pulls app, wires systemd + nginx, starts service.
export DEBIAN_FRONTEND=noninteractive
set -e
INFINITY_TOKEN="1aa0618a8ccaed2513508689"

echo "== 1/6 拉取 app（Infinity-Web）"
mkdir -p /tmp/iw && cd /tmp/iw
rm -rf iwapp && git clone --depth 1 -b browserweb https://github.com/steviezhong-pixel/shark iwapp 2>&1 | tail -1
sudo mkdir -p /home/ubuntu/infinity-web
sudo rsync -a /tmp/iw/iwapp/infinity-web/ /home/ubuntu/infinity-web/

echo "== 2/6 系统依赖（Xvfb / noVNC / websockify）"
sudo apt-get update -qq >/dev/null
sudo apt-get install -y -qq xvfb novnc websockify python3-venv >/dev/null

echo "== 3/6 引擎核心（Camoufox + Playwright，独立venv，不影响goChina.site）"
mkdir -p /home/ubuntu/infinity-lines
cd /home/ubuntu/infinity-lines
[ -f .venv/bin/python3 ] || python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip 2>/dev/null || true
.venv/bin/pip install --quiet "camoufox[geoip]" playwright
.venv/bin/python -m camoufox fetch --browseronly 2>/dev/null || .venv/bin/python -m camoufox fetch || true
[ -f main.py ] || echo "（提醒：把 Infinity Lines 仓库的 main.py + core/ 目录 rsync 到 /home/ubuntu/infinity-lines/ ——日后我来做）"

echo "== 4/6 systemd service"
sudo tee /etc/systemd/system/infinity-web.service >/dev/null <<UNIT
[Unit]
Description=Infinity Web fingerprint browser control
After=network.target

[Service]
WorkingDirectory=/home/ubuntu/infinity-web
ExecStart=/usr/bin/python3 /home/ubuntu/infinity-web/app.py
Environment=INFINITY_WEB_TOKEN=${INFINITY_TOKEN}
Environment=INFINITY_WEB_ROOT=/home/ubuntu/infinity-lines
Environment=INFINITY_WEB_DATA=/home/ubuntu/infinity-web-data
User=ubuntu
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now infinity-web
sleep 1
systemctl is-active infinity-web

echo "== 5/6 nginx: /browser/ 路径挂在 gochina 443 vhost（启websocket）"
if ! grep -q "location ^~ /browser/" /etc/nginx/sites-available/gochina; then
python3 - <<PYEOF
import re
p="/etc/nginx/sites-available/gochina"
t=open(p).read()
block='''
    location ^~ /browser/ {
        proxy_pass http://127.0.0.1:9001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        # websocket upgrade: use the closest standard form
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }

    location ^~ /browser-ws/6100/ {
        proxy_pass http://127.0.0.1:6100/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }

    location ^~ /browser-ws/6101/ {
        proxy_pass http://127.0.0.1:6101/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
'''
# insert before the final close brace of the 443 server block
idx=t.rfind("}\n}")
if idx == -1: idx=t.rfind("\n}")
t=(t[:idx]+block+t[idx:])
open(p,"w").write(t)
print("location inserted")
PYEOF
sudo nginx -t && sudo systemctl reload nginx
fi
echo DONE-all — open https://gochina.events/browser/${INFINITY_TOKEN}/
