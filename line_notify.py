#!/usr/bin/env python3
"""LINE push notification helper.

Usage:
  python3 line_notify.py "訊息"                      # 用 test OA 推給自己（測試用）
  python3 line_notify.py --profile student "訊息"    # 用學員 OA 推給自己
  python3 line_notify.py --to Uxxxxxxxxx "訊息"      # 推給指定 User ID（學員 OA）
  python3 line_notify.py --name test "訊息"          # 用學員名字查 User ID 發送
"""
import sys
import json
import subprocess
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude" / "line_config.json"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def resolve_user_id(name: str) -> str:
    cfg = load_config()
    uid = cfg.get("students", {}).get(name)
    if not uid:
        print(f"Error: 找不到學員「{name}」的 User ID", file=sys.stderr)
    return uid or ""


def send(message: str, profile: str = "test", to: str = None) -> bool:
    cfg = load_config()[profile]
    token = cfg["channel_access_token"]
    user_id = to or cfg.get("user_id", "")
    if not user_id:
        print(f"Error: no user_id for profile '{profile}'", file=sys.stderr)
        return False
    payload = json.dumps({"to": user_id, "messages": [{"type": "text", "text": message}]})
    result = subprocess.run(
        [
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "-X", "POST", "https://api.line.me/v2/bot/message/push",
            "-H", f"Authorization: Bearer {token}",
            "-H", "Content-Type: application/json",
            "-d", payload,
        ],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == "200"


if __name__ == "__main__":
    args = sys.argv[1:]
    profile = "student"
    to = None

    if "--confirmed" not in args:
        print("Error: 缺少 --confirmed 旗標。必須先在對話顯示 LINE 預覽並等待使用者說「確認」，才可呼叫此腳本。", file=sys.stderr)
        sys.exit(2)
    args.remove("--confirmed")

    if "--profile" in args:
        i = args.index("--profile")
        profile = args[i + 1]
        args = args[:i] + args[i + 2:]

    if "--name" in args:
        i = args.index("--name")
        name = args[i + 1]
        to = resolve_user_id(name)
        profile = "student"
        args = args[:i] + args[i + 2:]
        if not to:
            sys.exit(1)

    if "--to" in args:
        i = args.index("--to")
        to = args[i + 1]
        args = args[:i] + args[i + 2:]

    if "--message" in args:
        i = args.index("--message")
        msg = args[i + 1]
        args = args[:i] + args[i + 2:]
    else:
        msg = " ".join(args) if args else "通知"
    ok = send(msg, profile=profile, to=to)
    print("sent" if ok else "failed")
