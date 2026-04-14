#!/usr/bin/env python3
"""
安裝驗證腳本
執行：python3 install_check.py
"""
import sys, json, csv, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
OK = "✓"
FAIL = "✗"
WARN = "⚠"

results = []

def check(label, fn):
    try:
        ok, msg = fn()
        status = OK if ok else FAIL
        results.append((ok, label, msg))
        print(f"  {status}  {label:<45s}  {msg}")
    except Exception as e:
        results.append((False, label, str(e)))
        print(f"  {FAIL}  {label:<45s}  ERROR: {e}")

print("\n" + "="*65)
print("  VAD 標注系統 — 安裝驗證")
print("="*65)

print("\n[1/4] 資料檔案")
check("master_200_with_vad.csv 存在",
      lambda: (
          (ROOT/"data"/"master_200_with_vad.csv").exists(),
          "found" if (ROOT/"data"/"master_200_with_vad.csv").exists() else "missing"
      ))

check("200 筆樣本完整",
      lambda: (
          (lambda rows: (len(rows)==200, f"{len(rows)} rows"))
          (list(csv.DictReader(open(ROOT/"data"/"master_200_with_vad.csv"))))
      ))

check("標注者作業檔 A/B/C 都存在",
      lambda: (
          all((ROOT/"results"/f"annotator_{x}"/f"task_annotator_{x}.csv").exists()
              for x in "ABC"),
          "all 3 found"
      ))

print("\n[2/4] 前端檔案")
check("web/index.html 存在",
      lambda: ((ROOT/"web"/"index.html").exists(), "found"))

check("web/data.js 存在（200 筆 JSON）",
      lambda: (
          (ROOT/"web"/"data.js").exists() and
          "SAMPLES" in (ROOT/"web"/"data.js").read_text(),
          "found with SAMPLES"
      ))

check("APPS_SCRIPT_URL 已設定（非預設值）",
      lambda: (
          (lambda url: (
              "YOUR_SCRIPT_ID" not in url,
              "configured" if "YOUR_SCRIPT_ID" not in url else f"⚠ still placeholder"
          ))(
              next(
                  (l for l in (ROOT/"web"/"index.html").read_text().splitlines()
                   if "APPS_SCRIPT_URL" in l and "const" in l),
                  ""
              )
          )
      ))

print("\n[3/4] 後端設定")
check("Code.gs 存在",
      lambda: ((ROOT/"google_apps_script"/"Code.gs").exists(), "found"))

check("SPREADSHEET_ID 已設定（非預設值）",
      lambda: (
          "YOUR_SPREADSHEET_ID_HERE" not in
          (ROOT/"google_apps_script"/"Code.gs").read_text(),
          "configured" if "YOUR_SPREADSHEET_ID_HERE" not in
          (ROOT/"google_apps_script"/"Code.gs").read_text()
          else "⚠ still placeholder"
      ))

print("\n[4/4] 測試套件")
check("pytest 可用",
      lambda: (
          subprocess.run(
              [sys.executable, "-m", "pytest", "--version"],
              capture_output=True
          ).returncode == 0,
          "available"
      ))

check("43 個測試全部通過",
      lambda: (
          (lambda r: (r.returncode==0, f"{r.stdout.decode().strip().splitlines()[-1]}"))
          (subprocess.run(
              [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
              capture_output=True, cwd=ROOT
          ))
      ))

# ── Summary ────────────────────────────────────────────────────────────
total = len(results)
passed = sum(1 for ok, _, _ in results if ok)
print(f"\n{'─'*65}")
print(f"  結果：{passed}/{total} 項通過")

needs_action = [(label, msg) for ok, label, msg in results if not ok]
if needs_action:
    print(f"\n  待處理：")
    for label, msg in needs_action:
        print(f"    {WARN}  {label}")
        print(f"         → {msg}")
else:
    print(f"\n  🎉 所有檢查通過！系統已就緒。")
    print(f"\n  標注者連結（部署後）：")
    print(f"    A: https://augustchaotw.github.io/ill-posed-AffectTrace/labeling/?annotator=A")
    print(f"    B: https://augustchaotw.github.io/ill-posed-AffectTrace/labeling/?annotator=B")
    print(f"    C: https://augustchaotw.github.io/ill-posed-AffectTrace/labeling/?annotator=C")

print()
