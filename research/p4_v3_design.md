# P4 v3 Design — Context-aware Text Unit Relation Model

> READ-ONLY DESIGN ONLY. 不修改 P4 / P7.1 / Frozen 730 / 任何代码。
> 目标：设计 Context-aware Text Unit Relation Model，判断两个相邻 geometric observations 是否属于同一 Text Unit。

---

## 0. 数据基础

基于 Cross-Document Text-Unit Relation Audit + 本轮补充审计，覆盖 8 个文档：

| 文档 | 类型 | 审计页 | P1 obs | P4 spans | same-y 未合并 |
|---|---|---|---|---|---|
| arxiv_toc (arxiv_bio p2) | TOC 页 | p2 | 117 | 90 | 47 |
| arxiv_bio_body | 正文页 | p1,3,5,10 | 1424 | 474 | 23 |
| arxiv_2307 | 公式密集正文 | p1-3 | 921 | 553 | 338 |
| RA101 | 设备手册 | p1-3 | 116 | 36 | 0 |
| RM501-P4 | 设备手册 | p1-2 | 214 | 65 | 2 |
| E804 | 设备手册 | p1-2 | 84 | 31 | 1 |
| C216 | 设备手册 | p1-3 | 108 | 36 | 0 |
| DC201 | 设备手册 | p1,2,5 | 201 | 56 | 0 |

原始数据：`cross_doc_audit_raw.json` + `cross_doc_audit_supplement.json`

---

## 一、候选 Relation Ontology

基于跨文档证据，提出以下 relation 分类：

| Relation | 几何证据 | Merge? | 说明 |
|---|---|---|---|
| `SAME_TEXT_UNIT` | same_y + same_font + same_style + w_b≥25 + gap<50 + line_obs≤10 | ✅ MERGE | 序号+标题、附录字母+标题、同行正文续接 |
| `FORMULA_FRAGMENT` | line_obs≥10 OR (w_a<15 AND w_b<15) | ❌ BLOCK | 公式行内的符号碎片 |
| `COLUMN_BOUNDARY` | gap>50 (cross_column_gap_threshold) | ❌ BLOCK | 跨栏（标题→页码） |
| `TABLE_CELL_BOUNDARY` | gap>50 + same_y + 在 DENSE/SPARSE region 内 | ❌ BLOCK | 表格同行不同单元格 |
| `STRUCTURAL_BOUNDARY` | different_font OR different_style | ❌ BLOCK | 样式过渡（标题→正文） |
| `UNKNOWN` | 不满足以上任何条件 | ⏸ DEFER | 保守不合并，保持 P4 当前行为 |

### 设计原则
- `SAME_TEXT_UNIT` 是唯一允许 MERGE 的 relation
- 其他 relation 全部 BLOCK 或 DEFER
- `UNKNOWN` 保持保守（不合并）——宁可漏合并也不误合并
- 所有判断基于 geometry/layout features，不读文本内容

---

## 二、Feature 跨文档分析（A-K）

### A. Horizontal gap

| 属性 | 值 |
|---|---|
| Signal definition | A.x1 到 B.x0 的水平距离 |
| Geometric rationale | 同一文本单元内的相邻 observation gap 应小；跨栏/跨单元格 gap 大 |
| Cross-document evidence | TRUE merge gap=8-22pt；FALSE merge(formula) gap=8-312pt；CROSS_COL gap>50pt |
| Known false-positive | gap=8-12pt 区间同时含 TRUE(TOC序号+标题) 和 FALSE(公式符号) |
| Known false-negative | gap=22pt 的 arxiv_2307 section heading "1."→"Introduction" 被 8pt 阈值漏掉 |
| Safe as hard constraint? | **否**——gap<50 可作为 BLOCK cross-column 的 hard constraint，但不能单独决定 MERGE |
| Only usable as soft signal? | **是**——作为多特征组合中的一个必要条件（gap<50） |

### B. Vertical / baseline alignment (Δy)

| 属性 | 值 |
|---|---|
| Signal definition | A.center_y 与 B.center_y 的差值 |
| Geometric rationale | 同一文本单元应在同一基线（Δy≈0） |
| Cross-document evidence | TRUE merge: 30/30 Δy<1pt；FALSE merge(formula): 243/277 Δy<1pt |
| Known false-positive | 公式符号也在同一基线（Δy≈0），无法区分 |
| Known false-negative | 无——所有 TRUE merge 都 Δy<1pt |
| Safe as hard constraint? | **是**——Δy≤3pt 作为 SAME_TEXT_UNIT 的必要条件（hard constraint） |
| Only usable as soft signal? | 否——可作 hard constraint，但不够用（需组合其他 feature） |

### C. Observation density on same line (line_obs_count)

| 属性 | 值 |
|---|---|
| Signal definition | 同一 y-band(±3pt) 内的 observation 数量 |
| Geometric rationale | 标题行通常 2-4 个 observation（序号+标题+页码）；公式行通常 10-30 个 observation |
| Cross-document evidence | TRUE merge: line_obs=2-9 (median 3)；FALSE merge(formula): line_obs=5-21 (median 11) |
| Known false-positive | 13/27 FALSE merges 有 line_obs=5-10（公式行末尾的符号→正文过渡） |
| Known false-negative | 6/30 TRUE merges 有 line_obs=5-9（带公式引用的标题行） |
| Safe as hard constraint? | **部分**——line_obs≤10 可捕获 ALL 30 TRUE merges (0 false negative)，但有 13 false positive |
| Only usable as soft signal? | **是**——作为必要条件（line_obs≤10）有效，但不足以单独决定 MERGE |

### D. Nearest-neighbor relationship

| 属性 | 值 |
|---|---|
| Signal definition | A 和 B 是否在 source_index 上相邻（A.source_index = B.source_index - 1） |
| Cross-document evidence | 所有审计的 pair 都是 source-adjacent（按定义） |
| Safe as hard constraint? | **是**——必要条件，但不提供区分力（所有 pair 都满足） |

### E. Left/right surrounding observations

| 属性 | 值 |
|---|---|
| Signal definition | A 左侧是否有 observation？B 右侧是否有远距离 observation（gap>100pt）？ |
| Cross-document evidence | TOC 行: A=行首 + B 右侧有页码(gap>170pt)；公式行: A 非行首 + B 右侧密集 |
| Known false-positive | arxiv_2307 section heading 行也有远距离 observation |
| Safe as hard constraint? | **否**——`has_far_right` 在 TRUE(88%) 和 FALSE(90%) 中都高 |
| Only usable as soft signal? | **是**——弱信号，不单独使用 |

### F. Font size / geometric size (w_a, w_b)

| 属性 | 值 |
|---|---|
| Signal definition | w_b = B 的 bbox 宽度 |
| Cross-document evidence | **w_b≥25pt 是最强的单一 separator**：TRUE merge 30/30 w_b≥25；formula FALSE merge 0/277 w_b≥25（但有 27 个非公式 FALSE merge w_b≥25） |
| Known false-positive | 3 个公式碎片 w_b=25-28pt（公式间距产生的宽 bbox）；13 个公式→正文过渡 w_b≥25 |
| Known false-negative | 0——所有 TRUE merge 的 w_b≥25 |
| Safe as hard constraint? | **是**——w_b≥25pt 作为 SAME_TEXT_UNIT 的必要条件（hard constraint），0 false negative |
| Only usable as soft signal? | 否——可作 hard constraint |

### G. Line density

与 C (line_obs_count) 相同。

### H. Column boundary

| 属性 | 值 |
|---|---|
| Signal definition | gap > cross_column_gap_threshold (当前 30pt) |
| Cross-document evidence | TOC 跨栏 gap=170-338pt；设备手册表格跨列 gap=170-191pt |
| Safe as hard constraint? | **是**——gap>50 → COLUMN_BOUNDARY → BLOCK（hard constraint） |

### I. Table boundary

| 属性 | 值 |
|---|---|
| Signal definition | 在 P6 DENSE/SPARSE region 内 + same-y + gap>50 |
| Cross-document evidence | RM501 "Well"→"Components" gap=190pt in table region |
| Safe as hard constraint? | **部分**——需要 P6 region 信息作为输入（P4 v3 是否能访问 P6？需设计决策） |

### J. Graphic/vector boundary

| 属性 | 值 |
|---|---|
| Signal definition | P1 跳过了非文本 block（block_type≠0），不产生 observation |
| Cross-document evidence | 无——P4 只处理文本 observation，graphic 不在输入中 |
| Safe as hard constraint? | **不适用**——P4 输入不包含 graphic boundary 信息 |

### K. Page region / layout zone

| 属性 | 值 |
|---|---|
| Signal definition | P5/P6 的 region type（PAGE_TOP/FULL_WIDTH/COLUMN/DENSE/SPARSE） |
| Cross-document evidence | TOC 在 FULL_WIDTH/COLUMN region；公式在 COLUMN region；表格在 DENSE/SPARSE region |
| Safe as hard constraint? | **否**——region type 不能单独区分 TOC 行和公式行（都在 COLUMN region） |
| Only usable as soft signal? | **是**——可作辅助信号 |

---

## 三、Feature × Document × Failure Mode 矩阵

详见 `p4_v3_feature_matrix.md`。

### 关键回答

**1. 哪些 feature 在设备手册中稳定？**
- gap>50 → cross-column（稳定，0 false positive）
- same_font/same_style（稳定，设备手册表格同行单元格通常 same_font）
- line_obs_count（稳定，设备手册行密度低 1-4）

**2. 哪些 feature 在 arxiv 文档中稳定？**
- w_b≥25 → title text（稳定，0 false negative）
- line_obs_count≤10（稳定捕获 all TRUE merges）
- Δy≤3（稳定，all TRUE merge Δy<1pt）

**3. 哪些 feature 在两类文档之间发生 domain shift？**
- gap 绝对值：TOC 序号+标题 gap=10-12pt；arxiv_2307 section heading gap=22pt；设备手册无 same-y 未合并
- line_obs_count 分布：设备手册 1-4；TOC 2-9；公式 10-30

**4. 哪些 feature 可以作为 hard constraint？**
- Δy≤3pt（必要条件）
- w_b≥25pt（必要条件，0 false negative）
- gap<50pt（BLOCK cross-column）
- line_obs_count≤10（必要条件，0 false negative）

**5. 哪些只能作为 soft evidence？**
- has_far_right（弱信号，TRUE/FALSE 都高）
- page_region（辅助信号）
- is_leftmost（弱信号）

**6. 是否存在任何已经被数据证明具有 transferability 的 relation signal？**
- **部分是**：`same_y + same_font + same_style + w_b≥25 + gap<50 + line_obs≤10` 组合捕获 ALL 30 TRUE merges (0 false negative)，但仍有 13 false positive（公式→正文过渡）
- **不是完全可迁移**：13/27 false positive 无法用纯几何消除

---

## 四、Adversarial Case 分析

### Case A: arxiv_toc "1" + "Introduction"

| Feature | Value |
|---|---|
| gap | 10.0pt |
| Δy | 0.0pt |
| same_font | ✅ |
| same_style | ✅ |
| w_b | 68.6pt (≥25 ✅) |
| line_obs_count | 3 (≤10 ✅) |
| has_far_right | ✅ (页码在远右) |

→ 所有 hard constraints 通过 → `SAME_TEXT_UNIT` → MERGE ✅

### Case B: arxiv_2307 "ψ" + "ψψ"（公式碎片）

| Feature | Value |
|---|---|
| gap | 9.8pt |
| Δy | 0.0pt |
| same_font | ✅ |
| same_style | ✅ |
| w_b | 25.1pt (≥25 ✅) |
| line_obs_count | 16 (>10 ❌) |
| has_far_right | ✅ |

→ line_obs_count>10 → `FORMULA_FRAGMENT` → BLOCK ✅

### Case B': arxiv_2307 "ψ" + "is defined as per Eq." （公式→正文过渡，IRREDUCIBLE）

| Feature | Value |
|---|---|
| gap | 12.6pt |
| Δy | 0.3pt |
| same_font | ❌ (公式字体 vs 正文字体) |
| w_b | 89.7pt (≥25 ✅) |
| line_obs_count | 9 (≤10 ✅) |

→ same_font=❌ → `STRUCTURAL_BOUNDARY` → BLOCK ✅ （如果 same_font 是 hard constraint）

### Case B'': arxiv_2307 "ψ" + "[recall" （same_font=✅ 的公式→正文过渡）

| Feature | Value |
|---|---|
| gap | 11.7pt |
| same_font | ✅ |
| w_b | 25.8pt (≥25 ✅) |
| line_obs_count | 9 (≤10 ✅) |

→ **所有 hard constraints 通过** → 会被误判为 `SAME_TEXT_UNIT` → **IRREDUCIBLE FALSE POSITIVE**

### 什么额外 geometric/context signal 可以区分 A 与 B？

已验证的信号：
1. **w_b≥25pt**：区分 title text（宽）vs formula symbol（窄）—— **0 false negative**
2. **line_obs_count≤10**：区分 sparse line（标题行）vs dense line（公式行）—— **0 false negative**
3. **same_font + same_style**：区分 same-unit（同字体）vs structural boundary（字体过渡）

**无法区分的剩余 case**：
- 公式行末尾的符号→正文过渡（same_font=✅, w_b≥25, line_obs≤10）
- 这些是**几何上不可区分的**——公式符号与短标题在几何特征上同构

### 当前证据是否足以可靠区分？

**部分是。** 组合 filter 可达到：
- 0 false negative（所有 TRUE merge 被捕获）
- 13/307 false positive（4.2% false positive rate on all unmerged pairs）

但 13 个 false positive 中有 ~5 个是**几何不可区分的**（same_font + w_b≥25 + line_obs≤10 + gap<50），无法用纯几何消除。

---

## 五、候选模型设计

### Model A: Rule-based Relation Model

```
decide_relation(A, B, line_context):
  if not same_y(A, B):          → DIFFERENT_LINE (defer to P4 vertical merge logic)
  if gap > 50:                  → COLUMN_BOUNDARY (BLOCK)
  if not same_font(A, B):       → STRUCTURAL_BOUNDARY (BLOCK)
  if not same_style(A, B):      → STRUCTURAL_BOUNDARY (BLOCK)
  if w_b < 25:                  → FORMULA_FRAGMENT (BLOCK)
  if line_obs_count > 10:       → FORMULA_FRAGMENT (BLOCK)
  if gap > 8 AND gap < 50
     AND same_font AND same_style
     AND w_b >= 25
     AND line_obs_count <= 10:  → SAME_TEXT_UNIT (MERGE)
  else:                         → UNKNOWN (BLOCK, conservative)
```

| 属性 | 值 |
|---|---|
| 输入 | A/B bbox + font + style + line_obs_count |
| Relation decision | SAME_TEXT_UNIT / FORMULA_FRAGMENT / COLUMN_BOUNDARY / STRUCTURAL_BOUNDARY / UNKNOWN |
| Merge decision | 仅 SAME_TEXT_UNIT → MERGE |
| False merge 风险 | ~5 irreducible FPs (公式→正文过渡, same_font + w_b≥25 + line_obs≤10) |
| False split 风险 | 0 (all 30 TRUE merges captured) |
| Transferability | 高——所有 hard constraints 跨文档验证 (8 docs) |
| Deterministic | ✅ 纯几何，无随机性 |
| Explainability | ✅ 每个 BLOCK/MERGE 有明确 reason |

### Model B: Weighted Geometric Relation Score

```
score = 0
score += 30 if same_y(dy≤3)
score += 20 if same_font
score += 20 if same_style
score += 15 if w_b >= 25
score += 10 if gap < 50
score += 5  if line_obs_count <= 10
score -= 30 if line_obs_count > 15  (formula line penalty)
score -= 20 if gap > 100 (cross-column penalty)

if score >= 80:  → SAME_TEXT_UNIT (MERGE)
else:            → UNKNOWN (BLOCK)
```

| 属性 | 值 |
|---|---|
| False merge 风险 | 与 Model A 类似，但权重调优可能减少/增加 FP |
| False split 风险 | 需要验证 score≥80 是否捕获 all TRUE merges |
| Transferability | 中——权重需要跨文档验证 |
| Deterministic | ✅ |
| Explainability | 中——score 是多特征加权，不如 rule-based 直观 |

### Model C: Hierarchical Boundary-first Model

```
Step 1: Identify BLOCK boundaries first (conservative)
  if gap > 50:           → COLUMN_BOUNDARY (hard block)
  if not same_font:      → STRUCTURAL_BOUNDARY (hard block)
  if line_obs > 15:      → FORMULA_LINE (hard block)

Step 2: Within non-blocked pairs, identify MERGE candidates
  if same_y AND same_font AND same_style AND w_b >= 25 AND line_obs <= 10:
    → SAME_TEXT_UNIT (merge)

Step 3: Remaining pairs → UNKNOWN (defer to P4 current behavior)
```

| 属性 | 值 |
|---|---|
| False merge 风险 | 最低——先排除所有 hard block，再在剩余中找 merge |
| False split 风险 | 0 (all TRUE merges pass step 1 and match step 2) |
| Transferability | 最高——boundary detection 是最稳定的跨文档信号 |
| Deterministic | ✅ |
| Explainability | ✅——分步骤，每步有明确 reason |

### 模型对比

| 维度 | Model A (Rule) | Model B (Score) | Model C (Hierarchical) |
|---|---|---|---|
| False negative | 0 | 需验证 | 0 |
| Irreducible FP | ~5 | ~5 (tunable) | ~5 |
| Transferability | 高 | 中 | 最高 |
| Explainability | 高 | 中 | 高 |
| 实现复杂度 | 低 | 中 | 低 |
| **推荐** | | | ✅ Model C |

**推荐 Model C**：boundary-first 策略最保守，先排除所有不应合并的 case，再在安全区内合并。这与 P4 当前「keep separate by default」的保守哲学一致。

---

## 六、不应该做什么

### 1. 为什么不能继续扩大 max_horizontal_gap

- threshold=12pt: precision=17.7%（79 false merge，主要数学公式）
- threshold=20pt: precision=10.8%（157 false merge）
- gap 绝对值在 TRUE merge (10-22pt) 和 FALSE merge (8-312pt) 区间完全重叠
- **单一 gap 阈值无法区分 TOC 序号+标题 和 公式符号**

### 2. 为什么不能继续使用 width<15pt

- 设备手册表格字段 "5V"(12pt)、"10ms"(14pt) 会被误杀
- arxiv_2307 公式变量 "ψ"(7pt) 不应被过滤（它不是 heading candidate 的碎片，是公式的一部分）
- width<15pt 只在 arxiv_toc p2 有效，是 page-specific

### 3. 为什么不能使用 y±5pt

- 公式行也满足 y±5pt（同一基线）
- 设备手册表格同行也满足 y±5pt
- y±5pt 只在 arxiv_toc p2 有效（TOC 同行条目 y 相同）

### 4. 为什么不能针对 arxiv_toc p2 写特例

- 不具备跨文档迁移性
- 违反"geometry/layout only, cross-document transferable"原则
- 是 page-specific patch，不是 model

### 5. 为什么不能让 P7.1 修复 span fragmentation

- 碎片在 P4 span 构造阶段产生
- P7.1 是 semantic observation 层，不应承担 text reconstruction 职责
- 让 P7.1 合并 span 会模糊 layer 边界（Observation vs Relation）

### 6. 为什么不能用 LLM 判断是否 merge

- 违反 deterministic 原则
- 引入非确定性（LLM output varies）
- 引入 semantic interpretation（LLM 会读文本内容）
- 违反"no LLM"约束

---

## 七、P4 v3 Gate

### 数据证据总结

| 指标 | 值 |
|---|---|
| TRUE merges (should merge) | 30 对（跨 3 个文档：arxiv_toc/arxiv_2307/arxiv_bio_body） |
| FALSE merges (should not) | 277 对（formula）+ 30 对（cross-column）+ 13 对（formula→body transition） |
| Filter: same_y + same_font + same_style + w_b≥25 + gap<50 + line_obs≤10 | |
| → TRUE merges captured | 30/30 (0 false negative) ✅ |
| → FALSE merges remaining | 13/307 (4.2% false positive rate) |
| → Irreducible FPs (same_font + w_b≥25 + line_obs≤10) | ~5 对 |

### 结论：B. DESIGN-INCONCLUSIVE

**存在有希望的 signals，但证据不足以证明完全 transferability。**

理由：
1. **0 false negative**——组合 filter 捕获所有 30 个 TRUE merges，跨 3 个文档（arxiv_toc/arxiv_2307/arxiv_bio_body）
2. **~5 irreducible false positives**——存在几何上不可区分的 case（公式→正文过渡，same_font + w_b≥25 + line_obs≤10）
3. **设备手册无碎片问题**——5 个设备手册（RA101/RM501/E804/C216/DC201）完全没有 same-y 未合并（0-2 对，且全部是跨栏），P4 v3 对它们无影响
4. **公式密集文档（arxiv_2307）是主要挑战**——338 对 same-y 未合并中大部分是公式碎片，P4 v3 需要正确 BLOCK 它们

### 不可迁移的 case

~5 个公式→正文过渡对（如 arxiv_2307 "ψ"→"[recall"）满足所有 hard constraints：
- same_y (Δy<1pt)
- same_font (✅)
- same_style (✅)
- w_b≥25pt (25.8pt)
- gap<50pt (11.7pt)
- line_obs_count≤10 (9)

这些 pair 在几何上与 TRUE merge（如 "6.1"→"SMEFT"）**完全同构**。区分它们需要文本内容分析（reading the text），这违反"geometry/layout only"原则。

### 建议

- **不进入 Implementation Design**——证据不足以证明 100% transferability
- **保持 P4 frozen**——当前 8pt 阈值对 5/7 文档（设备手册+arxiv_2401）完全有效
- **calibration_filter 降级为 page-specific experimental tool**——不作为正式修复，只在 Human Validation 环节作为辅助
- **Human Validation 保留为必要路径**——对于 P4 无法自动合并的 TOC 碎片，Human Validation 是唯一可行的确认路径
- **如果未来要推进 P4 v3**，需要：
  1. 验证 line_obs_count 在更多文档上的稳定性（当前只验证了 8 个文档）
  2. 接受 ~4% false positive rate（或找到新的几何 feature 消除 irreducible FPs）
  3. 在 P4 v3 中实现 Model C（boundary-first），先 BLOCK 再 MERGE
  4. P4 v3 是 unfrozen 新版本，不修改 frozen P4，需要独立回归验证

---

## ROOT CAUSE

P4 `max_horizontal_gap=8.0pt` 用单一阈值处理所有页面结构。TOC 序号+标题（gap=10-22pt）和公式符号（gap=8-15pt）在同一 gap 区间重叠，单一阈值无法区分。

根因不是"8pt 太小"，而是"P4 缺乏 context-aware text unit relation model"——需要组合 same_y + same_font + w_b + line_obs_count 等多特征，而非单一 gap 阈值。

---

## TRANSFERABILITY ASSESSMENT

| Feature | Transferable? | Evidence |
|---|---|---|
| Δy≤3pt (hard constraint) | ✅ 是 | 30/30 TRUE merges Δy<1pt，跨 3 文档 |
| same_font (hard constraint) | ✅ 是 | 30/30 TRUE merges same_font=✅ |
| w_b≥25pt (hard constraint) | ✅ 是 | 30/30 TRUE merges w_b≥25，0 false negative |
| gap<50pt (hard constraint) | ✅ 是 | 排除所有 cross-column |
| line_obs_count≤10 (hard constraint) | ⚠️ 部分 | 0 false negative，但 13 false positive |
| **组合 filter** | ⚠️ **INCONCLUSIVE** | 0 FN + ~5 irreducible FP |

**结论：组合 filter 在 8 个文档上达到 0 false negative + 4.2% false positive，但存在 ~5 个几何不可区分的 irreducible false positive。不足以证明完全 transferability。**

---

## RECOMMENDED NEXT LAYER

**不进入 P4 v3 Implementation。**

保持 P4 frozen。Human Validation 保留为 TOC 碎片问题的必要路径。

如果未来积累更多 Human Validation 数据（覆盖更多文档类型），可以重新评估 line_obs_count + w_b 组合的迁移性。如果 irreducible FP 可接受（<5%），则可进入 P4 v3 Implementation Design（Model C boundary-first）。

---

**P4 v3 Design 完成。Gate 结论：B. DESIGN-INCONCLUSIVE。STOP。不实施。不修改任何代码。不进入 P7.3。**
