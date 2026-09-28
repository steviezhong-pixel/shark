#!/bin/bash
# daily-post.sh — publish one editorial-board post per day, automatically.
# Flow: pick first idea from src/blog.mjs queue → generate article via opencode (strict no-fabrication rules)
#       → rebuild site → rsync to server → IndexNow push. Leaves daily-post.log in project root.
set -e
cd "$(dirname "$0")/.."
LOG="daily-post.log"
log(){ echo "$(date '+%F %T') $*" | tee -a "$LOG"; }

log "=== daily post run start ==="

opencode run -m opencode/ling-3.0-flash-fin-free "$(cat lib/daily-prompt.txt)" >> "$LOG" 2>&1

log "run finished"
