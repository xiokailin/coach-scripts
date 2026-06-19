#!/bin/bash
# 自動維持 localhost.run tunnel 並更新 LINE webhook URL
# 斷線後自動重連

STUDENT_TOKEN=$(python3 -c "import json; c=json.load(open('$HOME/.claude/line_config.json')); print(c['student']['channel_access_token'])")
WEBHOOK_PORT=8765

while true; do
    echo "[$(date '+%H:%M:%S')] 啟動 tunnel..."

    # Start tunnel and capture URL
    URL=""
    while IFS= read -r line; do
        if echo "$line" | grep -q "lhr.life"; then
            URL=$(echo "$line" | grep -o '[a-z0-9]*\.lhr\.life' | head -1)
            FULL_URL="https://$URL"
            echo "[$(date '+%H:%M:%S')] URL: $FULL_URL"

            # Update LINE webhook
            RESULT=$(curl -s -X PUT "https://api.line.me/v2/bot/channel/webhook/endpoint" \
                -H "Authorization: Bearer $STUDENT_TOKEN" \
                -H "Content-Type: application/json" \
                -d "{\"endpoint\": \"$FULL_URL\"}")
            echo "[$(date '+%H:%M:%S')] LINE webhook 已更新: $RESULT"
        fi
    done < <(ssh -o StrictHostKeyChecking=no \
                 -o ServerAliveInterval=20 \
                 -o ServerAliveCountMax=3 \
                 -o ExitOnForwardFailure=yes \
                 -R 80:localhost:$WEBHOOK_PORT localhost.run 2>&1)

    echo "[$(date '+%H:%M:%S')] Tunnel 斷線，3 秒後重連..."
    sleep 3
done
