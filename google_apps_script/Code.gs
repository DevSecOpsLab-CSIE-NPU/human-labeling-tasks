/**
 * Google Apps Script — VAD 標注系統後端
 *
 * 部署步驟：
 *  1. 開啟 Google Spreadsheet，建立三個分頁：annotator_A、annotator_B、annotator_C
 *  2. 在選單選 Extensions → Apps Script
 *  3. 貼上此程式碼，並填入 SPREADSHEET_ID
 *  4. 點 Deploy → New deployment → 類型選 Web App
 *     Execute as: Me
 *     Who has access: Anyone
 *  5. 複製 Web App URL，貼到 index.html 的 APPS_SCRIPT_URL
 */

// ── 設定 ──────────────────────────────────────────────────────────────
const SPREADSHEET_ID = "1UNSxHUBvipUrb38flaGjtVRQBGzq4ZP8-zM6DfTsI_4";  // ← 填入你的 Spreadsheet ID

// 每個分頁的欄位標題
const HEADERS = [
  "sample_id",
  "annotator",
  "userName",
  "llm_emotion",
  "repaired_emotion",
  "A1_is_distorted",
  "A2_severity",
  "A3_correct_emotion",
  "annotator_notes",
  "timestamp",
  "domain",
];

// ── doPost：接收標注資料 ───────────────────────────────────────────────
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    const ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheetName = "annotator_" + data.annotator;
    let sheet = ss.getSheetByName(sheetName);

    // 如果分頁不存在就建立
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
      sheet.appendRow(HEADERS);
      sheet.getRange(1, 1, 1, HEADERS.length)
           .setFontWeight("bold")
           .setBackground("#2563eb")
           .setFontColor("#ffffff");
      sheet.setFrozenRows(1);
    }

    // 檢查是否已存在此 sample_id（避免重複寫入）
    const existing = findRow(sheet, data.sample_id);
    const row = [
      data.sample_id,
      data.annotator,
      data.userName     || "",
      data.llm_emotion  || "",
      data.repaired_emotion || "",
      data.A1_is_distorted  || "",
      data.A2_severity      || "",
      data.A3_correct_emotion || "",
      data.annotator_notes  || "",
      data.timestamp        || new Date().toISOString(),
      data.domain           || "",
    ];

    if (existing > 0) {
      // 更新現有行（覆寫）
      sheet.getRange(existing, 1, 1, row.length).setValues([row]);
    } else {
      sheet.appendRow(row);
    }

    // 色彩標記
    const lastRow = existing > 0 ? existing : sheet.getLastRow();
    const a1Val = data.A1_is_distorted;
    const color = a1Val === "NO" ? "#fef2f2" : a1Val === "YES" ? "#f0fdf4" : "#ffffff";
    sheet.getRange(lastRow, 1, 1, row.length).setBackground(color);

    return jsonResponse({ status: "ok", row: lastRow });

  } catch (err) {
    return jsonResponse({ status: "error", message: err.toString() });
  }
}

// ── doGet：回傳某標注者的進度摘要 ─────────────────────────────────────
function doGet(e) {
  try {
    const annotator = e.parameter.annotator;
    if (!annotator) {
      return jsonResponse({ error: "missing annotator param" });
    }

    const ss    = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = ss.getSheetByName("annotator_" + annotator);
    if (!sheet) {
      return jsonResponse({ annotator, count: 0, rows: [] });
    }

    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const rows = data.slice(1).map(r => {
      const obj = {};
      headers.forEach((h, i) => obj[h] = r[i]);
      return obj;
    });

    return jsonResponse({
      annotator,
      count: rows.length,
      rows,
    });

  } catch (err) {
    return jsonResponse({ status: "error", message: err.toString() });
  }
}

// ── Helper：找已存在的 sample_id 行號 ─────────────────────────────────
function findRow(sheet, sampleId) {
  const data = sheet.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === sampleId) return i + 1;  // 1-indexed
  }
  return -1;
}

// ── Helper：JSON 回應（帶 CORS header）────────────────────────────────
function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// ── 手動測試（在 Apps Script 編輯器執行）─────────────────────────────
function testPost() {
  const fakeEvent = {
    postData: {
      contents: JSON.stringify({
        annotator: "A",
        userName: "測試者",
        sample_id: "D001",
        domain: "Amazon",
        llm_emotion: "joy",
        repaired_emotion: "sadness",
        A1_is_distorted: "NO",
        A2_severity: "Severe",
        A3_correct_emotion: "joy",
        annotator_notes: "完全相反",
        timestamp: new Date().toISOString(),
      })
    }
  };
  Logger.log(doPost(fakeEvent).getContent());
}
