# coach-scripts

健身教練工作流程自動化腳本，搭配 [Claude Code](https://claude.ai/code) 使用。

---

## 前置需求

| 工具 | 說明 | 安裝方式 |
|------|------|----------|
| Python 3.10+ | 執行腳本 | `brew install python` |
| [gws](https://github.com/nicholasgasior/gws) | Google Workspace CLI | 見下方說明 |
| ffmpeg | 影片轉 MP4 / 擷取縮圖 | `brew install ffmpeg` |
| ssh | localhost.run tunnel | macOS 內建 |

---

## 設定步驟

### 1. gws（Google Workspace CLI）

```bash
brew install nicholasgasior/brew/gws
gws auth login   # 依提示完成 OAuth
```

預設路徑：`/opt/homebrew/bin/gws`。若路徑不同，修改各腳本頂端的 `GWS` 變數。

### 2. LINE config

複製範本並填入自己的 token：

```bash
cp line_config_template.json ~/.claude/line_config.json
```

編輯 `~/.claude/line_config.json`：

```json
{
  "student": {
    "channel_access_token": "你的 LINE OA Channel Access Token",
    "user_id": "你自己的 LINE User ID（U 開頭）"
  },
  "test": {
    "channel_access_token": "測試用 OA token（可與 student 相同）",
    "user_id": "你自己的 LINE User ID"
  },
  "students": {
    "學員姓名": "學員的 LINE User ID"
  }
}
```

取得 LINE User ID 的方式：啟動 webhook server + tunnel（見下方），讓學員傳訊息給 OA，ID 自動記錄至 `~/.claude/line_user_ids.json`。

---

## 腳本說明

### `video_upload.py` — 影片備份至 Google Drive

將 AirDrop 到 Downloads 的影片自動轉成 MP4 並上傳到學員資料夾。

```bash
# 只備份 Drive
python3 video_upload.py 學員姓名

# 備份 Drive + 輸出 LINE 發送資訊（JSON）
python3 video_upload.py 學員姓名 --line

# 指定 Drive 日期子資料夾（預設今天）
python3 video_upload.py 學員姓名 --date 6/9
```

首次使用某位學員，腳本會自動搜尋並快取其 Drive 資料夾 ID（`~/.claude/student_folders.json`）。
若找不到，用 `--folder-id DRIVE_FOLDER_ID` 手動指定。

### `line_notify.py` — LINE 推播

**⚠️ 必須帶 `--confirmed` 旗標才能發送**（防止意外推播）。

```bash
# 推給自己（測試）
python3 line_notify.py --profile student "訊息內容" --confirmed

# 推給指定 User ID
python3 line_notify.py --to Uxxxxxxxxx "訊息內容" --confirmed

# 用學員姓名查 User ID 推送
python3 line_notify.py --name 學員姓名 "訊息內容" --confirmed
```

### `line_webhook_server.py` — 捕捉學員 LINE User ID

```bash
python3 line_webhook_server.py YOUR_CHANNEL_ACCESS_TOKEN
```

啟動後監聽 port 8765。學員傳訊息給 OA 後，userId 自動寫入 `~/.claude/line_user_ids.json`。

### `tunnel_keeper.sh` — 自動維持 localhost.run tunnel

```bash
bash tunnel_keeper.sh
```

自動維持 SSH tunnel 並更新 LINE OA 的 webhook URL。斷線後自動重連。
需先在 `~/.claude/line_config.json` 填好 `student.channel_access_token`。

### `business_report.py` — 業績回報輔助

由 Claude Code 呼叫，不需手動執行。
設定頂端的 `SHEET_ID`（你的 Google Sheets ID）和 `TARGET_TRAINER`（你的姓名）。

---

## Claude Code 工作流程

`commands/` 資料夾包含 Claude Code 技能文件，可複製到自己的 `.claude/commands/` 使用：

- `腳本.md` — 拍攝前自動生成口說腳本
- `後製.md` — 簡體轉繁體 .srt + 文獻配對 + IG 說明文字

---

## 檔案結構

```
coach-scripts/
├── business_report.py        # 業績回報腳本
├── video_upload.py           # 影片上傳腳本
├── line_notify.py            # LINE 推播腳本
├── line_webhook_server.py    # LINE webhook 伺服器
├── tunnel_keeper.sh          # Tunnel 維護腳本
├── line_config_template.json # LINE config 範本
└── commands/
    ├── 腳本.md               # Claude Code：自媒體腳本技能
    └── 後製.md               # Claude Code：影片後製技能
```
