#!/usr/bin/env python3
"""讀取各學員最新 2 堂課表資料，輸出摘要供記憶更新。"""

import subprocess, json, sys

GWS = "/opt/homebrew/bin/gws"

STUDENTS = [
    # 格式：("學員姓名", "Google_Sheet_ID")
    # Sheet ID 從 Google Sheets 網址取得：
    # https://docs.google.com/spreadsheets/d/【這段就是 Sheet ID】/edit
    #
    # 範例（請替換成你的資料）：
    # ("王小明", "1abc123def456ghi789"),
    # ("李美華", "1xyz987uvw654rst321"),
]


def read_sheet(sheet_id):
    result = subprocess.run(
        [GWS, "sheets", "spreadsheets", "values", "get",
         "--params", json.dumps({"spreadsheetId": sheet_id, "range": "工作表1!A:I"})],
        capture_output=True, text=True
    )
    raw = result.stdout
    # 找 JSON 開始位置
    idx = raw.find('{')
    if idx == -1:
        return []
    data = json.loads(raw[idx:])
    return data.get("values", [])


def parse_sessions(rows):
    """把 rows 切成 {session_label, date, exercises} 清單。"""
    sessions = []
    current = None
    for row in rows:
        if not row:
            continue
        a = row[0].strip() if len(row) > 0 else ""
        # 日期列：A 欄有 2026/ 或 A 欄有數字（堂次編號）且同列其他欄空
        is_date_row = a.startswith("2026/") or a.startswith("202")
        # 堂次 label：S\d+ 或純數字（堂次）
        is_session_label = (a.startswith("S") and a[1:].isdigit()) or \
                           (a.isdigit() and int(a) > 0 and int(a) < 100)

        if is_date_row:
            current = {"date": a, "label": "", "exercises": []}
            sessions.append(current)
        elif is_session_label and current is None:
            current = {"date": "", "label": a, "exercises": []}
            sessions.append(current)
        elif is_session_label and current is not None:
            # 有時堂次與日期分開列
            if not current["label"]:
                current["label"] = a
        else:
            if current is not None:
                b = row[1].strip() if len(row) > 1 else ""
                c = row[2].strip() if len(row) > 2 else ""
                d = row[3].strip() if len(row) > 3 else ""
                f = row[5].strip() if len(row) > 5 else ""
                g = row[6].strip() if len(row) > 6 else ""
                h = row[7].strip() if len(row) > 7 else ""
                i = row[8].strip() if len(row) > 8 else ""
                # 忽略空行、純暖身、風扇車之外的無意義行
                if c and c not in ("自己暖身", ""):
                    ex = {"idx": b, "name": c, "note": d,
                          "kg": f, "sets": g, "reps": h, "sec": i}
                    current["exercises"].append(ex)
    return sessions


def format_session(s):
    lines = []
    label = f"{s['label']} {s['date']}".strip()
    lines.append(f"【{label}】")
    for ex in s["exercises"]:
        parts = [f"{ex['idx']}. {ex['name']}" if ex['idx'] else f"  {ex['name']}"]
        if ex['kg']:
            parts.append(f"{ex['kg']}kg" if not any(c.isalpha() for c in ex['kg']) else ex['kg'])
        if ex['sets'] and ex['reps']:
            parts.append(f"{ex['sets']}×{ex['reps']}")
        elif ex['sets'] and ex['sec']:
            parts.append(f"{ex['sets']}×{ex['sec']}\"")
        elif ex['reps']:
            parts.append(f"×{ex['reps']}")
        if ex['note']:
            parts.append(f"({ex['note']})")
        lines.append("  " + " ".join(parts))
    return "\n".join(lines)


def main():
    for name, sid in STUDENTS:
        print(f"\n{'='*60}")
        print(f"【{name}】")
        try:
            rows = read_sheet(sid)
            sessions = parse_sessions(rows)
            if not sessions:
                print("  （無資料）")
                continue
            last2 = sessions[-2:] if len(sessions) >= 2 else sessions
            for s in last2:
                print(format_session(s))
        except Exception as e:
            print(f"  讀取失敗：{e}")


if __name__ == "__main__":
    main()
