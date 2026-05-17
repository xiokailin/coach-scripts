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

## 回應風格

- 簡潔直接，不過度解釋
- 不加 emoji
- 小事直接執行，不需每次確認
- 結果導向，減少冗餘步驟

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

**觸發方式：** `生成明天課表`

**執行原則（不需確認，直接完成）：**
1. 讀取明天 Google Calendar → 找出所有課程行程；若無課則流程結束
2. 讀取各有課學員 Sheets「橫式課表」分頁，找最近一堂課資料
3. 依 ACSM 漸進超負荷原則生成新課表，遵守各學員禁忌與健康限制
4. 直接寫入 Google Sheets，不詢問確認
5. 對話顯示簡短摘要

各學員 Sheets ID、禁忌與健康注意事項詳見記憶系統（`workflow_schedule_generation.md`）。

---

## 學員影片上傳工作流程

**觸發方式：** `上傳 學員姓名 日期`（日期省略時預設今天）

**範例：**
- `上傳 王小明 5/17`
- `上傳 李大華`（預設今天）
- `上傳 王小明、李大華 5/17`（批次）

**執行步驟：**
1. 在 `~/Downloads` 找出符合指定日期的影片與照片（.mp4 / .mov / .MOV / .MP4 / .jpg / .JPG / .heic / .HEIC）
2. 在 Google Drive 搜尋該學員資料夾（跨所有班別：週一~週六、一週兩次、不定期約等）
3. 在學員資料夾下建立日期子資料夾（格式：`M/D`，如 `5/17`）
4. 將影片與照片複製到 `~/Downloads/forclaude/` → 上傳至 Drive → 刪除 forclaude 暫存檔
5. 刪除 `~/Downloads` 的原始影片與照片（**不需詢問，直接刪除**）
6. 完成後直接附上該日期資料夾的 Google Drive 網址（純文字，格式：`https://drive.google.com/drive/folders/{folder_id}`）

**Drive 根資料夾 ID：** `17LXhIiKLvhw-cTio9ASOY1hNe0PZmTt8`

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

【體驗課未成交追蹤】

【本月總業績】
NNN,NNN 元

【本月新合約】
M/D學員姓名一對一教練課N堂 N,NNN元 單堂N,NNN元（M/D刷卡全額）

【本月續約】
...

已上堂數：N
```

**每月維護：** 新月份開始時，在 Sheets 找新月份各日分頁的 GID，更新 `business_report.py` 內 `SHEET_GIDS`，同步到記憶系統。

---

## 領域知識提示

處理特殊族群相關問題時，請考量：
- 運動禁忌與注意事項（contraindications）
- 藥物對運動反應的影響（如腎衰竭患者電解質、癌症患者疲勞）
- 功能性動作評估（FMS、ROM、MMT）
- 原則：安全第一、漸進超負荷（progressive overload）
