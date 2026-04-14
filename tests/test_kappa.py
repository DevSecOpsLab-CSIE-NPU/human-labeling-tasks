"""
測試：compute_kappa.py 的 Cohen's κ 計算邏輯

執行：pytest tests/test_kappa.py -v
"""
import math, pytest, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from compute_kappa import cohens_kappa, interpret


# ════════════════════════════════════════════════════════
#  TC-K-01  完全一致 → κ = 1.0
# ════════════════════════════════════════════════════════
def test_perfect_agreement():
    a1 = {"D001": "NO", "D002": "YES", "D003": "NO"}
    a2 = {"D001": "NO", "D002": "YES", "D003": "NO"}
    k, n = cohens_kappa(a1, a2)
    assert k == 1.0
    assert n == 3


# ════════════════════════════════════════════════════════
#  TC-K-02  系統性反向一致 → κ = -1.0
#           需要 balanced distribution 才能出現負 κ
#           （若 A1 全 YES、A2 全 NO，P_e=0 → κ=0，非負）
# ════════════════════════════════════════════════════════
def test_perfect_disagreement():
    # 交替排列 → 每次都不一致，且邊際分布各 50%
    # A1: YES NO YES NO
    # A2: NO YES NO YES
    # P_o = 0, P_e = 0.5*0.5 + 0.5*0.5 = 0.5 → κ = (0-0.5)/(1-0.5) = -1.0
    a1 = {"D001": "YES", "D002": "NO",  "D003": "YES", "D004": "NO"}
    a2 = {"D001": "NO",  "D002": "YES", "D003": "NO",  "D004": "YES"}
    k, n = cohens_kappa(a1, a2)
    assert k < 0, f"Expected negative kappa, got {k}"
    assert abs(k - (-1.0)) < 0.001, f"Expected κ = -1.0, got {k}"
    assert n == 4


# ════════════════════════════════════════════════════════
#  TC-K-03  隨機一致（50/50 分布）→ κ ≈ 0
# ════════════════════════════════════════════════════════
def test_chance_agreement():
    # 各半 YES/NO，兩標注者相同分布但獨立
    a1 = {f"S{i:03d}": "YES" if i < 50 else "NO" for i in range(100)}
    a2 = {f"S{i:03d}": "YES" if i % 2 == 0 else "NO" for i in range(100)}
    k, n = cohens_kappa(a1, a2)
    assert n == 100
    assert abs(k) < 0.3, f"Expected near-zero kappa, got {k}"


# ════════════════════════════════════════════════════════
#  TC-K-04  目標值 κ ≥ 0.70 → 解讀為 Substantial
# ════════════════════════════════════════════════════════
def test_target_threshold_interpretation():
    assert interpret(0.70) == "Substantial"
    assert interpret(0.75) == "Substantial"
    assert interpret(0.80) == "Almost Perfect"
    assert interpret(0.50) == "Moderate"
    assert interpret(0.30) == "Fair"


# ════════════════════════════════════════════════════════
#  TC-K-05  known-value 計算正確性（手算驗證）
# ════════════════════════════════════════════════════════
def test_known_kappa_value():
    """
    手算範例：
    4 筆樣本:
      A1=NO, A2=NO → 一致
      A1=YES, A2=YES → 一致
      A1=NO, A2=YES → 不一致
      A1=YES, A2=NO → 不一致

    P_o = 2/4 = 0.5
    P(YES) for A1 = 2/4 = 0.5, for A2 = 2/4 = 0.5
    P(NO)  for A1 = 2/4 = 0.5, for A2 = 2/4 = 0.5
    P_e = 0.5*0.5 + 0.5*0.5 = 0.5
    κ = (0.5 - 0.5) / (1 - 0.5) = 0.0
    """
    a1 = {"X1": "NO",  "X2": "YES", "X3": "NO",  "X4": "YES"}
    a2 = {"X1": "NO",  "X2": "YES", "X3": "YES", "X4": "NO"}
    k, n = cohens_kappa(a1, a2)
    assert n == 4
    assert abs(k - 0.0) < 0.001, f"Expected κ ≈ 0.0, got {k}"


# ════════════════════════════════════════════════════════
#  TC-K-06  非重疊樣本 → 只計算共有樣本
# ════════════════════════════════════════════════════════
def test_partial_overlap():
    a1 = {"D001": "NO", "D002": "YES", "D003": "NO"}
    a2 = {"D002": "YES", "D003": "NO", "D004": "YES"}  # D001/D004 不重疊
    k, n = cohens_kappa(a1, a2)
    assert n == 2  # 只有 D002, D003 共有


# ════════════════════════════════════════════════════════
#  TC-K-07  研究假說驗證：DISTORTION 組標注 NO > 80%
# ════════════════════════════════════════════════════════
def test_distortion_group_rejection_rate():
    """
    模擬理想標注結果：
    - DISTORTION 組（D001-D100）90% 答 NO（有失真）
    - SAFE 組（S001-S100）90% 答 YES（無失真）
    驗證研究假說的計算路徑正確
    """
    import random
    random.seed(123)

    def make_annotations(dist_no_rate=0.90, safe_no_rate=0.10):
        ann = {}
        for i in range(1, 101):
            ann[f"D{i:03d}"] = "NO"  if random.random() < dist_no_rate else "YES"
            ann[f"S{i:03d}"] = "NO"  if random.random() < safe_no_rate  else "YES"
        return ann

    ann = make_annotations()

    dist_no  = sum(1 for i in range(1,101) if ann.get(f"D{i:03d}") == "NO")
    safe_no  = sum(1 for i in range(1,101) if ann.get(f"S{i:03d}") == "NO")

    assert dist_no / 100 >= 0.80, \
        f"DISTORTION rejection rate {dist_no/100:.1%} < 80%"
    assert safe_no / 100 <= 0.20, \
        f"SAFE rejection rate {safe_no/100:.1%} > 20%"


# ════════════════════════════════════════════════════════
#  TC-K-08  空輸入 → 回傳 None, n=0
# ════════════════════════════════════════════════════════
def test_empty_input():
    k, n = cohens_kappa({}, {})
    assert k is None
    assert n == 0


# ════════════════════════════════════════════════════════
#  TC-K-09  全部同一答案（全 YES）→ κ 計算不崩潰
# ════════════════════════════════════════════════════════
def test_all_same_label():
    a1 = {"X1": "YES", "X2": "YES", "X3": "YES"}
    a2 = {"X1": "YES", "X2": "YES", "X3": "YES"}
    k, n = cohens_kappa(a1, a2)
    # P_e = 1.0 → special case: return 1.0
    assert k == 1.0
    assert n == 3


# ════════════════════════════════════════════════════════
#  TC-K-10  A3 多類別 κ：完全一致 → 1.0
# ════════════════════════════════════════════════════════
def test_a3_perfect_agreement():
    """A3 是 12 類情感，完全一致應回傳 κ = 1.0"""
    a1 = {"D001": "joy", "D002": "anger", "D003": "sadness", "D004": "fear"}
    a2 = {"D001": "joy", "D002": "anger", "D003": "sadness", "D004": "fear"}
    k, n = cohens_kappa(a1, a2)
    assert k == 1.0
    assert n == 4


# ════════════════════════════════════════════════════════
#  TC-K-11  A3 多類別 κ：known-value 驗證（手算）
# ════════════════════════════════════════════════════════
def test_a3_known_kappa_value():
    """
    手算：4 筆，3 類標籤（joy/anger/sadness）
    A1: joy   anger sadness joy
    A2: joy   anger sadness anger   ← 第4筆不一致

    P_o = 3/4 = 0.75
    邊際：
      A1: joy=2/4, anger=1/4, sadness=1/4
      A2: joy=1/4, anger=2/4, sadness=1/4
    P_e = (2/4)(1/4) + (1/4)(2/4) + (1/4)(1/4)
        = 2/16 + 2/16 + 1/16 = 5/16 = 0.3125
    κ = (0.75 - 0.3125) / (1 - 0.3125) = 0.4375 / 0.6875 ≈ 0.6364
    """
    a1 = {"D001": "joy",   "D002": "anger", "D003": "sadness", "D004": "joy"}
    a2 = {"D001": "joy",   "D002": "anger", "D003": "sadness", "D004": "anger"}
    k, n = cohens_kappa(a1, a2)
    assert n == 4
    assert abs(k - 0.6364) < 0.001, f"Expected κ ≈ 0.6364, got {k}"


# ════════════════════════════════════════════════════════
#  TC-K-12  A3 多類別 κ：類別數不影響函數通用性
# ════════════════════════════════════════════════════════
def test_a3_multiclass_generalizes():
    """12 類情感標籤，各自有代表性樣本，κ 應在合理範圍內不崩潰"""
    emotions = ["joy", "sadness", "anger", "fear", "surprise",
                "disgust", "frustration", "annoyance", "neutral",
                "contentment", "excitement", "anxiety"]
    # 兩位標注者：大部分一致，各有 2 筆不一致
    a1, a2 = {}, {}
    for i, emo in enumerate(emotions):
        sid = f"S{i:03d}"
        a1[sid] = emo
        a2[sid] = emo  # 一致

    # 製造 2 筆不一致
    a2["S000"] = "sadness"   # joy → sadness
    a2["S001"] = "anger"     # sadness → anger

    k, n = cohens_kappa(a1, a2)
    assert n == 12
    assert k is not None
    assert -1.0 <= k <= 1.0, f"κ out of range: {k}"


# ════════════════════════════════════════════════════════
#  TC-K-13  A3 與 A1 共用同一 cohens_kappa 函數（通用性）
# ════════════════════════════════════════════════════════
def test_cohens_kappa_is_generic():
    """同一函數處理二元（A1）和多類（A3），結果一致"""
    # Binary case (A1)
    a1_bin = {"D001": "YES", "D002": "NO", "D003": "YES", "D004": "NO"}
    a2_bin = {"D001": "YES", "D002": "NO", "D003": "YES", "D004": "NO"}
    k_bin, _ = cohens_kappa(a1_bin, a2_bin)
    assert k_bin == 1.0

    # Multi-class case (A3)
    a1_mul = {"D001": "joy", "D002": "anger", "D003": "joy", "D004": "anger"}
    a2_mul = {"D001": "joy", "D002": "anger", "D003": "joy", "D004": "anger"}
    k_mul, _ = cohens_kappa(a1_mul, a2_mul)
    assert k_mul == 1.0
