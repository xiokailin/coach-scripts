#!/usr/bin/env python3
"""
業績回報自動化腳本
用法: python3 business_report.py [M/D]
若不指定日期則以今天為準
"""

import sys, os, re, json
from datetime import date, datetime

# ──────────────────────────────────────────
# 設定
# ──────────────────────────────────────────

SHEET_ID = "1wqdXP0YwnnadeirI-s0ScEj6kBJ8gt-E"
TARGET_TRAINER = "林誌楷"

# ──────────────────────────────────────────
# 固定時數規則（行政/開會/內訓）
# ──────────────────────────────────────────

FIXED_HOURS = {
    0: 1,  # 週一: 1小時
    3: 2,  # 週四: 2小時
    4: 2,  # 週五: 2小時
}


def _cell(row, i, default=''):
    return str(row[i]).strip() if len(row) > i and row[i] is not None else default


def parse_rows_for_trainer(rows, trainer=TARGET_TRAINER):
    """從 Sheets API 回傳的 rows（list of list）找出指定教練的業績記錄"""
    records = []
    for row in rows:
        if not any(trainer in str(cell) for cell in row):
            continue
        if len(row) < 5:
            continue

        desc = _cell(row, 2)
        amount_raw = re.sub(r'[,"$]', '', _cell(row, 4, '0'))
        payment = _cell(row, 7)
        note = _cell(row, 1)

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
        if '體驗' in desc:
            continue  # 體驗課不計入
        elif '續約' in desc:
            contract_type = '續約'
        else:
            contract_type = '新約'

        # 單堂金額
        unit_price = amount // sessions if sessions > 0 else 0

        records.append({
            'student': student,
            'course_type': course_type,
            'sessions': sessions,
            'amount': amount,
            'payment': payment,
            'unit_price': unit_price,
            'contract_type': contract_type,
            'desc': desc,
        })

    return records


def format_contract_line(day, month, rec):
    """格式化合約記錄為報表格式"""
    d = f"{month}/{day}"
    # 一律以「...全額」呈現，無論來源儲存格是否已帶後綴
    pay = rec['payment'].removesuffix('全額') + '全額'
    return (f"{d}{rec['student']}{rec['course_type']}教練課{rec['sessions']}堂 "
            f"{rec['amount']:,}元 單堂{rec['unit_price']:,}元（{d}{pay}）")


PRIVATE_KW = ('一對一', '一對二')


def _count_events(events, *keywords):
    return sum(1 for e in events
               if any(kw in e.get('summary', '') for kw in keywords)
               and e.get('status') != 'cancelled')


def generate_report(target_date, calendar_events_today, calendar_events_month, all_day_records):
    """生成完整業績回報文字"""
    month = target_date.month
    day = target_date.day
    weekday = target_date.weekday()

    # 時數計算
    private_sessions = _count_events(calendar_events_today, *PRIVATE_KW)
    trial_sessions = _count_events(calendar_events_today, '體驗')
    group_sessions = _count_events(calendar_events_today, '團課')
    admin_hours = FIXED_HOURS.get(weekday, 0)

    # 已上堂數（本月所有一對一/一對二）
    monthly_session_count = _count_events(calendar_events_month, *PRIVATE_KW)

    # 業績分類
    new_contracts = []
    renewals = []
    total = 0
    for d in range(1, day + 1):
        for rec in all_day_records.get(d, []):
            total += rec['amount']
            if rec['contract_type'] == '新約':
                new_contracts.append((d, rec))
            elif rec['contract_type'] == '續約':
                renewals.append((d, rec))

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
    lines.append("【本月總業績】")
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
