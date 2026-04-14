# 人工標注任務 — VAD 距離失真驗證

**研究目的**：驗證 VAD 距離（ε = 0.5）是否對應人類可感知的情感失真  
**論文**：IEEE Transactions on Affective Computing — 生產級 NLP 管線中的情感完整性  
**GitHub Issue**：[#141](https://github.com/AugustChaoTW/ill-posed-AffectTrace/issues/141)

---

## 研究核心問題

> 當 LLM 輸出被結構修復管線修正後，修復操作改變的情感標籤 **是否與人類感知的情感失真一致**？

本研究驗證論文的核心設計選擇：
- **VAD 距離 > 0.5** → 修復造成了人類可感知的情感失真
- **VAD 距離 < 0.5** → 修復在人類感知閾值內，不構成失真

---

## 目錄結構

```
human_labeling_tasks/
├── README.md                          ← 本文件
├── data/
│   ├── master_200_with_vad.csv        ← 完整資料（含 VAD 距離，標注完成後才開啟）
│   ├── samples_distortion_100.csv     ← 高失真組（VAD > 0.5）參考檔
│   └── samples_safe_100.csv          ← 安全修復組（VAD < 0.5）參考檔
├── results/
│   ├── annotator_A/
│   │   └── task_annotator_A.csv      ← 標注者 A 的作業檔（請填寫此檔）
│   ├── annotator_B/
│   │   └── task_annotator_B.csv      ← 標注者 B 的作業檔
│   ├── annotator_C/
│   │   └── task_annotator_C.csv      ← 標注者 C 的作業檔
│   └── adjudicated_final.csv         ← 裁定結果（計算後自動產生）
└── scripts/
    └── compute_kappa.py              ← 計算 Cohen's κ 與多數決裁定
```

---

## 樣本集說明

### 總覽

| 組別 | 樣本數 | VAD 距離範圍 | 定義 |
|------|--------|-------------|------|
| **DISTORTION** | 100 | 0.72 – 1.60（均值 1.23） | 修復讓情感標籤跨越 ε=0.5 邊界 |
| **SAFE** | 100 | 0.12 – 0.53（均值 0.32） | 修復在 ε=0.5 以內，屬感知相近情感 |

### 情感類別對照表（VAD 空間）

| 情感 | 效價 V | 喚醒 A | 支配 D | 中文對應 |
|------|--------|--------|--------|---------|
| joy | +0.90 | +0.70 | +0.60 | 喜悅 |
| sadness | -0.80 | -0.40 | -0.50 | 悲傷 |
| anger | -0.60 | +0.80 | +0.50 | 憤怒 |
| fear | -0.70 | +0.60 | -0.40 | 恐懼 |
| surprise | +0.30 | +0.80 | +0.10 | 驚訝 |
| disgust | -0.55 | +0.30 | +0.40 | 厭惡 |
| frustration | -0.45 | +0.50 | +0.30 | 挫折感 |
| annoyance | -0.35 | +0.45 | +0.25 | 惱怒 |
| neutral | 0.00 | 0.00 | 0.00 | 中性 |
| contentment | +0.50 | +0.10 | +0.40 | 滿足 |
| excitement | +0.80 | +0.90 | +0.60 | 興奮 |
| anxiety | -0.60 | +0.70 | -0.50 | 焦慮 |

### DISTORTION 組：高失真轉換類型（各 5 筆）

| 原始情感 | 修復後情感 | VAD 距離 | 失真類型 |
|---------|-----------|---------|---------|
| joy → sadness | 喜悅 → 悲傷 | 1.60 | 極性反轉（最極端） |
| joy → anger | 喜悅 → 憤怒 | 1.59 | 極性反轉 |
| sadness → joy | 悲傷 → 喜悅 | 1.60 | 極性反轉 |
| joy → fear | 喜悅 → 恐懼 | 1.48 | 跨象限失真 |
| excitement → fear | 興奮 → 恐懼 | 1.50 | 高喚醒正負反轉 |
| neutral → anger/sadness | 中性 → 負向 | 0.80 | 過度修正 |
| frustration → joy | 挫折 → 喜悅 | 1.23 | 負向誤判為正向 |
| sadness → anger | 悲傷 → 憤怒 | 0.72 | 負向內類別誤判 |
| ... | ... | ... | ... |

### SAFE 組：低失真轉換類型（各 8–9 筆）

| 原始情感 | 修復後情感 | VAD 距離 | 說明 |
|---------|-----------|---------|------|
| frustration ↔ annoyance | 挫折 ↔ 惱怒 | 0.12 | 近義情感，最安全 |
| fear ↔ anxiety | 恐懼 ↔ 焦慮 | 0.14 | 近義情感 |
| disgust ↔ annoyance | 厭惡 ↔ 惱怒 | 0.25 | 同負向象限 |
| frustration ↔ disgust | 挫折 ↔ 厭惡 | 0.28 | 同負向象限 |
| joy ↔ contentment | 喜悅 ↔ 滿足 | 0.40 | 同正向象限 |
| anger ↔ disgust | 憤怒 ↔ 厭惡 | 0.48 | 邊界情感 |
| joy ↔ surprise | 喜悅 ↔ 驚訝 | 0.47 | 邊界情感 |

---

## 標注指引

### 每個樣本包含的資訊

| 欄位 | 說明 |
|------|------|
| `sample_id` | 樣本編號（D001–D100 失真組；S001–S100 安全組） |
| `original_text` | 亞馬遜商品評論原文（英文） |
| `llm_raw_output` | LLM 輸出的**格式錯誤**原始 JSON |
| `malformation_type` | 結構錯誤類型（8 種） |
| `stage1_output` | Stage 1 修復後（語法修復，情感未變） |
| `repaired_output` | **最終修復輸出**（情感標籤可能已改變） |
| `llm_emotion` | LLM 原始偵測到的情感 |
| `repaired_emotion` | 修復後的情感標籤 |

> ⚠️ **標注時請勿查看 `data/master_200_with_vad.csv`（含 VAD 距離）**  
> 所有標注必須在不知道 VAD 距離的情況下獨立完成。

### 需要填寫的三個欄位

**A1_is_distorted**（核心問題）  
修復後的情感標籤是否**忠實代表**原文的情感內容？
- `YES` = 修復保留了情感含義（或改變不明顯）
- `NO`  = 修復改變了情感含義（明顯可感知的失真）

**A2_severity**（失真程度，A1=YES 時填 None）
- `None`     = 無失真（A1=YES）
- `Slight`   = 輕微偏差，大方向仍正確
- `Moderate` = 明顯偏差，情感性質不同
- `Severe`   = 嚴重錯誤，情感完全相反

**A3_correct_emotion**（你認為正確的情感標籤）  
從以下選擇：joy / sadness / anger / fear / surprise / disgust / frustration / annoyance / neutral / contentment / excitement / anxiety  
若同意修復結果，請填入 `repaired_emotion` 的值。

### 標注範例

**範例 A — 失真（應填 NO）**
```
original_text:   "Absolutely love this product! Best purchase I've made this year."
llm_raw_output:  {"emotion": "joy", "polarity": "positive", "intensity": 0.86   ← 格式不完整
repaired_output: {"emotion": "sadness", "polarity": "negative", "intensity": 0.87}
```
→ A1_is_distorted: `NO` | A2_severity: `Severe` | A3_correct_emotion: `joy`  
說明：原文明顯是喜悅情感，修復卻輸出悲傷，情感完全相反。

**範例 B — 安全修復（應填 YES）**
```
original_text:   "So frustrating — the instructions are wrong and nothing fits."
llm_raw_output:  {"emotion": 'frustration', "polarity": "negative"}  ← 引號格式錯誤
repaired_output: {"emotion": "annoyance", "polarity": "negative", "intensity": 0.53}
```
→ A1_is_distorted: `YES` | A2_severity: `None` | A3_correct_emotion: `annoyance`  
說明：挫折感和惱怒在此語境幾乎同義，改變不可感知。

---

## 執行流程

### Step 1：獨立標注（預計 45–60 分鐘）

每位標注者獨立完成自己的作業檔：
- 標注者 A → `results/annotator_A/task_annotator_A.csv`
- 標注者 B → `results/annotator_B/task_annotator_B.csv`
- 標注者 C → `results/annotator_C/task_annotator_C.csv`

直接在 CSV 中填入 A1、A2、A3 欄位。

### Step 2：計算一致性

三位標注者完成後執行：
```bash
cd scripts/
python3 compute_kappa.py
```

輸出：
- 兩兩之間的 Cohen's κ
- 平均 κ（目標 ≥ 0.70）
- 多數決裁定結果
- 衝突樣本清單

### Step 3：裁定（如有衝突）

若三人各不相同（三向衝突），研究者組織討論會，逐一解決衝突樣本。

### Step 4：驗證分析

裁定完成後，用 `data/master_200_with_vad.csv` 的 VAD 距離進行驗證：

```python
# 預期結果
DISTORTION 組（VAD > 0.5）→ 標注者認為失真（A1=NO）的比例 > 80%
SAFE 組（VAD < 0.5）       → 標注者認為失真（A1=NO）的比例 < 15%
```

---

## 品質控制

| 指標 | 目標值 | 意義 |
|------|--------|------|
| Cohen's κ（A1 二元） | ≥ 0.70 | 標注者間一致性充分 |
| DISTORTION 組誤判率 | < 20% | VAD > 0.5 邊界有效 |
| SAFE 組誤判率 | < 15% | VAD < 0.5 邊界有效 |
| 三向衝突比例 | < 10% | 標注指引清晰度 |

---

## 成果用途

標注結果將：
1. 作為論文 Section 3.2（Psychophysical Validity of ε=0.5）的實驗依據
2. 計算出現在 Table X 中（Human validation of VAD threshold）
3. 回應 GitHub Issue [#141](https://github.com/AugustChaoTW/ill-posed-AffectTrace/issues/141) 和 [#143](https://github.com/AugustChaoTW/ill-posed-AffectTrace/issues/143) 的實驗要求
4. 支撐論文的核心主張：ε=0.5 是心理物理學有效的感知邊界

---

## 相關文件

- `TAC-ORIGINAL.tex` Section 3.2 — Affective Distance Metric（ε=0.5 定義）
- `_paper_trace/v2/8_limitation_reviewer_risk.yaml` — R1（ε 任意性）、R2（Layer-4 選擇）
- GitHub Issue [#141](https://github.com/AugustChaoTW/ill-posed-AffectTrace/issues/141) — 人工標注驗證
- GitHub Issue [#143](https://github.com/AugustChaoTW/ill-posed-AffectTrace/issues/143) — VAD 心理學有效性
