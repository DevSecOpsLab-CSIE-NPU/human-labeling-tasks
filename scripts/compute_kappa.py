#!/usr/bin/env python3
"""
計算三位標注者之間的 Cohen's κ（kappa）一致性
用法: python3 compute_kappa.py
"""

import csv, os, math
from itertools import combinations

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "../results")
ANNOTATORS = ["annotator_A", "annotator_B", "annotator_C"]

def load_annotations(annotator):
    path = os.path.join(RESULTS_DIR, annotator, f"task_{annotator}.csv")
    with open(path) as f:
        return {r["sample_id"]: r["A1_is_distorted"].strip().upper()
                for r in csv.DictReader(f)
                if r["A1_is_distorted"].strip()}

def cohens_kappa(a1_labels, a2_labels):
    """Binary Cohen's kappa for two annotators on same sample_ids."""
    common = sorted(set(a1_labels) & set(a2_labels))
    if not common:
        return None, 0
    n = len(common)
    agree = sum(1 for sid in common if a1_labels[sid] == a2_labels[sid])
    p_o = agree / n

    # marginal probabilities
    all_vals = ["YES", "NO"]
    p_e = 0
    for v in all_vals:
        p1 = sum(1 for sid in common if a1_labels[sid] == v) / n
        p2 = sum(1 for sid in common if a2_labels[sid] == v) / n
        p_e += p1 * p2

    if p_e == 1:
        return 1.0, n
    kappa = (p_o - p_e) / (1 - p_e)
    return round(kappa, 4), n

def interpret(k):
    if k is None: return "N/A"
    if k < 0:    return "Poor (< 0)"
    if k < 0.20: return "Slight"
    if k < 0.40: return "Fair"
    if k < 0.60: return "Moderate"
    if k < 0.80: return "Substantial"
    return "Almost Perfect"

if __name__ == "__main__":
    data = {}
    for ann in ANNOTATORS:
        try:
            data[ann] = load_annotations(ann)
            print(f"  {ann}: {len(data[ann])} annotations loaded")
        except FileNotFoundError:
            print(f"  {ann}: file not found — skipping")
            data[ann] = {}

    print("\n=== Pairwise Cohen\'s κ ===")
    kappas = []
    for a1, a2 in combinations(ANNOTATORS, 2):
        if not data[a1] or not data[a2]:
            continue
        k, n = cohens_kappa(data[a1], data[a2])
        kappas.append(k)
        print(f"  {a1} vs {a2}: κ = {k}  ({interpret(k)})  n={n}")

    if len(kappas) == 3:
        avg_k = sum(kappas) / len(kappas)
        print(f"\n  Average κ: {avg_k:.4f}  ({interpret(avg_k)})")
        if avg_k >= 0.70:
            print("  ✓ TARGET MET: κ ≥ 0.70")
        else:
            print(f"  ✗ Below target (0.70). Gap: {0.70 - avg_k:.4f}")

    # Majority-vote adjudication
    print("\n=== Adjudication (majority vote) ===")
    all_ids = sorted(set().union(*[set(d.keys()) for d in data.values()]))
    adjudicated = {}
    conflict_ids = []
    for sid in all_ids:
        votes = [data[ann].get(sid, "") for ann in ANNOTATORS if data[ann].get(sid)]
        yes = votes.count("YES")
        no  = votes.count("NO")
        if yes > no:
            adjudicated[sid] = "YES"
        elif no > yes:
            adjudicated[sid] = "NO"
        else:
            adjudicated[sid] = "CONFLICT"
            conflict_ids.append(sid)

    yes_total = sum(1 for v in adjudicated.values() if v == "YES")
    no_total  = sum(1 for v in adjudicated.values() if v == "NO")
    print(f"  Total adjudicated: {len(adjudicated)}")
    print(f"  YES (distorted):   {yes_total} ({yes_total/len(adjudicated)*100:.1f}%)")
    print(f"  NO  (preserved):   {no_total}  ({no_total/len(adjudicated)*100:.1f}%)")
    print(f"  CONFLICT:          {len(conflict_ids)}")
    if conflict_ids:
        print(f"  Conflict IDs: {conflict_ids[:10]}{'...' if len(conflict_ids)>10 else ''}")

    # Write adjudicated output
    out_path = os.path.join(RESULTS_DIR, "adjudicated_final.csv")
    with open(out_path, "w", newline="") as f:
        import csv as csv_mod
        w = csv_mod.writer(f)
        w.writerow(["sample_id", "adjudicated_A1", "votes_yes", "votes_no"])
        for sid in all_ids:
            votes = [data[ann].get(sid, "") for ann in ANNOTATORS]
            w.writerow([sid, adjudicated.get(sid,""), votes.count("YES"), votes.count("NO")])
    print(f"\n  Adjudicated file: {out_path}")
