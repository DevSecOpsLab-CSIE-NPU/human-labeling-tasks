#!/usr/bin/env python3
"""
生成 6 位標注者的 task CSV 檔案（Rotating Overlap 設計）

Quarter 定義（依 sample_id 前綴與編號）：
  Q1: D001-D050 + S001-S050
  Q2: D051-D100 + S051-S100
  Q3: D101-D150 + S101-S150
  Q4: D151-D200 + S151-S200

標注者分配：
  A: Q1+Q2   B: Q1+Q3   C: Q1+Q4
  D: Q2+Q3   E: Q2+Q4   F: Q3+Q4

執行：python scripts/generate_task_files.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER = ROOT / "data" / "master_400_with_vad.csv"

QUARTER_ASSIGNMENT = {
    "A": ["Q1", "Q2"],
    "B": ["Q1", "Q3"],
    "C": ["Q1", "Q4"],
    "D": ["Q2", "Q3"],
    "E": ["Q2", "Q4"],
    "F": ["Q3", "Q4"],
}

FIELDNAMES = [
    "sample_id", "annotator", "userName",
    "llm_emotion", "repaired_emotion",
    "A1_is_distorted", "A2_severity", "A3_correct_emotion",
    "annotator_notes", "timestamp", "domain",
]


def get_quarter(sample_id: str) -> str:
    """回傳 sample_id 所屬的 Quarter（Q1-Q4），若不符合則回傳 None。"""
    num = int(sample_id[1:])   # D001 → 1, S050 → 50
    if 1 <= num <= 50:
        return "Q1"
    elif 51 <= num <= 100:
        return "Q2"
    elif 101 <= num <= 150:
        return "Q3"
    elif 151 <= num <= 200:
        return "Q4"
    return None


def load_master() -> list[dict]:
    with open(MASTER, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_task(annotator: str, rows: list[dict]):
    out_dir = ROOT / "results" / f"annotator_{annotator}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"task_annotator_{annotator}.csv"

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  annotator_{annotator}: {len(rows)} rows → {out.relative_to(ROOT)}")


def main():
    print("=== Generating task files (Rotating Overlap, 6 annotators) ===\n")
    master = load_master()

    # 按 sample_id 建索引
    master_by_id = {r["sample_id"]: r for r in master}

    for ann, quarters in QUARTER_ASSIGNMENT.items():
        # 篩選屬於該標注者負責的 quarter
        task_rows = []
        for row in master:
            q = get_quarter(row["sample_id"])
            if q in quarters:
                task_row = {
                    "sample_id":        row["sample_id"],
                    "annotator":        ann,
                    "userName":         "",
                    "llm_emotion":      row["llm_emotion"],
                    "repaired_emotion": row["repaired_emotion"],
                    "A1_is_distorted":  "",
                    "A2_severity":      "",
                    "A3_correct_emotion": "",
                    "annotator_notes":  "",
                    "timestamp":        "",
                    "domain":           row["domain"],
                }
                task_rows.append(task_row)

        write_task(ann, task_rows)

    print(f"\n完成！共產生 6 份作業檔，每份 200 筆。")
    print("Quarter 分配：")
    for ann, quarters in QUARTER_ASSIGNMENT.items():
        print(f"  {ann}: {'+'.join(quarters)}")


if __name__ == "__main__":
    main()
