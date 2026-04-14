"""
測試：Google Apps Script Code.gs 的業務邏輯（Python mock 模擬）

Apps Script 無法直接在 Python 執行，但其核心邏輯
（欄位驗證、重複寫入、分頁路由）可用 mock 物件測試。

執行：pytest tests/test_apps_script_mock.py -v
"""
import json, pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, call


# ── Mock Google Sheets API ────────────────────────────────────────────
class MockSheet:
    def __init__(self, name):
        self.name = name
        self._rows = []
        self._headers_set = False
        self._bg_colors = {}

    def appendRow(self, row):
        self._rows.append(list(row))

    def getDataRange(self):
        m = MagicMock()
        m.getValues.return_value = self._rows
        return m

    def getRange(self, row, col, nrows=1, ncols=1):
        m = MagicMock()
        m.setValues = MagicMock()
        m.setBackground = MagicMock(return_value=m)
        m.setFontWeight = MagicMock(return_value=m)
        m.setFontColor  = MagicMock(return_value=m)
        return m

    def getLastRow(self):
        return len(self._rows)

    def setFrozenRows(self, n): pass


class MockSpreadsheet:
    def __init__(self):
        self._sheets = {}

    def getSheetByName(self, name):
        return self._sheets.get(name)

    def insertSheet(self, name):
        sheet = MockSheet(name)
        self._sheets[name] = sheet
        return sheet


# ── Python re-implementation of Code.gs logic ────────────────────────
HEADERS = [
    "sample_id","annotator","userName","llm_emotion","repaired_emotion",
    "A1_is_distorted","A2_severity","A3_correct_emotion",
    "annotator_notes","timestamp","domain",
]

def do_post(data: dict, ss: MockSpreadsheet) -> dict:
    """Python reimplementation of Code.gs doPost() logic"""
    sheet_name = "annotator_" + data["annotator"]
    sheet = ss.getSheetByName(sheet_name)

    if not sheet:
        sheet = ss.insertSheet(sheet_name)
        sheet.appendRow(HEADERS)

    # Find existing row
    existing = find_row(sheet, data["sample_id"])

    row = [
        data.get("sample_id",""),
        data.get("annotator",""),
        data.get("userName",""),
        data.get("llm_emotion",""),
        data.get("repaired_emotion",""),
        data.get("A1_is_distorted",""),
        data.get("A2_severity",""),
        data.get("A3_correct_emotion",""),
        data.get("annotator_notes",""),
        data.get("timestamp", datetime.now().isoformat()),
        data.get("domain",""),
    ]

    if existing > 0:
        sheet.getRange(existing, 1, 1, len(row)).setValues([row])
        return {"status": "ok", "action": "updated", "row": existing}
    else:
        sheet.appendRow(row)
        return {"status": "ok", "action": "appended", "row": sheet.getLastRow()}


def find_row(sheet, sample_id) -> int:
    data = sheet.getDataRange().getValues()
    for i, row in enumerate(data):
        if i == 0: continue  # skip header
        if row and row[0] == sample_id:
            return i + 1
    return -1


# ════════════════════════════════════════════════════════
#  TC-GAS-01  首次寫入：建立分頁 + header + 新增一行
# ════════════════════════════════════════════════════════
def test_first_write_creates_sheet():
    ss = MockSpreadsheet()
    data = {
        "annotator": "A", "userName": "Test User",
        "sample_id": "D001", "domain": "Amazon",
        "llm_emotion": "joy", "repaired_emotion": "sadness",
        "A1_is_distorted": "NO", "A2_severity": "Severe",
        "A3_correct_emotion": "joy", "annotator_notes": "",
        "timestamp": "2026-04-14T10:00:00Z",
    }

    result = do_post(data, ss)

    assert result["status"] == "ok"
    assert result["action"] == "appended"
    sheet = ss.getSheetByName("annotator_A")
    assert sheet is not None
    # Row 0 = HEADERS, Row 1 = data
    assert len(sheet._rows) == 2
    assert sheet._rows[0] == HEADERS
    assert sheet._rows[1][0] == "D001"
    assert sheet._rows[1][5] == "NO"   # A1_is_distorted


# ════════════════════════════════════════════════════════
#  TC-GAS-02  重複寫入同一 sample_id → 覆寫（不重複 append）
# ════════════════════════════════════════════════════════
def test_duplicate_write_updates_not_appends():
    ss = MockSpreadsheet()
    base = {
        "annotator": "B", "userName": "User B",
        "sample_id": "S042", "domain": "Amazon",
        "llm_emotion": "frustration", "repaired_emotion": "annoyance",
        "A1_is_distorted": "YES", "A2_severity": "None",
        "A3_correct_emotion": "annoyance", "annotator_notes": "",
        "timestamp": "2026-04-14T10:00:00Z",
    }

    do_post(base, ss)
    # Same sample_id, different answer
    updated = {**base, "A1_is_distorted": "NO", "A2_severity": "Slight"}
    result = do_post(updated, ss)

    assert result["action"] == "updated"
    sheet = ss.getSheetByName("annotator_B")
    # Still only 2 rows (header + 1 data), not 3
    assert len(sheet._rows) == 2


# ════════════════════════════════════════════════════════
#  TC-GAS-03  三位標注者寫入各自的分頁，不互相干擾
# ════════════════════════════════════════════════════════
def test_three_annotators_isolated():
    ss = MockSpreadsheet()

    for annotator in ["A", "B", "C"]:
        do_post({
            "annotator": annotator, "userName": f"User {annotator}",
            "sample_id": "D001", "domain": "Amazon",
            "llm_emotion": "joy", "repaired_emotion": "sadness",
            "A1_is_distorted": "NO", "A2_severity": "Severe",
            "A3_correct_emotion": "joy", "annotator_notes": "",
            "timestamp": "2026-04-14T10:00:00Z",
        }, ss)

    # Each annotator has their own sheet with 2 rows (header + 1 data)
    for annotator in ["A", "B", "C"]:
        sheet = ss.getSheetByName(f"annotator_{annotator}")
        assert sheet is not None, f"Sheet annotator_{annotator} not created"
        assert len(sheet._rows) == 2

    # No cross-contamination
    assert ss.getSheetByName("annotator_A")._rows[1][1] == "A"
    assert ss.getSheetByName("annotator_B")._rows[1][1] == "B"
    assert ss.getSheetByName("annotator_C")._rows[1][1] == "C"


# ════════════════════════════════════════════════════════
#  TC-GAS-04  400 筆全部寫入後，分頁有 401 行（1 header + 400 data）
# ════════════════════════════════════════════════════════
def test_full_400_samples_write():
    import csv
    from pathlib import Path

    ss = MockSpreadsheet()
    ann_file = Path(__file__).parent.parent / "results" / "annotator_A" / "task_annotator_A.csv"
    with open(ann_file) as f:
        samples = list(csv.DictReader(f))

    for s in samples:
        do_post({
            "annotator": "A", "userName": "Test",
            "sample_id": s["sample_id"], "domain": s["domain"],
            "llm_emotion": s["llm_emotion"],
            "repaired_emotion": s["repaired_emotion"],
            "A1_is_distorted": "NO",   # mock answer
            "A2_severity": "Severe",
            "A3_correct_emotion": s["llm_emotion"],
            "annotator_notes": "",
            "timestamp": "2026-04-14T10:00:00Z",
        }, ss)

    sheet = ss.getSheetByName("annotator_A")
    assert len(sheet._rows) == 401, \
        f"Expected 401 rows (1 header + 400 data), got {len(sheet._rows)}"


# ════════════════════════════════════════════════════════
#  TC-GAS-05  欄位順序符合 HEADERS 定義
# ════════════════════════════════════════════════════════
def test_column_order():
    ss = MockSpreadsheet()
    do_post({
        "annotator": "A", "userName": "Alice",
        "sample_id": "D099", "domain": "Amazon",
        "llm_emotion": "anger", "repaired_emotion": "joy",
        "A1_is_distorted": "NO", "A2_severity": "Severe",
        "A3_correct_emotion": "anger",
        "annotator_notes": "clear reversal",
        "timestamp": "2026-04-14T12:00:00Z",
    }, ss)

    sheet = ss.getSheetByName("annotator_A")
    header_row = sheet._rows[0]
    data_row   = sheet._rows[1]

    assert header_row == HEADERS
    idx = {h: i for i, h in enumerate(HEADERS)}
    assert data_row[idx["sample_id"]]        == "D099"
    assert data_row[idx["A1_is_distorted"]]  == "NO"
    assert data_row[idx["A3_correct_emotion"]] == "anger"
    assert data_row[idx["annotator_notes"]]  == "clear reversal"


# ════════════════════════════════════════════════════════
#  TC-GAS-06  缺少欄位時填入空字串，不 crash
# ════════════════════════════════════════════════════════
def test_missing_fields_default_empty():
    ss = MockSpreadsheet()
    result = do_post({
        "annotator": "C",
        "sample_id": "S001",
        # 故意缺少 A2_severity, annotator_notes, timestamp
        "A1_is_distorted": "YES",
        "A3_correct_emotion": "frustration",
    }, ss)

    assert result["status"] == "ok"
    sheet = ss.getSheetByName("annotator_C")
    data_row = sheet._rows[1]
    idx = {h: i for i, h in enumerate(HEADERS)}
    assert data_row[idx["A2_severity"]] == ""
    assert data_row[idx["annotator_notes"]] == ""
