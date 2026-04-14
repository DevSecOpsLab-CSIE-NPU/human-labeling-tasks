# 部署指南

## 完整架構

```
標注者瀏覽器
    │
    │  (GitHub Pages 靜態頁面)
    ├─► index.html + data.js
    │       │ localStorage 本地進度儲存
    │       │ fetch() POST (非阻塞)
    │       ▼
    │  Google Apps Script Web App
    │       │ doPost() 寫入
    │       ▼
    └─► Google Spreadsheet
            ├── annotator_A 分頁
            ├── annotator_B 分頁
            └── annotator_C 分頁
```

---

## Step 1：設定 Google Spreadsheet

1. 開啟 [Google Sheets](https://sheets.google.com)，新增一個 spreadsheet
2. 記下 URL 中的 Spreadsheet ID（`/d/` 和 `/edit` 之間的字串）
   ```
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          這是 Spreadsheet ID
   ```
3. 建立三個分頁（工作表）：`annotator_A`、`annotator_B`、`annotator_C`

---

## Step 2：部署 Google Apps Script

1. 在 Spreadsheet 選單：**Extensions → Apps Script**
2. 刪除預設的 `myFunction()`，貼上 `google_apps_script/Code.gs` 的內容
3. 將第 14 行的 `YOUR_SPREADSHEET_ID_HERE` 換成你的 Spreadsheet ID
4. 點 **Deploy → New deployment**
   - Type: **Web App**
   - Execute as: **Me**
   - Who has access: **Anyone**
5. 點 **Deploy**，複製產生的 Web App URL（格式：`https://script.google.com/macros/s/XXX/exec`）

---

## Step 3：設定前端

開啟 `web/index.html`，找到第 3 行：

```javascript
const APPS_SCRIPT_URL = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec";
```

將 `YOUR_SCRIPT_ID` 換成 Step 2 複製的完整 URL。

---

## Step 4：部署到 GitHub Pages

```bash
# 確認在專案根目錄
cd /home/fychao/ill-posed-AffectTrace

# 只需要 web/ 目錄下的檔案
# 方法 A：直接推 main branch（如果 Pages 設定為 /docs 或根目錄）
cp -r 00_Paper/TAC/human_labeling_tasks/web/* docs/labeling/

# 方法 B：建立 gh-pages branch
git checkout -b gh-pages
# 複製 web/ 內容到根目錄
git push origin gh-pages

# 方法 C（推薦）：使用 GitHub Actions 自動部署
```

部署後 URL 格式：
```
https://augustchaotw.github.io/ill-posed-AffectTrace/labeling/
```

---

## Step 5：發給標注者

給三位標注者各別的連結（用 URL 參數可預設身份）：

```
標注者 A: https://augustchaotw.github.io/ill-posed-AffectTrace/labeling/?annotator=A
標注者 B: https://augustchaotw.github.io/ill-posed-AffectTrace/labeling/?annotator=B
標注者 C: https://augustchaotw.github.io/ill-posed-AffectTrace/labeling/?annotator=C
```

---

## 資料流說明

| 儲存位置 | 時機 | 用途 |
|---------|------|------|
| `localStorage` | 每次儲存立即寫入 | 中途離開可繼續，不依賴網路 |
| Google Spreadsheet | 每次儲存後非同步推送 | 研究者即時查看進度、匯出計算 κ |

若網路斷線，資料仍安全存在 localStorage。重新連線後再次儲存同一筆會自動覆寫（不重複）。

---

## 查看進度

直接在 Google Sheets 查看各標注者分頁。或用 GET 請求查詢：

```
https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec?annotator=A
```

回傳 JSON：
```json
{ "annotator": "A", "count": 45, "rows": [...] }
```

---

## 匯出並計算 κ

標注完成後，從 Google Sheets 匯出各分頁為 CSV，放到：
```
results/annotator_A/task_annotator_A.csv
results/annotator_B/task_annotator_B.csv
results/annotator_C/task_annotator_C.csv
```

執行：
```bash
cd scripts/
python3 compute_kappa.py
```
