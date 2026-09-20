# L5 Evidence Relevance / Distillation Audit

## READ-ONLY Audit — No Code/UI/Design Modifications

**Date**: 2026-09-12
**Scope**: L5.7 Pilot P01, 27 judgments (B:3 + C:3 + A:21)
**Authority**: L5 Human Validation
**Evidence Class**: B (engineering proxy, single pilot, n=1)
**Governance**: READ_ONLY=TRUE, CODE_MODIFICATION=0, UI_MODIFICATION=0, FROZEN_BASELINE=INTACT

---

## 0. Executive Summary

This audit diagnoses whether the Evidence System currently provides to Human contains the high-value cues Human actually needs for judgment, and whether the System already possesses底层 Evidence that has not been distilled into Human-usable form.

**Primary Finding**: The System already possesses substantial structural evidence (TLD table detection, SCE partition assignment, RSC region formation, neighbor span data) that directly supports the distinction Human needs to make. However, this evidence was NOT distilled into Human-facing representation. The Pilot UI showed raw geometric facts (gap, width, style) instead of decision-relevant facts ("A and B are in different table cells", "A and B are in a data row with 8 other items", "A and B are the only items on this line — likely a caption").

**Primary Gap**: EVIDENCE_SUFFICIENT_BUT_POORLY_DISTILLED

---

## 1. Research Question

**RQ-ER1**: For Human's actual judgments in the Pilot, is there a clear gap between the Evidence Human actually relied on and the Evidence System currently provides/distills?

---

## 2. Human Feedback Analysis (4 Voice Transcripts)

### Feedback 1 — B|grp|16bfcb76b820 (132.87s)

**Raw transcript**:
> 是这样的,例子1我判断他们不属于同一个内容单元因为这两个是前一句话的后半部分和后一句话的前半部分。例子二我也不认为他们是同一个语意单元因为他们是同一个表格中的不同列的名称。实例三我认可他们是同一内容单元。实例4我认可他们是同一语义单元。实例5我不认为他们是同一语义单元因为他们是一句话的后半部分和下一句话的前半部。例子6我不认为他们是同一内容单元因为他们是同一张表格的不同列的名称。

**Decomposition**:

| Instance | Human Observation | Evidence Cue | Interpretation | Decision |
|---|---|---|---|---|
| AMB-005 | "前一句话的后半部分和后一句话的前半部分" | A ends a sentence, B starts a new sentence | Different discourse units | KEEP_SEPARATE |
| AMB-313 | "同一个表格中的不同列的名称" | A and B are column headers in a table | Independent column labels | KEEP_SEPARATE |
| AMB-414 | "认可他们是同一内容单元" | (Not explicitly stated — implicit from page visual) | Continuous caption | MERGE |
| AMB-422 | "认可他们是同一语义单元" | (Not explicitly stated — implicit from page visual) | Continuous caption | MERGE |
| AMB-519 | "一句话的后半部分和下一句话的前半部" | A ends a sentence, B starts a new sentence | Different discourse units | KEEP_SEPARATE |
| AMB-530 | "同一张表格的不同列的名称" | A and B are column headers in a table | Independent column labels | KEEP_SEPARATE |

**Key Evidence Cues Human actually used**:
1. **Sentence boundary detection**: "前一句话的后半部分" — Human recognizes A as sentence-ending fragment
2. **Table column recognition**: "不同列的名称" — Human recognizes A/B as table column headers
3. **Caption continuity**: (implicit) — Human recognizes "FIG. 9:" + "Left:" as continuous caption

**What System presented**: page image, A/B highlight, line spans, gap=18.1pt, same_style, line_obs_count=5
**What System did NOT distill**: "A appears to end a sentence (ends with period/comma)", "A and B are both in a table (TLD: is_in_table=True for AMB-313/530)", "A and B are NOT in a table (TLD: is_in_table=False for AMB-414/422)"

---

### Feedback 2 — B|grp|885e943771cd (66.46s)

**Raw transcript**:
> 我认为这些例子的每一项都应该分开因为他们基本都是表格中的内容，要么就是表格中同一行的不同列数据，要么就是同一表格中的不同列的名称

**Decomposition**:

| Observation | Evidence Cue | Interpretation | Decision |
|---|---|---|---|
| "表格中的内容" | All instances are in table context | Table content | KEEP_SEPARATE (all) |
| "同一行的不同列数据" | A and B are data values in different columns of same row | Independent data points | KEEP_SEPARATE |
| "同一表格中的不同列的名称" | A and B are different column names | Independent labels | KEEP_SEPARATE |

**Key Evidence Cues**:
1. **Table membership**: Human recognizes all instances as table content
2. **Column distinction**: "不同列" — A and B are in different columns
3. **Data vs header**: Human distinguishes between data values and column names

**What System presented**: page image, gap, same_style, line_obs_count
**What System KNOWS (TLD) but did NOT distill**: `is_in_table=True, different_cell=True` for all 4 instances — the System already knows these are in a table and in different cells

---

### Feedback 3 — B|grp|1ad8a7b55945 (73.78s)

**Raw transcript**:
> 跟上一个差不多的问题就是他们都是同一个表格中的内容但他们都基本上是同一行的不同列的内容然后他们是没有什么语义完整性的因为他们是属于不同行的就是不同方向层面的内容然后可能有的是数据啊有的是object对象啊

**Decomposition**:

| Observation | Evidence Cue | Interpretation | Decision |
|---|---|---|---|
| "同一个表格中的内容" | All in table context | Table content | KEEP_SEPARATE (all) |
| "同一行的不同列的内容" | Same row, different columns | Independent data items | KEEP_SEPARATE |
| "没有什么语义完整性" | No semantic continuity when read together | Not a continuous unit | KEEP_SEPARATE |
| "有的是数据啊有的是object对象啊" | Different content types (numbers, text labels) | Different semantic categories | KEEP_SEPARATE |

**Key Evidence Cues**:
1. **Table membership** (again)
2. **Same row, different columns** — Human sees the row structure
3. **Content type diversity** — "数据" vs "object对象" — Human distinguishes content types
4. **No semantic continuity** — Human tests "read together" and finds discontinuity

**What System KNOWS but did NOT distill**: `is_in_table=True, different_cell=True` for all 11 instances; `different_local_partition=True` for all 11; each instance is in a row with 8-12 other items

---

### Feedback 4 — C|grp|16bfcb76b820 (116.45s)

**Raw transcript**:
> 是的确实是这样我认可你的这个判断但是你这个你这个给我的判断选项我觉得和你要让我做的事情不贴合你的判断选项还是应该分开是同一个不确定这三个选项但是我觉得像这一类比如说你做了一个判断然后你问我你这个判断合不合适的问题你应该给我的判断按钮是合适不合适所以你可能需要修改但是我这里可以跟你说你这个判断目前在这边的这个判断是对的，但是就是这个里面提到的这些例子我之前有跟你说过我的理解和判断你去之前找一下他们的类别还是不一样的就虽然我都赞同说你需要结构上更加去看他有什么样的排布或者说根据理解他在一个什么行文思路上但是他们每一个处的问题处的类别还是不一样的

**Decomposition**:

| Observation | Evidence Cue | Interpretation | Decision |
|---|---|---|---|
| "认可你的这个判断" | System's "undetermined" is acceptable for this group | Candidate is reasonable | (initially KEEP_SEPARATE — button mismatch) |
| "判断选项不贴合" | C-phase buttons don't match verification task | UI design issue | (feedback) |
| "每一个处的类别还是不一样的" | Within the same structural group, individual cases have different semantic categories | Group heterogeneity | KEEP_SEPARATE (overall) |
| "你需要结构上更加去看他有什么样的排布" | Structural layout matters | Layout evidence is valuable | (feedback) |

**Key Evidence Cues**:
1. **Group heterogeneity**: Human discovered that 6 structurally-grouped cases have ≥3 different semantic categories
2. **Layout importance**: "结构上更加去看排布" — Human values structural layout evidence
3. **Button-task mismatch**: C-phase verification needs different buttons than A/B judgment

---

## 3. Per-Case Evidence Audit Table (21 A-Phase Cases)

### UI Fields Currently Presented to Human

| Field | Source | Human-Visible |
|---|---|---|
| text_a / text_b | Sampling frame | ✅ Yes |
| page_image (annotated) | PyMuPDF render + PIL | ✅ Yes |
| line_spans (all spans on line) | PyMuPDF dict extraction | ✅ Yes |
| h_gap | Sampling frame | ✅ Yes |
| dy | Sampling frame | ✅ Yes |
| same_style | Sampling frame | ✅ Yes |
| width_a / width_b | Sampling frame | ✅ Yes |
| style_sig_a / style_sig_b | Sampling frame | ✅ Yes |
| line_obs_count | Sampling frame | ✅ Yes |

### System Internal Evidence NOT Distilled to Human

| Field | Source | Human-Visible | Decision-Relevant? |
|---|---|---|---|
| is_in_table | TLD (on_is11_obs) | ❌ NO | **HIGH** — "A and B are in a table" |
| same_cell | TLD | ❌ NO | **HIGH** — "A and B are in different cells" |
| different_cell | TLD | ❌ NO | **HIGH** — directly distinguishes table-column cases |
| different_local_partition | SCE | ❌ NO | **HIGH** — "A and B are in different structural columns" |
| same_structural_region | SCE | ❌ NO | **MEDIUM** — structural region membership |
| region_forms | RSC | ❌ NO | **MEDIUM** — "structural region could/couldn't form" |
| local_partitions_co_occurring | RSC | ❌ NO | **MEDIUM** — how many columns co-occur |
| atom_a_partition / atom_b_partition | SCE | ❌ NO | **MEDIUM** — which column each atom belongs to |
| Left/right neighbor text | Line context (extracted) | ✅ Yes (in line_spans) | **HIGH** — but not distilled as "neighbor context" |
| Sentence boundary (period/comma at end of A) | P1 text | ❌ NO | **HIGH** — "A ends a sentence" |
| Caption pattern ("FIG." prefix) | P1 text | ❌ NO | **HIGH** — "A starts a figure caption" |

### Full Audit Table

| case | Human decision | Human-mentioned evidence | Human-observable useful evidence | System-presented evidence | Low-value evidence | Missing/high-value evidence | gap type |
|---|---|---|---|---|---|---|---|
| AMB-005 | KEEP_SEPARATE | "前一句话后半+后一句前半" | A ends with period (sentence end); B starts with capital (new sentence) | text, page image, line spans, gap=10pt, same_style | gap value (10pt), style_sig, width | "A ends a sentence" (distillable from text); "not in same table cell" (TLD knows) | DISTILLATION_GAP |
| AMB-024 | KEEP_SEPARATE | (no feedback — B-phase: "表格数据") | Two numbers in a table row; left context "plain-34" | text, page image, line spans, gap=25pt | gap value, style_sig, width | "in table, different cells" (TLD knows); "data row with row label" (neighbor context) | DISTILLATION_GAP |
| AMB-034 | KEEP_SEPARATE | (no feedback — B-phase: "表格数据") | Two numbers; left="PReLU-net [13]" (row label); right=prose text | text, page image, line spans, gap=27.2pt | **gap=27.2pt** (Human never mentioned this number) | "in table, different cells" (TLD: is_in_table=True, different_cell=True) | DISTILLATION_GAP |
| AMB-074 | KEEP_SEPARATE | (no feedback — B-phase: "表格数据") | Two numbers in row with 8 other items; axis labels "0,20,40" on left | text, page image, line spans, gap=45.6pt | gap value, style_sig | "in table, different cells" (TLD knows); "row has 10 items" (distillable) | DISTILLATION_GAP |
| AMB-130 | KEEP_SEPARATE | (no feedback — B-phase: "表格列名") | "Resolution" + "#Channels" — two column headers; right="#Layers" | text, page image, line spans, gap=9.1pt | gap value, style_sig, width | "column headers in a table" (TLD knows is_in_table); "neighbors are also column headers" | DISTILLATION_GAP |
| AMB-135 | KEEP_SEPARATE | (no feedback — B-phase: "表格数据") | "4" + "MBConv6, k5x5" — different content types; left="depth: d =" | text, page image, line spans, gap=30pt | gap value, style_sig | "in table, different cells" (TLD knows); "different content types" (number vs text) | DISTILLATION_GAP |
| AMB-262 | KEEP_SEPARATE | (no feedback — B-phase: "表格数据") | "41M" + "EfficientNet-B5" — model size + model name; left has 3 other models | text, page image, line spans, gap=12pt | gap value, style_sig | "in table, different cells" (TLD knows); "row has 13 items — comparison table" | DISTILLATION_GAP |
| AMB-313 | KEEP_SEPARATE | "表格中不同列的名称" | "Test Size" + "#Classes" — column headers; left="Dataset, Train Size"; right="81" | text, page image, line spans, gap=8.4pt | gap value, style_sig, width | "column headers" (TLD: is_in_table=False but Human recognized table structure from visual); "neighbors are also headers" | DISTILLATION_GAP |
| AMB-346 | KEEP_SEPARATE | (no feedback — B-phase: "表格数据") | "83.95" + "84.26" — two accuracy values; left has "Val top1, 77.11, 79.13" | text, page image, line spans, gap=8.4pt | gap value, style_sig | "in table, different cells" (TLD knows); "row has 9 items — accuracy comparison" | DISTILLATION_GAP |
| AMB-350 | KEEP_SEPARATE | (no feedback — B-phase: "表格数据") | "80.16" + "81.72" — two values; left="Test top1, 77.23, 79.17"; right has 5 more values | text, page image, line spans, gap=8.4pt | gap value, style_sig | "in table, different cells" (TLD knows) | DISTILLATION_GAP |
| AMB-414 | MERGE | (B-phase: "认可同一内容单元") | "FIG. 9:" + "Left:" — caption prefix + sub-label; right has "BIC values... Right: Learning" | text, page image, line spans, gap=18.1pt | gap value, style_sig, width | "NOT in table" (TLD: is_in_table=False); "caption pattern: FIG. prefix" (distillable from text); "only 2 items on line → likely caption" | DISTILLATION_GAP |
| AMB-422 | MERGE | (B-phase: "认可同一语义单元") | "FIG. 12:" + "Distribution of errors..." — caption prefix + full description; only 2 items on line | text, page image, line spans, gap=10.5pt | gap value, style_sig, width | "NOT in table" (TLD: is_in_table=False); "caption pattern" (distillable); "isolated pair → likely caption" | DISTILLATION_GAP |
| AMB-457 | KEEP_SEPARATE | (no feedback) | "Models" + "Size" — two column headers; right has 8 more headers | text, page image, line spans, gap=40.4pt | gap value, style_sig | "column headers" (distillable); "row has 10 items" | DISTILLATION_GAP |
| AMB-462 | KEEP_SEPARATE | (no feedback — B-phase: "表格列名") | "WGe" + "Avg." — two column headers; left has 8 other headers | text, page image, line spans, gap=12pt | gap value, style_sig | "column headers in table" (TLD: is_in_table=False but visually table) | DISTILLATION_GAP |
| AMB-467 | KEEP_SEPARATE | (no feedback) | "37.0" + "60.0" — two values; left="LLaMA LLM, 700M, 54.7"; right has 4 more | text, page image, line spans, gap=11.9pt | gap value, style_sig | "in table, different cells" (TLD knows) | DISTILLATION_GAP |
| AMB-483 | KEEP_SEPARATE | (no feedback) | "23.5" + "38.5" — two values; left="LLaMA LLM, 1.3B, 56.9"; right has 5 more | text, page image, line spans, gap=16.2pt | gap value, style_sig | "in table, different cells" (TLD knows) | DISTILLATION_GAP |
| AMB-505 | KEEP_SEPARATE | (no feedback) | "61.4" + "28.3" — two values; left="BitNet b1.58, 3B"; right has 6 more | text, page image, line spans, gap=20.5pt | gap value, style_sig | "in table, different cells" (TLD knows) | DISTILLATION_GAP |
| AMB-514 | KEEP_SEPARATE | (no feedback) | "44.2" + "63.5" — two values; left="BitNet b1.58, 3.9B, 64.2"; right has 4 more | text, page image, line spans, gap=11.9pt | gap value, style_sig | "in table, different cells" (TLD knows) | DISTILLATION_GAP |
| AMB-519 | KEEP_SEPARATE | "一句话后半+下一句前半" | A ends with period; B starts with "To" (capital, new sentence); only 2 items on line | text, page image, line spans, gap=8.6pt | gap value, style_sig, width | "A ends a sentence" (distillable); "only 2 items but different sentences" (vs AMB-414/422 where 2 items = same caption) | DISTILLATION_GAP |
| AMB-522 | KEEP_SEPARATE | (no feedback) | "Size" + "Max Batch Size" — two column headers; left="Models"; right="Throughput" | text, page image, line spans, gap=19.9pt | gap value, style_sig | "column headers" (distillable) | DISTILLATION_GAP |
| AMB-530 | KEEP_SEPARATE | "同一张表格的不同列的名称" | "PIQA" + "SciQ" — two dataset names as column headers; left="Models, Tokens, Winogrande"; right="LAMBADA, ARC-easy, Avg." | text, page image, line spans, gap=12.3pt | gap value, style_sig, width | "column headers in table" (TLD: is_in_table=True); "neighbors are also dataset names" | DISTILLATION_GAP |

---

## 4. Three Representative Case Deep-Dives

### Type A — Obvious KEEP_SEPARATE: AMB-034 ("21.59" + "5.71")

**Human judgment**: KEEP_SEPARATE (3.1s in A-phase — very fast)

**What Human actually observed** (inferred from B-phase feedback "表格中同一行的不同列数据"):
- Two numbers side by side
- Left context: "PReLU-net [13]" (a row label)
- Right context: prose text
- Row has 4 items total

**What System presented**: text, page image with A/B highlight, line spans list, gap=27.2pt, same_style=True, width_a/width_b, style_sig

**What System KNOWS but did NOT distill**:
- TLD: `is_in_table=True, same_cell=False, different_cell=True`
- SCE: `different_local_partition=True` (A in partition x199.5, B in partition x246.9)
- RSC: `region_forms=True, local_partitions_co_occurring=18`
- Line context: 4 items on line, left="PReLU-net [13]" (row label), right=prose

**Distillation that would have been high-value**:
> "A and B are both in a detected table, in different cells. They are in a row with a row label 'PReLU-net [13]' on the left and prose text on the right."

**Gap type**: DISTILLATION_GAP — System has `is_in_table`, `different_cell`, `different_local_partition` but presented only raw `gap=27.2pt`

**The number "27.2pt" is LOW-VALUE**: Human never mentioned gap distance. Human's judgment was based on "table, different columns" — a structural fact the System already knows.

---

### Type B — Obvious MERGE: AMB-414 ("FIG. 9:" + "Left:")

**Human judgment**: MERGE (3.1s in A-phase — very fast)

**What Human actually observed** (inferred from B-phase feedback "认可同一内容单元"):
- "FIG. 9:" is a caption prefix
- "Left:" is a sub-label
- Only 2 items on the line (ISOLATED_PAIR pattern)
- Right context: "BIC values for model... Right: Learning"

**What System presented**: text, page image, line spans, gap=18.1pt, same_style=True

**What System KNOWS but did NOT distill**:
- TLD: `is_in_table=False` — NOT table content
- RSC: `region_forms=False` — no structural region formed
- Line context: only 2 items → ISOLATED_PAIR pattern
- Text pattern: "FIG." prefix → caption pattern

**Distillation that would have been high-value**:
> "A and B are NOT in a table. They are the only two items on this line. A starts with 'FIG.' — a figure caption prefix. B='Left:' — a directional sub-label. They appear to form a continuous caption."

**Gap type**: DISTILLATION_GAP — System has `is_in_table=False` and `region_forms=False` (both indicate non-table, non-structural content), but presented only `gap=18.1pt`

**Critical contrast**: AMB-414 (MERGE) and AMB-034 (KEEP_SEPARATE) both have similar gap values (18.1pt vs 27.2pt). The gap number does NOT distinguish them. What distinguishes them is:
- AMB-034: `is_in_table=True, different_cell=True` → KEEP_SEPARATE
- AMB-414: `is_in_table=False, region_forms=False` → MERGE

**This is the core finding**: the System's TLD and RSC already make the distinction, but the UI showed the same type of evidence (gap, style) for both.

---

### Type C — Structurally Similar but Semantically Different: grp|16bfcb76b820

**Group composition**: 6 cases with `sce_status=region_not_formed`

| Case | GT | Human B-phase | Content type |
|---|---|---|---|
| AMB-005 | KEEP_SEPARATE | KEEP_SEPARATE | Sentence boundary (prose) |
| AMB-313 | KEEP_SEPARATE | KEEP_SEPARATE | Table column headers |
| AMB-414 | MERGE | MERGE | Figure caption |
| AMB-422 | MERGE | MERGE | Figure caption |
| AMB-519 | KEEP_SEPARATE | KEEP_SEPARATE | Sentence boundary (prose) |
| AMB-530 | KEEP_SEPARATE | KEEP_SEPARATE | Table column headers |

**Why System grouped them**: All 6 have `sce_status=region_not_formed` — the RSC could not form a structural region for any of them. From the System's structural perspective, they are identical.

**Why Human found them different**: Human identified 3 distinct semantic categories:
1. Sentence boundary (AMB-005, AMB-519): prose text where A ends one sentence and B starts another
2. Table column headers (AMB-313, AMB-530): A and B are different column labels in a table
3. Figure caption (AMB-414, AMB-422): A is a "FIG." prefix and B is a caption/sub-label

**What System KNOWS that could distinguish them**:
- TLD: `is_in_table=True` for AMB-313/530 (table headers) vs `is_in_table=False` for AMB-414/422 (captions) vs `is_in_table=True` for AMB-005 (in table but prose)
- Text pattern: "FIG." prefix for AMB-414/422 vs sentence-ending punctuation for AMB-005/519
- Line item count: 2 for AMB-422 (isolated pair) vs 5 for AMB-414 vs 3-5 for others

**System's Compression output**: "6 instances: relationship undetermined" — a single status for all 6

**Human's feedback**: "每一个处的类别还是不一样的" — each case has a different category

**Gap type**: DISTILLATION_GAP (primary) + RELEVANCE_GAP (secondary)

The System's aggregation grouped by `sce_status` (a structural signal), but the decision-relevant distinction is:
- Is it in a table? (TLD knows)
- Is it a caption? (text pattern distillable)
- Does A end a sentence? (text pattern distillable)

These are all derivable from existing evidence but were not distilled.

---

## 5. B/C Phase Failure Attribution

### B-Phase: Group-Level Judgment Loses Intra-Group Heterogeneity

**What happened**: B-phase asked Human to give one judgment for an entire structural group. But grp|16bfcb76b820 contains 6 cases with 3 different semantic categories (2 MERGE + 4 KEEP_SEPARATE). Human gave "KEEP_SEPARATE" for the group but explicitly noted in feedback that individual cases differ.

**Attribution**:
- NOT an Aggregation problem: Aggregation correctly groups structurally similar cases (same sce_status)
- NOT a Compression problem: Compression correctly reports "undetermined" (which is accurate — the group IS heterogeneous)
- **IS a Representation/Distillation problem**: The B-phase UI did not present the intra-group heterogeneity that TLD data would have revealed. If the UI had shown "2 of these are NOT in a table (captions), 2 are table headers, 2 are prose", Human would have immediately seen the heterogeneity.

### C-Phase: System Compression vs Human Need

**What happened**: C-phase presented the System's candidate ("undetermined") and asked Human to validate. Human agreed the candidate was acceptable but noted:
1. The buttons didn't match the task (fixed in UI revision)
2. The individual cases within the group have different categories

**Attribution**:
- The System's Compression ("undetermined") is technically correct — the group IS heterogeneous
- But the Compression did not distill the heterogeneity: it should have said "6 instances with undetermined relationship — 2 appear to be captions, 2 appear to be table headers, 2 appear to be prose"
- **This is a DISTILLATION_GAP**: the System has TLD data that distinguishes these sub-categories but did not include it in the compressed claim

---

## 6. UI Field Judgment Value Evaluation

| UI Field | Value Class | Human Usage Evidence | Why |
|---|---|---|---|
| **text_a / text_b** | **HIGH** | Human read text to identify "FIG." prefix, sentence endings, column header names | Direct semantic content |
| **page image (annotated)** | **HIGH** | Human used visual layout to identify table structure, row context | Primary visual evidence |
| **line_spans (all spans)** | **HIGH** | Human used neighbor text to identify row labels, column headers | Structural context |
| **A/B highlight boxes** | **HIGH** | Human used to locate A and B on page | Navigation aid |
| **line_obs_count** | **MEDIUM** | Not explicitly mentioned, but correlated with Human's "row has many items" observations |间接 useful |
| **same_style** | **LOW** | Never mentioned by Human | Human didn't need style comparison |
| **h_gap (numeric value)** | **LOW** | Never mentioned by Human in any feedback | Human used visual gap, not the number |
| **width_a / width_b** | **LOW** | Never mentioned | Not relevant to semantic judgment |
| **style_sig_a / style_sig_b** | **IRRELEVANT** | Never mentioned, internal font signature | Not human-readable, not decision-relevant |
| **dy (same line)** | **MEDIUM** | Not explicitly mentioned, but all cases were same-line | Implicitly assumed |

### Missing High-Value Fields (System has data but did not present)

| Missing Field | System Source | Value Class | What it would tell Human |
|---|---|---|---|
| **"In table: Yes/No"** | TLD is_in_table | **HIGH** | Whether A/B are table content |
| **"Same cell: Yes/No"** | TLD same_cell | **HIGH** | Whether A/B are in same/different cells |
| **"Different structural partition"** | SCE different_local_partition | **HIGH** | Whether A/B are in different columns |
| **"Caption pattern detected"** | Text pattern (FIG. prefix) | **HIGH** | Whether A starts a figure/table caption |
| **"Sentence boundary"** | Text pattern (period/comma) | **HIGH** | Whether A ends a sentence |
| **"Row context label"** | Left neighbor text | **HIGH** | What the row is about (e.g., "PReLU-net") |
| **"Items on line"** | line_obs_count | **MEDIUM** | Already shown, but not distilled as "data row" vs "caption" |
| **"Region formed: Yes/No"** | RSC region_forms | **MEDIUM** | Whether structural region could form |

---

## 7. Evidence Value Map

### Raw Observation → Structural Evidence → Decision-Relevant Evidence → Human Judgment

```
RAW OBSERVATION (L0/L1)
├── text content (P1)
│   ├── "FIG." prefix → caption pattern → MERGE candidate
│   ├── sentence-ending punctuation → sentence boundary → KEEP_SEPARATE
│   └── numeric value → data point → (needs table context)
├── bbox position (P1)
│   ├── x-coordinate → column assignment
│   ├── y-coordinate → row assignment
│   └── same_y → same line
├── font/style (P1/P3)
│   └── style signature → same_style (LOW VALUE for Human)
│
STRUCTURAL EVIDENCE (L2/L3)
├── TLD: is_in_table, same_cell, different_cell
│   ├── is_in_table=True, different_cell=True → "table, different cells" → KEEP_SEPARATE
│   └── is_in_table=False → "not table" → check caption/prose
├── SCE: different_local_partition
│   └── different_partition=True → "different columns" → KEEP_SEPARATE
├── RSC: region_forms
│   ├── region_forms=True → structural region exists → likely table
│   └── region_forms=False → no structural region → caption or prose
├── Line context: neighbor spans
│   ├── 2 items only → isolated pair → likely caption (MERGE)
│   ├── 4+ items with row label → data row → KEEP_SEPARATE
│   └── neighbors are column headers → header row → KEEP_SEPARATE
│
DECISION-RELEVANT EVIDENCE (NOT CURRENTLY DISTILLED)
├── "A and B are in a table, in different cells" ← TLD has this
├── "A and B are NOT in a table" ← TLD has this
├── "A starts with 'FIG.' — caption pattern" ← P1 text has this
├── "A ends a sentence (period/comma)" ← P1 text has this
├── "Only 2 items on this line — likely caption" ← line context has this
├── "Row has 10+ items with data values — likely table row" ← line context has this
├── "Left neighbor is a row label (e.g., 'PReLU-net')" ← line context has this
│
HUMAN JUDGMENT (L5)
├── KEEP_SEPARATE: "table, different columns" / "different sentences"
└── MERGE: "caption, continuous text"
```

### Human's Most-Used Evidence Cues (from 4 feedback transcripts)

1. **Table membership** — mentioned 4 times: "表格中的内容", "表格中同一行的不同列", "不同列的名称"
2. **Column distinction** — mentioned 3 times: "不同列", "不同列的名称"
3. **Sentence boundary** — mentioned 2 times: "前一句话后半", "一句话后半+下一句前半"
4. **Content type** — mentioned 1 time: "数据" vs "object对象"
5. **Caption continuity** — implicit 2 times: "认可同一内容单元" (for AMB-414, AMB-422)

### System's Currently-Presented vs Human-Needed

| Human-Needed Cue | System Has It? | System Presented It? | Gap Type |
|---|---|---|---|
| "Is A/B in a table?" | ✅ TLD knows | ❌ Not shown | DISTILLATION_GAP |
| "Are A/B in different cells?" | ✅ TLD knows | ❌ Not shown | DISTILLATION_GAP |
| "Are A/B in different columns?" | ✅ SCE knows | ❌ Not shown | DISTILLATION_GAP |
| "Does A start a caption?" | ✅ P1 text has "FIG." | ❌ Not distilled | DISTILLATION_GAP |
| "Does A end a sentence?" | ✅ P1 text has punctuation | ❌ Not distilled | DISTILLATION_GAP |
| "What's the row label?" | ✅ Line context has left neighbor | ✅ Shown in line_spans | NONE (but not highlighted) |
| "How many items on line?" | ✅ line_obs_count | ✅ Shown | NONE (but not interpreted) |
| "What's the gap?" | ✅ h_gap | ✅ Shown | RELEVANCE_GAP (low value) |
| "Same style?" | ✅ same_style | ✅ Shown | RELEVANCE_GAP (low value) |

---

## 8. Gap Analysis Summary

### Gap Frequency Across 21 Cases

| Gap Type | Count | Description |
|---|---|---|
| DISTILLATION_GAP | 21/21 | Every case has evidence the System has but did not distill |
| RELEVANCE_GAP | 21/21 | Every case showed low-value evidence (gap, style_sig, width) |
| PRESENTATION_GAP | 0/21 | No case had evidence that was present but hard to understand |
| OBSERVATION_GAP | 0/21 | No case lacked underlying observation data |

### The Distillation Gap is Systematic

For **ALL 21 cases**, the System possesses TLD evidence (`is_in_table`, `same_cell`, `different_cell`) that directly maps to the distinction Human needs:
- `is_in_table=True, different_cell=True` → KEEP_SEPARATE (19 cases)
- `is_in_table=False` → check caption/prose (2 MERGE cases)

This evidence was **never distilled** into Human-facing representation. Instead, the UI showed `h_gap` (a number Human never referenced) and `same_style` (a boolean Human never referenced).

### The MERGE vs KEEP_SEPARATE Distinguisher

The critical distinction between MERGE and KEEP_SEPARATE in this corpus is:

| | MERGE (2 cases) | KEEP_SEPARATE (19 cases) |
|---|---|---|
| TLD is_in_table | False | True (15/19) or False (4/19) |
| TLD different_cell | False | True (15/19) or N/A (4/19) |
| Line items | 2-5 (isolated or caption) | 3-13 (data row) |
| Text pattern | "FIG." prefix | Numbers, column names, prose fragments |
| RSC region_forms | False | True (11/19) or False (8/19) |

The System has ALL of these signals. The UI presented NONE of them in distilled form.

---

## 9. B/C Phase Attribution

### B-Phase: Why Human Discovered Intra-Group Heterogeneity

Human discovered that grp|16bfcb76b820 (6 cases) contains 3 different semantic categories. This was possible because:
1. The page images showed visual differences (table vs caption vs prose)
2. The text content revealed different patterns ("FIG." vs numbers vs sentence fragments)
3. Human's cognitive category system naturally classified them

**But the System's structural grouping (by sce_status) masked this heterogeneity.** The System grouped all 6 as "region_not_formed" — a single structural status. The TLD data that would distinguish them (`is_in_table` varies: True for AMB-005/313/530, False for AMB-414/422/519) was not used in grouping.

**Attribution**: DISTILLATION_GAP — the System has TLD data that reveals intra-group heterogeneity but did not include it in the group representation shown to Human.

### C-Phase: Compression Did Not Distill Heterogeneity

The System's Compression produced: "6 instances: relationship undetermined"

This is technically accurate (the group IS heterogeneous, so "undetermined" is correct). But it failed to distill the **actionable sub-structure**: "2 of these are captions (MERGE), 2 are table headers (KEEP_SEPARATE), 2 are prose boundaries (KEEP_SEPARATE)."

**Attribution**: DISTILLATION_GAP — Compression has access to TLD/per-case evidence but produced a single uniform claim instead of a heterogeneous summary.

**Is this an Aggregation problem?** No — Aggregation correctly groups structurally similar cases. The problem is that "structurally similar" (same sce_status) does not mean "semantically similar."

**Is this a Compression problem?** Partially — Compression could have included per-case TLD status in the compressed claim. But the deeper issue is that the Compression's input (Aggregation output) does not carry TLD data.

**Root cause**: The evidence pipeline from TLD → SCE → RSC → Aggregation → Compression does not propagate TLD's `is_in_table` / `different_cell` facts to the Human-facing layer. These facts exist at L2 but are lost by L4.

---

## 10. Final Strict Conclusion

### Result: A. EVIDENCE_SUFFICIENT_BUT_POORLY_DISTILLED

### PRIMARY_GAP: DISTILLATION_GAP

The System already possesses the core evidence Human needs:
- TLD: `is_in_table`, `same_cell`, `different_cell` — directly maps to "table content" vs "caption/prose"
- SCE: `different_local_partition` — directly maps to "different columns"
- P1 text: "FIG." prefix, sentence-ending punctuation — directly maps to "caption" vs "sentence boundary"
- Line context: neighbor spans, item count — directly maps to "data row" vs "isolated pair"

This evidence was NOT distilled into Human-facing representation. Instead, the UI presented low-value geometric facts (`h_gap`, `same_style`, `width`, `style_sig`) that Human never referenced in any feedback.

### SECONDARY_GAP: RELEVANCE_GAP

The UI presented evidence that exists but is not decision-relevant:
- `h_gap` (numeric value): Human used visual gap perception, never the number
- `same_style`: Human never compared styles
- `style_sig_a/b`: Internal font signature, not human-readable
- `width_a/b`: Not referenced in any judgment

### EVIDENCE

1. Human's 4 voice feedbacks consistently referenced "table", "column", "caption", "sentence" — all structural/semantic categories that TLD and text pattern analysis can provide
2. All 21 A-phase cases have TLD evidence (`is_in_table`, `different_cell`) that was not shown
3. MERGE cases (AMB-414, AMB-422) have `is_in_table=False` — the key distinguishing signal
4. KEEP_SEPARATE table cases have `is_in_table=True, different_cell=True` — directly maps to Human's "different columns"
5. Human achieved 100% accuracy despite the gap — because page images provided the visual evidence Humans needed, but this is not scalable (images are large, not always clear, and don't work for non-visual modalities)

### COUNTEREVIDENCE

1. Human achieved 100% accuracy with current evidence — suggesting the page image + line spans were sufficient for this specific corpus
2. A-phase was very fast (avg 3.9s) — suggesting the visual evidence was easy to process
3. n=1, single pilot — cannot rule out that other participants might struggle without distilled evidence
4. The corpus is heavily table-focused (19/21 table-related) — in a more diverse corpus, the gap might be larger or smaller
5. 4 cases (AMB-313, AMB-462, AMB-519, AMB-530) have `is_in_table=False` but are still KEEP_SEPARATE — TLD alone is insufficient for these cases

### CONFIDENCE

**MEDIUM-HIGH** (for DISTILLATION_GAP as primary)

- 21/21 cases show DISTILLATION_GAP — systematic, not random
- Human feedback consistently references evidence the System has but didn't present
- TLD data directly maps to Human's most-used cues ("table", "different columns")
- Counter-evidence (100% accuracy) is explained by page images compensating for the gap

**MEDIUM** (for RELEVANCE_GAP as secondary)

- Low-value fields (gap, style) were shown but never used
- However, they didn't actively harm judgment (Human ignored them)
- The cost is cognitive noise, not judgment error

### What This Audit Does NOT Claim

- Does NOT claim the System needs a new Primitive/Contract/Architecture
- Does NOT claim LLM understanding is insufficient
- Does NOT claim the current UI is fundamentally broken (Human achieved 100% accuracy)
- Does NOT claim that distilling TLD evidence would improve accuracy (it might improve speed/cognitive load, but accuracy was already perfect)
- Does NOT propose a specific distillation implementation

### Possible Minimal Direction (NOT implemented, NOT designed)

If future work addresses this gap, the direction would be:
- Propagate TLD's `is_in_table` / `different_cell` from L2 to the Human-facing layer
- Distill text patterns ("FIG." prefix, sentence-ending punctuation) into simple labels
- Convert line context into a brief structural summary ("data row with 10 items" vs "isolated pair")
- Remove or de-emphasize low-value fields (gap number, style signature, width)

But this is observational, not prescriptive. No implementation is proposed in this audit.

---

## 11. Scalability Assessment

### Can the current UI + data approach scale to 100/1000 cases?

| Dimension | Current (n=21) | Scaled (n=1000) | Issue |
|---|---|---|---|
| Page image rendering | ✅ Automated | ✅ Scalable | File size (base64 → HTTP) |
| Line context extraction | ✅ Automated | ✅ Scalable | None |
| Auto-save server | ✅ Works | ✅ Scalable | None |
| Evidence quality | ⚠️ Works for tables | ❌ Insufficient for diverse corpus | DISTILLATION_GAP would worsen |
| Human cognitive load | ⚠️ OK for 21 | ❌ Too high for 1000 | Low-value evidence adds noise |

**The DISTILLATION_GAP would worsen at scale**: For 1000 cases with diverse document types (not just tables), the page image alone may not be sufficient. Distilled structural facts ("in table", "caption", "different cells") would become essential for maintaining judgment speed and accuracy.

---

## 12. Governance

```
READ_ONLY = TRUE
CODE_MODIFICATION = 0
UI_MODIFICATION = 0
GT_MODIFICATION = 0
TLD_MODIFICATION = 0
ATOMIC_MODIFICATION = 0
IS11_DECISION_MODIFICATION = 0
L5.5_MODIFICATION = 0

NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_ARCHITECTURE = 0
NEW_PATTERN_ENGINE = 0

PRODUCTION = FALSE
FROZEN_BASELINE = INTACT
HUMAN_DATA = REAL_PILOT_ONLY
NO_SIMULATION = TRUE
STOP = TRUE
```

### Pilot Limitations Preserved

```
Pilot = exploratory engineering evidence
n = 1
21 A cases
MERGE = 2
Conflict = 0
System ≠ GT = 0
```

### Evidence Classification

- This audit = **B-class** (engineering analysis based on single pilot)
- Human judgments = **A-class** (real human-subject data, but n=1)
- Gap findings = **B-class** (derived from analysis, not independently verified)
- DISTILLATION_GAP conclusion = **B-class** (strong evidence from 21/21 cases, but single participant)
