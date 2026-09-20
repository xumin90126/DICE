# P7 Validation Plan

> 本轮不写识别测试。本文档定义未来 P7 实现后必须通过的验证维度与断言。

---

## 1. Structural Correctness（结构正确性）

| 指标 | 定义 |
|---|---|
| hypothesis_coverage | 每个「应当产生假设」的对象是否有对应 hypothesis（基于手工标注的 golden set） |
| false_positive_count | 产生了 hypothesis 但 golden 标记为「不应产生」的数量 |
| false_negative_count | golden 标记为「应产生」但未产生的数量 |
| ambiguous_classification_count | 证据冲突时是否正确标 AMBIGUOUS（而非强猜） |
| confidence_calibration | hypothesis 置信度与其「验证通过率」的单调性 |

**断言**：false_positive 与 false_negative 在 P7.1 的几何/样式确定性对象上应低；对弱信号对象（caption/formula/page-number/reference）允许较高 false rate，但必须落入 `confidence=UNKNOWN/LOW` 桶，而非误报为 HIGH。

---

## 2. Traceability（可追溯性）

验证链完整：

```
StructureHypothesis
  → source_region_ids  → P6 RegionObservation
  → source_span_ids    → P4 ExperimentalSpan
  → source_observation_ids → P1 Atomic (经 span 回溯)
  → style_facts / geometry_facts / order_facts（经 observation_id 引用）
```

**断言**：
- 每个 hypothesis 的 `supporting_facts` 必须能沿引用链回溯到具体 observation/span/region。
- 不得出现「无来源的结论字段」。
- `decision_trace` 的每条决策必须引用具体事实值（数值/布尔），而非空泛描述。

---

## 3. Uncertainty Propagation（不确定性传播）

**断言**（违反即回归失败）：
- 对每个 hypothesis，`hypothesis.confidence` 不得高于 `min(引用上游置信度)`，除非 decision_trace 中有「新增独立证据」的可解释提升记录。
- 上游 `LOW / AMBIGUOUS / UNKNOWN` 必须在 hypothesis 的 provenance 中保留原文。
- 冲突证据必须出现在 `conflicting_evidence`，不得被静默丢弃。

---

## 4. No Semantic Leakage（无语义泄漏）

静态 + 行为双重检查，禁止以下单信号 shortcut：

```
if bold → heading            ❌
if aligned → table           ❌
if small text → caption      ❌
if large rectangle → image   ❌
if empty gap → figure        ❌
if many aligned spans → table❌
if numeric → page_number     ❌
if document_id == "RM501" → ❌
```

**断言**：P7 引擎源码中不得出现「单类事实直接映射到结构类型」的分支；所有 hypothesis 必须由 ≥2 类独立证据合成（见 text_structure_contract / structure_concept_matrix）。

---

## 5. Human Validation 可审阅性（Human Validation）

验证「人能否完整审阅一个 hypothesis」，每个 hypothesis 的展示必须包含：

- hypothesis 类型 + 置信度
- supporting_evidence（支持证据，含数值）
- conflicting_evidence（冲突证据，如有）
- source_span（文本内容 + bbox）
- source_region（region_type + bbox）
- decision_trace（为什么这么判）
- 上游置信度引用（不被抹除）

**断言**：human gate 界面必须能显示以上全部字段；缺字段 → 视为不可审阅，回归失败。

---

## 6. 验证方式（未来 P7 落地后）

1. **单元断言**：对每个 synthetic 结构场景（heading 对比、列表对齐、表格行列对齐、孤立公式等）断言 hypothesis 产出 + confidence 传播正确。
2. **回归门**：复用 P6 的 regression_gate，确保 P7 不改 P1–P6 / Frozen 730 / C1 / restore frozen。
3. **Deterministic rerun**：同一输入两次运行，hypothesis 集合与 confidence 完全一致。
4. **Golden-set 对比**：在人工标注的少量页面（RM501/DC201/arxiv）上计算 precision/recall/ambiguous rate。
5. **Confidence calibration**：把 hypothesis 按置信桶分组，检验验证通过率随置信单调上升。
