#!/usr/bin/env python3
"""為每位學員記憶檔新增/更新「近期訓練摘要」區塊。

用法：
  python3 update_student_memory.py

執行後自動掃描 SUMMARIES 裡的每個學員，
將近期訓練摘要寫入對應的 student_*.md 記憶檔。
"""

import os, re
from pathlib import Path

# 記憶檔資料夾路徑（改成你自己的 Claude 記憶路徑）
MEM_DIR = str(Path.home() / ".claude" / "projects" / "你的專案路徑" / "memory")

# 各學員摘要內容
# 格式：{ "student_姓名拼音.md": "摘要文字" }
#
# 摘要建議包含以下區塊：
#   ## 近期訓練摘要（更新：YYYY-MM-DD）
#   **最近兩堂（S?=M/D、S?=M/D）：**
#   - 動作：重量 組×次（進退說明）
#   **當前工作重量基準：**
#   - 動作：重量
#   **動作執行注意點：**
#   - 注意事項
#   **下次課方向：**
#   - 計劃
#
SUMMARIES = {
    # 範例（請替換成你的學員資料）：
    # "student_wang_xiaoming.md": """
    # ## 近期訓練摘要（更新：2026-06-01）
    #
    # **最近兩堂（S1=5/25、S2=6/1）：**
    # - 壺鈴硬舉：8kg 3×10
    #
    # **當前工作重量基準：**
    # - 壺鈴硬舉：8kg
    #
    # **動作執行注意點：**
    # - 注意事項
    #
    # **下次課方向：**
    # - 壺鈴硬舉鞏固 8kg 或嘗試 10kg
    # """,
}


def update_file(filename, new_section):
    filepath = os.path.join(MEM_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [跳過] 找不到 {filename}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 移除舊的近期訓練摘要區塊（若存在）
    pattern = r"\n## 近期訓練摘要.*$"
    content = re.sub(pattern, "", content, flags=re.DOTALL)
    content = content.rstrip()

    # 附加新區塊
    content += "\n" + new_section.strip() + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [完成] {filename}")


def main():
    if not SUMMARIES:
        print("SUMMARIES 是空的，請先填入學員訓練摘要。")
        return
    for filename, section in SUMMARIES.items():
        update_file(filename, section)
    print(f"\n全部完成，共更新 {len(SUMMARIES)} 個學員記憶檔。")


if __name__ == "__main__":
    main()
