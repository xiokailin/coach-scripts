#!/usr/bin/env python3
"""LINE Webhook server — 只記錄 userId，不發送任何訊息"""
import json, http.server, urllib.request, os

LOG_PATH = os.path.expanduser("~/.claude/line_user_ids.json")
LINE_TOKEN = ""  # 由啟動腳本填入

def get_display_name(user_id):
    try:
        req = urllib.request.Request(
            f"https://api.line.me/v2/bot/profile/{user_id}",
            headers={"Authorization": f"Bearer {LINE_TOKEN}"}
        )
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()).get("displayName", user_id)
    except:
        return user_id

def load_log():
    try:
        with open(LOG_PATH) as f:
            return json.load(f)
    except:
        return {}

def save_log(data):
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.send_response(200)
        self.end_headers()
        try:
            events = json.loads(body).get("events", [])
            log = load_log()
            for ev in events:
                uid = ev.get("source", {}).get("userId")
                if not uid:
                    continue
                name = get_display_name(uid)
                log[name] = uid
                save_log(log)
                print(f"[captured] {name} → {uid}")
        except Exception as e:
            print(f"[error] {e}")

    def log_message(self, *_): pass  # 靜音 access log

if __name__ == "__main__":
    import sys
    LINE_TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
    port = 8765
    print(f"Webhook server listening on port {port}")
    http.server.HTTPServer(("", port), Handler).serve_forever()
