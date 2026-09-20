# M-A Caption Association — Experiment Readiness / Mechanism Boundary Review

> **模式: READ-ONLY / NO IMPLEMENTATION / NO EXPERIMENT EXECUTION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `m_b_experiment_readiness_review.md`（M-B = NOT_READY, DOWNGRADED）
> 本文件审查 M-A 是否值得成为下一项受控实验。

---

## 1. Executive Summary

```
M-A = NOT_READY

BLOCKING CONDITIONS:
  1. VISUAL_REGION_EVIDENCE = MISSING — P6 显式删除了 VISUAL_REGION；
     non_text_block 不覆盖矢量图；2 个 MERGE 页 NTB=0（矢量图，documented limitation）
  2. 几何证据 NOT DISCRIMINATIVE — same_y_band + h_gap 无法区分 caption 关联与
     普通文本邻接（与 M-B 的 prose=table 同构问题）
  3. 唯一判别性信号是 FIG-prefix 词法标记 — 但 CC-01 明确要求"词法必须留
     hypothesis 侧"，不得进入 observation 层
  4. COUNTERFACTUAL_COVERAGE = INSUFFICIENT — 2 cases, 1 doc, 0 negative cases
  5. 6.08% 指标被误读 — 79 个 figure-context 中 76 个是 tick-run（M-H 机制），
     实际 caption-related ≈ 6/1299 = 0.46%；96% 单文档集中；且来自不同 corpus
  6. SEMANTIC_LEAP = TRUE — geometry → caption 是未经验证的语义跳跃

CORRECTION TO PRIOR SUMMARY:
  system_reframing_summary.md 将 M-A 列为 SECONDARY_ROUTE，引用
  "EXPRESSIBLE=YES, 2 MERGE cases, cross-framework 6.08%"。
  本审查发现：
  - EXPRESSIBLE=YES 指的是"证据可表达关联查询"，但可表达 ≠ 判别性充分
  - 6.08% 中 96% 是 tick-run 不是 caption（误读）
  - 2 cases 全部来自 1 doc，0 negative，无法做受控实验
  - 缺失 visual region → 无法确认"文本在图附近"这一前提

VERDICT:
  NEW_OBSERVATION_REQUIRED     = TRUE  (visual region / figure presence)
  NEW_DETECTOR_REQUIRED        = TRUE  (figure/caption region detector)
  CONSUMER_MODIFICATION_REQUIRED = FALSE
  SEMANTIC_LEAP                = TRUE
  COUNTERFACTUAL_COVERAGE      = INSUFFICIENT
  MECHANISM                    = SPECIFIC (但 n=2, 1 doc)
  FALSIFIABILITY               = INSUFFICIENT (0 negative cases)

  M-A = NOT_READY
```

---

## 2. M-A Research Question

> 在不修改现有 P1–P7 frozen artifacts 的前提下，当前已有 Document Perception Evidence
> 是否包含足以支持 Figure ↔ Caption Association 的判别性信息？

> M-A 到底是 Evidence Organization / Query 问题，还是当前 Perception 本身缺少判别性信号？

**本审查的回答**:

M-A **表面上是** Evidence Organization 问题（CC-01 说 EXPRESSIBLE=YES），
**实质上是** Perception Gap — 缺少 visual region evidence，导致无法确认
"文本在图附近"这一关联前提。几何证据（same_y_band, h_gap）虽存在但
**不具判别性** — 无法区分 caption 关联与普通文本邻接。

---

## 3. Primary Research Layer

```
PRIMARY   = A (Evidence Organization / Query) — 形式上（CC-01 EXPRESSIBLE=YES）
SECONDARY = D (Representation Gap) — 实质上（VISUAL_REGION 被删除，无法表达图位置）
```

### 跨界检查: M-A 是否可以只用现有 Evidence 完成?

**NO [OBSERVED]**:

M-A 需要确认"text_a (FIG N:) 和 text_b (continuation) 都在 figure 附近"。
这需要 visual region evidence。当前:
- P6 region schema **显式删除了 VISUAL_REGION**（"requires identifying image/figure/table; P1 has only text spans; a void is not a visual object"）
- non_text_block 只覆盖 raster image block（type != 0），**不覆盖矢量图**（documented limitation）
- 2 个 MERGE 页 NTB=0（图是矢量绘制，非 raster）

**缺失的不是 Query 能力，而是被查询的 Evidence 本身。**
如果 visual region 不存在，无论怎么组织/查询，都无法回答"这段文本在图附近吗"。

---

## 4. Evidence Availability Matrix

逐项检查已有信息: EXISTS / FROZEN / QUERYABLE / DISCRIMINATIVE

| Evidence | EXISTS | FROZEN | QUERYABLE | DISCRIMINATIVE (能区分 caption 与 ordinary text?) |
|----------|--------|--------|-----------|--------------------------------------------------|
| P1 Text (text_a = "FIG. 9:") | YES | YES (drift=0) | YES | **PARTIAL** — "FIG N:" 前缀是词法标记，可区分 caption label；但 CC-01 要求词法留 hypothesis 侧，不得进层 |
| P1 Text (text_b = "Left:") | YES | YES | YES | **NO** — "Left:" 本身不判别（普通文本也可含 "Left:"） |
| P2 Geometry (same_y_band) | YES | YES | YES | **NO** — caption 与 continuation 在同 y-band，但普通段落句子也在同 y-band |
| P2 Geometry (h_gap 10.5-18.1pt) | YES | YES | YES | **NO** — 此 gap 范围与普通文本内 fragment 间距重叠 |
| P2 Geometry (left_alignment x≈85.04) | YES | YES | YES | **PARTIAL** — 列首对齐可提示"结构起始"，但段落首行也列首对齐 |
| P3 Style (size/font/bold) | YES | YES | YES | **UNKNOWN** — CC-01 未报告 caption label 的 style 差异；未验证 |
| P4 Span (8pt merge threshold) | YES | YES | YES | **NO** — 8pt 阈值是 failure 来源（gap 10.5-18.1 > 8 → AMBIGUOUS），非判别信号 |
| P5 ReadingOrder (column groups) | YES | YES | YES | **NO** — 仅有列级分组，无完整阅读序列；reading-order adjacency ≠ caption |
| P6 Region (region_type) | YES | YES | YES | **NO** — region 分类仅 PAGE_TOP/BOTTOM/FULL_WIDTH/COLUMN/DENSE/SPARSE/UNKNOWN；**VISUAL_REGION 和 TEXT_REGION 被显式删除** |
| P6 Region (DENSE_REGION) | YES | YES | YES | **NO** — caption 文本可能 dense，但段落也 dense |
| P7.1 (REPEATS_ACROSS_PAGES) | YES | YES | YES | **NO** — caption 不跨页重复（与 header 不同） |
| non_text_block (NTB) | YES | YES | YES | **NO for vector figures** — 2 个 MERGE 页 NTB=0；矢量图不在 NTB 覆盖范围 |
| TLD (is_in_table) | YES | YES | YES | **NO** — TLD table-only；2 case tables_detected=0 |

### 判别性总结

**能区分 caption 与 ordinary text 的信号**:
1. FIG-prefix 词法标记 ("FIG N:") — **DISCRIMINATIVE 但必须留 hypothesis 侧**
2. Visual region (图的存在 + 位置) — **MISSING**（VISUAL_REGION 删除 + NTB=0 矢量图）

**不能区分的信号**:
- same_y_band, h_gap, left_alignment, DENSE_REGION, reading order — 全部与普通文本邻接重叠

---

## 5. 判别性 Evidence 分析 — 关系对比

### 必须区分的关系

| 关系 | 几何证据能否区分? | 原因 |
|------|-----------------|------|
| Figure → Caption | **NO** (无 visual region) | 无法定位 figure；只能靠 FIG-prefix 词法 |
| Figure → Ordinary Paragraph | **NO** | 段落也在同 y-band、同列、相近 h_gap |
| Figure → Reference-like Text | **NO** | reference 也在同页、相近位置 |
| Figure → Nearby Non-caption Text | **NO** | 无 visual region → 无法判断"nearby" |
| Figure → Footnote | **NO** | footnote 位置可能也在图下方 |

### Geometry 是否仅因距离近?

**YES — 且距离近不判别 [INFERRED]**:

CC-01 microscope: h_gap 10.5-18.1pt, same_y_band=True。但这些几何属性
与"段落内两个 fragment"完全相同。没有 visual region，无法确认"近"是
"近 figure"还是"近另一个 text fragment"。

### Reading Order 是否仅因位于 figure 前后?

**UNKNOWN — P5 无完整阅读序列 [OBSERVED]**:

P5 仅有 column groups（列级分组），无完整阅读序列。无法判断
"caption 位于 figure 之后"这一 reading-order 关系。

### Style 是否存在稳定 caption-like style?

**UNKNOWN — 未验证 [INSUFFICIENT_EVIDENCE]**:

CC-01 microscope 未报告 caption label "FIG. 9:" / "FIG. 12:" 的
style（size/font/bold）是否与正文不同。P3 style 存在但未用于此分析。
需验证，但不能假设。

### P7.1 是否能表达 caption-like structural role?

**NO [OBSERVED]**:

P7.1 只有 REPEATS_ACROSS_PAGES 关系类型。caption 不跨页重复。
无 "caption-like role" 结构关系。

### Region 是否能表达 visual region?

**NO — VISUAL_REGION 被显式删除 [OBSERVED]**:

P6 region_schema.json:
```
deleted_region_types: {
  "TEXT_REGION": "requires semantic text-vs-nontext knowledge; ...",
  "VISUAL_REGION": "requires identifying image/figure/table; P1 has only text spans;
                    a void is not a visual object; '这是 Image' forbidden."
}
```

P6 的设计原则明确: "Region taxonomy is geometric ONLY (no heading/title/body/
caption/table/image/formula/flowchart/page_number/header/footer)"。

```
VISUAL_REGION_EVIDENCE = MISSING
```

---

## 6. M-A 是否存在与 M-B 相同的问题

**YES — 同构问题 [INFERRED + OBSERVED]**:

M-B 的问题: "local geometric concentration ≠ table"（prose 与 table 几何相同）
M-A 的问题: "same_y_band + h_gap ≠ caption association"（caption 关联与普通文本邻接几何相同）

### 主动寻找反例

必须在以下情况中测试 M-A 是否会误关联:

| 反例类型 | 当前 corpus 中是否存在? | M-A 是否会误关联? |
|----------|----------------------|------------------|
| figure + ordinary paragraph (图下方段落) | **UNKNOWN** — IS-11 无此 case | **UNKNOWN** — 无 negative 测试 |
| figure + reference text (图附近参考文献) | **UNKNOWN** | **UNKNOWN** |
| figure + footnote (图下方脚注) | **UNKNOWN** | **UNKNOWN** |
| figure + source note (图注来源) | **UNKNOWN** | **UNKNOWN** |
| figure + continuation paragraph (跨段延续) | **UNKNOWN** | **UNKNOWN** |
| "Table N:" + nearby text (表格标签 vs 图标签) | **UNKNOWN** | **UNKNOWN** — FIG-prefix 无法区分 "FIG" vs "Table" |

**关键**: 当前 corpus 中 **0 个 negative case**。无法测试 M-A 是否会在这些情况下误关联。

如果仅靠 "FIG N:" 词法 + same_y_band + h_gap ∈ (8,50]:
- "FIG. 9:" + 同行普通段落文本 → 可能误 MERGE（几何相同）
- "FIG. 9:" + 同行 reference → 可能误 MERGE
- 需要预注册负例集，但当前 corpus 无法提供

---

## 7. 最小反事实集合

### Positive (suspected caption associations)

| Case | text_a | text_b | GT | Doc | Page |
|------|--------|--------|----|-----|------|
| AMB-414 | FIG. 9: | Left: | MERGE | med_001 | 20 |
| AMB-422 | FIG. 12: | Distribution of errors... | MERGE | med_001 | 24 |

**2 positive cases, 1 document, 2 pages。**

### Negative (non-caption nearby text)

**0 cases。**

当前 IS-11 corpus 中无 figure + ordinary-paragraph / figure + reference /
figure + footnote 等 negative case。Phase3 universe 中 caption-block = 3
（universe 1299 中），但 96% 单文档集中（GraphCast），且未标注为 negative。

### Boundary / ambiguous

**0 cases。**

无 adjudicated caption-boundary case。2 个 MERGE case 均为 LEVEL_2_AGREED
（两位 reviewer 一致同意 MERGE），无分歧。

```
COUNTERFACTUAL_COVERAGE = INSUFFICIENT
```

2 positive + 0 negative + 0 boundary = 无法做受控实验。
不得自行补造 GT。

---

## 8. M-A 层级判定

### 如果只使用现有 Evidence，M-A 是否可以完成?

**NO [OBSERVED + INFERRED]**:

M-A 需要确认两个前提:
1. text_a 是 caption label（FIG N: 前缀）→ **词法可判，但必须留 hypothesis 侧**
2. text_a 和 text_b 都在 figure 附近 → **需要 visual region，当前 MISSING**

前提 1 可用词法完成（但受限: 不得进 observation 层）。
前提 2 无法用现有 Evidence 完成（VISUAL_REGION 删除 + NTB=0 矢量图）。

### 缺失的是什么?

```
缺失 = Visual Region Evidence (figure presence + position)
     ≠ Perception Algorithm (不是算法不够好)
     ≠ Evidence Organization (不是查询不够好)
     = Representation Gap (P6 无法表达 visual region)
```

具体: P6 设计时**显式选择不表达 VISUAL_REGION**（因 "requires identifying
image/figure/table; a void is not a visual object"）。non_text_block 只覆盖
raster image，不覆盖 vector drawing。2 个 MERGE 页的图是矢量绘制 → NTB=0。

**这不是"查询缺口"，是"Evidence 本身不存在"。**

---

## 9. 禁止复制的 M-B 错误

### 未经证明的推理检查

| 推理 | 是否被证明? | 问题 |
|------|-----------|------|
| near figure → caption | **NO** | 无 visual region，无法判断 "near figure" |
| same page → caption | **NO** | 同页文本不一定关联 |
| same style → caption | **UNKNOWN** | 未验证 caption style 差异 |
| reading-order adjacency → caption | **NO** | P5 无完整阅读序列 |
| text below figure → caption | **NO** | 无 visual region，无法判断 "below figure" |
| "FIG N:" prefix → caption | **PARTIAL** | 词法标记可判，但须留 hypothesis 侧；且无法区分 figure caption vs table caption |

### Evidence vs Interpretation 区分

```
Evidence (可观测):
  - text_a = "FIG. 9:" (P1 text)
  - same_y_band = True (P2)
  - h_gap = 18.11pt (P2)
  - left_alignment x≈85.04 (P2)
  - NTB = 0 (non_text_block)
  - DENSE_REGION (P6, 可能)

Interpretation (需推断):
  - "FIG. 9: 是 caption label" → 词法推断 (hypothesis-side)
  - "Left: 是 caption continuation" → 需 visual region 确认近图
  - "二者是同一 caption 单元" → 结构关联推断
```

从 Evidence 到 Interpretation 需要词法推断 + visual region 确认。
词法推断受限于"必须留 hypothesis 侧"；visual region 不存在。

---

## 10. New Observation Requirement

```
NEW_OBSERVATION_REQUIRED = TRUE
```

### 最小缺失 Evidence

**Visual Region Evidence** — figure 的存在 + 位置 (bbox)。

当前状态:
- P6 VISUAL_REGION 被显式删除（设计选择，非遗漏）
- non_text_block 只覆盖 raster image (type != 0)
- vector drawing (page.get_drawings) 不在任何 surface
- 2 个 MERGE 页 NTB=0（矢量图）

最小缺失:
1. **Figure presence + bbox** — 通过 page.get_drawings() 或 raster image block
2. **Figure ↔ text proximity** — figure bbox 与 text bbox 的空间关系

注意: 这里只识别缺失 Evidence，**不设计实现方案**。
page.get_drawings() 是 PyMuPDF 已有能力，但当前 DICE 未将其纳入任何 observation surface。

### 次要缺失

- **Caption marker typography** — caption label 是否有稳定 style 差异（P3 存在但未用于此分析）
  - 这不是新 observation（P3 已存在），但需验证 discriminative power

---

## 11. New Detector Requirement

```
NEW_DETECTOR_REQUIRED = TRUE
```

已有 Evidence 无法表达 figure presence/position → 需要 figure region detector。

但这不是"因为 consumer 不会查询已有 Evidence"——而是 **Evidence 本身不存在**。
P6 无法表达 visual region；non_text_block 无法覆盖矢量图。

注意: 当前禁止新增 detector。此判定仅记录需求，不授权实现。

---

## 12. Semantic Leap 检查

```
SEMANTIC_LEAP = TRUE
```

### 检查项

| 跳跃 | 是否存在? | 说明 |
|------|----------|------|
| geometry → caption | **YES** | same_y_band + h_gap → "caption association" 需语义判定 |
| style → caption | **UNKNOWN** | 未验证 style 差异；即使有，style → caption 也是语义跳跃 |
| adjacency → caption | **YES** | 同 y-band 邻接 → "同一 caption 单元" 需确认近图 |

### 与 M-B 的同构

M-B: "local geometric concentration → table" = SEMANTIC_LEAP (prose 几何 = table)
M-A: "same_y_band + h_gap → caption association" = SEMANTIC_LEAP
     (普通文本邻接 几何 = caption 关联)

**根本原因相同**: 无 visual/semantic signal 区分结构角色。
M-B 缺"table vs prose 区分"；M-A 缺"caption vs ordinary text 区分"。
两者都需要超出当前几何 observation 的能力。

---

## 13. Consumer Modification 检查

| 下游组件 | M-A 是否需要修改? |
|----------|-----------------|
| TLD | NO (TLD table-only, caption 不在其 scope) |
| P7.1 | NO (P7.1 是 structure hypothesis, 不改) |
| P7.3 | NO (not authorized) |
| Decision Policy | **UNKNOWN** — 如果 M-A 产生 caption-association evidence，IS-11 consumer 需要新证据类来消费它 |
| Merge/Keep Logic | **UNKNOWN** — 当前 IS-11 无 caption-association 证据类；如新增需 consumer 改 |
| Ranking | NO |
| Confidence | NO |
| Fallback | NO |
| Authority | NO |

```
CONSUMER_MODIFICATION_REQUIRED = FALSE (当前)
```

当前 consumer 不需要修改（因为 M-A 不 ready，不会产生新 evidence）。
但如果 M-A 未来 ready，IS-11 consumer 需要新增 caption-association 证据类
来消费 visual region + FIG-prefix 组合信号。这属于未来授权范围，当前不判定。

---

## 14. 历史 2 个 MERGE Cases 重新审查

### AMB-414 (med_001 p20)

| 问题 | 回答 |
|------|------|
| 为什么机器没有 MERGE? | IS-01=False ("FIG. 9:" 非数字前缀), IS-02=True ("Left:" 有文本), IS-11 is_in_table=False (TLD table-only), → INSUFFICIENT_EVIDENCE → ABSTAIN |
| 当前 Evidence 是否包含所需信息? | **PARTIAL** — P1 text ("FIG. 9:") + P2 geometry (same_y_band, h_gap=18.11) 存在；但 visual region MISSING (NTB=0, VISUAL_REGION deleted) |
| 缺的是 Query / Organization / Association? | **缺的是 Evidence (visual region)**，不是 Query。CC-01 说 EXPRESSIBLE=YES 但前提是"NTB presence" — 而 NTB=0 |
| 如果不包含，缺什么? | Visual region (figure presence + bbox) |
| 是否属于同一 mechanism? | **见下** |

### AMB-422 (med_001 p24)

| 问题 | 回答 |
|------|------|
| 为什么机器没有 MERGE? | 同 AMB-414: IS-01=False, IS-02=True, IS-11 ABSTAIN |
| 当前 Evidence 是否包含所需信息? | 同 AMB-414: P1+P2 存在, visual region MISSING |
| 缺的是 Query / Organization / Association? | 同: 缺 Evidence |
| 如果不包含，缺什么? | Visual region |

### 两个 case 是否属于同一 mechanism?

**YES — 同一 mechanism [OBSERVED]**:
- 都是 figure caption label ↔ continuation 过切
- 都是 P4 8pt 阈值 < 真实 gap (18.11/10.47) → AMBIGUOUS
- 都是 med_001 (同文档)
- 都是矢量图 (NTB=0)
- 都是 LEVEL_2_AGREED (无分歧)

```
M-A_SINGLE_MECHANISM = TRUE
```

但: n=2, 1 doc, 2 pages → 统计功效极低。

### 是否存在 counterexample?

**0 counterexample [OBSERVED]**:
- IS-11 中无 figure + ordinary-paragraph 的 KEEP_SEPARATE case
- 无 "FIG N:" + non-caption-text 的 case
- 无法测试 M-A 是否会误关联

### 是否存在 cross-document evidence?

**NO [OBSERVED]**:
- 2 cases 全部来自 med_001
- Phase3 universe 中 caption-related ≈ 6/1299，但 96% 集中于 GraphCast（不同文档）
- IS-11 corpus (med_001) 与 Phase3 corpus (GraphCast) 是不同文档集
- 无跨文档重复观测

---

## 15. Cross-framework 6.08% 重新解释

### 6.08% 到底是什么?

```
Population: 1299 AMBIGUOUS cases in Phase3 IS-14 candidate universe
            (4-doc corpus: GraphCast / ASTRO-001 / EHT / CAGI / MRI)
            — 这是 IS-14 corpus，不是 IS-11 corpus

79 "figure-context" cases = caption-block 3 + OBS-A 3 + tick-run 76 (有重叠)
prevalence = 79/1299 = 6.08%
```

### 6.08% 的分类

```
A. observed failure prevalence — NO (79 是 candidate count, 不是 failure count)
B. merge prevalence — NO (无 GT 标注)
C. framework disagreement — NO
D. candidate coverage — YES (79 个 figure-context AMBIGUOUS candidate)
E. 其他 — YES (figure-context candidate prevalence, 非 caption-association failure)
```

```
METRIC_INTERPRETATION = D (candidate coverage)
```

### 关键纠正

**6.08% ≠ caption-association failure prevalence**:

1. 79 个 figure-context 中 **76 个是 tick-run**（axis tick 序列，M-H 机制），
   不是 caption association（M-A 机制）
2. 实际 caption-related: caption-block 3 + OBS-A 3 ≈ **6/1299 = 0.46%**
3. **96.2% 集中于 GraphCast 单文档**（76/79 GraphCast）
4. IS-11 的 2 个 MERGE case 来自 **med_001**（不同 corpus，不同文档）
5. Phase3 的 caption prevalence 无法直接外推到 IS-11

### 上轮 summary 的引用纠正

`system_reframing_summary.md` 引用 "cross-framework 6.08%" 作为 M-A 价值背书。
实际:
- 6.08% 中 96% 是 tick-run（M-H），非 caption（M-A）
- caption 实际 prevalence ≈ 0.46%
- 单文档集中 96%
- 不同 corpus

**6.08% 不能作为 M-A 的 cross-framework 价值证明。**

---

## 16. 实验 Ready 的严格条件

| 条件 | 状态 | 依据 |
|------|------|------|
| EXISTING_EVIDENCE_SUFFICIENT | **FALSE** | visual region MISSING; 几何 NOT DISCRIMINATIVE |
| NEW_OBSERVATION_REQUIRED | **TRUE** | visual region / figure presence |
| NEW_DETECTOR_REQUIRED | **TRUE** | figure region detector |
| CONSUMER_MODIFICATION_REQUIRED | FALSE | 当前不需（M-A 不 ready） |
| SEMANTIC_LEAP | **TRUE** | geometry → caption 未验证 |
| COUNTERFACTUAL_COVERAGE | **INSUFFICIENT** | 2 positive, 0 negative, 0 boundary |
| MECHANISM | SPECIFIC | 同一 mechanism, 但 n=2, 1 doc |
| FALSIFIABILITY | **INSUFFICIENT** | 0 negative → 只能证明成功, 不能证明失败 |

```
M-A = NOT_READY
```

不满足 8 项条件中的 6 项。

---

## 17. 最终判断: 当前是否有安全的 algorithm experiment route?

### M-A 和 M-B 都 NOT_READY — 当前状态

| 候选 | 状态 | 阻塞原因 |
|------|------|---------|
| M-B (table locality) | NOT_READY (CLOSED) | prose=table 几何重叠; DCE-07 证伪; recovery 需改 TLD |
| M-A (caption association) | NOT_READY | visual region MISSING; 几何不判别; 0 negative; 6.08% 误读 |
| M-C (column membership) | REJECTED | PH-02 15/15 failed; patch accumulation HIGH |
| M-D (header contamination) | UNKNOWN | 0 in-frame cases; in-frame frequency NOT QUANTIFIED |
| M-E (column-blind band) | UNKNOWN | 0 独立 case; frequency NOT QUANTIFIED |
| M-F (prose boundary) | FROZEN | IS-10 HUMAN_OWNED |
| M-G (cross-page) | INSUFFICIENT | 0 cases; observation gap |
| M-I (table header role) | LOW | 0 direct impact; default correct |
| M-H (axis tick) | LOW | single doc; 0-1 impact |

### 是否有 safe algorithm route?

```
SAFE_ALGORITHM_ROUTE = NOT_CURRENTLY_AVAILABLE
```

### 原因分析（结构性，非工程性）

DICE 当前 Perception 层（P1-P7）提供**几何/结构 observation**，
但 **NO semantic content understanding** 和 **NO visual region detection**。

剩余的失败（M-B table vs prose, M-A caption vs ordinary text, figure/caption/flowchart/equation）
全部需要以下**之一**:
1. **Semantic content understanding** (LLM) — 禁止
2. **Visual region detection** (新 observation / 新 detector) — VISUAL_REGION 被 P6 显式删除;
   non_text_block 不覆盖矢量图; 新 observation 未授权
3. **Threshold tuning** (P4 8pt / TLD 0.75 / 0.45) — 禁止

这是**能力层面的结构性缺口**，不是工程层面的调优问题。

### 是否应该强行提出第三个 algorithm experiment?

**NO**。

当前证据不支持新的算法路线。不应该为了"继续推进项目"而强行提出第三个实验。

### 应该做什么?

1. **扩大/改善研究对象与失败 corpus**:
   - 当前 IS-11 (45 cases, 4 docs) 和 P7 (69 cases, 4 docs) 的 failure 类型高度集中
   - IS-11 88% TABLE; P7 39% PROSE / 23% REFERENCE
   - 需要包含 figure/caption/flowchart/equation 真实失败案例的 corpus
   - 需要 negative cases (figure + ordinary text, figure + reference)
   - 但: 不得补造 GT; 需要真实文档 + 真实人工标注

2. **定义新的可观测 Evidence**:
   - Visual region (figure presence + bbox) 是最关键的缺失
   - PyMuPDF page.get_drawings() 可提供矢量绘图信息，但当前未纳入任何 surface
   - 这是 observation 层面的扩展，不是算法层面的优化
   - 但: 新 observation 未授权; 需明确授权后才能设计

3. **重新定义研究问题**:
   - 当前研究问题假设"已有 Evidence 足够，只需更好的 Query/Organization"
   - 事实证明: 已有 Evidence **不够** — 缺 visual region + 语义区分能力
   - 需要重新定义: "DICE Document Perception 需要哪些新 observation surface
     才能支持 figure/caption/table 的结构判别?"

### 不应该做什么

- 强行提出第三个 algorithm experiment（无证据支持）
- 修改 TLD / P1-P7 / threshold（FORBIDDEN）
- 引入 LLM（FORBIDDEN）
- 补造 GT / negative cases（FORBIDDEN）
- 把 6.08% 误读当作 M-A 价值证明
- 把 EXPRESSIBLE=YES 当作 READY

---

## 18. Frozen Baseline Safety

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
TLD_MODIFICATION                    = NO
GT_MODIFICATION                     = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_ARTIFACT_MODIFICATION        = FALSE
```

本审查为 READ-ONLY，未修改任何冻结文件。

---

## 19. VGA Downstream Impact

```
DOWNSTREAM_IMPACT = UNVERIFIED
```

DICE 无真实 VGA evaluation。M-A 即使 ready (假设) 也只能建立:
```
M-A → caption association evidence → possible improvement of figure-context evidence
    → VGA impact = UNVERIFIED
```
禁止写成 "M-A → VGA improvement"。

当前 M-A = NOT_READY，VGA 讨论无实际意义。

---

## 20. Recommended Next Action

### M-A 的最小补充工作 (不授权执行，仅指出方向)

要使 M-A ready，需要以下**全部**:

1. **Visual Region Evidence** — figure presence + bbox
   - 路径: page.get_drawings() 纳入新 observation surface
   - 阻塞: 新 observation 未授权; P6 显式删除 VISUAL_REGION (需重新审视设计决策)
   - → **当前不可行 (未授权)**

2. **Negative case set** — figure + ordinary paragraph / reference / footnote
   - 需要: 真实文档 + 真实人工标注
   - 阻塞: 不得补造 GT; 当前 corpus 无此类 case
   - → **当前不可行 (无 corpus)**

3. **Cross-document validation** — caption association 在 ≥2 docs 上重复
   - 当前: 2 cases 全部 med_001 (1 doc)
   - 阻塞: 无其他文档的 caption MERGE case
   - → **当前不可行 (无 corpus)**

4. **6.08% 重新计算** — 仅 caption-related (排除 tick-run)
   - 实际: ≈ 0.46% (6/1299), 96% 单文档
   - → **已纠正 (本审查)**

### 如果 M-A 也 NOT_READY，下一步是什么?

**不强行提出第三个 algorithm experiment。**

当前证据表明: DICE 的 Document Perception 能力存在**结构性缺口**
(visual region missing + 语义区分缺失)，不是通过 algorithm experiment
可以解决的。

建议方向 (不授权):
1. 重新审视 P6 VISUAL_REGION 删除决策 — 是否需要新的 visual observation surface?
2. 扩大 corpus — 包含 figure/caption 真实失败 + negative cases
3. 重新定义研究问题 — 从"优化已有 Evidence Query"转向"需要哪些新 observation"

但这些都需要**明确授权**，本审查不授权任何行动。

---

## 最终状态

```text
M-A = NOT_READY

BLOCKING SUMMARY:
  1. VISUAL_REGION_EVIDENCE = MISSING (P6 deleted; NTB=0 for vector figures)
  2. Geometric evidence NOT DISCRIMINATIVE (same_y_band + h_gap = ordinary text adjacency)
  3. Only discriminative signal (FIG-prefix) must stay hypothesis-side
  4. COUNTERFACTUAL_COVERAGE = INSUFFICIENT (2 positive, 0 negative, 0 boundary)
  5. 6.08% misread (76/79 are tick-run M-H, not caption M-A; 96% single-doc; different corpus)
  6. SEMANTIC_LEAP = TRUE (geometry → caption unvalidated)

SAFE_ALGORITHM_ROUTE = NOT_CURRENTLY_AVAILABLE

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED      = FALSE
FROZEN_BASELINE            = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
DICE_CORE_DRIFT            = 0
PRODUCTION                 = FALSE
RUNTIME_AUTHORITY          = ZERO
STOP                       = TRUE
```

M-A = NOT_READY。当前无安全的 algorithm experiment route。
等待下一条明确授权。

`STOP = TRUE`。
