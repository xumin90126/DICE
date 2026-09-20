# P4 v3 Feature × Document × Failure Mode Matrix

> READ-ONLY. P4 v3 Design 的数据支撑文档。

---

## 1. Feature × Document 矩阵

每个单元格 = 该 feature 在该文档上的表现。

### A. Horizontal gap

| 文档 | TRUE merge gap 范围 | FALSE merge(formula) gap 范围 | CROSS_COL gap 范围 | 区分力 |
|---|---|---|---|---|
| arxiv_toc | 8.8-12.4pt | N/A | 170-338pt | gap<50 可区分 cross-col |
| arxiv_bio_body | 12.5-13.5pt | 10.7-116.3pt | N/A | gap<50 部分有效 |
| arxiv_2307 | 22.0-22.1pt | 8.1-311.6pt | 47.8-100.7pt | gap<50 漏掉 gap=22 的 TRUE merge |
| RA101 | N/A (0 unmerged) | N/A | N/A | 不适用 |
| RM501-P4 | N/A | N/A | 172-191pt | gap<50 可区分 cross-col |
| E804 | N/A | N/A | 171pt | gap<50 可区分 cross-col |
| C216 | N/A | N/A | N/A | 不适用 |
| DC201 | N/A | N/A | N/A | 不适用 |

**结论**：gap 绝对值跨文档不稳定（TOC=10-12pt, arxiv_2307 heading=22pt）。gap<50 作为 BLOCK cross-column 的 hard constraint 有效。

### B. Δy (vertical/baseline alignment)

| 文档 | TRUE merge Δy | FALSE merge Δy | 区分力 |
|---|---|---|---|
| arxiv_toc | 0.0-0.3pt | 0.0-0.3pt | ❌ 无法区分 |
| arxiv_bio_body | 0.0pt | 0.0-2.5pt | ❌ 无法区分 |
| arxiv_2307 | 0.0pt | 0.0-2.2pt | ❌ 无法区分 |
| 设备手册(5) | N/A | N/A | 不适用 |

**结论**：Δy≤3 作为必要条件有效（all TRUE Δy<1pt），但无区分力。

### C. line_obs_count

| 文档 | TRUE merge line_obs | FALSE merge(formula) line_obs | 区分力 |
|---|---|---|---|
| arxiv_toc | 3-9 (median 3) | N/A | ✅ 全部 ≤10 |
| arxiv_bio_body | 2-8 (median 2) | 9-31 (formula lines) | ✅ TRUE ≤8 |
| arxiv_2307 | 3 (median 3) | 5-21 (median 11) | ⚠️ TRUE ≤3, FALSE 5-21 |
| RA101 | N/A | N/A | 不适用 |
| RM501-P4 | N/A | N/A | 不适用 |
| E804 | N/A | N/A | 不适用 |
| C216 | N/A | N/A | 不适用 |
| DC201 | N/A | N/A | 不适用 |

**结论**：line_obs_count≤10 捕获 ALL 30 TRUE merges (0 FN)，但 13/27 FALSE merges 也有 line_obs≤10（公式→正文过渡行）。

### F. w_b (width of B)

| 文档 | TRUE merge w_b | FALSE merge(formula) w_b | 区分力 |
|---|---|---|---|
| arxiv_toc | 31.8-295.0pt | N/A | ✅ 全部 ≥25 |
| arxiv_bio_body | 74.0-143.6pt | 22.3-27.7pt | ⚠️ FALSE 有 22-28pt |
| arxiv_2307 | 49.5-221.2pt | 1.6-28.4pt | ⚠️ FALSE 有 25-28pt |
| 设备手册(5) | N/A | N/A | 不适用 |

**结论**：w_b≥25 是最强单一 separator（0 false negative），但有 3 个公式碎片 w_b=25-28pt（irreducible FP）。

### same_font + same_style

| 文档 | TRUE merge same_font | FALSE merge same_font | 区分力 |
|---|---|---|---|
| arxiv_toc | 23/23 ✅ | N/A | ✅ |
| arxiv_bio_body | 3/3 ✅ | 5/20 ✅ | ⚠️ |
| arxiv_2307 | 4/4 ✅ | 225/242 (93%) ✅ | ❌ 公式符号也 same_font |
| 设备手册(5) | N/A | N/A | 不适用 |

**结论**：same_font 作为必要条件有效（all TRUE same_font），但公式符号之间也 same_font，区分力有限。

---

## 2. Failure Mode × Document 矩阵

| Failure Mode | arxiv_toc | arxiv_bio_body | arxiv_2307 | 设备手册(5) |
|---|---|---|---|---|
| FALSE SPLIT (漏合并 TRUE merge) | 21 对 | 3 对 | 4 对 | 0 对 |
| FALSE MERGE if threshold=12pt | 17 对 TRUE + 0 FALSE | 3 对 TRUE + 5 FALSE | 4 对 TRUE + 75 FALSE | 0 |
| FALSE MERGE if threshold=20pt | 19 TRUE + 22 FALSE | 3 TRUE + 11 FALSE | 4 TRUE + 157 FALSE | 0 |
| IRREDUCIBLE FP (组合 filter 后) | 0 | 0 | ~5 对 | 0 |

---

## 3. 组合 Filter 效果

### Filter chain: same_y(Δy≤3) → same_font → same_style → w_b≥25 → gap<50 → line_obs≤10

| 阶段 | 剩余 TRUE | 剩余 FALSE | Precision |
|---|---|---|---|
| 初始 (gap>8, same_y) | 30 | 307 | 8.9% |
| + same_font | 30 | 27 | 52.6% |
| + same_style | 30 | 27 | 52.6% |
| + w_b≥25 | 30 | 27 | 52.6% |
| + gap<50 | 30 | 13 | 69.8% |
| + line_obs≤10 | 30 | 13 | 69.8% |

**最终**：30 TRUE / 13 FALSE = 69.8% precision, 0% false negative

### 13 个剩余 FALSE 的构成

| 类型 | 数量 | 可消除? |
|---|---|---|
| 公式→正文过渡 (same_font=❌) | 8 | ✅ same_font 可消除 |
| 公式→正文过渡 (same_font=✅) | 5 | ❌ irreducible |
| 合计 | 13 | 8 可消除 + 5 irreducible |

**修正**：如果 same_font 在 w_b≥25 之后仍作为 hard constraint（实际已包含），则 8 个 same_font=❌ 的应在 same_font 阶段被消除。

重新统计：

| 阶段 | 剩余 TRUE | 剩余 FALSE |
|---|---|---|
| same_y + gap>8 | 30 | 307 |
| + same_font=✅ | 30 | 27 (剔除 280 个 diff_font) |
| + same_style=✅ | 30 | 27 |
| + w_b≥25 | 30 | 27 (w_b<25 的全是 formula symbol，已在 same_font 后全部 <15) |
| + gap<50 | 30 | 13 (剔除 14 个 cross-col) |
| + line_obs≤10 | 30 | 13 (line_obs>10 的全是 formula dense line) |

**13 个 FALSE 中**：
- same_font=❌ 的 0 个（已被 same_font 消除）
- same_font=✅ 的 13 个 → 全部 irreducible

### 13 个 Irreducible FALSE 的详细清单

全部在 arxiv_2307，全部是公式→正文过渡（same_font=✅, w_b≥25, gap<50, line_obs≤10）：

| # | gap | w_b | line_obs | text_a | text_b |
|---|---|---|---|---|---|
| 1 | 9.8 | 25.1 | 16→BLOCK | | |
| 2 | 12.8 | 28.4 | 16→BLOCK | | |
| 3 | 15.7 | 25.3 | 21→BLOCK | , | ( , , ) |
| 4 | 11.7 | 25.8 | 9 | | [recall |
| 5 | 12.6 | 89.7 | 9 | | is defined as p |
| 6 | 44.4 | 92.7 | 8 | | with a periodic |
| 7 | 20.8 | 167.8 | 6 | | form bands sepa |
| 8 | 10.3 | 165.2 | 5 | | (in contrast to |
| 9 | 9.2 | 177.6 | 5 | | by lines with ci |
| 10 | 8.8 | 42.3 | 10 | | , while red |
| 11 | 8.6 | 30.5 | 10 | | (b) and |
| 12 | 8.8 | 81.4 | 8 | | in Eq. (2) (SOC |
| 13 | 26.3 | 33.0 | 10 | | (c), and |

其中 #1-3 的 line_obs>10，实际会被 line_obs≤10 消除。

**真正 irreducible 的 = #4-13 = 10 个**（line_obs≤10, same_font=✅, w_b≥25, gap<50）

这 10 个全是 arxiv_2307 公式行末尾的符号→正文过渡，几何上与 section heading 不可区分。

---

## 4. Domain Shift 分析

| Feature | 设备手册 | arxiv TOC | arxiv 正文(公式密集) | Domain Shift? |
|---|---|---|---|---|
| gap (TRUE merge) | N/A | 10-12pt | 13-22pt | ✅ 是 (TOC vs body) |
| line_obs (TRUE merge) | N/A | 3 | 2-3 | ❌ 否 (一致) |
| w_b (TRUE merge) | N/A | 32-295pt | 50-221pt | ❌ 否 (都≥25) |
| same_font (TRUE merge) | N/A | ✅ | ✅ | ❌ 否 |
| line_obs (FALSE merge) | N/A | N/A | 5-21 | — |
| w_b (FALSE merge) | N/A | N/A | 1.6-28.4 | — |

**结论**：TRUE merge 的 hard constraints (Δy≤3, same_font, w_b≥25, line_obs≤10) 跨文档一致（无 domain shift）。Domain shift 主要在 gap 绝对值（TOC 10-12pt vs arxiv_2307 heading 22pt），但 gap 不作为 MERGE 的决定性 feature（只作为 BLOCK cross-column）。

---

## 5. 最终 Feature 推荐

| Feature | 角色 | Hard/Soft | 验证状态 |
|---|---|---|---|
| Δy≤3pt | SAME_TEXT_UNIT 必要条件 | Hard | ✅ 8 docs, 0 FN |
| same_font | SAME_TEXT_UNIT 必要条件 | Hard | ✅ 8 docs, 0 FN |
| same_style | SAME_TEXT_UNIT 必要条件 | Hard | ✅ 8 docs, 0 FN |
| w_b≥25pt | SAME_TEXT_UNIT 必要条件 | Hard | ✅ 8 docs, 0 FN |
| gap<50pt | BLOCK cross-column | Hard | ✅ 8 docs |
| line_obs≤10 | SAME_TEXT_UNIT 必要条件 | Hard | ✅ 0 FN, ⚠️ 10 irreducible FP |
| has_far_right | 辅助 | Soft | ❌ 弱信号 |
| page_region | 辅助 | Soft | ❌ 需 P6 输入 |

**Gate 判定**：6 个 hard constraints 组合 → 0 false negative + 10 irreducible false positive → **INCONCLUSIVE**。
