# coach-scripts

**用 Claude Code 幫健身教練自動化行政作業。**

把每天花在打業績、算薪資、數課量、消課堂的時間，交給 AI 處理。

---

## 這個 repo 有什麼？

兩類工具，搭配使用：

| 類型 | 放哪 | 用途 |
|------|------|------|
| Claude 指令（`commands/`）| 複製到 `~/.claude/commands/` | 在 Claude Code 對話視窗輸入 `/指令名` 自動執行 |
| Python 腳本（根目錄）| 本機執行 | 批次讀 Google Sheets、更新學員資料、銷課 |

---

## Claude 指令（3 個）

把 `commands/` 資料夾內的 `.md` 全部複製到 `~/.claude/commands/`，即可在 Claude Code 使用。

每個指令**開頭有「使用前設定」區**，填入你自己的資料（教練姓名、Sheet ID、費率）後即可使用，其餘內容不需修改。

### `/本月課量預估`
查 Google Calendar 計算本月剩餘教練課堂數，附請假率試算與薪資估算。

### `薪資試算`
輸入本月課數與業績，依你填入的抽潤率表計算稅前／實領薪資。

### `/續約業績`
月底執行，從學員合約記憶檔撈出下個月預計完課的人，整理成預計續約業績草稿後寫入 Google Sheet。

---

## Python 腳本（4 個）

每個腳本**頂端有「設定」區**，填入你的 Google Sheets ID、教練姓名後即可執行。

### `business_report.py` — 業績回報
解析月營運報表 Sheet，抓出指定教練的新約／續約／總業績，依星期算行政時數，產出每日業績回報文字。

```python
# 設定
SHEET_ID       = "YOUR_GOOGLE_SHEET_ID"
TARGET_TRAINER = "你的姓名"
```

### `extract_student_summary.py` — 讀取學員課表摘要
批次讀各學員 Google Sheets，切出最近兩堂課表，輸出整理後摘要。

```python
# 設定
STUDENTS = [
    ("學員姓名", "Google_Sheet_ID"),
]
```

### `update_student_memory.py` — 更新學員記憶檔
把近期訓練摘要批次寫入 Claude 記憶系統的學員 `.md` 檔。

```python
# 設定
MEM_DIR   = "你的 Claude 記憶資料夾路徑"
SUMMARIES = { "student_姓名.md": "摘要文字" }
```

### `class_deduction.py` — 銷課
把上次銷課日到今天的教練課，從公司合約名單（.xlsx）的「剩餘堂數」欄逐筆扣除。採「只改目標格」做法，不破壞檔內圖表。

```python
# 設定
CONTRACT_FILE_ID = "YOUR_CONTRACT_XLSX_FILE_ID"
TARGET_TRAINER   = "你的姓名"
SHARED_CONTRACT  = { "行事曆名字": "合約登記名字" }  # 共用合約配對
```

```bash
python3 class_deduction.py --dry-run         # 先試算不寫入（建議）
python3 class_deduction.py                   # 銷上次到今天
python3 class_deduction.py --since 2026/6/1  # 指定起算日
```

---

## 前置需求

| 工具 | 用途 | 安裝 |
|------|------|------|
| Python 3.10+ | 執行腳本 | `brew install python` |
| Claude Code | 執行 Claude 指令 | [claude.ai/code](https://claude.ai/code) |
| gws | 串接 Google Workspace（Sheets / Drive / Calendar） | `brew install nicholasgasior/brew/gws` |
| openpyxl | 銷課讀回驗證 | `pip install openpyxl` |

安裝 gws 後授權（選含 Sheets / Drive / Calendar 的完整 scope）：
```bash
gws auth login
which gws   # 預設應為 /opt/homebrew/bin/gws；路徑不同時改各腳本頂端 GWS 變數
```

---

## 快速開始

```bash
git clone https://github.com/xiokailin/coach-scripts.git
cd coach-scripts

# Claude 指令
cp commands/*.md ~/.claude/commands/
# 打開各 .md，填入「使用前設定」區的資料

# Python 腳本
# 打開各 .py，填入頂端「設定」區的資料
pip install openpyxl
python3 class_deduction.py --dry-run   # 測試
```
