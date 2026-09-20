# P7.2 Validation Infrastructure — Gate Review

> 对 Human Validation Infrastructure 设计的正式审查。回答四个核心问题，给出是否批准实施的判定。
> 本轮为设计审查，不写代码、不修改任何已有文件。

---

## 1. Validation Infrastructure 是否能让 Observation 进入 Evidence？

**能。设计已证明链路贯通。**

当前阻塞：P7.1 产出 175 StructureHypothesis（status=PROPOSED），validated=0 → Evidence 产出 = 0。链路在 `Hypothesis → Human Validation` 处断开。

本设计通过三对象 + 状态机打通：

```
Observation (PROPOSED, P7.1 产出)
    + ValidationTask (派生审阅单元)
    + Human ACCEPT
    + ValidationRecord (immutable 裁定)
    → Validated Evidence (derived)
    → Evidence Candidate → 下游 Evidence 治理
```

**关键验证点**：
- Observation 保持 PROPOSED 不可变 → 审计完整性 ✓
- Human ACCEPT 是唯一从 PROPOSED 到 Evidence 的路径 → 无自动绕过 ✓
- Validated Evidence 是派生引用（observation_id + validation_id）→ 不复制事实，可回溯 ✓
- REJECTED 的 Observation 保留为校准数据 → 假阳性可量化 ✓

**链路成立性证明**：以 Priority 0（arxiv_toc 33 条）为例——
- "Contents"（MEDIUM, 3 信号）→ Human ACCEPT → Validated Evidence（evidence_type=HEADING）→ 证明一条 Observation 成功进入 Evidence
- 其余 32 条 TOC 条目 → Human REJECT → 无 Evidence 产生，但校准数据产出（「TOC 页 heading 候选 ≈ 97% 假阳性」）
- 33 条审完后：≥1 条 Evidence 产出 + 假阳性率可计算 → **Observation→Evidence 链成立**

**结论：是。** 本设计是当前让 Observation 进入 Evidence 的唯一合规路径。

---

## 2. Human 成本是否低于重新人工标注？

**是。确认界面 ≠ 标注界面，成本降一个数量级。**

| 维度 | 重新人工标注（from scratch） | 本设计（确认界面） |
|---|---|---|
| Human 任务 | 在全文中找到标题 → 判定 → 画框 → 标类型 | 看系统已提出的候选 + 证据 + 理由 → 三选一 + 理由 |
| 信息准备 | Human 自己找 | 系统预解析（bbox 高亮 + 文本 + 信号值 + 页面图像） |
| 每条耗时 | ~30–60 秒（定位 + 标注） | ~5–10 秒（确认 + 理由） |
| 漏检风险 | 高（Human 可能遗漏） | 低（系统已穷举候选，Human 只做确认/否决） |
| 一致性 | 低（不同标注者标准不同） | 高（系统理由统一展示，Human 在相同信息下裁定） |
| 批量效率 | 低（每条独立定位） | 高（同类候选连续审阅，如 33 条 TOC 可连续处理） |

**成本估算（Priority 0）**：33 条 × 8 秒/条 ≈ **4.4 分钟**。对比重新标注同页 90 个 span ≈ 45–90 分钟。**成本降低 ~10–20×**。

**额外价值**：REJECTED 记录的 reviewer_reason 形成假阳性归因数据——这是重新标注**无法**产出的（标注只产生正例，不产生「为什么系统误报」的结构化归因）。

**结论：是。** 确认界面的 Human 成本显著低于重新标注，且产出更丰富的校准数据。

---

## 3. 未来 Visual/Table Observation 是否可以复用这个 Validation 框架？

**可以。框架对 observation_type 完全无关。**

| 复用维度 | 当前（P7.1 文本类） | 未来（Visual/Table 类） | 是否复用 |
|---|---|---|---|
| 三对象模型 | Observation=StructureHypothesis | Observation=FigureHypothesis/TableHypothesis | ✅ 模型不变 |
| ValidationTask 字段 | observation_type=HEADING_CANDIDATE | observation_type=FIGURE_CANDIDATE | ✅ 字段不变，值变 |
| candidate_content | span text + bbox | image bbox + 周围文本 | ✅ 解析方式变，字段不变 |
| visual_reference | 页面 PNG + bbox 高亮 | 页面 PNG + 图像区域高亮 | ✅ 格式不变 |
| 状态机 | PROPOSED→PENDING→ACCEPT/REJECT | 完全相同 | ✅ 不变 |
| 界面原则 | 确认界面（Accept/Reject/Need Review） | 完全相同 | ✅ 不变 |
| ValidationRecord | reviewer_decision + reason | 完全相同 | ✅ 不变 |
| Validated Evidence 派生 | observation + ACCEPT → evidence | 完全相同 | ✅ 不变 |

**唯一需要适配的**：candidate_content 的解析逻辑（figure 候选需解析图像区域而非文本 span）。这是展示层差异，不影响数据模型与状态机。

**前置依赖**：Visual/Table Observation 须先由 P7.2 上游扩展（Visual Object Observation / Table Cell Geometry）产出对应 Hypothesis，才能进入本验证框架。本框架本身不需要改动——它已经准备好接收任何 `*_CANDIDATE` 类型。

**结论：是。** 本框架是 observation-type-agnostic 的通用验证基础设施，Visual/Table 可直接复用。

---

## 4. 是否可以作为 DICE Evidence Intelligence 核心组件？

**是。它是 Evidence 可信度与可审计性的治理根基。**

| 核心组件属性 | 本设计是否满足 |
|---|---|
| 强制门控 | ✅ 每条 Evidence 必须过 Human ACCEPT；无自动路径 |
| 可审计 | ✅ Observation（不可变）+ Record（不可变）+ 派生 Evidence（引用链）= 完整审计链 |
| 可校准 | ✅ REJECT 数据 → 假阳性率/信号可靠性 → 未来 P7.x 调优依据 |
| 可扩展 | ✅ observation-type-agnostic，Visual/Table/Formula 可复用 |
| 边界保持 | ✅ Observation ≠ Evidence；不碰 P1–P7.1/Runtime/Capability |
| 不替代 Human | ✅ 禁止 LLM 自动 approve；Human 是唯一裁定者 |
| 成本可控 | ✅ 确认界面，~5–10 秒/条，批量友好 |

**在 DICE 架构中的定位**：

```
Document → Observation (P1–P7.1) → Structural Relation → StructureHypothesis
    → [Human Validation Infrastructure]    ← 本设计 = 此处
    → Validated Structure → Evidence Candidate → Evidence
    → Validation → Capability → Runtime
```

它是 `Hypothesis → Evidence` 之间的**唯一合规桥梁**。没有它，DICE 的 Evidence 不可信（无人工确认）、不可审计（无裁定记录）、不可校准（无假阳性数据）。

**Evidence Intelligence 的三个支柱**：
1. **可信**（Trustworthy）：每条 Evidence 有 Human ACCEPT 背书
2. **可审计**（Auditable）：Observation + Record + Evidence 三者引用链完整
3. **可进化**（Evolvable）：校准数据驱动未来感知层迭代（非自动，需评审）

本设计同时满足三个支柱。

**结论：是。** 建议作为 DICE Evidence Intelligence 的核心治理组件立项。

---

## 5. 综合判定与建议

### 判定

| 问题 | 结论 |
|---|---|
| 1. 能让 Observation 进入 Evidence？ | ✅ 是——唯一合规路径 |
| 2. Human 成本低于重新标注？ | ✅ 是——降 ~10–20×，且产出更丰富 |
| 3. Visual/Table 可复用？ | ✅ 是——type-agnostic 通用框架 |
| 4. 可作 DICE 核心组件？ | ✅ 是——可信/可审计/可进化三支柱 |

### 建议

**建议批准 P7.2 Human Validation Infrastructure 进入实施阶段，以 Priority 0（arxiv_toc 33 条）为第一个验证目标。**

理由：
1. 175 hypotheses / 0 validated 是已证实的真实瓶颈——不解决则 Evidence 产出永远为 0。
2. 设计已完成，边界清晰，不碰任何冻结对象。
3. Priority 0（33 条 TOC heading）可在 ~5 分钟内完成首轮验证，立即证明 Observation→Evidence 链成立 + 产出首批校准数据。
4. 框架可复用——一次建设，Visual/Table/Formula 全部受益。
5. 实施风险最低——纯治理侧，不扩展感知层，不修改 P1–P7.1。

### 实施前提（实施时须遵守）

- 不修改 P1–P7.1 任何代码/schema/输出
- 不修改 Frozen 730 / Annotation / Capability / Runtime
- 不引入 LLM 自动 approve
- Validated Evidence = Evidence Candidate（最终 Evidence Store 准入是下游独立流程）
- 校准数据只 inform 未来调优，不自动修改 P7.1 阈值
- 实施后须回归验证 P1–P7.1 / Frozen 730 全部 UNCHANGED

---

**Gate Review 完成。设计阶段结束。等待批准。**
