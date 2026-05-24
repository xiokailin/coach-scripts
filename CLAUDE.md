# Claude 使用指南

## 使用者背景

**姓名：** 林誌楷
**IG：** @ot.coach_kai

**三重身份：**
- 職能治療師（OT）— 台大職能治療學系、中華民國執照
- 健康中高齡肌力訓練私人教練 — ACSM-CPT 認證
- 三鐵業餘運動員

**工作經歷：**
- 現職：謙信銀髮健身房 運動指導員
- 教練合作：CoreFit、躍動空間、JoinFot
- 醫療背景：台大醫院、署立台北醫院、愛迪樂治療所

**其他認證：** 樂齡體適能指導員、彼拉提斯認證、紅十字會急救證

**服務族群：**
- 50歲以上中高齡學員（有免費體驗評估）
- 特殊族群：中風、腎衰竭、癌症、脊椎側彎、長短腳等疾病患者

**核心理念：** "cure sometimes, treat often, comfort always." — 相信預防醫學能創造社會價值

## 回應語言

- 主要使用**繁體中文**
- 專業術語保留英文（ACSM、OT、ROM、1RM、MMT、FMS 等）
- 英文文獻：提供繁體中文摘要，保留關鍵英文詞彙

## 主要用途

1. **當前**：簡化繁瑣工作流程（紀錄、報告、課表設計等）
2. **未來**：閱讀並摘要復健醫學、運動科學文獻
3. **未來**：協助 IG 等社群媒體內容撰寫與貼文規劃

## 記憶原則

當使用者說「幫我記憶」或「記住」時：
- **優先寫入 CLAUDE.md**（每次對話自動載入，最可靠）
- 同步更新記憶系統（`.claude/memory/`）

---

## 回應風格

- 簡潔直接，不過度解釋
- 不加 emoji
- 小事直接執行，不需每次確認
- 結果導向，減少冗餘步驟
- **主題切換時自動重命名 tab**：判斷對話進入新的主要任務時，執行 `printf '\033]0;新標題\007'` 更新 tab 標題（英文，簡短）。命名規則：
  - 課表生成 → `Schedule-[姓]`（如 `Schedule-Wang`）
  - 業績回報 → `Report-[MMDD]`（如 `Report-0520`）
  - 影片上傳 → `Upload-[姓]`（如 `Upload-Li`）
  - 腳本撰寫 → `Script-[主題關鍵字]`
  - 後製 → `Edit-[主題關鍵字]`
  - 其他 → 2-3 個英文關鍵字描述任務
- **每次修改 Google Sheets、Drive、Docs 或任何網頁資源後，回應末尾必須附上該資源的完整網址**（若多個則全部列出）
- **產出任何本地文字檔後，立即用 `open` 指令自動開啟檔案**，並在回應末尾附上完整路徑

## 已安裝的 MCP 工具

| 工具 | 用途 |
|------|------|
| **Filesystem** | 讀寫桌面、文件、下載資料夾的檔案（含 PDF） |
| **Playwright** | 操作瀏覽器、讀取需要登入的網頁（如 Instagram） |
| **Firecrawl** | 抓取任何公開網頁內容、學術搜尋結果 |
| **Google Workspace** | 串接 Gmail、行事曆、Drive、Sheets、Docs |
| **Notion** | 存放 ACSM 相關運動課程設計原則，供課表規劃參考 |

**Firecrawl API Key：** 存放於 `~/.claude.json` 的環境變數 `FIRECRAWL_API_KEY`
**Node.js 路徑：** `/opt/homebrew/Cellar/node/26.0.0/bin`（PATH 已寫入各 MCP env）
**gws 路徑：** `/opt/homebrew/bin/gws`
**設定檔位置：** `~/.claude.json` → projects → /Users/linxiaokai/Downloads/forclaude → mcpServers

若 MCP 連線失敗，排查步驟：
1. 確認 Node.js 仍在 `/opt/homebrew/Cellar/node/26.0.0/bin/`
2. 執行 `claude mcp list` 檢查狀態
3. 若版本升級導致路徑變更，更新 `~/.claude.json` 中各 MCP 的 `env.PATH`

---

## 課表自動生成工作流程

**觸發方式：** `生成今日課表`（預設今天；或 `生成課表 5/17` 指定日期）

**執行原則（不需確認，直接完成）：**
1. 讀取今天 Google Calendar → 找出今日有上課的學員；若無課則流程結束
2. 讀取各學員新格式課表（`工作表1` 分頁），找 B 欄最大堂次 → 讀取該堂所有行取得上一堂資料
3. 依 ACSM 漸進超負荷原則生成下一堂課表，遵守各學員禁忌與健康限制
4. 直接 append 新行寫入 Google Sheets，不詢問確認
5. 用 batchUpdate 設定新堂次的 backgroundColor（奇數堂白色 #FFFFFF，偶數堂淡藍 #C9DAF8）
6. 對話顯示簡短摘要（學員姓名 + 主要調整）

**新格式欄位：** A=日期, B=堂次(S1/S2...), C=項次, D=動作, E=備註, F=RPE, G=公斤, H=組數, I=次數, J=秒數, K=公尺

各學員新課表 Sheets ID、舊課表 ID（歸檔）、禁忌與健康注意事項詳見記憶系統（`workflow_schedule_generation.md`）。

---

## 業績回報工作流程

**觸發方式：** `業績回報`（預設今天；或 `業績回報 5/17` 指定日期）

**執行步驟（不需確認，直接完成）：**
1. 讀取 Google Calendar 今天行程 → 計算教練課數（含「一對一」「一對二」關鍵字）
2. 讀取 Google Calendar 本月至今行程 → 計算已上堂數（累計）
3. 用 Playwright 下載當天 Google Sheets 分頁 CSV → 解析林誌楷業績記錄
4. 彙整本月 1 到今日所有業績（新約/續約/總計）
5. 生成報表文字，輸出至 `~/Downloads/forclaude/業績回報_YYYY-MM-DD.txt`

**資料來源：**
- Google Sheets ID：`1wqdXP0YwnnadeirI-s0ScEj6kBJ8gt-E`（練健康西門店2026年5月營運報表.xlsx）
- CSV 下載：`https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}`
- GID 對照表與每月 CSV 快取：詳見記憶系統（`workflow_business_report.md`）

**固定時數（行政/開會/內訓）：**
- 週一：1小時，週四：2小時，週五：2小時

**時數回報原則：**
- 私人教練課程 + 團體課程 + 體驗課 + 行政 總計必須 ≥ 8 小時
- 若課程時數不足 8，行政欄補足差額（取 max(固定時數, 8 − 課程時數)）

**攜帶欄位原則（月底才清空）：**
- 【體驗課回報】、【體驗課未成交追蹤】、【本月學員國衛院參與人數】三個區塊內容**從前一天的報表原文複製**，不自動更改
- 月底最後一天生成後清空，隔月重新開始

**Sheets 下載方式：**
- Playwright 可用時：用 Playwright 下載 CSV
- Playwright 被鎖時：用 `gws drive files get --params '{"fileId":"1wqdXP0YwnnadeirI-s0ScEj6kBJ8gt-E","alt":"media"}' --output "業績表_2026-05.xlsx"` 下載 xlsx，再用 Python + openpyxl 解析，完成後刪除 xlsx

**輸出格式範例：**
```
YYYY/M/D
【時數回報】
私人教練課程：N
團體課程：
體驗課：
行政：N
ㄧ

【體驗課回報】
（前一天內容複製）

【體驗課未成交追蹤】
（前一天內容複製）

【本月總業績】
NNN,NNN 元

【本月新合約】
M/D學員姓名一對一教練課N堂 N,NNN元 單堂N,NNN元（M/D刷卡全額）

【本月續約】
...

【本月學員國衛院參與人數】：
（前一天內容複製）

@吳皓宇Howard @曾子桓 @陳亮宇 感謝🙏

已上堂數：N
```

**每月維護：** 新月份開始時，在 Sheets 找新月份各日分頁的 GID，更新 `business_report.py` 內 `SHEET_GIDS`，同步到記憶系統。

---

## 影片上傳工作流程

**觸發方式：** `上傳 [學員姓名]`（例如：`上傳 黃蕙敏`）

**執行步驟（不需確認，直接完成）：**
1. 在 `~/Downloads` 找出 ctime 在 2 小時內、且未出現在上傳日誌的 `.MOV` / `.MP4` 檔案
2. 從快取（`~/.claude/student_folders.json`）取得學員 Drive 資料夾 ID；若無快取則搜尋 Drive 並存入快取
3. 在學員資料夾下取得或建立當天日期子資料夾（格式：`5/20`）
4. 用 `gws --upload` 逐一上傳影片
5. 上傳成功後：將檔名寫入 `~/.claude/video_upload_log.txt`，刪除本地檔案
6. 回報 Drive 資料夾連結

**腳本位置：** `~/Downloads/forclaude/video_upload.py`

**呼叫方式：**
```bash
python3 ~/Downloads/forclaude/video_upload.py 黃蕙敏
```

**識別「新影片」的邏輯：**
- 用 `stat().st_ctime`（inode change time）判斷：AirDrop 落地時 ctime 會被更新，不受 iPhone 原始拍攝時間影響
- 雙重保護：2 小時內 ctime + 未出現在上傳日誌 = 確定是這次的影片

**Tab 重命名：** `Upload-[姓]`（如 `Upload-Huang`）

**每位學員資料夾 ID：** 存於 `~/.claude/student_folders.json`（首次用到時自動搜尋並快取）

---

## 自媒體工作流程

**拍攝前（寫腳本）：** `/腳本 主題名稱`
詳細規則見 `~/.claude/commands/腳本.md`

**拍攝後（後製）：** `/後製 .srt路徑`
詳細規則見 `~/.claude/commands/後製.md`

兩個指令共用同一套語氣原則（不否定他人）、文獻標準（優先 meta-analysis、2020後）與封面設計規則（主題詞白色小字 + 懸念詞紅色大字）。

---

## 領域知識提示

處理特殊族群相關問題時，請考量：
- 運動禁忌與注意事項（contraindications）
- 藥物對運動反應的影響（如腎衰竭患者電解質、癌症患者疲勞）
- 功能性動作評估（FMS、ROM、MMT）
- 原則：安全第一、漸進超負荷（progressive overload）
