# 人工標注任務 — VAD 距離失真驗證

> ## ⛔ 標注工作已結束
>
> **本研究的人工標注階段已於 2026-05-28 正式結束。**  
> 論文已投稿至 IEEE Transactions on Affective Computing（Manuscript ID: TAFFC-2026-04-0456）。  
> **不再接受新的標注提交。** 此 repository 現為唯讀存檔。

---

**研究目的**：驗證 VAD 距離（ε = 0.5）是否對應人類可感知的情感失真  
**論文**：IEEE Transactions on Affective Computing  
**標題**：Affective Integrity Under Structural Constraints: Defining and Bounding Repair-Induced Distortion in Structured Sentiment Systems  
**Manuscript ID**：TAFFC-2026-04-0456  
**投稿日期**：2026-05-28

---

## 研究成果摘要

| 指標 | 結果 |
|------|------|
| 標注樣本數 | N = 400 |
| 標注者數 | 6 位（A–F） |
| 多數決失真率 | 4.5%（18/400；95% CI: [2.9%, 7.0%]） |
| Group Fleiss κ | 0.215 – 0.627（組別間） |
| 裁定結果 | `results/adjudicated_final.csv` |

完整統計分析請見 `statistics_study.md`。

---

## 資料說明

| 目錄/檔案 | 說明 |
|-----------|------|
| `results/adjudicated_final.csv` | 400 筆裁定結果（最終資料，已匿名化） |
| `results/annotator_{A–F}/` | 各標注者原始作業檔（已匿名化） |
| `scripts/compute_kappa.py` | Fleiss κ 與 Cohen's κ 計算腳本 |
| `statistics_study.md` | 完整統計分析與 Delphi 解讀 |
| `data/` | 樣本集（高失真組 DISTORTION × 100；安全組 SAFE × 100） |

---

## 引用

若引用本資料集，請使用：

```
Anonymous (2026). Human Annotation Dataset for VAD-Bounded Affective Repair Validation.
IEEE Transactions on Affective Computing Submission TAFFC-2026-04-0456.
https://github.com/DevSecOpsLab-CSIE-NPU/human-labeling-tasks
```

---

*Repository archived: 2026-05-28*
