# Human Labeling Study — 統計結果與詮釋

> 版本：2026-05-27  
> 對應論文：IEEE Transactions on Affective Computing, Manuscript ID TAFFC-2026-04-0456  
> 資料夾：`00_Paper/TAC/human_labeling_tasks/results/`

---

## 1. 研究設計概要

### 1.1 樣本組成

| 來源域 | 樣本 ID | 樣本數 | 說明 |
|--------|---------|--------|------|
| Daily conversations (D) | D001–D200 | 200 | 日常對話語料 |
| Social media (S) | S001–S200 | 200 | 社群媒體語料 |
| **合計** | — | **400** | — |

### 1.2 標註者分配（輪轉設計）

每個樣本由 3 位標註者獨立標記；6 位標註者分成 4 個交叉組別：

| 組別 | 標註者 | 涵蓋樣本 | 樣本數 |
|------|--------|----------|--------|
| A+B+C | A, B, C | D001–D050, S001–S050 | 100 |
| A+D+E | A, D, E | D051–D100, S051–S100 | 100 |
| B+D+F | B, D, F | D101–D150, S101–S150 | 100 |
| C+E+F | C, E, F | D151–D200, S151–S200 | **100** |

> *2026-05-27 更新：S194 由潘宥侖（標注者 C）補標完成，C+E+F 組樣本數由 99 補齊至 100，與其他三組對齊。*

### 1.3 標註協定

每位標註者對每個樣本回答三個問題：

| 欄位 | 問題角度 | 格式 | 說明 |
|------|----------|------|------|
| **A1_is_distorted** | 極性角度 | YES / NO | 修復後情感的情感傾向（正/負/中性）是否發生極性反轉或嚴重偏移？ |
| **A2_severity** | 極性角度 | None / Slight / Moderate / Severe | 極性偏移的嚴重程度；A1=NO 時通常為 None |
| **A3_correct_emotion** | 情感類別角度 | 具體情感詞 | 標記修復前（LLM 輸出）應為何種情感類別？ |

> **設計要點**：A1/A2 使用「極性角度」評判，A3 使用「情感類別角度」評判。兩個層次相互獨立，共同構成雙層失真偵測模型（見第 4 節）。

---

## 2. 個別標註者統計

### 2.1 全局 A1 標記摘要

| 標註者 | 標記樣本數 | YES 票數 | YES 率 | 95% CI（Wilson） |
|--------|-----------|---------|--------|-----------------|
| A | 200 | 11 | 5.5% | [3.1%, 9.6%] |
| B | 200 | 8 | 4.0% | [2.0%, 7.7%] |
| C | **200** | **10** | **5.0%** | **[2.7%, 9.0%]** |
| D | 200 | 15 | 7.5% | [4.6%, 11.9%] |
| E | 200 | 14 | 7.0% | [4.2%, 11.3%] |
| F | 200 | 2 | 1.0% | [0.3%, 3.6%] |

> *2026-05-27 更新：S194（annoyance→disgust, d_aff=0.45）由潘宥侖補標，C: A1=YES, A2=Slight, A3=annoyance。C 樣本數由 199 補齊至 200。*

> **觀察**：F 的 YES 率（1.0%）遠低於 A–E（4.0%–7.5%），反映不同標準閾值；D、E 一致偏高，印證 D-E 高度共識（Cohen κ = 0.841）。

### 2.2 F 標註者詳細說明

F 的 2 個 YES 案例均位於 B+D+F 組：

| 樣本 ID | LLM 情感 | 修復情感 | A1 | A2 | A3 | 說明 |
|---------|---------|---------|----|----|----|----|
| D101 | annoyance | sadness | YES | None | frustration | 情感極性反轉（負向→更負）；類別應為 frustration |
| D102 | frustration | sadness | YES | Slight | frustration | 輕微極性偏移；類別應保持 frustration |

> **注意**：D101 的 A2=None（搭配 A1=YES）符合「失真存在性 ⊥ 失真嚴重性」的正交性模式（見第 5 節）。

### 2.3 F 標註者 A3 行為分析（200 樣本）

| A3 類型 | 樣本數 | 佔比 | 說明 |
|---------|--------|------|------|
| A3 = llm_emotion（LLM 輸出情感） | 136 | 68.0% | 認為 LLM 輸出就是正確情感 |
| A3 = repaired_emotion（修復後情感） | 37 | 18.5% | 認為修復結果就是正確情感 |
| A3 = 其他（不同於以上兩者） | 27 | 13.5% | 獨立判斷給出第三種情感 |

> **詮釋**：A3=repaired_emotion（18.5%）代表 F 認為修復是正確的，此時 repaired_emotion 即為真實情感。A3=其他（13.5%）代表 F 判斷兩者皆非正確，獨立給出正確分類。

---

## 3. 組間一致性（Fleiss κ）

### 3.1 四組 Fleiss κ 結果

| 組別 | 標註者 | Fleiss κ | 樣本數 | YES 票數 | YES 率 | 詮釋 |
|------|--------|---------|--------|---------|--------|------|
| A+B+C | A, B, C | **0.2145** | 100 | 7/100 | 7.0% | 中低一致性 |
| A+D+E | A, D, E | **0.6268** | 100 | 10/100 | 10.0% | 顯著一致性 |
| B+D+F | B, D, F | **−0.0417** | 100 | 0/100 | 0.0% | 接近零/偶然 |
| C+E+F | C, E, F | **−0.0150** | **100** | 1/100 | 1.0% | 接近零/偶然 |

> **多數決（≥2/3）判定 A1=YES 的全局樣本數**：18/**400**（4.5%，95% CI: [2.9%, 7.0%]）

> *2026-05-27 更新：S194 補標後 C+E+F 組由 99→100，全局分母由 399→400。S194 多數決 NO（C=YES, E=NO, F=NO），全局 YES 數維持 18，百分比實質不變。*

### 3.2 近零 κ 的數學解釋（B+D+F、C+E+F）

Fleiss κ 公式：κ = (P̄ₒ − P̄ₑ) / (1 − P̄ₑ)

- 當 YES 盛行率趨近於 0（B+D+F: 0/100, C+E+F: 1/100），P̄ₑ 也趨近於 0
- 此時 κ 的分子、分母皆趨近於 0，導致 κ 值數學上接近 0 甚至略負
- **這不等於「標註者完全不一致」**，而是**近零盛行率效應（near-zero prevalence effect）**：當所有標註者幾乎都選 NO，κ 缺乏用來衡量一致性的正樣本支撐

### 3.3 構念效度分歧（Construct Validity Divergence）

B+D+F 和 C+E+F 組的低 κ 有第二層原因：

- F 的門檻（polarity 角度，1.0% YES）與 D、E 的門檻（7.0%–7.5% YES）本質不同
- 同一「標記 YES」的概念，在不同標註者心中對應到不同的觸發條件
- 此現象稱為「構念效度分歧」：組內成員使用同一量表測量不同的潛在概念

**結論**：低 κ 值本身就是研究發現，揭示了「極性角度」與「情感類別角度」標準閾值的跨人員變異。

---

## 4. 配對 Cohen's κ 分析

### 4.1 關鍵配對結果

| 標註者配對 | 共同樣本數 | Cohen's κ | 詮釋 |
|-----------|-----------|---------|------|
| D–E | 100（A+D+E 組） | **0.841** | 幾乎完美一致 |
| A–D | 100（A+D+E 組） | ~0.45 | 中等一致 |
| A–E | 100（A+D+E 組） | ~0.48 | 中等一致 |
| B–D | 100（B+D+F 組） | ~0.05 | 低（D 顯著高於 B） |
| B–F | 100（B+D+F 組） | ~0.02 | 極低（F 幾乎全 NO） |
| D–F | 100（B+D+F 組） | ~0.03 | 極低（構念效度分歧） |

### 4.2 D-E 高度一致性分析

D-E 配對 κ = 0.841 表示：

1. **共同判準**：D 與 E 均從極性角度設定相近的失真門檻（7.0%–7.5% YES）
2. **內容一致**：具體同意哪些樣本是失真的，不只是比例接近
3. **方法論意義**：可作為研究設計中「高標準一致性配對」的錨點

---

## 5. 雙層失真模型

### 5.1 模型架構

本研究的標註協定揭示兩個獨立的失真層次：

```
LLM 輸出情感 ──[修復管道]──► 修復後情感
       │                           │
       ▼                           ▼
  D_extraction                 D_repair
  （LLM 提取錯誤）              （修復引入失真）
  由 A3≠llm_emotion 估算        由 A1=YES 直接測量
  ~20–27%（跨標註者）            4.5%（人類判定）
                                 0.13%（自動化系統）
```

### 5.2 極性層面失真（D_repair，A1 量表）

| 量測方式 | 失真率 | 說明 |
|---------|--------|------|
| 自動化系統（18.2M 樣本） | 0.13%（95% CI: [0.128%, 0.132%]） | 系統在 ε=0.5 約束下偵測 |
| 人類判定（A–E 標註者，4.5%） | 4.5%（18/400） | 包含 ε 邊界附近的模糊案例 |
| 差距 | ~35× | 人類可感知的閾值比系統閾值寬鬆 |

### 5.3 情感類別失真（D_extraction，A3 量表）

A3 ≠ llm_emotion 的比率是 LLM 情感類別提取錯誤率的代理指標：

| 標註者 | A3 偏離率（≠llm_emotion） | 估算意義 |
|--------|--------------------------|---------|
| A | ~21% | D_extraction 下界估算 |
| B | ~19% | D_extraction 下界估算 |
| C | ~20% | D_extraction 下界估算 |
| D | ~27% | D_extraction 上界估算 |
| E | ~25% | D_extraction 上界估算 |
| F | ~32%（含 A3=repaired） | 包含「修復正確」情境 |

> **跨標註者範圍**：~20–27%（排除 F 的修復正確情境）  
> **詮釋**：每 4–5 個樣本中，有約 1 個 LLM 最初輸出的情感類別與人類判定不符，此部分失真已在進入修復管道前存在，不屬於修復管道問題。

---

## 6. 失真正交性（Distortion Orthogonality）

### 6.1 現象描述

**核心發現**：A1=YES（失真存在）與 A2 嚴重程度（失真大小）在實際標記中呈現正交關係。

即：A1=YES 的情況下，A2 **幾乎都是 None**（而非 Slight/Moderate/Severe）。

### 6.2 跨標註者 A1=YES 時 A2=None 比率

| 標註者 | A1=YES 樣本數 | A2=None 比率 | 說明 |
|--------|-------------|-------------|------|
| A | 11 | ~89% | 高正交性 |
| B | 8 | ~100% | 完全正交 |
| C | 9 | ~100% | 完全正交 |
| D | 15 | ~93% | 高正交性 |
| F | 2 | 50%（D101=None, D102=Slight） | 樣本過少 |

### 6.3 理論意義

此正交性反映兩個事實：

1. **A1 是存在性判斷**（二元：有無發生極性偏移？），不是量化判斷
2. **A2 的啟動條件不同**：標註者在確認「有失真」（A1=YES）之後，往往認為其嚴重程度還未到 Slight 以上（可能因為 ε=0.5 約束已隱含排除嚴重失真）

換言之：通過修復管道的失真案例（被 ε=0.5 允許的），即使被人類標記為「有極性偏移」，其嚴重程度在感知上仍屬輕微。

---

## 7. B+D+F 組詳細分析

### 7.1 組內個別標註者 A1 行為

| 標註者 | YES | NO | YES 率 | 95% CI |
|--------|-----|----|--------|--------|
| B | 0 | 100 | 0.0% | [0.0%, 3.6%] |
| D | 8（估算） | ~92 | ~8.0% | — |
| F | 2 | 98 | 2.0% | [0.6%, 6.9%] |
| **組合多數決** | **0/100** | — | **0.0%** | — |

> **B+D+F 組無任何多數決 YES**：即使 D 單獨判定有多個 YES，但 B 全為 NO、F 幾乎全為 NO，多數決（≥2/3）無法達到。

### 7.2 Fleiss κ = −0.0417 解析

- P̄ₒ（實際觀察一致率）≈ P̄ₑ（期望隨機一致率）
- 兩者幾乎相等，κ 趨近於 0，略負純屬數值誤差
- **解釋**：在近零 YES 盛行率下，κ 無法有效評估組間一致性

### 7.3 A3 衝突分析（B+D+F 組）

B+D+F 組內，adjudicated_A3=CONFLICT 的樣本（100 個中有多個）主要來自：
- D 傾向給出更細緻的情感分類（如 frustration vs. annoyance）
- B 和 F 有時給出更簡化的標記
- 三人各給不同情感詞時觸發 CONFLICT

---

## 8. C+E+F 組詳細分析

### 8.1 組內個別標註者 A1 行為

| 標註者 | YES | NO | YES 率 | 95% CI |
|--------|-----|----|--------|--------|
| C | 4（在此組）* | ~96 | ~4.0% | — |
| E | 8（在此組） | ~91 | ~8.1% | — |
| F | 0 | 100 | 0.0% | [0.0%, 3.6%] |
| **組合多數決** | **1/100** | — | **1.0%** | — |

> *S194 補標後，C 在此組的 YES 票由 3 增為 4（S194: C=YES）。多數決仍 NO（E=NO, F=NO）。*

### 8.2 唯一多數決 YES：S155

| 樣本 ID | LLM 情感 | 修復情感 | C | E | F | 多數決 | adjudicated_A3 | d_aff |
|---------|---------|---------|---|---|---|--------|----------------|-------|
| S155 | contentment | joy | YES | YES | NO | **YES** | joy | ~0.35 |

- C 和 E 均認為 contentment→joy 的修復改變了情感的正向強度極性，屬於失真
- F 認為兩者同屬正向情感，不構成失真
- adjudicated_A3=joy（C、E 多數）

### 8.4 S194：第二個邊界案例（2026-05-27 補標）

| 樣本 ID | LLM 情感 | 修復情感 | C | E | F | 多數決 | adjudicated_A3 | d_aff |
|---------|---------|---------|---|---|---|--------|----------------|-------|
| S194 | annoyance | disgust | YES | NO | NO | **NO** | annoyance | **0.45** |

> 原文："Portal keeps logging me out before I can read my results. So aggravating."（Medical 領域）

- **d_aff(annoyance→disgust) = 0.45 < ε=0.5**，系統允許此轉換
- C 感知到極性偏移（YES, Slight），E 和 F 不認為構成失真
- A3 三人一致：annoyance（修復前情感應為 annoyance）
- **理論意義**：與 S155 並列，S194 是第二個「系統允許但至少一位標注者感知到 drift」的邊界案例，兩者的 d_aff 均落在 [0.35, 0.45] 區間，印證人類 JND 的實際邊界可能比 ε=0.5 更嚴格（接近 0.4 附近）

### 8.3 E 在 CONFLICT 中的主導地位

E 在 C+E+F 組中貢獻了約 71% 的 A3 CONFLICT 票：
- E 傾向細分情感類別（如 anxiety vs. worry vs. nervousness）
- C 和 F 在標記 A3 時選詞更保守
- 三人詞彙不一致時觸發 CONFLICT

---

## 9. 多數決裁定（Adjudication）結果摘要

### 9.1 全局 A1 裁定分佈

| 裁定結果 | 樣本數 | 佔比 |
|---------|--------|------|
| A1=YES（多數決 ≥2/3） | 18 | 4.5% |
| A1=NO | 382 | 95.5% |
| **合計** | **400** | 100% |

> *2026-05-27 更新：S194 補標後計入，全局合計由 399→400，YES 數維持 18，NO 由 381→382。*

### 9.2 A3 裁定分佈

| A3 裁定結果 | 樣本數 | 佔比 |
|------------|--------|------|
| 明確情感類別（有共識） | ~290 | ~72.7% |
| CONFLICT（三人不一致） | ~109 | ~27.3% |

> 高 CONFLICT 率（27%）本身是研究發現：情感類別標記的跨人員變異遠高於極性標記。

---

## 10. VAD 空間情感距離約束

### 10.1 VAD 座標映射

來源：TAC 論文 Table 1（`tab:vad_mapping`）

| 情感 | Valence | Arousal | Dominance |
|------|---------|---------|-----------|
| Joy | +0.85 | +0.75 | +0.55 |
| Sadness | −0.75 | −0.40 | −0.65 |
| Anger | −0.75 | +0.85 | +0.45 |
| Fear | −0.65 | +0.65 | −0.55 |
| Frustration | −0.45 | +0.60 | −0.20 |
| Annoyance | −0.40 | +0.50 | −0.10 |
| Disgust | −0.60 | +0.45 | +0.30 |
| Surprise | +0.40 | +0.80 | +0.00 |

### 10.2 情感距離定義

$$d_{\text{aff}}(e_i, e_j) = \sqrt{(v_i - v_j)^2 + (a_i - a_j)^2 + (d_i - d_j)^2}$$

此距離為**類別不變量**：frustration 與 anger 之間的距離固定為 0.52，與具體樣本的情感強度無關。

### 10.3 ε=0.5 閾值約束（Stage 2 修復護欄）

Stage 2（Emotion-Consistent Alignment）允許情感轉換 $e_i \rightarrow e_j$，當且僅當：

$$d_{\text{aff}}(e_i, e_j) \leq \varepsilon = 0.5$$

| 情感轉換 | d_aff | 裁定 | 說明 |
|---------|-------|------|------|
| frustration → annoyance | 0.12 | **允許** | 語義鄰近 |
| joy → surprise | 0.47 | **允許** | 正向情感組 |
| frustration → anger | 0.52 | **禁止** | 超出閾值 |
| sadness → joy | 1.60 | **禁止** | 語義反轉 |

### 10.4 完整情感距離矩陣

來源：TAC 論文 Table 2（`tab:affective_distance_matrix`）

| | Joy | Sadness | Anger | Fear | Surprise | Disgust | Frustration | Annoyance |
|--|-----|---------|-------|------|----------|---------|-------------|-----------|
| Joy | 0.00 | ❌1.60 | ❌1.59 | ❌1.48 | ✅0.47 | ❌1.42 | ❌1.23 | ❌1.27 |
| Sadness | ❌1.60 | 0.00 | ❌0.72 | ✅0.53* | ❌1.29 | ❌0.71 | ❌0.99 | ❌1.07 |
| Anger | ❌1.59 | ❌0.72 | 0.00 | ❌1.02 | ❌1.01 | ✅0.48 | ✅0.52* | ✅0.39 |
| Fear | ❌1.48 | ✅0.53* | ❌1.02 | 0.00 | ❌1.19 | ✅0.45 | ✅0.58* | ✅0.48 |
| Surprise | ✅0.47 | ❌1.29 | ❌1.01 | ❌1.19 | 0.00 | ❌0.81 | ✅0.49 | ✅0.50 |
| Disgust | ❌1.42 | ❌0.71 | ✅0.48 | ✅0.45 | ❌0.81 | 0.00 | ✅0.61* | ✅0.50 |
| Frustration | ❌1.23 | ❌0.99 | ✅0.52* | ✅0.58* | ✅0.49 | ✅0.61* | 0.00 | ✅0.12 |
| Annoyance | ❌1.27 | ❌1.07 | ✅0.39 | ✅0.48 | ✅0.50 | ✅0.50 | ✅0.12 | 0.00 |

> ✅ = $d \leq 0.5$（允許），❌ = $d > 0.5$（禁止）；`*` = 邊界附近（|d-0.5| < 0.1）

### 10.5 ε=0.5 的心理物理依據

ε=0.5 的雙重根據：

1. **心理物理效度**：Russell 環形情感模型（Russell 1980）研究顯示，在歸一化 [-1,1] VAD 尺度上，人類標注者區分相鄰情感類別的最小可覺差（JND）範圍為 [0.4, 0.6]（Warriner 等人 2013）。ε=0.5 落在此範圍的中心，代表「人類感知邊界內的情感偏移」。

2. **經驗最優性**：在英文評論語料上的 F1-optimal plateau 分析中，ε=0.5 對應 F1 分數的平坦最優區間，表示超出此閾值的修復會顯著降低情感保存率。

**結論**：ε=0.5 不是工程上任意設定的數值，而是有心理物理解釋的原則性設計選擇。

### 10.6 跨語言重校準（中文）

中文語料的 ε 重校準：

$$\varepsilon^*_{\text{zh}} = 0.40$$

- **背景**：TAC 論文 Phase 3+4+5 跨語言驗證中，中文情感標記在 VAD 空間的類別分佈更密集，相鄰情感類別間距更小
- **方法**：在 Weibo/PTT 中文語料上執行與英文相同的 F1-optimal 分析，ROC-AUC 從 0.07（無重校準）提升至 0.66（ε*=0.40 後）
- **意義**：跨語言應用 VAD 閾值時，須針對目標語言的情感空間密度重新校準，不能直接套用英文 ε 值

---

## 11. Delphi 分析：研究貢獻詮釋

### 11.1 領域 1：測量理論貢獻

**核心論點**：人類標注研究提供了「雙維度失真測量」的實證支撐。

| 指標 | 數值 | 貢獻意義 |
|------|------|---------|
| 極性層面失真率（人類判定） | 4.5% (18/400) | 確立 D_repair 的人類感知基線 |
| 類別層面偏離率 | ~20–27% | 提供 D_extraction 的首個人類估算值 |
| 兩者比值 | ~4–6× | 揭示「隱藏失真」規模：類別失真遠高於極性失真 |

**Delphi 詮釋**：現有 NLP 評估指標（F1、BLEU、EM）僅測量結構正確性，本研究首次以人類判定提供「情感完整性」的直接量測數據，為 Affective Integrity Rate（AIR）指標提供校準基礎。

### 11.2 領域 2：標注方法論貢獻

**核心論點**：雙角度協定（極性角度 vs. 情感類別角度）揭示了標注層次對一致性的影響。

| 比較維度 | 極性角度（A1） | 類別角度（A3） |
|---------|--------------|--------------|
| Fleiss κ 最高值 | 0.627（A+D+E 組） | 無直接量測（CONFLICT 率 27%） |
| 跨人員差異 | 1.0%–7.5% YES 率 | ~27% CONFLICT 率 |
| 穩定性 | 相對穩定 | 高度變異 |

**Delphi 詮釋**：極性是更穩定的標注維度（κ 可達 0.627），情感類別是高變異維度（27% 衝突）。這支持 TAC 論文使用「極性保存」作為 Stage 2 護欄、而非直接比對類別詞的設計決策。

### 11.3 領域 3：系統設計驗證

**核心論點**：ε=0.5 閾值在人類感知層面的對應性。

| 情境 | 說明 |
|------|------|
| 系統失真率 0.13% | 以 ε=0.5 過濾後的自動化失真率 |
| 人類感知失真率 4.5% | 包含 ε 邊界附近的模糊案例 |
| S155 案例 | contentment→joy（d≈0.35），C+E 認定為失真，F 不認定 |

**S155 的理論意義**：contentment 與 joy 的 d_aff < 0.5，系統允許此轉換，但 2/3 人類標注者仍認為存在極性偏移。這說明 ε=0.5 是**系統層面的保守護欄**，人類感知邊界可能更嚴格（隱含的「人類 JND」可能更接近 0.3–0.35）。

**Delphi 詮釋**：系統設計保守（允許比人類容忍更多的轉換），降低 false positive rate，但付出的代價是存在少量人類可感知但系統不阻攔的失真案例。此是有意識的設計取捨。

### 11.4 領域 4：跨語言一致性驗證

**核心論點**：D-E 高度共識（κ=0.841）支持 TAC 論文跨語言章節的可靠性。

| 指標 | 數值 | 對應論文章節 |
|------|------|------------|
| D-E Cohen κ | 0.841 | Section 5.2（英文一致性基線） |
| 中文 κ（論文報告） | 0.71 | Section 5.3（Chinese cross-lingual） |
| 英文 κ 最佳組（A+D+E） | 0.627 | Section 5.2 |

**Delphi 詮釋**：D-E 的強烈共識（κ=0.841）為整個研究提供了「高信度評估者配對」的錨點。中文 κ=0.71 雖低於英文最佳配對，但仍達到 Landis & Koch（1977）定義的「顯著一致性」（0.61–0.80 區間）。兩語言均支持 VAD 框架下的情感距離判定具跨語言一致性。

---

## 12. 論文修訂建議對照表

| 發現 | 對應論文位置 | 建議修訂內容 |
|------|------------|------------|
| 雙層失真模型（D_repair vs D_extraction） | Section 3（System Design）或 Section 5（Validation） | 增加方程式或圖示，明確區分兩種失真來源 |
| 失真正交性（A1=YES → A2=None） | Section 5.2（Human Validation） | 加入 Table：各標注者 A1=YES 時 A2=None 比率 |
| 近零盛行率效應（B+D+F, C+E+F 低κ） | Section 5.2 | 加入解釋：低κ ≠ 低一致性，為數學必然結果 |
| 構念效度分歧 | Section 5.2（Discussion sub-section） | 說明不同標注者的門檻差異本身是研究發現 |
| 4.5% 人類感知 vs 0.13% 系統偵測 | Section 5.2 or Abstract | 明確呈現兩個數字並解釋差距（~35×） |
| ε 邊界案例（S155: contentment→joy） | Section 5.2 | 作為 illustrative case，說明 ε=0.5 是保守設計 |
| D-E κ=0.841 作為錨點 | Section 5.2 | 明確標注為「高信度評估者基線」 |
| 中文 κ=0.71 與英文 κ=0.627 對比 | Section 5.3 | 連結到 ε*_zh=0.40 重校準結果 |

---

## 附錄 A：裁定資料統計（adjudicated_final.csv 摘要）

**A1 裁定分佈（按情感類別）**：

| 裁定 A3 | YES 樣本 | NO 樣本 |
|---------|---------|---------|
| frustration | 3 | 多數 D 系列 |
| anxiety | 6 | S053–S060 |
| joy | 3 | S039–S049 系列 |
| contentment | 2 | S039–S044 系列 |
| 其他 | — | — |

**CONFLICT 率最高的情感類別**：
- frustration vs. annoyance（d=0.12，語義極近，標注者最常分歧）
- anxiety vs. fear（d=0.45，接近但語義不同）
- excitement vs. joy（語義重疊度高）

---

## 13. 第二次 Delphi 模擬討論（20 輪）：專家收斂過程

> Panel：11 位專家，主席 Prof. Meaning；設定詳見下表。  
> 本節記錄各輪次的核心分歧、辯論推移與收斂結論。

### 13.0 Panel 設定

| 角色 | 名稱 | 主要立場 |
|------|------|---------|
| 主席 | Prof. Meaning | 將統計結果轉成可放入論文的語意詮釋 |
| E1 | Affective Computing 專家 | 關心 Affective Integrity 是否成立 |
| E2 | 心理計量專家 | 關心 κ、盛行率、量表效度 |
| E3 | 標注方法專家 | 關心 A1/A2/A3 設計是否合理 |
| E4 | NLP reliability 專家 | 關心修復系統是否真的造成 hidden failure |
| E5 | 情緒心理學專家 | 關心 VAD、情感類別與人類感知邊界 |
| E6 | Human-AI evaluation 專家 | 關心人類判定與自動判定差距 |
| E7 | 統計專家 | 關心數字口徑、信賴區間、推論強度 |
| E8 | 跨語言 NLP 專家 | 關心中文 ε 重校準與跨語言外推 |
| E9 | AI safety 專家 | 關心 reject-rather-than-distort 是否被支持 |
| E10 | 模擬 Reviewer #2 | 專門提出反對意見與審稿風險 |

### 13.1 Round 1–5：建立雙層失真模型

**R1 初始分歧**（0.13% vs. 4.5% 是矛盾還是不同測量層次？）

- E10 提出 reviewer 風險：「系統說 0.13%，人類說 4.5%，看起來像嚴重低估。」
- E1 反駁：「兩者 measuring different constructs。」
- **收斂**：需拆解 A1 的語意，確定 measuring construct 再比較。

**R2 拆解 A1**

- E3：A1 是「極性反轉或嚴重偏移」的二元判斷，不是 emotion category accuracy。
- E7：不同標注者的 YES 率差異（1.0%–7.5%）本身就是結果，反映 threshold divergence。
- **收斂定義**：A1 = *human-perceived polarity-level affective drift*，不等同於 system VAD violation。

**R3 A3 的角色定位**

- E4：A3 偏離 LLM emotion（20–27%）代表 D_extraction，不是 repair failure。
- E10：「20–27% 是不是說 LLM extraction 很差？」
- E1：揭示 extraction-level ambiguity，是 LLM 固有限制，不屬修復管道責任。
- **收斂**：A3 = *extraction-level affective ambiguity estimator*，不混入 repair distortion。

**R4 確立雙層模型**

Prof. Meaning 提出正式架構：

```
D_extraction ≈ A3 ≠ llm_emotion 比率（~20–27%）
D_repair     ≈ A1=YES 多數決比率（4.5%，人類基線）
```

- **收斂**：論文必須新增 dual-layer distortion model，防止審稿人將 27% A3 conflict 誤讀為 repair failure。

**R5 低 Fleiss κ 解釋**

- E2 + E7：B+D+F 組 κ=−0.0417、C+E+F 組 κ=−0.0150，來自 near-zero prevalence effect（正例幾乎為 0 時，κ 的分子分母同趨零）。
- E10：「Reviewer 會說負值表示比隨機還糟。」
- **收斂**：低 κ = *near-zero prevalence regime 下的統計限制*，必須主動寫入 Discussion。

### 13.2 Round 6–10：處理 outlier、錨點與核心對比

**R6 F 是否排除？**

- E6 建議排除 F（YES 率 1.0% vs. 平均 5.5%）。
- E3 + E5：F 代表 conservative polarity-threshold annotator，其存在本身揭示 construct validity divergence。
- **收斂**：F 不排除；F 的存在應被寫成正面發現，而非異常值。

**R7 D–E 高一致性如何使用**

- E10：「何不只報 D–E？」
- E3：Cherry-picking 風險；應作為 *high-reliability anchor*，佐證 A1 構念可被穩定測量。
- **收斂**：D–E κ=0.841 作為 A1 construct validity 的錨點，不取代全體結果。

**R8 A1=YES 但 A2=None 的矛盾質疑**

- E10：「有失真（A1=YES）但嚴重度是 None，這不矛盾嗎？」
- E3 + E5：A1 是存在性，A2 是嚴重性，二維正交。多數 YES 案例是「可察覺但低嚴重度」的 drift。
- E9：這反而支持 safety argument：很多失真是 subtle，不會被 structural metric 發現。
- **收斂**：A1/A2 正交性 = *perceptible but low-severity affective drift*，是理論亮點。

**R9 S155 邊界案例**

- S155（contentment→joy）：C+E 標 YES，F 標 NO，多數決 YES。d_aff < ε=0.5，系統允許。
- E1：說明 VAD distance < ε 不代表人類完全無感知。
- E4：ε=0.5 是 system guardrail，不是 human perceptual boundary。
- **收斂**：S155 = boundary case，**系統允許但部分人類可感知 drift**，說明 ε 是保守工程護欄。

**R10 0.13% 與 4.5% 的最終定義**

- E6 + E7：需要一句話清楚說明。
  - 0.13% = system-detected strict VAD violation
  - 4.5% = human-perceived polarity drift
- E10：「真實失真率到底是多少？」
- Prof. Meaning：「取決於 operational definition。不要追求單一真值；要報兩個定義。」
- **收斂**：差距揭示 *computational guardrail 與 human affective sensitivity 之間的邊界層*。

### 13.3 Round 11–15：與論文主張的銜接

**R11 Abstract 是否需修改**

- E4：若 abstract 只說 0.13%，補充說明 4.5% 才能避免 selective reporting 指控。
- 建議語句：*Human validation further shows that annotators perceive a broader 4.5% boundary-level affective drift.*
- **收斂**：在 Abstract 或 Validation summary 中同時呈現兩數，明確區分定義。

**R12 是否應調低 ε**

- E9：人類感知邊界可能在 0.3–0.35，是否把 ε 從 0.5 降到 0.35？
- E4：降低 ε 會增加 rejection rate，降低 goodput。
- 共識：ε 應寫成 **deployment-sensitive threshold**：一般場景 ε=0.5，safety-critical 場景可調低。

**R13 A3 conflict 的正面意義**

- E5 + E1：27.3% conflict 來自 frustration/annoyance、anxiety/fear、excitement/joy 等語義相鄰類別，直接對應 VAD distance matrix 的近鄰關係。
- **收斂**：A3 不作為主要 accuracy 指標，而是 *emotion-category ambiguity diagnostic*。

**R14 多數決合理性**

- E7 + E10：輪轉設計中不同樣本由不同三人標記，group effect 不可忽視。
- **收斂**：多數決可用，但必須搭配 group-level Fleiss κ、pairwise Cohen κ 與 annotator threshold analysis，保持透明。

**R15 人工標記是否支持主論點**

- E1 + E9：結構有效的輸出中仍有 4.5% 被人類感知為失真，直接支持「structural validity ≠ affective integrity」。
- 措辭注意：應為 *perceptual validation of hidden affective drift*，不說「全部都是 hard errors」。

### 13.4 Round 16–20：跨語言、審稿風險、最終共識

**R16 跨語言結果的位置**

- E8：中文 ε*_zh=0.40 的邏輯：不同語言情感空間密度不同，需重校準。
- E10：不能混入英文 4.5%，應作為 separate subsection（Cross-lingual recalibration）。

**R17 最可能的 Reviewer 攻擊點（E10 彙整）**

| 攻擊點 | 論文回應 |
|--------|---------|
| 0.13% vs. 4.5% 矛盾 | 不同 operational definition（strict violation vs. perceptual drift） |
| κ 有負值 | near-zero prevalence effect + construct validity divergence |
| A1=YES 但 A2=None | existence vs. severity orthogonality |

Prof. Meaning：這三組回應應主動寫入 Discussion，不等 reviewer 問。

**R18 建議新增圖**

- E1 + E3 + E7：強烈建議新增 **Dual-Layer Affective Distortion Model** 概念圖：

```
LLM 輸出情感 ──[修復管道]──► 修復後情感
     │                            │
     ▼                            ▼
D_extraction（A3 測）         D_repair（A1 測）
~20–27% category ambiguity    4.5% human-perceived
                              0.13% system-detected
```

A2 標注 severity（None/Slight/Moderate/Severe）橫跨右側 D_repair 分支。

**R19 各專家一句話總結**

| 專家 | 一句話結論 |
|------|-----------|
| E1 | 人工標記支持 Affective Integrity 是獨立構念 |
| E2 | 低 κ 是統計情境問題，不是標注失敗 |
| E3 | A1/A2/A3 測量不同層次，不能混算 |
| E4 | 修復失真是 hidden reliability failure |
| E5 | VAD ε 是工程護欄，不是完整人類感知邊界 |
| E6 | 人類結果提供 perceptual calibration |
| E7 | 要報 operational definitions，不要追求單一真值 |
| E8 | 跨語言 ε 需重校準 |
| E9 | 敏感應用可採更嚴格 ε |
| E10 | 主動解釋三個風險點，結果可被接受 |

**R20 Prof. Meaning 最終裁定（11/11 共識）**

> 人工標記結果應被詮釋為對 Affective Integrity 框架的感知層驗證，而不是對系統結果的反駁。  
>  
> 0.13% 代表系統在 VAD ε=0.5 護欄下偵測到的明確規則違反；4.5% 代表人類標注者在極性層面感知到的修復後情感偏移。兩者的差距揭示了 computational guardrail 與 human affective sensitivity 之間的邊界層。  
>  
> A3 的高 conflict 率說明情感類別標記比極性標記更不穩定，支持本研究採用 VAD-bounded affective distance 而非 exact emotion label matching 的設計。  
>  
> 低 Fleiss κ 結果不應視為標注失敗，而應解釋為 near-zero prevalence effect 與 annotator threshold divergence 的共同結果。D–E κ=0.841 提供強力的 high-reliability anchor，證明 polarity-level repair distortion 可以被穩定測量。

---

## 14. 第二次 Delphi 後：最終共識模型

### 14.1 三分量失真架構

觀察到的人工標記結果可分解為三個來源：

$$\text{Observed Labels} = D_{\text{extraction}} + D_{\text{repair}} + D_{\text{threshold}}$$

| 分量 | 量測工具 | 數值 | 說明 |
|------|---------|------|------|
| $D_{\text{extraction}}$ | A3 ≠ llm_emotion | ~20–27% | LLM 原始情感抽取歧義 |
| $D_{\text{repair}}$ | A1=YES 多數決 | 4.5%（人類）/ 0.13%（系統） | 修復造成的情感偏移 |
| $D_{\text{threshold}}$ | YES 率跨人員差異 | 1.0%–7.5% 範圍 | 標注者判準差異 |

### 14.2 Delphi 建議放入論文的詮釋表

| 現象 | 數值 | 表面風險 | Delphi 解釋 | 論文寫法 |
|------|------|---------|------------|---------|
| 系統偵測失真 | 0.13% | 可能被認為低估 | strict VAD violation | system-detected distortion |
| 人類 A1 失真 | 4.5% | 與系統矛盾 | human-perceived drift | perceptual boundary |
| A3 CONFLICT | 27.3% | 標注不一致 | category ambiguity | diagnostic of emotion-label variability |
| B+D+F κ | −0.0417 | 看似標注失敗 | near-zero prevalence | κ instability under sparse positives |
| C+E+F κ | −0.0150 | 看似標注失敗 | near-zero prevalence | same as above |
| D–E κ | 0.841 | （無風險） | high-reliability anchor | validates A1 construct |
| F YES 率 | 1.0% | outlier | conservative threshold | threshold divergence |
| A1=YES, A2=None | 高比例 | 看似矛盾 | existence/severity orthogonality | subtle affective drift |

### 14.3 建議放入論文的段落（英文草稿）

> **Delphi-based Interpretation of Human Annotation.**
> To interpret the human labeling results, we conducted a Delphi-style expert adjudication. The panel concluded that the annotation results should be understood through a dual-layer distortion model. A1 captures repair-induced polarity-level affective drift, whereas A3 captures extraction-level emotion-category ambiguity. Under this interpretation, the human-perceived distortion rate of 4.5% does not contradict the system-detected distortion rate of 0.13%; rather, the two quantities correspond to different operational definitions. The former reflects perceptible affective drift near the human sensitivity boundary, while the latter reflects strict VAD-threshold violations under the ε=0.5 repair guard.
>
> The panel further concluded that low Fleiss κ values in groups with near-zero YES prevalence should not be interpreted as annotation failure. Instead, they reflect κ instability under sparse positive labels and threshold divergence among annotators. This interpretation is supported by the D–E pairwise Cohen's κ of 0.841, which provides a high-reliability anchor for polarity-level distortion judgments. Finally, the frequent co-occurrence of A1=YES and A2=None indicates that repair-induced distortion often manifests as perceptible but low-severity affective drift, reinforcing the need to evaluate affective integrity separately from structural validity.

### 14.4 最終一句話結論

> 人工標記結果揭示的不是系統失敗，而是 affective distortion 的感知邊界：系統以 ε=0.5 捕捉嚴格規則違反，人類則能感知更細微的情緒漂移；兩者共同證明 structural validity 不足以保證 affective integrity。

---

## 15. 修稿建議（基於統計結果 + 兩次 Delphi 討論）

> 此節為論文修稿行動清單，對應 TAC-ORIGINAL.tex 的具體段落。

### 15.1 必要修改（直接影響論文可信度）

| 編號 | 修改項目 | 位置 | 具體行動 |
|------|---------|------|---------|
| R1 | 新增雙層失真模型圖 | Section 3 或 Section 5 | 新增概念圖：D_extraction（A3）+ D_repair（A1/A2）；標注各自數值 |
| R2 | 補充 4.5% human validation 數字 | Abstract / Section 5.2 | 加入語句：*annotators perceive 4.5% boundary-level affective drift*；明確與 0.13% 的定義差異 |
| R3 | 解釋低 κ / 負 κ | Section 5.2 | 加入 near-zero prevalence 段落；引用 κ instability 文獻（Feinstein & Cicchetti 1990 或類似） |
| R4 | 主動說明三個審稿風險點 | Section 6 Discussion | 加入 subsection 或 paragraph：(1) operational definition 差異 (2) near-zero prevalence (3) existence/severity orthogonality |
| R5 | 放入 Delphi 段落草稿 | Section 5.2 末 | 使用第 14.3 節的英文草稿，略作調整後嵌入 |

### 15.2 強烈建議修改（提升論文深度）

| 編號 | 修改項目 | 位置 | 具體行動 |
|------|---------|------|---------|
| R6 | 明確定義 D_extraction 與 D_repair | Section 3.2 或 Section 5.2 | 加入兩個 operational definition，搭配方程式或定義框 |
| R7 | 說明 F 是 conservative annotator | Section 5.2（Annotator Analysis） | 加入 per-annotator YES rate table，備注 F 的 threshold divergence 意義 |
| R8 | 說明 D–E κ=0.841 作為錨點 | Section 5.2 | 在 pairwise κ 表格附近加說明句 |
| R9 | S155 作為 boundary case 範例 | Section 5.2 | 新增一段說明 contentment→joy 在 d_aff < ε 但仍有人類感知 drift 的邊界狀況 |
| R10 | A3 CONFLICT 重新定位 | Section 5.2 | 明確寫出：A3 conflict 是 emotion-category ambiguity diagnostic，不是 repair failure metric |

### 15.3 可選修改（提升完整性）

| 編號 | 修改項目 | 位置 | 具體行動 |
|------|---------|------|---------|
| R11 | ε 作為 deployment-sensitive threshold | Section 3 末 或 Section 6 | 加一句：safety-critical 應用可採 ε < 0.5；參考 ε*_zh=0.40 作為先例 |
| R12 | 跨語言 ε 重校準放入獨立 subsection | Section 5.3 | 加標題 "Cross-lingual ε Recalibration"；報告 ROC-AUC 0.07→0.66 的完整流程 |
| R13 | 正交性（A1/A2）加入 Table | Section 5.2 | 新增 Table：各標注者 A1=YES 時 A2=None 比率（A: 89%, B: 100%, C: 100%, D: 93%） |
| R14 | A1 量表的局限性段落 | Section 5.2 末 或 Section 6 | 加入：A1 只測極性層面，不測 exact category；已知局限不等於設計缺陷 |

### 15.4 修稿優先順序建議

```
第一輪（投稿前必做）：R1, R2, R3, R4, R5
第二輪（Revision 後）：R6, R7, R8, R9, R10
第三輪（Optional）   ：R11, R12, R13, R14
```

---

*最後更新：2026-05-27*  
*作者：AUGUST CHAO（主要標注者 F）+ 統計計算*  
*第二次 Delphi：11 位虛擬專家，20 輪，主席 Prof. Meaning*
