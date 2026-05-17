#!/usr/bin/env python3
"""
業績回報自動化腳本
用法: python3 business_report.py [M/D]
若不指定日期則以今天為準
"""

import sys, os, re, csv, io, json
from datetime import date, datetime

# ──────────────────────────────────────────
# 設定
# ──────────────────────────────────────────

SHEET_ID = "1wqdXP0YwnnadeirI-s0ScEj6kBJ8gt-E"
TARGET_TRAINER = "林誌楷"
CSV_DIR = os.path.expanduser("~/.claude_sheets_cache")

# 月份 → GID 對照表（每月更新）
# 格式: { "YYYY-MM": { day: gid } }
SHEET_GIDS = {
    "2026-05": {
        1: "1984060835",
        2: "779959662",
        3: "1662021019",
        4: "17518307",
        5: "659564820",
        6: "401552876",
        7: "909009745",
        8: "618307406",
        9: "2038489536",
        10: "752426272",
        11: "1003400530",
        12: "399754302",
        13: "1107157881",
        14: "1339312539",
        15: "935923252",
        16: "726045306",
        17: "989601606",
        18: "261793430",
        19: "INSERT_DAY19_GID",
        20: "INSERT_DAY20_GID",
        21: "INSERT_DAY21_GID",
        22: "INSERT_DAY22_GID",
        23: "INSERT_DAY23_GID",
        24: "INSERT_DAY24_GID",
        25: "INSERT_DAY25_GID",
        26: "INSERT_DAY26_GID",
        27: "INSERT_DAY27_GID",
        28: "INSERT_DAY28_GID",
        29: "INSERT_DAY29_GID",
        30: "INSERT_DAY30_GID",
        31: "INSERT_DAY31_GID",
    }
}

# ──────────────────────────────────────────
# 固定時數規則（行政/開會/內訓）
# ──────────────────────────────────────────

FIXED_HOURS = {
    0: 1,  # 週一: 1小時
    3: 2,  # 週四: 2小時
    4: 2,  # 週五: 2小時
}


def parse_csv_for_trainer(csv_content, trainer=TARGET_TRAINER):
    """從 CSV 內容找出指定教練的業績記錄"""
    records = []
    for line in csv_content.split('\n'):
        if trainer not in line:
            continue
        reader = csv.reader(io.StringIO(line))
        row = next(reader, None)
        if not row or len(row) < 5:
            continue

        desc = row[2].strip() if len(row) > 2 else ''
        amount_raw = row[4].strip().replace(',', '').replace('"', '').replace('$', '') if len(row) > 4 else '0'
        payment = row[7].strip() if len(row) > 7 else ''
        note = row[1].strip() if len(row) > 1 else ''

        # 排除訂金記錄
        if '訂金' in desc or '訂金' in note:
            continue

        try:
            amount = int(float(amount_raw or 0))
        except:
            amount = 0

        if amount <= 0:
            continue

        # 解析學員名稱
        student_match = re.search(rf'{trainer}學員(.+?)(?:一對[一二]|團課|教練課)', desc)
        student = student_match.group(1).strip() if student_match else ''

        # 課程類型
        course_type = '一對二' if '一對二' in desc else ('團課' if '團課' in desc else '一對一')

        # 堂數
        sessions_match = re.search(r'(\d+)堂', desc)
        sessions = int(sessions_match.group(1)) if sessions_match else 0

        # 新約/續約
        if '續約' in desc:
            contract_type = '續約'
        elif '體驗' in desc:
            return records  # 體驗課不計入
        else:
            contract_type = '新約'

        # 單堂金額
        unit_price = amount // sessions if sessions > 0 else 0

        # 付款方式轉換
        pay_map = {'刷卡': '刷卡全額', '現金': '現金全額', '匯款': '匯款全額'}
        pay_str = pay_map.get(payment, payment + '全額')

        records.append({
            'student': student,
            'course_type': course_type,
            'sessions': sessions,
            'amount': amount,
            'payment': payment,
            'pay_str': pay_str,
            'unit_price': unit_price,
            'contract_type': contract_type,
            'desc': desc,
        })

    return records


def format_contract_line(day, month, rec):
    """格式化合約記錄為報表格式"""
    d = f"{month}/{day}"
    student = rec['student']
    ctype = rec['course_type']
    sessions = rec['sessions']
    amount = rec['amount']
    unit = rec['unit_price']
    pay = rec['pay_str']

    return f"{d}{student}{ctype}教練課{sessions}堂 {amount:,}元 單堂{unit:,}元（{d}{pay}）"


def count_coaching_sessions(events):
    """從行事曆事件計算一對一教練課數量"""
    count = 0
    for e in events:
        summary = e.get('summary', '')
        status = e.get('status', 'confirmed')
        if status == 'cancelled':
            continue
        if '一對一' in summary or '一對二' in summary:
            count += 1
    return count


def count_trial_sessions(events):
    """計算體驗課數量"""
    count = 0
    for e in events:
        summary = e.get('summary', '')
        if '體驗' in summary and e.get('status') != 'cancelled':
            count += 1
    return count


def count_group_sessions(events):
    """計算團課數量"""
    count = 0
    for e in events:
        summary = e.get('summary', '')
        if '團課' in summary and e.get('status') != 'cancelled':
            count += 1
    return count


def generate_report(target_date, calendar_events_today, calendar_events_month, all_day_records):
    """生成完整業績回報文字"""
    month = target_date.month
    day = target_date.day
    weekday = target_date.weekday()

    # 時數計算
    private_sessions = count_coaching_sessions(calendar_events_today)
    trial_sessions = count_trial_sessions(calendar_events_today)
    group_sessions = count_group_sessions(calendar_events_today)
    admin_hours = FIXED_HOURS.get(weekday, 0)

    # 已上堂數（本月所有一對一/一對二）
    monthly_session_count = count_coaching_sessions(calendar_events_month)

    # 業績分類
    new_contracts = []
    renewals = []
    for d in range(1, day + 1):
        recs = all_day_records.get(d, [])
        for rec in recs:
            if rec['contract_type'] == '新約':
                new_contracts.append((d, rec))
            elif rec['contract_type'] == '續約':
                renewals.append((d, rec))

    total = sum(r['amount'] for _, r in new_contracts) + sum(r['amount'] for _, r in renewals)

    # 格式化
    lines = []
    lines.append(f"{target_date.year}/{month}/{day}")
    lines.append("【時數回報】")
    lines.append(f"私人教練課程：{private_sessions if private_sessions else ''}")
    lines.append(f"團體課程：{group_sessions if group_sessions else ''}")
    lines.append(f"體驗課：{trial_sessions if trial_sessions else ''}")
    lines.append(f"行政：{admin_hours if admin_hours else ''}")
    lines.append("ㄧ")
    lines.append("")
    lines.append("【體驗課回報】")
    lines.append("")
    lines.append("")
    lines.append("【體驗課未成交追蹤】")
    lines.append("")
    lines.append("")
    lines.append(f"【本月總業績】")
    lines.append(f"{total:,} 元")
    lines.append("")
    lines.append("【本月新合約】")
    for d, rec in new_contracts:
        lines.append(format_contract_line(d, month, rec))

    lines.append("")
    lines.append("【本月續約】")
    for d, rec in renewals:
        lines.append(format_contract_line(d, month, rec))

    lines.append("")
    lines.append(f"已上堂數：{monthly_session_count}")

    return '\n'.join(lines)


if __name__ == '__main__':
    print("業績回報腳本已載入")
    print("此腳本供 Claude 呼叫，請輸入「業績回報」指令觸發")
