# coach-scripts

健身房教練工作流程自動化腳本（範例版）。搭配 Claude Code 使用，減少重複性行政作業。

所有腳本僅含**佔位範例資料**，使用前請依各檔頂端「設定」區填入自己的資料。

---

## 四項功能

### 1. `business_report.py` — 業績回報
解析月營運報表 Sheet，抓出指定教練的新約／續約／總業績，並依星期算固定行政時數，產出每日業績回報文字。

設定（檔案頂端）：
```python
SHEET_ID = "YOUR_GOOGLE_SHEET_ID"   # 月營運報表 Sheet ID
TARGET_TRAINER = "你的姓名"          # 你在表中的教練姓名
```

### 2. `extract_student_summary.py` — 讀取學員課表摘要
批次讀各學員 Google Sheets，切出最近兩堂課表（動作／重量／組數／次數），輸出整理後摘要。

設定：
```python
STUDENTS = [
    ("學員姓名", "Google_Sheet_ID"),
]
```
```bash
python3 extract_student_summary.py
```

### 3. `update_student_memory.py` — 更新學員記憶檔
把近期訓練摘要批次寫入 Claude 記憶系統的學員 `.md` 檔。

設定：
```python
MEM_DIR = "你的 Claude 記憶資料夾路徑"
SUMMARIES = { "student_姓名.md": "摘要文字" }
```
```bash
python3 update_student_memory.py
```

### 4. `class_deduction.py` — 銷課
把上次銷課日到今天、行事曆上實際上過的課，從公司合約名單（.xlsx）的「剩餘堂數」欄逐筆扣除。採「xlsx 當 zip 改單一儲存格」做法，避免 openpyxl 存檔破壞檔內圖表。

設定：
```python
CONTRACT_FILE_ID = "YOUR_CONTRACT_XLSX_FILE_ID"  # 合約名單在 Drive 的 fileId
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
# 1. 安裝 gws 並授權
# 2. 修改各腳本頂端「設定」區（SHEET_ID、STUDENTS、CONTRACT_FILE_ID 等）
# 3. 測試
python3 extract_student_summary.py
```

---

## 搭配 Claude Code

本腳本設計為由 Claude Code 呼叫，建議在 `CLAUDE.md` 設定對應工作流程指令，由 Claude 自動觸發。
