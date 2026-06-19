# coach-scripts

練健康健身房教練工作流程自動化腳本。搭配 Claude Code 使用，減少重複性行政作業。

---

## 包含腳本

### `business_report.py` — 業績回報輔助

解析月營運報表的業績資料，供 Claude 生成每日業績回報文字。

設定項目（開啟檔案修改頂端兩行）：
```python
SHEET_ID = "YOUR_GOOGLE_SHEET_ID"   # 改成你的月報表 Sheet ID
TARGET_TRAINER = "你的姓名"          # 改成你在 Sheet 中的教練名稱
```

### `video_upload.py` — 影片備份至 Google Drive

將 AirDrop 到 Downloads 的學員訓練影片自動轉檔（MOV → MP4）並上傳至學員的 Drive 資料夾。

```bash
python3 video_upload.py 學員姓名           # 只備份 Drive
python3 video_upload.py 學員姓名 --line    # 備份 Drive + 輸出 LINE 發送資訊
python3 video_upload.py 學員姓名 --date 6/9  # 指定日期子資料夾（預設今天）
```

### `extract_student_summary.py` — 讀取學員課表摘要

批次讀取各學員 Google Sheets 最近兩堂課表，輸出整理後的訓練摘要。

設定項目（開啟檔案填入 `STUDENTS` 清單）：
```python
STUDENTS = [
    ("學員姓名", "Google_Sheet_ID"),
    # Sheet ID 從 Sheets 網址取得：
    # https://docs.google.com/spreadsheets/d/【這段】/edit
]
```

```bash
python3 extract_student_summary.py
```

### `update_student_memory.py` — 更新學員記憶檔

將整理好的近期訓練摘要批次寫入 Claude 記憶系統的學員 `.md` 檔案。

設定項目（開啟檔案修改）：
```python
MEM_DIR = "你的 Claude 記憶資料夾路徑"
SUMMARIES = {
    "student_姓名拼音.md": "訓練摘要內容",
}
```

```bash
python3 update_student_memory.py
```

---

## 前置需求

| 工具 | 用途 | 安裝方式 |
|------|------|----------|
| Python 3.10+ | 執行腳本 | `brew install python` |
| gws | 串接 Google Workspace（Sheets / Drive） | 見下方說明 |
| ffmpeg | 影片轉檔與縮圖擷取 | `brew install ffmpeg` |

### 安裝 gws

```bash
brew install nicholasgasior/brew/gws
gws auth login
```

授權時選擇包含 Sheets 與 Drive 的完整 scope。完成後確認路徑：

```bash
which gws   # 應為 /opt/homebrew/bin/gws
```

若路徑不同，修改各腳本頂端的 `GWS` 變數。

---

## 快速開始

```bash
# 1. Clone repo
git clone https://github.com/xiokailin/coach-scripts.git
cd coach-scripts

# 2. 安裝 gws 並授權（見上方說明）

# 3. 修改各腳本的設定項目（SHEET_ID、STUDENTS 等）

# 4. 測試
python3 extract_student_summary.py
```

---

## 搭配 Claude Code

本腳本設計為由 Claude Code 呼叫，建議在 `CLAUDE.md` 中設定對應的工作流程指令，由 Claude 自動觸發執行。
