#!/usr/bin/env python3
"""
回收標注結果
─────────────────────────────────────────────────────────
從 Google Apps Script doGet 端點拉取三位標注者的最新資料，
寫入 results/annotator_{A,B,C}/task_annotator_{X}.csv。

執行方式：
  本地：python scripts/collect_results.py
  CI：  由 GitHub Actions 每 4 小時自動呼叫

環境變數：
  APPS_SCRIPT_URL  Apps Script Web App URL（可選，已內建預設值）
  ANNOTATORS       要同步的標注者，逗號分隔，預設 A,B,C
"""

import csv, json, os, sys, time, logging
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── 設定 ──────────────────────────────────────────────────────────────────
APPS_SCRIPT_URL = os.environ.get(
    "APPS_SCRIPT_URL",
    "https://script.google.com/macros/s/"
    "AKfycbw8kmgAVT-EAKtAxzWhayRNmeydw9uoghciJsFeZTMMFTqb-gZSdqtKxjzrEukaAALwEw/exec"
)

ANNOTATORS = [a.strip() for a in os.environ.get("ANNOTATORS", "A,B,C").split(",")]

ROOT     = Path(__file__).parent.parent
LOG_DIR  = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

FIELDNAMES = [
    "sample_id", "annotator", "userName",
    "llm_emotion", "repaired_emotion",
    "A1_is_distorted", "A2_severity", "A3_correct_emotion",
    "annotator_notes", "timestamp", "domain",
]

TIMEOUT      = 30   # 秒
MAX_RETRIES  = 3
RETRY_DELAY  = 5    # 秒

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ── 核心邏輯 ─────────────────────────────────────────────────────────────
def fetch_with_retry(annotator: str) -> dict:
    """呼叫 doGet，失敗最多重試 MAX_RETRIES 次。"""
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                APPS_SCRIPT_URL,
                params={"annotator": annotator},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise ValueError(f"API error: {data['error']}")
            return data
        except Exception as e:
            last_err = e
            log.warning(f"[{annotator}] 第 {attempt} 次嘗試失敗：{e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    raise RuntimeError(f"[{annotator}] 已重試 {MAX_RETRIES} 次，放棄。最後錯誤：{last_err}")


def save_csv(annotator: str, rows: list[dict]) -> Path:
    """將標注資料存為 CSV，回傳路徑。"""
    out_dir = ROOT / "results" / f"annotator_{annotator}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"task_annotator_{annotator}.csv"

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return out


def check_duplicates(rows: list[dict]) -> list[str]:
    """
    偵測同一 sample_id 被不同 userName 標注的情況。
    （對應前面討論的「換人標記」問題）
    """
    from collections import defaultdict
    seen: dict[str, set] = defaultdict(set)
    for r in rows:
        seen[r.get("sample_id", "")].add(r.get("userName", ""))

    conflicts = [
        f"  sample_id={sid} 被 {users} 標注"
        for sid, users in seen.items()
        if len(users) > 1
    ]
    return conflicts


def append_sync_log(report: dict):
    """在 logs/sync_history.jsonl 追加一筆同步紀錄。"""
    log_file = LOG_DIR / "sync_history.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")


# ── 主程式 ───────────────────────────────────────────────────────────────
def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    log.info(f"開始同步：{now}  標注者={ANNOTATORS}")

    total     = 0
    report    = {"timestamp": now, "annotators": {}}
    has_error = False

    for ann in ANNOTATORS:
        try:
            data = fetch_with_retry(ann)
            rows = data.get("rows", [])
            count = len(rows)

            # 偵測換人標記衝突
            conflicts = check_duplicates(rows)
            if conflicts:
                log.warning(f"[{ann}] ⚠ 發現跨用戶標注同一樣本：")
                for c in conflicts:
                    log.warning(c)

            if count == 0:
                log.info(f"[{ann}]  尚無資料（0 筆），跳過寫檔")
                report["annotators"][ann] = {"count": 0, "conflicts": []}
                continue

            out = save_csv(ann, rows)
            log.info(f"[{ann}]  {count:>3} 筆 → {out.relative_to(ROOT)}")
            total += count
            report["annotators"][ann] = {
                "count": count,
                "conflicts": conflicts,
            }

        except Exception as e:
            log.error(f"[{ann}] 同步失敗：{e}")
            report["annotators"][ann] = {"count": -1, "error": str(e)}
            has_error = True

    # 整體摘要
    log.info(f"─" * 50)
    log.info(f"合計 {total} 筆標注已同步")
    report["total"] = total

    # 追加到歷史紀錄
    append_sync_log(report)

    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
