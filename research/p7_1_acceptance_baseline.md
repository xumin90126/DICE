# P7.1 Acceptance Baseline — StructureHypothesis Foundation

> 本文档将 P7.1 从「实现完成」正式固化为「可复现、可审计、可冻结」的基线，并记录下一阶段真正的 Evidence 缺口。
> 本轮为 READ-ONLY 复核：未新增任何结构算法，未修改 P1–P6，未进入 P7.2 / P7.3 / P8。

---

## 1. Acceptance Status

**ACCEPTED** — 全部 10 项独立验收指标通过：

| # | 指标 | 结果 |
|---|---|---|
| 1 | deterministic = True | ✅ True（重跑 5 例，hypothesis/relation 数与类型分布完全一致） |
| 2 | provenance completeness = 1.0 | ✅ 1.0 |
| 3 | decision_trace completeness = 1.0 | ✅ 1.0 |
| 4 | semantic_leakage = 0 | ✅ 0 |
| 5 | negative_case_failure = 0 | ✅ 0 |
| 6 | blocked type leakage = 0 | ✅ 0（TABLE/IMAGE/FORMULA/FLOWCHART 等均未出现） |
| 7 | P1–P6 regression = True | ✅ True（SHA256 与 P6 基线逐字节一致） |
| 8 | Frozen 730 md5_8 = a10b368e | ✅ a10b368e |
| 9 | Annotation / C1 / C2 / Evidence / Capability / Runtime 未修改 | ✅ 未修改（见 §12） |
| 10 | P7.2 / P7.3 保持 BLOCKED | ✅ BLOCKED |

---

## 2. Frozen Files

P7.1 实现自此冻结（禁止为「优化准确率」修改算法）：

```
perception/sandbox/structure/structure_config.py
perception/sandbox/structure/structure_relation.py
perception/sandbox/structure/structure_hypothesis.py
perception/sandbox/structure/structure_engine.py
perception/sandbox/structure/__init__.py
perception/sandbox/p7_runner.py
```

机器可读哈希清单：`tmp/perception/p7/p7_1_freeze_hashes.json`、`p7_1_acceptance_metrics.json`。

---

## 3. Baseline Hashes（SHA256 前 16 位）

| 文件 | SHA256 (16) |
|---|---|
| structure_config.py | `6924631dc6fa01b5` |
| structure_relation.py | `95719a919bebd89b` |
| structure_hypothesis.py | `a2f3bd9c8dff771b` |
| structure_engine.py | `7512167fa1689d92` |
| structure/\_\_init\_\_.py | `3e90a7d68c7ed9bc` |
| p7_runner.py | `d5f18439969a74c2` |

冻结后重跑一次完整验证，哈希 **UNCHANGED**（冻结完整性确认）。

---

## 4. Hypothesis Metrics

- **total_hypotheses = 175**（合成 11 例 + 真实 4 文档）
- 状态分布：**PROPOSED = 175**（100%），Human Validated = **0**，等待 Human Validation = **175**

| 类型 | 数量 | 置信度分布 | span coverage(真实) | region coverage(真实) |
|---|---|---|---|---|
| HEADING_CANDIDATE | 67 | LOW 58 / MEDIUM 9 / HIGH 0 | 0.353 | 0.655 |
| PARAGRAPH_GROUP_CANDIDATE | 28 | HIGH 9 / MEDIUM 9 / LOW 10 | 0.947 | 0.793 |
| SECTION_CANDIDATE | 67 | LOW 63 / MEDIUM 4 | 0.988 | 0.931 |
| LIST_CANDIDATE | 8 | HIGH 1 / MEDIUM 7 | 0.106 | 0.517 |
| HEADER_CANDIDATE | 2 | LOW 2 | 0.000 | 0.000 |
| FOOTER_CANDIDATE | 2 | LOW 2 | 0.000 | 0.000 |
| MULTI_COLUMN_CONTINUATION_CANDIDATE | 1 | MEDIUM 1 | 0.000 | 0.000 |

---

## 5. Relation Metrics

- **total_relations = 367**
- 分布：ADJACENT_TO 172 · PRECEDES 67 · STYLE_CONTRAST 53 · VERTICAL_SEPARATION 25 · SHARES_REGION 28 · LEFT_ALIGNED_WITH 13 · REPEATS_ACROSS_PAGES 8 · CONTINUES_FROM 1
- 全部为确定性几何/拓扑关系；relation_id 为稳定 hash。

---

## 6. Confidence Metrics

- 整体：LOW 135 / MEDIUM 30 / HIGH 10 / AMBIGUOUS 0 / UNKNOWN 0
- 传播契约执行：`confidence = min(upstream, structural)`。真实页面上游（P5/P6）为 MEDIUM，因此任何 hypothesis 都不超过 MEDIUM——下游未静默抹除上游不确定性。
- 偏保守（LOW 偏多）是契约的正确结果，不是缺陷：置信度宁可低也不可虚高。

---

## 7. Provenance / Trace Metrics

- provenance_completeness = **1.0**
- decision_trace_completeness = **1.0**（每条含 input / signals / decision / confidence 四步，可审计）
- supporting_fact_refs 完整率 = **1.0**（分类型亦为 1.0）
- supporting_relation_ids 完整率 = **1.0**（HEADING 0.955，源于无 gap 信号时不产生 VERTICAL_SEPARATION 关系，属正常）

---

## 8. Semantic Leakage Result

- 源码静态扫描：**0** 项命中（去注释/去 docstring 后扫描 `bold→heading`、`top region→header`、`aligned→table`、`small text→caption`、LLM、embedding、RM501/DC201 特例）。
- 行为验证：`conflicting_style_geometry`（bold-only）产出 0 个 HEADING_CANDIDATE；`single_page_top_no_header` 产出 0 个 HEADER_CANDIDATE。
- 结论：**无单信号 shortcut，无语义泄漏。**

---

## 9. Negative Case Result

- negative_case_failure_count = **0**
- bold text ≠ heading ✅（bold 单信号不产生候选）
- top region ≠ header ✅（无跨页重复即不产生）
- bottom region ≠ footer ✅
- aligned text ≠ table ✅（TABLE 根本未实现）
- empty rectangle ≠ image ✅（IMAGE 未实现）
- small text ≠ caption ✅（CAPTION 未实现）

---

## 10. P1–P6 Regression

- P1–P6 代码 SHA256 与 P6 验收基线（`tmp/perception/p6/regression_baseline.json`）逐字节一致，changed_files = []。
- P5/P6 输出未被 P7.1 触碰（P7.1 只读消费）。

---

## 11. Frozen 730 Verification

- Frozen 730 Pool md5_8 = **a10b368e**（期望 a10b368e）✅
- restore 区：registry.py=50e3db50 ✅ · bootstrap.py=d7f09fef ✅ · capability_loader.py=830fca24 ✅
- C1 layout_analyzer.py SHA256 与基线一致 ✅

---

## 12. Downstream Isolation Verification

- P7.1 源码（structure/*.py + p7_runner.py）**零引用** Evidence / Annotation / Capability / Runtime / registry / bootstrap 模块（grep 验证）。
- P7.1 全部写入路径仅为 `tmp/perception/p7/`（schema/config/测试结果/报告/debug PNG）。零写入 Evidence Store、Annotation、Capability、Runtime。
- Runtime Authority 保持 ZERO；P7.1 Hypothesis ≠ Evidence。

---

## 13. Error / Uncertainty Classification（只读观察，不修复）

### A. 上游事实不足导致的候选不确定性
- 真实页面上游置信度为 MEDIUM（P5/P6），封顶一切 hypothesis 置信度 → 大量 LOW 是传播契约的正确表现。
- HEADER/FOOTER：真实语料仅采样每文档前 2 页，未检出重复单元（这些文档可能确实无 running header）→ 真实语料 HEADER/FOOTER 覆盖率 0.000，属上游证据不足，非算法缺陷。
- MULTI_COLUMN_CONTINUATION：真实语料为单栏（或行对齐 TOC，P5 按行序读），无跨栏续接场景 → 真实覆盖 0.000，仅合成例触发。

### B. P1–P6 事实足够、但 P7.1 无法稳定判断
- **HEADING 58/67 为 LOW**：多数仅触发 2 个独立信号（short_line + style_contrast），达到最低门槛 → structural=LOW。事实存在，但现有 4 类信号（style/gap/position/short-line）的区分度不足以把「真实标题」与「加粗字段标签」分开。
- **TOC 页假阳性模式（观察，不修复）**：`arxiv_toc_p2` 在 90 个 span 中产出 33 个 heading 候选（37%）、`rm501_p2` 在 44 个 span 中产出 21 个（48%）。目录条目（短行+样式差异+页码）与章节标题在纯几何事实上不可区分——这正是「不引入文本证据」的代价。候选率偏高但全部为 PROPOSED + LOW，未污染下游。

### C. 必须引入新的 Observation 才能解决
- Table / Table Cell → Table Cell Geometry（cell 级行列 grid）
- Figure / Image / Chart → Visual Object Observation（P1 目前跳过非文本块）
- Flowchart → Graphic/Vector Observation（shape/arrow/text-node/connectivity）
- Formula（可靠级）→ character-level baseline / subscript / symbol-class observation
- Caption（可靠级）→ 可靠 object reference（依赖 Visual/Table Object 先落地）

### D. 必须经过 Human Validation 才能解决
- 全部 175 条 PROPOSED hypothesis 均在等待 Human Validation（Human Validated = 0）。
- 优先级最高（假阳性风险最大）：arxiv_toc 的 33 个 heading 候选、rm501 的 21 个 heading 候选（加粗标签 vs 真实标题）。
- 文本类消歧（TOC 点线、页码模式、编号列表）被**有意**排除在 P7.1 之外 → 按设计归入 Human Validation，而非引入关键词规则。

### E. 继续保持 BLOCKED 的对象（本轮未加任何 heuristic）
| 对象 | 处置 |
|---|---|
| Table / Table Cell | BLOCKED — 等 Table Cell Geometry |
| Figure / Image / Chart | BLOCKED — 等 Visual Object Observation |
| Flowchart | BLOCKED — 等 Graphic/Vector Observation |
| Formula（可靠级） | BLOCKED — 等 baseline/subscript/symbol-class |
| Caption（可靠级） | BLOCKED — 等可靠 object reference |
| Page Number / Reference / Footnote | HUMAN-FIRST — 文本证据有意不引入 |

---

## 14. Blocked Object Classification

见 §13-E。本轮为以上对象添加的 heuristic 数量 = **0**。

---

## 15. Boundary Confirmation

### Boundary 1 — P7.1 Candidate ≠ Validated Structure
- 全部 175 条输出类型均为 `*_CANDIDATE`；集合中不存在 HEADING / TABLE / FIGURE / CAPTION / FORMULA / IMAGE 等最终语义结构类型。
- status 集合 = {PROPOSED}，无 VALIDATED / PARTIALLY_VALIDATED / REJECTED。
- ✅ 确认。

### Boundary 2 — P7.1 StructureHypothesis ≠ Evidence
- P7.1 代码零引用 Evidence/Annotation/Capability/Runtime 模块；写入路径仅 `tmp/perception/p7/`。
- Evidence Store / Annotation / Capability / Runtime 哈希全部未变。
- Runtime Authority = ZERO 保持。
- ✅ 确认。

---

## 16. Final Recommendation

1. **P7.1 正式 ACCEPTED / FROZEN**（6 个文件哈希已固化，可复现、可审计）。
2. 置信度整体偏保守（LOW 为主）是 min-传播契约的正确行为，**不**应通过提高置信度来「优化」。
3. 下一阶段真正的缺口是 **Evidence 缺口**，而非算法缺口：
   - **Visual Object Observation**（解锁 Figure/Image/Chart，连带解锁可靠 Caption）
   - **Table Cell Geometry**（解锁 Table/Table Cell）
   - **Graphic/Vector Observation**（解锁 Flowchart）
   - **Formula atomic extension**（baseline/subscript/symbol-class）
   - **Human Validation 基础设施**（175 条 PROPOSED 候选的审阅通道；hypothesis 已携带审阅所需的全部字段：supporting evidence / conflicting evidence / source span / bbox / decision trace）
4. 在上述上游扩展完成之前，P7.2 / P7.3 / P8 维持 BLOCKED。

---

**P7.1 Acceptance Baseline 完成。STOP。**
