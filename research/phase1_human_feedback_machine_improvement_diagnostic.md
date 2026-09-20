# Phase 1 — Human Feedback → Machine Improvement Diagnostic

> **READ-ONLY 诊断。不实施任何 Information Source。不修改 Frozen Baseline。**
>
> 阶段: Phase 1 — Human Feedback → Machine Improvement Diagnostic
> 前置: Stage 5 COMPLETE (PRIMARY NEXT RESEARCH QUESTION = Evidence Sufficiency)
> 本阶段验证: `Human Feedback → Can it produce machine-actionable information?`

---

## 1. Executive Conclusion

**FINAL DECISION: LOOP_SUPPORTED** (附明确边界条件)

核心发现:

1. **Human feedback 包含 final decision 之外的大量的、可复用的结构信息。** 在冻结的 45-case Stage 3 证据中，45/45 个人工决策的 rationale 都引用了 case-independent 的结构概念（不同表格列、不同 cell、列头、图注、坐标轴刻度、同段落句子边界等）。仅存 final label 将丢失绝大部分信息。

2. **重复失败模式真实存在**: 88.9% (40/45) 的决策落入 ≥3 个 case 的重复模式 — TABLE_CELL_COLUMN (26), TABLE_HEADER (7), PROSE_SENTENCE_PARAGRAPH (4), FIGURE_AXIS_TICK (3)。P7.2 calibration records (33 条) 独立地呈现同样的重复模式 (TOC entry / reference marker / footnote / formula fragment)。

3. **Human Feedback → Machine Improvement 闭环已被完整演示一次** (端到端，有测量): 69-case 冻结评估中人工 FP rationale 引用 table context → IS-11 hypothesis → experiment-only observer → Stage 3/4 受控实验 → **测量到的机器改进**: ΔCoverage +17.8pp, 8/8 新增决策正确, ΔFP=0 (无退化), Determinism PASS。

4. **反事实检验结论明确**: 若 Human 永远只提供 MERGE/KEEP_SEPARATE 标签且系统永不学习新的 observable information → Baseline B coverage 永远停在 42.2% → 57.8% 弃权持续产生 → 未来人工审查工作量**不会下降，反而随文档增长**。缺失环节 = reason → machine-observable variable 的转换链。该转换链已被证明可执行（IS-11 迭代），但尚无结构化 schema 支撑、仅 n=1 次成功转换。

5. **IS-14 独立地、直接地源于本诊断发现的信息缺口** (不是来自 Stage 5 排名): 13/45 决策引用了**当前无任何 IS 覆盖**的结构角色 (TABLE_HEADER 7, FIGURE_AXIS_TICK 3, FIGURE_CAPTION 2, DIAGRAM_LIST_ITEM 1)；P7.2 records 另引用 TOC/reference/footnote/formula 角色。IS-14 = candidate information source, **HYPOTHESIS ONLY, IMPLEMENTATION = NOT AUTHORIZED**。

**LOOP_SUPPORTED 的含义边界**: 本判定授权进入受控实验**设计**讨论，不授权任何实现、不授权 IS 集成、不授权 Frozen 修改。已演示的改进是 in-sample 的、coverage-only 的 (G7 FP-reduction FAIL)；这些限制必须由下一个受控实验解决，而不是被本判定掩盖。

---

## 2. Frozen Evidence Used

全部 READ-ONLY，未重新运行任何实验:

### Stage 3 (Human Review)
| Artifact | 内容 |
|----------|------|
| `tmp/is11_semantic_ground_truth.json` | 45 cases, MERGE=2, KEEP_SEPARATE=43; 每条含 reviewer_a_rationale + reviewer_b_rationale + adjudication_rationale (free text); SHA-256 `7349963d...286959` 验证未变 |
| `tmp/is11_reviewer_a_results.json` / `_b_results.json` | 45+45 条 label + rationale |
| A/B agreement | 41/45, Kappa=0.464, 4 disagreements adjudicated |
| GT provenance audit | 6/6 PASS |

### Stage 4 (Machine Evaluation, sealed)
| Artifact | 内容 |
|----------|------|
| `tmp/is11_machine_evaluation_results.json` | 每 case 的 A/B/C 决策 + IS-01/IS-02 观察 + IS-11 观察 (in_table/cell) |
| `tmp/is11_machine_evaluation_metrics.json` | B: FP=1, Cov=42.2%; C: FP=1, Cov=60.0%; ΔFP=0, ΔCoverage=+17.8pp; G7=FAIL, G8=PASS |
| `tmp/is11_machine_evaluation_determinism.json` | PASS (0 mismatches) |
| 32/45 table unavailable | 25 TABLE_NOT_DETECTED + 7 CANDIDATE_OUTSIDE_TABLE_BBOX |

### P7.2 Validation Memory (现有 Human Feedback 存储)
| Artifact | 内容 |
|----------|------|
| `perception/sandbox/validation/validation_models.py` | ValidationRecord schema |
| `perception/sandbox/validation/validation_engine.py` | record 创建 / evidence 派生 (ACCEPT-only) 规则 |
| `perception/sandbox/validation/review_interface.py` | 确认式界面: decision + required reason + notes + duration |
| `tmp/perception/p7/p7_2_calibration/validation_records.json` | 33 条 calibration records (synthetic/ai_assisted_round1; duration 字段为非真实交互值, 仅作 schema 证据) |

### 历史闭环起点
| Artifact | 内容 |
|----------|------|
| `tmp/perception/p7/independent_machine_resolvability_results.json` | 69-case 冻结评估 (FP=3 全 TABLE_CELL, ABSTAIN=56) |
| Failure analysis | 3/3 FP 人工 rationale 引用 table/cell/column → IS-11 hypothesis 来源 |

---

## 3. Current Human Feedback Representation

### 3.1 系统实际保存了什么

**P7.2 ValidationRecord (生产 schema)**:
```
reviewer_decision : ACCEPT / REJECT / NEED_REVIEW   ← 1-click 结构化
reviewer_reason   : str (自由文本, REQUIRED)         ← 保存但从不解析
reviewer_notes    : str (自由文本, optional)
duration_seconds  : float (真实交互时间)
timestamp / reviewer_id / revision_status / provenance
```

派生规则 (`validation_engine.derive_evidence`):
- ACCEPT → ValidatedEvidence (human reason 仅复制进 `validation_provenance` 字段)
- REJECT / NEED_REVIEW → **None** (人工理由被存储，但不产生任何机器可用对象)

**Stage 3 experiment schema** (本 45-case 证据):
```
label      : MERGE / KEEP_SEPARATE               ← 结构化
rationale  : str (自由文本)                       ← 保存但从不解析
```

**关键事实**: `validation_memory.py` 与 `CapabilityCandidateObservation` 在代码库中**不存在**。当前 memory = ValidationRecord + ValidatedEvidence + ValidationAuditChain。

### 3.2 五类信息的现状区分

| 信息类别 | 是否存在 | 形态 | 机器可利用? |
|----------|---------|------|-----------|
| Final Decision | ✅ 存在 | 结构化 (label/decision) | ✅ 直接可用 |
| Decision Reason | ⚠️ 存在 | **自由文本, 未解析, 未分类** | ❌ 当前不可直接利用 |
| Evidence Context | ✅ 存在 | bbox/span_ids/decision_trace (Task 侧) | ✅ 已有 |
| Information Missing | ❌ 不存在 | — (只能由分析者交叉推导) | ❌ |
| Machine-Observable Signal | ❌ 不存在 | — (reason 从未映射到 observable) | ❌ |

**结论**: 当前系统保存了 reason 但**没有任何机制**把它转换为机器可利用的信息。Value 链在 "Decision Reason" 处断裂。

---

## 4. Information Loss Analysis

### 4.1 若只存 final label，丢失了什么

以真实证据为例（均来自冻结 Stage 3 rationale）:

| Case | Label only | 实际 rationale 携带的可复用信息 |
|------|-----------|------------------------------|
| IS11-AMB-024 | KEEP_SEPARATE | "'28.54' is **top-1 error** and '10.02' is **top-5 error** … **two different table columns**" |
| IS11-AMB-130 | KEEP_SEPARATE | "**two distinct column headers** in the Table 1 header row" |
| IS11-AMB-401 | KEEP_SEPARATE | "**adjacent axis tick labels** on the AUC axis of FIG. 8 — **separate tick marks**" |
| IS11-AMB-414 | MERGE | "both prefix fragments of the **same figure caption**, forming one continuous caption" |
| IS11-AMB-005 | KEEP_SEPARATE | "text_a **ends a sentence with a period** … text_b **starts a new sentence**" (adjudicator 使用的正是这个 machine-observable 规则) |
| IS11-AMB-380 | KEEP_SEPARATE | "**distinct base-kernel list items** in the FIG. 4 kernel-construction diagram" |

**仅存 label 时丢失**: 结构角色 (table cell/header/caption/axis/diagram/prose)、分离原因 (different column vs different cell vs sentence boundary)、合并原因 (same caption vs same paragraph)。机器无法区分 "为什么 KEEP" — 而**正是 "为什么" 决定了下一个 Information Source 应该观察什么**。

### 4.2 丢失的量化

- 45/45 rationale 引用 case-independent 结构概念 → label-only 表示丢弃 ≥95.6% 的决策理由信息
- 4 个 adjudicated 分歧中, adjudication_rationale 本身就是一条 machine-observable 规则 (period + capital → separate sentences) — label-only 完全丢失该规则
- FP 根因归因 (IS-11 gap) 在 Stage 4 中由人工分析完成 — 若无 rationale，该归因不可能

---

## 5. Feedback Value Taxonomy (基于实际证据归纳，非预设定)

> 分类方法: 对 45 条 GT rationale 做关键词分类（两名 reviewer rationale 一致时取一致类；adjudicated 时取与 final label 一致的 reviewer 类），再人工复核。分类是**分析者归纳**，非人工预先标注。

### 归纳出的概念分布 (primary classification)

| 人类引用的概念 | Cases | GT 分布 | 重复模式? |
|--------------|-------|---------|----------|
| TABLE_CELL_COLUMN (不同表格列/cell) | 26 (57.8%) | 26 KEEP | ✅ n=26 |
| TABLE_HEADER (列头对) | 7 (15.6%) | 7 KEEP | ✅ n=7 |
| PROSE_SENTENCE_PARAGRAPH (句子边界/同段) | 4 (8.9%) | 4 KEEP | ✅ n=4 |
| FIGURE_AXIS_TICK (坐标轴刻度) | 3 (6.7%) | 3 KEEP | ✅ n=3 |
| FIGURE_CAPTION (同图注) | 2 (4.4%) | **2 MERGE** | ⚠️ n=2 |
| DIAGRAM_LIST_ITEM (图示列表项) | 1 (2.2%) | 1 KEEP | ⚠️ n=1 |
| OTHER (关键词未命中) | 2 (4.4%) | 2 KEEP | — (人工复核: 实际仍引用 Dataset/Train-Size 表列, 属分类器漏检) |

### Type 分层判定

**Type 0 — Pure Resolution**: 每个决策都解决了当前 case (45/45)。Governance Value = YES, Learning Value = 单独看不成立。

**Type 1 — Repeated Failure Pattern**: **已证明存在**。4 个模式 n≥3 覆盖 40/45 (88.9%)。最大模式 TABLE_CELL_COLUMN n=26 — 同一类机器缺口被人工反复以同一概念描述。

**Type 2 — Information Gap**: **已证明存在**。将 rationale 概念与 Stage 4 机器观察交叉:

| 人类概念 | 机器 IS-11 观察 | 缺口结论 |
|----------|----------------|---------|
| TABLE_CELL_COLUMN (26) | 7 in_table / 19 unavailable | IS-11 覆盖缺口 (Stage 4 已量化) |
| TABLE_HEADER (7) | 3 in_table / 4 unavailable | 列头角色无任何 IS 判别 (IS-11 的 cell 粒度不覆盖 header 对) |
| FIGURE_AXIS_TICK (3) | 0 可用 | **无任何 IS 覆盖** |
| FIGURE_CAPTION (2, 全部 MERGE GT) | 0 可用 | **无任何 IS 覆盖** — 唯一 MERGE 类缺口 |
| DIAGRAM_LIST_ITEM (1) | 0 可用 | **无任何 IS 覆盖** |
| PROSE_SENTENCE_PARAGRAPH (4) | 0 专用 IS (IS-10 = HUMAN_OWNED, 冻结) | 观察到 adjudicator 用 period+capital 规则 — 该信号本身 machine-observable，但重开 IS-10 不在本阶段授权范围 |

**Type 3 — Machine-Observable Feedback**: **已证明可行, 已演示一次**。
- 演示链: 人工 "different table cells" 模式 → IS-11 C2 (cell_membership) → Stage 4 observer 自动从 geometry 提取 (13/45 case 无需人工逐例标注) → 受控实验 → 8/8 决策正确。
- 关键机制发现: **人工 feedback 的价值是告诉机器 "该建什么 observer" (which observable matters)，而不是逐例告诉机器观察结果** — 观察本身由机器从 geometry 自动完成。
- 未演示: 第 2 次转换 (header/axis/caption/diagram → IS-14)。

---

## 6. Governance / Diagnostic / Learning / Workload Value

| 维度 | 评估 | 证据 |
|------|------|------|
| **A. Governance Value** | **FULLY PRESENT** | 45/45 case 得到 Level-2 裁决; provenance 6/6 PASS; GT frozen |
| **B. Diagnostic Value** | **PRESENT** (需交叉机器状态, label 单独不足) | 43–45/45 决策引用结构概念 → 定位机器缺口; Stage 4 交叉确认 32/45 table gap + 13 case 无任何 IS 覆盖 |
| **C. Learning Value** | **PRESENT but n=1, in-sample** | 完整演示 1 次转换 (IS-11, +17.8pp coverage, 0 退化, determinism PASS); 第 2 次候选 (IS-14) 已识别未验证 |
| **D. Future Workload Reduction Potential** | **POTENTIAL ONLY (HYPOTHESIS)** | 机制存在且部分演示 (8 case 已变机器可判); 规模化/出样未证明; 不得宣称已降载 |

---

## 7. Machine-Observable Information Analysis

对每个归纳概念回答: 机器能否观察?

| 人类引用概念 | Machine-observable? | 观察途径 | 状态 |
|-------------|--------------------|---------|------| 
| TABLE_CELL_COLUMN | ✅ (部分已证) | 表格检测 + cell/column membership (x-alignment) | IS-11 observer 已存在 (experiment-only); Stage 4 实测 13/45 可用, cell 判别 13/13 正确; 覆盖率受限 (frozen detector) |
| TABLE_HEADER | ✅ 理论上 | 表格首行角色 / 短文本 + 表格成员 + 行位置 | 无 observer (IS-14 候选信号) |
| FIGURE_AXIS_TICK | ✅ 理论上 | 数字模式 + 小字号 + 等间距近邻 | 无 observer (IS-14 候选信号) |
| FIGURE_CAPTION | ✅ 理论上 | "FIG. N:" 前缀模式 + 位置 | 无 observer (IS-14 候选信号); **唯一 MERGE 类缺口** |
| DIAGRAM_LIST_ITEM | ⚠️ 较难 | 图示区域检测 (更难) | 无 observer |
| PROSE sentence boundary | ✅ (信号本身) | period + capital 规则 (adjudicator 实际使用) | 信号 machine-observable 但 IS-10 = HUMAN_OWNED 冻结; 本阶段不重开 |

**核心结论**: 人工引用的理由大多对应机器**原则上可自动观察**的变量。瓶颈不是 "人工必须告诉机器每个 case 的理由"，而是 (a) observer 尚未实现/评估 (IS-14), (b) 已实现 observer 的覆盖率受限 (IS-11, frozen detector)。

---

## 8. Human Effort Budget Analysis

### 8.1 现有实际负担 (来自证据)

| 协议 | Human 实际做的事 | Effort |
|------|----------------|--------|
| P7.2 interface | 1-click decision + **required 自由文本 reason** + optional notes | 1-click + 打字 |
| Stage 3 | 1-click label + 自由文本 rationale (盲审) | 1-click + 打字 |

**发现**: 当前协议已要求自由文本 reason — 且证据显示这些 reason 高度重复 (P7.2: 33 条 reason 落入 ~6 个重复模板; Stage 3: 45 条落入 ~6 个概念类)。

### 8.2 Human 不应做的事 (全部满足现状)

本阶段及现有协议均未要求 Human: 写规则、写代码、调参、判断 detector/parser 错误、标注复杂表格结构、手工建 feature、诊断机器失败 — ✅ 约束满足。

### 8.3 关键问题: reason_category 是否必要?

证据指向 **不必要增加人工字段**:
1. 45/45 Stage 3 rationale 的结构概念可以从 `page_context + geometry + machine observation` **自动交叉推导** (本报告 §5 的分类本身主要由机器可计算的关键词+Stage 4 观察完成; 仅 OTHER 2 例需人工复核)
2. P7.2 的 33 条 reason 同样呈现机器可归类的重复模板
3. Stage 4 已证明: 一旦确定 "该观察什么", 机器可**无人工参与**地自动观察 (IS-11 observer 从 geometry 提取 table context, 13 case 零人工标注)

**推断**: 相比让 Human 选择 reason_category，更符合低负担原则的是: 保留 1-click decision (+可选自由文本)，由**机器自动推断 reason 类别**，人工仅在机器推断与决策矛盾时介入。但此推断管道尚未构建 — 属于下一步实验设计的内容，本阶段不实现。

---

## 9. Minimum Additional Feedback Schema Hypothesis

> **SCHEMA HYPOTHESIS ONLY — 不得 implementation。**

| Field | Human must provide? | Can machine infer? | Human effort | Learning value |
|-------|--------------------:|--------------------|--------------|----------------|
| decision | **YES** (1-click; 现有) | NO — 这是裁决本身 | ~0 (1-click) | Governance (必选基础) |
| reason_category | **NO** (证据不支持新增) | **部分可推断** — 从 page_context+geometry+machine observation 交叉推导 (本报告 §5 演示); 矛盾时人工确认 | ~0 (若机器推断) | **HIGH** — Type 1/2 模式提取的输入 |
| evidence_scope | NO | 可推断 — bbox/page/region 已在机器侧存在 | 0 | MEDIUM — 界定模式适用范围 |
| information_missing | NO | 可推断 — 决策 + 机器观察差集 (本报告 §5 交叉表即此推导) | 0 | **HIGH** — 直接指向下一个 IS |
| reviewability | 可选 | 可推断 — duration + A/B agreement + adjudication 历史 | 0 | LOW-MEDIUM — 样本权重 |

**最小增量结论**: 唯一可能值得考虑的新字段是 **机器推断的 reason_category** (而非人工填写)。人工负担保持 1-click。是否构建该推断管道 = 下一阶段实验设计问题。

---

## 10. Can Machine Infer Feedback Reason Automatically?

**已演示的证据**:

1. **本报告 §5 的分类**: 45 条 rationale 中 43 条由关键词+结构规则自动归类; 2 条 (318, 346) 关键词漏检但人工复核确认同属 TABLE_CELL_COLUMN — 即机器可自动达到 ≥95.6% 准确率 (以人工复核为 gold, n=1 次分析)。
2. **Stage 3 adjudicator**: 4 个分歧的裁决理由 ("ends with sentence-ending punctuation and starts with capital") 本身就是一条机器可执行规则。
3. **Stage 4 IS-11 observer**: 确定观察目标后, 机器从 geometry **零人工参与**地提取了 table/cell 信息 (13/45), 且 13/13 cell 判别正确。

**限制**: 自动推断管道未构建为可复用组件; 分类词表基于本 45-case 语料 (过拟合风险); 45-case 不足以验证推断稳定性。

**结论**: 自动推断 **可行且有初步证据**，但需要独立验证 (这正是下一受控实验可以测的)。

---

## 11. Feedback Value Metrics (measurement framework only — 无阈值预注册)

| Metric | 定义 | 本冻结证据上的测量值 |
|--------|------|-------------------|
| **M1 Feedback Actionability Rate** | 决策中引用 case-independent 结构概念的比例 | 43/45 ≥ **95.6%** (严格关键词); 人工复核上限 45/45 |
| **M2 Machine-Observable Feedback Rate** | 可映射到机器可观察变量的比例 | Tier A (现有 IS-11 observer): 13/45 = **28.9%**; Tier B (若 IS-14 存在, HYPOTHESIS): 39/45 = 86.7% (假设, 非测量) |
| **M3 Repeated Failure Pattern Rate** | 落入 n≥3 重复模式的决策比例 | 40/45 = **88.9%** (4 个模式) |
| **M4 Potential Future Review Reduction** | 若映射 observer 存在且通过 gate, 理论可转机器判定的 case 比例 | 已演示 in-sample: -8/45 = -17.8pp; 假设上限: 至多再 -26 case。**POTENTIAL/HYPOTHESIS ONLY** |
| **M5 Governance-only Rate** | 仅解决当前 case、无可复用信息的比例 | 严格: 2/45 = 4.4%; 人工复核: 0/45 = 0% |

> 注: M2 Tier B 与 M4 上限是**假设值**，依赖未实现的 IS-14，不得作为预测引用。M1/M3/M5 基于 keyword 分类器 + 人工复核，45-case 样本，仅代表 "observed in current frozen evidence"。

---

## 12. Counterfactual Analysis

### 12.1 反事实检验 (要求明确回答)

> 若 Human 每次只提供 MERGE/KEEP_SEPARATE，系统永不学习新的 observable information — 人工审查能否降低未来工作量?

**答案: 不能。**

- Baseline B coverage 恒为 42.2% → 57.8% AMBIGUOUS 永远弃权 → 每个新文档持续产生同类 AMBIGUOUS case → 人工审查队列**只增不减** (随文档量线性增长)。
- 标签只解决单例 (Type 0)，不产生任何可复用变量 — M1 证明 ≥95.6% 的理由信息被丢弃。
- 结论: **Human Review ≠ Permanent Manual Fallback** 的必要条件是系统必须把反馈转换为新的 machine-observable information。

### 12.2 当前架构中缺失的环节 (基于代码/artifact 判断，非假设)

| 环节 | 状态 | 证据 |
|------|------|------|
| Feedback representation | ⚠️ **半缺失** — reason 以自由文本保存，无结构 schema | ValidationRecord.reviewer_reason (str); Stage 3 rationale (str) |
| Pattern extraction | ❌ **缺失** (人工可完成, 已由本诊断人工演示) | 无任何解析/分类组件存在 |
| Information gap identification | ⚠️ 人工完成过 (Stage 5), 无管道 | failure analysis / closure 文档为人工产物 |
| Feature / signal acquisition | ✅ 已证明可行 (IS-11 observer, experiment-only) | Stage 4: geometry → table context, 13/45 |
| Controlled experiment | ✅ 管道成熟 (Stage 3/4 协议完整可复用) | 冻结的实验设计 + GT + gates + provenance |
| Model improvement | N/A (规则系统) — 等价物 = 新 IS + 预注册 gate 评估 | IS-11 迭代即此过程 |

**缺失环节 = 前两项**: 结构化 feedback representation + pattern extraction。二者均可作为 analysis-layer 组件添加，**不触碰 Frozen Baseline**。

---

## 13. 45-Case Evidence Limitations

- GT MERGE=2 / KEEP=43 极端不平衡 → MERGE 类结论 (figure caption 模式 n=2) 统计极弱
- taxonomy 由关键词分类 + 人工复核归纳，未经独立标注验证
- 全部测量为 in-sample (45 cases, 4 PDFs, 3 领域); 不代表真实分布
- M2 Tier B / M4 上限为假设值
- P7.2 calibration records 为 synthetic/ai_assisted (duration 非真实) — 仅作 schema/模式证据, 不作工作量证据
- 一次闭环演示 ≠ 规模化验证

本报告所有结论限定为: **"observed in current frozen evidence"** 或 **"preliminary hypothesis"**。

---

## 14. Human → Machine Improvement Loop Assessment

### 14.1 六问回答

| # | 问题 | 回答 | 依据 |
|---|------|------|------|
| Q1 | Human feedback 是否含 final decision 之外的信息? | **YES** — ≥95.6% 决策含 case-independent 结构概念 (M1) | §4/§5 |
| Q2 | 能否在不增加 Human 负担下获得? | **YES (初步)** — 1-click 保留; reason 可由机器从已有 context 交叉推断 (≥95.6% 自动分类演示); 无需新增人工字段 | §8/§10 |
| Q3 | 能否转化为 machine-observable variables? | **YES (部分已证)** — IS-11 演示了 table 概念的完整转换; 其余概念理论上可观察但无 observer | §7 |
| Q4 | 这些变量能否改变未来机器决策? | **YES (已测量)** — Stage 4: 8 个原弃权 case 转为正确 KEEP_SEPARATE, ΔCoverage +17.8pp, 0 退化, determinism PASS | Stage 4 frozen |
| Q5 | 能否设计独立实验验证 Baseline vs Baseline+新信息? | **YES** — Stage 3/4 协议 (A/B/C 三条件, 盲审 GT, 预注册 gate, provenance audit) 完整成熟可复用 | Stage 3/4 设计 |
| Q6 | 若验证成功, 是否有合理机制降低未来 Human Review? | **POTENTIAL YES** — 机制存在且部分演示; 规模化与出样验证未完成; 只能称 hypothesis | M4 |

### 14.2 已演示的完整闭环 (frozen, auditable)

```
69-case 冻结评估 (FP=3 全 TABLE_CELL)
    ↓ 人工 FP rationale: "table / different columns / separate cells" (Human Feedback)
Failure Analysis → Information Gap 定性 (IS-11 缺失)
    ↓ IS-11 experiment design 冻结 (G1–G12 预注册)
IS-11 experiment-only observer (geometry → table/cell, 零逐例人工标注)
    ↓ Stage 3 盲审 GT (45 cases, 双盲 + adjudication, provenance 6/6)
Stage 4 受控 A/B/C 实验 (GT 先冻结, 确定性验证)
    ↓ 测量
机器改进: ΔCoverage +17.8pp, 8/8 新增决策正确, ΔFP=0 (无退化), Determinism PASS
    ↓
同类 case (该类型) 机器可判 → 未来此类人工审查需求下降 (该类型, in-sample)
```

**每一次转换都有冻结 artifact 可审计。这不是理论链，是已执行一次的测量链。**

---

## 15. IS-14 Relevance Assessment

**问题: IS-14 是否真的来自 Human Feedback → Machine Improvement diagnostic 发现的信息缺口?**

**回答: YES — 直接且独立地来自本诊断。**

依据 (全部来自冻结 evidence, 与 Stage 5 排名无关):

1. 13/45 人工决策引用了**当前无任何 IS 覆盖**的文档结构角色:
   - TABLE_HEADER ×7 ("two distinct column headers")
   - FIGURE_AXIS_TICK ×3 ("separate axis tick labels")
   - FIGURE_CAPTION ×2 ("parts of the same figure caption" — **全部 2 个 MERGE GT 都在此类**)
   - DIAGRAM_LIST_ITEM ×1
2. P7.2 calibration reasons 独立引用同类角色: TOC entry / reference marker / footnote marker / formula fragment
3. 唯一 FP case 的根因也属于结构角色误判 (cell value + operator 识别)
4. IS-14 的候选信号 (位置/格式/邻域模式) 均为机器可观察变量 (§7)

**但状态严格限定**:

```
IS-14 = candidate information source (evidence-grounded)
IS-14 = HYPOTHESIS ONLY
IS-14 IMPLEMENTATION = NOT AUTHORIZED
IS-14 EXPERIMENT = REQUIRES SEPARATE AUTHORIZATION + PRE-REGISTERED DESIGN
```

IS-12 (ROW_COLUMN_POSITION): 不由本诊断优先驱动 — 它是 IS-11 的子组件, 与 IS-11 共享同一 perception 依赖 (§7); 保持 HYPOTHESIS ONLY, 优先级不因本阶段提升。

---

## 16. Final Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   FINAL DECISION:  LOOP_SUPPORTED                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**判定依据** (对应 §13 定义): 当前冻结证据**已经证明** Human Feedback → Machine Improvement 具有可实验验证的结构 — 该结构不仅合理, 而且已被完整执行一次并产生测量到的机器改进 (ΔCoverage +17.8pp, 8/8 正确, 0 退化, determinism PASS, 全链 provenance)。因此满足 LOOP_SUPPORTED: "可以进入受控实验设计"。

**LOOP_SUPPORTED 的强制边界条件** (不满足则判定应降级):

1. n=1 次 IS 转换 (table context), in-sample (45 cases) — **规模化与出样验证仍未完成**
2. 已演示改进为 coverage-only; **G7 FP-reduction FAIL 未被推翻** — IS-11 的 FP 价值仍未证实
3. taxonomy 为初步归纳 (45-case, keyword+人工复核), 不声称普适
4. 本判定**只授权进入受控实验设计讨论**; 不授权实现、不授权 IS-14 observer 构建、不授权 Frozen 修改、不授权 P7.3
5. 任何下一实验必须: GT 先冻结、spec 先冻结、预注册 gate、保持 Frozen Baseline、保持 1-click 人工负担

**若下一受控实验失败** (如新 IS 无法稳定观察、产生新 FP、coverage < 现有), 应重新评估为 LOOP_PLAUSIBLE_BUT_MISSING_EVIDENCE 并分析原因; **不得**为使 loop 成立而增加复杂人工标注 (遵守 §6 Human Effort Budget)。

---

## 16. Required Safety Statement

```
IMPLEMENTATION              = NOT AUTHORIZED
NEW IS IMPLEMENTATION       = NOT AUTHORIZED
IS-14                       = HYPOTHESIS ONLY (candidate, evidence-grounded)
IS-12                       = HYPOTHESIS ONLY
FROZEN BASELINE             = INTACT (P7.1=0, P7.2=0, P4 unchanged, GT SHA unchanged)
FROZEN MODIFICATION         = NOT AUTHORIZED
P7.3                        = NOT AUTHORIZED
PRODUCTION                  = FALSE
CAPABILITY / RUNTIME        = NOT AUTHORIZED
STOP                        = TRUE
```

本阶段只判断 Human Feedback → Machine Improvement 是否具有证据基础。不实施任何新的 Information Source，不修改 Frozen Baseline，不进入 Runtime，不改变 Capability Authority。所有分析基于 READ-ONLY 读取的冻结 artifact; 无文件被修改; 无实验被重新运行; GT (SHA-256 `7349963d...286959`) 未被触碰。

---

## 17. 核心原则回顾

> Human Review 的价值不能只定义为 "帮助机器解决当前案例"，而必须进一步追问: Human 做出的判断，究竟给机器增加了什么它原来无法观察的信息?

本诊断的回答:

- **标签本身**: 只给机器 Governance value (45/45, Type 0)
- **理由 (结构概念)**: 给机器 Diagnostic value (定位缺口: table 71.1% unavailable + 13 case 零 IS 覆盖) — 但仅当与机器观察交叉时才可提取
- **理由 → observer 的转换**: 给机器 Learning value — **已演示一次** (IS-11, +17.8pp, 0 退化)
- **规模化**: Workload Reduction **潜力存在但未证明** — 这正是下一受控实验要回答的问题

链路 `Human Review → Information Gain → Machine-Observable Signal → Machine Improvement → Future Human Load ↓` 的**前四环已建立并有冻结证据; 第五环 (规模化的负载下降) 是下一个受控实验的验证对象**。

---

*Phase 1 diagnostic complete. STOP = TRUE. WAIT FOR EXPLICIT AUTHORIZATION.*
