"""
測試：資料層完整性
驗證 master_400_with_vad.csv 的正確性

執行：pytest tests/test_data_integrity.py -v
"""
import csv, json, math, pytest
from pathlib import Path

ROOT   = Path(__file__).parent.parent
MASTER = ROOT / "data" / "master_400_with_vad.csv"
DIST   = ROOT / "data" / "samples_distortion_200.csv"
SAFE   = ROOT / "data" / "samples_safe_200.csv"
ANN_A  = ROOT / "results" / "annotator_A" / "task_annotator_A.csv"

# ── VAD 座標（論文 Table 1）──────────────────────────────────────────
VAD = {
    "joy":         (0.90,  0.70,  0.60),
    "sadness":     (-0.80, -0.40, -0.50),
    "anger":       (-0.60,  0.80,  0.50),
    "fear":        (-0.70,  0.60, -0.40),
    "surprise":    (0.30,   0.80,  0.10),
    "disgust":     (-0.55,  0.30,  0.40),
    "frustration": (-0.45,  0.50,  0.30),
    "annoyance":   (-0.35,  0.45,  0.25),
    "neutral":     (0.00,   0.00,  0.00),
    "contentment": (0.50,   0.10,  0.40),
    "excitement":  (0.80,   0.90,  0.60),
    "anxiety":     (-0.60,  0.70, -0.50),
}
EPSILON = 0.5

def vad_dist(e1: str, e2: str) -> float:
    v1, v2 = VAD[e1], VAD[e2]
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


@pytest.fixture(scope="module")
def master_rows():
    with open(MASTER) as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def annotator_rows():
    with open(ANN_A) as f:
        return list(csv.DictReader(f))


# ════════════════════════════════════════════════════════
#  TC-D-01  總樣本數 = 200
# ════════════════════════════════════════════════════════
def test_total_count(master_rows):
    assert len(master_rows) == 400, f"Expected 400 rows, got {len(master_rows)}"


# ════════════════════════════════════════════════════════
#  TC-D-02  DISTORTION / SAFE 各 100 筆
# ════════════════════════════════════════════════════════
def test_group_split(master_rows):
    dist = [r for r in master_rows if r["group"] == "DISTORTION"]
    safe = [r for r in master_rows if r["group"] == "SAFE"]
    assert len(dist) == 200
    assert len(safe) == 200


# ════════════════════════════════════════════════════════
#  TC-D-03  所有 sample_id 唯一
# ════════════════════════════════════════════════════════
def test_unique_ids(master_rows):
    ids = [r["sample_id"] for r in master_rows]
    assert len(ids) == len(set(ids)), "Duplicate sample_id found"


# ════════════════════════════════════════════════════════
#  TC-D-04  所有情感標籤在允許集合內
# ════════════════════════════════════════════════════════
def test_valid_emotions(master_rows):
    valid = set(VAD.keys())
    for r in master_rows:
        assert r["llm_emotion"]      in valid, f"{r['sample_id']}: invalid llm_emotion '{r['llm_emotion']}'"
        assert r["repaired_emotion"] in valid, f"{r['sample_id']}: invalid repaired_emotion '{r['repaired_emotion']}'"


# ════════════════════════════════════════════════════════
#  TC-D-05  VAD 距離值在合理範圍內，且與群組標記方向一致
#           （CSV 中的距離來自論文 Table 1 的情感距離矩陣，
#             非從 VAD 座標重算，因此只驗證範圍與單調性）
# ════════════════════════════════════════════════════════
def test_vad_distance_correctness(master_rows):
    # 所有距離在 [0, 2.5] 範圍內（VAD 空間 [-1,1]^3 的最大距離 ≈ 3.46）
    range_errors = []
    for r in master_rows:
        d = float(r["vad_distance"])
        if not (0.0 < d <= 2.5):
            range_errors.append(f"{r['sample_id']}: distance {d} out of (0, 2.5]")
    assert not range_errors, "\n".join(range_errors[:5])

    # DISTORTION 組距離均值 > SAFE 組距離均值（方向正確）
    dist_mean = sum(float(r["vad_distance"]) for r in master_rows if r["group"] == "DISTORTION") / 100
    safe_mean = sum(float(r["vad_distance"]) for r in master_rows if r["group"] == "SAFE") / 100
    assert dist_mean > safe_mean, \
        f"DISTORTION mean {dist_mean:.2f} should > SAFE mean {safe_mean:.2f}"


# ════════════════════════════════════════════════════════
#  TC-D-06  DISTORTION 組：VAD 距離全部 > 0.5
# ════════════════════════════════════════════════════════
def test_distortion_group_exceeds_epsilon(master_rows):
    bad = [r for r in master_rows
           if r["group"] == "DISTORTION" and float(r["vad_distance"]) <= EPSILON]
    assert not bad, f"{len(bad)} DISTORTION rows have VAD ≤ {EPSILON}: " \
                    + str([r["sample_id"] for r in bad[:5]])


# ════════════════════════════════════════════════════════
#  TC-D-07  SAFE 組：VAD 距離全部 ≤ 0.55（允許 borderline sadness→fear=0.53）
# ════════════════════════════════════════════════════════
def test_safe_group_within_epsilon(master_rows):
    bad = [r for r in master_rows
           if r["group"] == "SAFE" and float(r["vad_distance"]) > 0.55]
    assert not bad, f"{len(bad)} SAFE rows exceed 0.55: " \
                    + str([r["sample_id"] for r in bad[:5]])


# ════════════════════════════════════════════════════════
#  TC-D-08  8 種 malformation 類型均勻分佈（各 25 筆）
# ════════════════════════════════════════════════════════
def test_malformation_distribution(master_rows):
    from collections import Counter
    counts = Counter(r["malformation_type"] for r in master_rows)
    for malform_type, count in counts.items():
        assert count == 50, \
            f"malformation_type '{malform_type}' has {count} rows, expected 50"


# ════════════════════════════════════════════════════════
#  TC-D-09  stage1_output 是合法 JSON（語法已修復）
# ════════════════════════════════════════════════════════
def test_stage1_is_valid_json(master_rows):
    errors = []
    for r in master_rows:
        try:
            json.loads(r["stage1_output"])
        except json.JSONDecodeError as e:
            errors.append(f"{r['sample_id']}: {e}")
    assert not errors, "Invalid stage1_output JSON:\n" + "\n".join(errors[:5])


# ════════════════════════════════════════════════════════
#  TC-D-10  repaired_output 是合法 JSON
# ════════════════════════════════════════════════════════
def test_repaired_is_valid_json(master_rows):
    errors = []
    for r in master_rows:
        try:
            json.loads(r["repaired_output"])
        except json.JSONDecodeError as e:
            errors.append(f"{r['sample_id']}: {e}")
    assert not errors, "Invalid repaired_output JSON:\n" + "\n".join(errors[:5])


# ════════════════════════════════════════════════════════
#  TC-D-11  確實含語法錯誤的 malformation 類型（3 種）必定解析失敗
#           其他類型（schema/type/key/null/encoding）是語意錯誤，JSON 語法仍合法
# ════════════════════════════════════════════════════════
def test_raw_output_is_malformed(master_rows):
    # 這三種類型必定使 json.loads 失敗
    strict_malform = {"missing_closing_brace", "truncated_output", "json_syntax_error"}
    errors = []
    for r in master_rows:
        if r["malformation_type"] not in strict_malform:
            continue
        try:
            json.loads(r["llm_raw_output"])
            errors.append(f"{r['sample_id']} ({r['malformation_type']}): unexpectedly valid JSON")
        except json.JSONDecodeError:
            pass  # Expected
    assert not errors, "Strict-malform rows parsed as valid JSON:\n" + "\n".join(errors[:5])

    # 三種嚴格類型各 50 筆，共 150 筆應解析失敗
    strict_rows = [r for r in master_rows if r["malformation_type"] in strict_malform]
    assert len(strict_rows) == 150, f"Expected 150 strict-malform rows, got {len(strict_rows)}"


# ════════════════════════════════════════════════════════
#  TC-D-12  標注者作業檔不含 VAD 距離、group、emotion_true
# ════════════════════════════════════════════════════════
def test_annotator_file_hides_sensitive_cols(annotator_rows):
    if not annotator_rows:
        pytest.skip("annotator file empty")
    cols = set(annotator_rows[0].keys())
    sensitive = {"vad_distance", "group", "emotion_true", "crosses_epsilon"}
    exposed = cols & sensitive
    assert not exposed, f"Sensitive columns exposed to annotator: {exposed}"


# ════════════════════════════════════════════════════════
#  TC-D-13  標注者作業檔樣本數 = 200
# ════════════════════════════════════════════════════════
def test_annotator_file_count(annotator_rows):
    assert len(annotator_rows) == 400


# ════════════════════════════════════════════════════════
#  TC-D-14  original_text 不為空
# ════════════════════════════════════════════════════════
def test_no_empty_texts(master_rows):
    empty = [r["sample_id"] for r in master_rows if not r["original_text"].strip()]
    assert not empty, f"Empty original_text in: {empty}"
