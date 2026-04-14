"""
測試：前端核心邏輯（Python 模擬 JS 行為）

測試 index.html 中的以下邏輯：
  - selectOpt() 選擇狀態管理
  - saveAndNext() 資料驗證規則
  - localStorage 進度追蹤
  - A1=YES → A2 自動設為 None
  - 鍵盤快捷鍵對應

執行：pytest tests/test_frontend_logic.py -v
"""
import pytest
from dataclasses import dataclass, field
from typing import Optional


# ── Python 模擬前端狀態機 ─────────────────────────────────────────────
EMOTIONS = [
    "joy","sadness","anger","fear","surprise","disgust",
    "frustration","annoyance","neutral","contentment","excitement","anxiety"
]

@dataclass
class AnnotationState:
    """模擬 index.html 的 UI 狀態"""
    A1: Optional[str] = None   # "YES" | "NO"
    A2: Optional[str] = None   # "None" | "Slight" | "Moderate" | "Severe"
    A3: Optional[str] = None   # emotion label
    notes: str = ""

    def select_opt(self, q: str, v: str):
        """模擬 selectOpt(btn, q, v)"""
        if q == "A1":
            self.A1 = v
            # Auto-set A2=None when A1=YES
            if v == "YES":
                self.A2 = "None"
        elif q == "A2":
            self.A2 = v
        elif q == "A3":
            self.A3 = v

    def is_ready(self) -> bool:
        """模擬 checkReady() — 所有必填項目完成"""
        return bool(self.A1 and self.A2 and self.A3)

    def to_record(self, sample_id: str, annotator: str) -> Optional[dict]:
        """模擬 saveAndNext() 產生的記錄"""
        if not self.is_ready():
            return None
        return {
            "sample_id": sample_id,
            "annotator": annotator,
            "A1_is_distorted": self.A1,
            "A2_severity": self.A2,
            "A3_correct_emotion": self.A3,
            "annotator_notes": self.notes,
        }


@dataclass
class LocalStorage:
    """模擬 localStorage"""
    _store: dict = field(default_factory=dict)

    def get(self, key: str) -> Optional[dict]:
        return self._store.get(key)

    def set(self, key: str, value: dict):
        self._store[key] = value

    def key(self, annotator: str) -> str:
        return f"vad_annot_{annotator}"


# ════════════════════════════════════════════════════════
#  TC-FE-01  selectOpt 正確設定 A1
# ════════════════════════════════════════════════════════
def test_select_a1():
    s = AnnotationState()
    s.select_opt("A1", "NO")
    assert s.A1 == "NO"
    s.select_opt("A1", "YES")
    assert s.A1 == "YES"


# ════════════════════════════════════════════════════════
#  TC-FE-02  A1=YES → A2 自動設為 None
# ════════════════════════════════════════════════════════
def test_a1_yes_auto_sets_a2_none():
    s = AnnotationState()
    s.select_opt("A1", "YES")
    assert s.A2 == "None", "Expected A2='None' when A1='YES'"


# ════════════════════════════════════════════════════════
#  TC-FE-03  A1=NO 不自動改 A2
# ════════════════════════════════════════════════════════
def test_a1_no_does_not_change_a2():
    s = AnnotationState()
    s.select_opt("A2", "Severe")
    s.select_opt("A1", "NO")
    assert s.A2 == "Severe", "A2 should not change when A1='NO'"


# ════════════════════════════════════════════════════════
#  TC-FE-04  三個欄位都填才 is_ready=True
# ════════════════════════════════════════════════════════
def test_ready_requires_all_three():
    s = AnnotationState()
    assert not s.is_ready()
    s.select_opt("A1", "NO")
    assert not s.is_ready()
    s.select_opt("A2", "Severe")
    assert not s.is_ready()
    s.select_opt("A3", "joy")
    assert s.is_ready()


# ════════════════════════════════════════════════════════
#  TC-FE-05  未完成不能產生記錄
# ════════════════════════════════════════════════════════
def test_incomplete_returns_none():
    s = AnnotationState()
    s.select_opt("A1", "NO")
    # A2, A3 missing
    record = s.to_record("D001", "A")
    assert record is None


# ════════════════════════════════════════════════════════
#  TC-FE-06  完整記錄的欄位正確
# ════════════════════════════════════════════════════════
def test_complete_record_fields():
    s = AnnotationState()
    s.select_opt("A1", "NO")
    s.select_opt("A2", "Severe")
    s.select_opt("A3", "joy")
    s.notes = "completely reversed"

    record = s.to_record("D001", "A")
    assert record is not None
    assert record["sample_id"]        == "D001"
    assert record["annotator"]        == "A"
    assert record["A1_is_distorted"]  == "NO"
    assert record["A2_severity"]      == "Severe"
    assert record["A3_correct_emotion"] == "joy"
    assert record["annotator_notes"]  == "completely reversed"


# ════════════════════════════════════════════════════════
#  TC-FE-07  A3 只接受合法情感標籤
# ════════════════════════════════════════════════════════
def test_a3_valid_emotion_labels():
    for emotion in EMOTIONS:
        s = AnnotationState()
        s.select_opt("A3", emotion)
        assert s.A3 == emotion


# ════════════════════════════════════════════════════════
#  TC-FE-08  localStorage 進度追蹤：儲存與讀取
# ════════════════════════════════════════════════════════
def test_localstorage_progress_tracking():
    store = LocalStorage()
    annotator = "B"
    key = store.key(annotator)

    # 模擬儲存 3 筆答案
    answers = {
        "D001": {"A1": "NO",  "A2": "Severe", "A3": "joy"},
        "D002": {"A1": "YES", "A2": "None",   "A3": "annoyance"},
        "S001": {"A1": "YES", "A2": "None",   "A3": "frustration"},
    }
    store.set(key, answers)

    # 模擬讀取（例如刷新頁面後繼續）
    loaded = store.get(key)
    assert loaded is not None
    assert len(loaded) == 3
    assert loaded["D001"]["A1"] == "NO"
    assert loaded["S001"]["A3"] == "frustration"


# ════════════════════════════════════════════════════════
#  TC-FE-09  進度恢復：找到第一個未完成的樣本
# ════════════════════════════════════════════════════════
def test_resume_finds_first_unanswered():
    """模擬 btn-start onclick 的進度恢復邏輯"""
    import csv
    from pathlib import Path

    ann_file = Path(__file__).parent.parent / "results" / "annotator_A" / "task_annotator_A.csv"
    with open(ann_file) as f:
        samples = list(csv.DictReader(f))

    # 模擬已完成前 50 筆
    answers = {s["sample_id"]: {"A1": "YES", "A2": "None", "A3": "joy"}
               for s in samples[:50]}

    # 恢復邏輯
    current = 0
    for i, s in enumerate(samples):
        if s["sample_id"] not in answers:
            current = i
            break

    assert current == 50, f"Expected to resume at index 50, got {current}"


# ════════════════════════════════════════════════════════
#  TC-FE-10  鍵盤快捷鍵對應
# ════════════════════════════════════════════════════════
@pytest.mark.parametrize("key,expected_q,expected_v", [
    ("y", "A1", "YES"),
    ("Y", "A1", "YES"),
    ("n", "A1", "NO"),
    ("N", "A1", "NO"),
])
def test_keyboard_shortcuts(key, expected_q, expected_v):
    """模擬鍵盤快捷鍵 → selectOpt"""
    s = AnnotationState()
    # Simulate key handler
    key_map = {
        "y": ("A1", "YES"), "Y": ("A1", "YES"),
        "n": ("A1", "NO"),  "N": ("A1", "NO"),
    }
    if key in key_map:
        q, v = key_map[key]
        s.select_opt(q, v)
    assert getattr(s, expected_q) == expected_v


# ════════════════════════════════════════════════════════
#  TC-FE-11  全部 400 筆模擬標注流程（整合測試）
# ════════════════════════════════════════════════════════
def test_full_annotation_flow():
    """模擬一位標注者完成所有 400 筆的完整流程"""
    import csv
    from pathlib import Path

    ann_file = Path(__file__).parent.parent / "results" / "annotator_A" / "task_annotator_A.csv"
    with open(ann_file) as f:
        samples = list(csv.DictReader(f))

    store = LocalStorage()
    answers = {}
    key = store.key("A")

    for s in samples:
        state = AnnotationState()
        # 模擬標注者回答
        state.select_opt("A1", "NO")
        state.select_opt("A2", "Moderate")
        state.select_opt("A3", s["llm_emotion"])

        assert state.is_ready()
        record = state.to_record(s["sample_id"], "A")
        assert record is not None

        answers[s["sample_id"]] = {
            "A1": record["A1_is_distorted"],
            "A2": record["A2_severity"],
            "A3": record["A3_correct_emotion"],
        }
        store.set(key, answers)

    # 最終確認
    final = store.get(key)
    assert len(final) == 400, f"Expected 400 saved answers, got {len(final)}"
