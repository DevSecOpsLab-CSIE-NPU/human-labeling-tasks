#!/usr/bin/env python3
"""
計算三位標注者之間的 Cohen's κ（kappa）一致性

支援：
  A1 (A1_is_distorted)    — 二元 κ（YES/NO）
  A3 (A3_correct_emotion) — 多類別 κ（12 種情感）

用法: python3 compute_kappa.py
"""

import csv, os, math
from itertools import combinations

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "../results")
ANNOTATORS = ["annotator_A", "annotator_B", "annotator_C",
               "annotator_D", "annotator_E", "annotator_F"]


def load_annotations(annotator):
    """載入標注結果，回傳 {A1: {sample_id: label}, A3: {sample_id: label}}"""
    path = os.path.join(RESULTS_DIR, annotator, f"task_{annotator}.csv")
    result = {"A1": {}, "A3": {}}
    with open(path) as f:
        for r in csv.DictReader(f):
            sid = r["sample_id"]
            a1 = r.get("A1_is_distorted", "").strip().upper()
            a3 = r.get("A3_correct_emotion", "").strip().lower()
            if a1:
                result["A1"][sid] = a1
            if a3:
                result["A3"][sid] = a3
    return result


def cohens_kappa(a1_labels: dict, a2_labels: dict):
    """
    通用 Cohen's κ（支援二元與多類別）。

    Parameters
    ----------
    a1_labels, a2_labels : dict[sample_id → label]

    Returns
    -------
    (kappa, n) : (float | None, int)
    """
    common = sorted(set(a1_labels) & set(a2_labels))
    if not common:
        return None, 0

    n = len(common)
    agree = sum(1 for sid in common if a1_labels[sid] == a2_labels[sid])
    p_o = agree / n

    # 所有出現過的類別（兩位標注者合集）
    all_vals = sorted(
        set(a1_labels[sid] for sid in common) |
        set(a2_labels[sid] for sid in common)
    )
    p_e = sum(
        (sum(1 for sid in common if a1_labels[sid] == v) / n) *
        (sum(1 for sid in common if a2_labels[sid] == v) / n)
        for v in all_vals
    )

    if p_e >= 1.0:
        return 1.0, n
    return round((p_o - p_e) / (1 - p_e), 4), n


def interpret(k):
    if k is None:  return "N/A"
    if k < 0:      return "Poor (< 0)"
    if k < 0.20:   return "Slight"
    if k < 0.40:   return "Fair"
    if k < 0.60:   return "Moderate"
    if k < 0.80:   return "Substantial"
    return "Almost Perfect"


def krippendorff_alpha_nominal(data: dict) -> tuple:
    """
    Compute Krippendorff's α for nominal data with partial overlap.
    data: {annotator: {unit_id: label}}
    Returns (alpha, n_valid_units)
    """
    annotators = list(data.keys())
    all_units = sorted(set().union(*[set(d.keys()) for d in data.values()]))
    units = [u for u in all_units if sum(1 for a in annotators if data[a].get(u)) >= 2]
    n_valid = len(units)
    if n_valid < 2:
        return None, n_valid

    all_labels = sorted(set(v for d in data.values() for v in d.values() if v))
    cat_idx = {c: i for i, c in enumerate(all_labels)}
    n_cat = len(all_labels)

    o = [[0.0] * n_cat for _ in range(n_cat)]
    for unit in units:
        labels = [data[a][unit] for a in annotators if data[a].get(unit)]
        mu = len(labels)
        for i in range(mu):
            for j in range(mu):
                if i != j:
                    o[cat_idx[labels[i]]][cat_idx[labels[j]]] += 1.0 / (mu - 1)

    n = sum(sum(row) for row in o)
    if n == 0:
        return None, n_valid

    marginals = [sum(o[c][k] for k in range(n_cat)) for c in range(n_cat)]
    D_o = sum(o[c1][c2] for c1 in range(n_cat) for c2 in range(n_cat) if c1 != c2) / n
    D_e = sum(
        marginals[c1] * marginals[c2]
        for c1 in range(n_cat) for c2 in range(n_cat) if c1 != c2
    ) / (n * (n - 1))

    if D_e == 0:
        return 1.0, n_valid
    return round(1 - D_o / D_e, 4), n_valid


# 非重疊對（數學限制）
NO_OVERLAP_PAIRS = {
    ("annotator_A", "annotator_F"),
    ("annotator_B", "annotator_E"),
    ("annotator_C", "annotator_D"),
}


def _print_kappa_section(title: str, field_data: dict[str, dict]):
    """印出某欄位（A1 或 A3）的 pairwise κ 表格。"""
    print(f"\n=== {title} ===")
    kappas = []
    for ann1, ann2 in combinations(ANNOTATORS, 2):
        pair = tuple(sorted([ann1, ann2]))
        if pair in NO_OVERLAP_PAIRS:
            print(f"  {ann1} vs {ann2}: 無重疊樣本（rotating design）— 跳過")
            continue
        d1, d2 = field_data.get(ann1, {}), field_data.get(ann2, {})
        if not d1 or not d2:
            continue
        k, n = cohens_kappa(d1, d2)
        kappas.append(k)
        print(f"  {ann1} vs {ann2}: κ = {k}  ({interpret(k)})  n={n}")

    if kappas:
        valid_kappas = [k for k in kappas if k is not None]
        if valid_kappas:
            avg_k = sum(valid_kappas) / len(valid_kappas)
            print(f"\n  Average κ: {avg_k:.4f}  ({interpret(avg_k)})  ({len(valid_kappas)} pairs)")
            target = 0.70
            if avg_k >= target:
                print(f"  ✓ TARGET MET: κ ≥ {target}")
            else:
                print(f"  ✗ Below target ({target}). Gap: {target - avg_k:.4f}")
    return kappas


def _adjudicate(all_data: dict[str, dict], field: str):
    """Majority-vote adjudication for one field."""
    all_ids = sorted(set().union(*[set(d[field].keys()) for d in all_data.values()]))
    adjudicated = {}
    conflict_ids = []

    for sid in all_ids:
        votes = [d[field].get(sid, "") for d in all_data.values() if d[field].get(sid)]
        if not votes:
            continue
        from collections import Counter
        top = Counter(votes).most_common(1)[0]
        # 若最高票有並列 (count < majority)
        counts = Counter(votes)
        max_count = max(counts.values())
        if sum(1 for c in counts.values() if c == max_count) > 1:
            adjudicated[sid] = "CONFLICT"
            conflict_ids.append(sid)
        else:
            adjudicated[sid] = top[0]

    return adjudicated, conflict_ids


if __name__ == "__main__":
    # ── 載入 ──────────────────────────────────────────────────────────────
    data = {}
    for ann in ANNOTATORS:
        try:
            data[ann] = load_annotations(ann)
            n_a1 = len(data[ann]["A1"])
            n_a3 = len(data[ann]["A3"])
            print(f"  {ann}: A1={n_a1} annotations, A3={n_a3} annotations")
        except FileNotFoundError:
            print(f"  {ann}: file not found — skipping")
            data[ann] = {"A1": {}, "A3": {}}

    # ── A1: 二元 κ（是否失真）────────────────────────────────────────────
    a1_data = {ann: data[ann]["A1"] for ann in ANNOTATORS}
    _print_kappa_section("Pairwise Cohen's κ — A1: is_distorted (YES/NO)", a1_data)

    # Adjudication A1
    print("\n=== Adjudication A1 (majority vote) ===")
    adj_a1, conflicts_a1 = _adjudicate(data, "A1")
    if adj_a1:
        from collections import Counter
        cnt = Counter(adj_a1.values())
        print(f"  Total adjudicated: {len(adj_a1)}")
        print(f"  YES (distorted):   {cnt.get('YES', 0):>4}  "
              f"({cnt.get('YES', 0)/len(adj_a1)*100:.1f}%)")
        print(f"  NO  (preserved):   {cnt.get('NO', 0):>4}  "
              f"({cnt.get('NO', 0)/len(adj_a1)*100:.1f}%)")
        print(f"  CONFLICT:          {len(conflicts_a1)}")
        if conflicts_a1:
            print(f"  Conflict IDs: {conflicts_a1[:10]}"
                  f"{'...' if len(conflicts_a1) > 10 else ''}")

    # ── A3: 多類別 κ（正確情感類別）──────────────────────────────────────
    a3_data = {ann: data[ann]["A3"] for ann in ANNOTATORS}
    has_a3 = any(d for d in a3_data.values())
    if has_a3:
        _print_kappa_section(
            "Pairwise Cohen's κ — A3: correct_emotion (12-class)", a3_data
        )

        # Adjudication A3
        print("\n=== Adjudication A3 (majority vote) ===")
        adj_a3, conflicts_a3 = _adjudicate(data, "A3")
        if adj_a3:
            from collections import Counter
            cnt = Counter(adj_a3.values())
            print(f"  Total adjudicated: {len(adj_a3)}")
            for emo, c in sorted(cnt.items(), key=lambda x: -x[1]):
                if emo != "CONFLICT":
                    print(f"  {emo:<15} {c:>4}  ({c/len(adj_a3)*100:.1f}%)")
            print(f"  CONFLICT:          {len(conflicts_a3)}")
    else:
        print("\n[A3] No annotations yet — skipping.")

    # ── Krippendorff's α（A1，6 人 partial overlap）─────────────────────
    print("\n=== Krippendorff's α（A1，所有 6 人，partial overlap）===")
    alpha_a1, n = krippendorff_alpha_nominal(a1_data)
    print(f"  α = {alpha_a1}  ({interpret(alpha_a1)})  n={n} valid units")

    # ── 寫出 adjudicated CSV ──────────────────────────────────────────────
    if adj_a1:
        all_ids = sorted(set(adj_a1) | (set(adj_a3) if has_a3 else set()))
        out_path = os.path.join(RESULTS_DIR, "adjudicated_final.csv")
        with open(out_path, "w", newline="") as f:
            import csv as csv_mod
            w = csv_mod.writer(f)
            w.writerow(["sample_id", "adjudicated_A1", "adjudicated_A3",
                        "votes_yes", "votes_no"])
            for sid in all_ids:
                votes_a1 = [data[ann]["A1"].get(sid, "") for ann in ANNOTATORS]
                w.writerow([
                    sid,
                    adj_a1.get(sid, ""),
                    adj_a3.get(sid, "") if has_a3 else "",
                    votes_a1.count("YES"),
                    votes_a1.count("NO"),
                ])
        print(f"\n  Adjudicated file: {out_path}")
