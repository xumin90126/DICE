# P7.2 — Human Validation Infrastructure Design

> **DESIGN ONLY.** 本文档定义 Human Validation Infrastructure 的数据模型、状态机、验证目标与界面原则。
> 不写代码、不修改 HTML、不修改 schema、不修改 runtime。等待批准后实施。
>
> 真实瓶颈（Evidence Gap Analysis 已证）：P7.1 产生 175 StructureHypothesis / 0 validated →
> Document → Evidence 链路唯一阻塞点 = Human Validation。

---

## 0. 边界声明

| 冻结/不变 | 说明 |
|---|---|
| P1–P7.1 | 全部代码与输出冻结（SHA256 已固化） |
| Frozen 730 / Annotation / Capability Registry / Runtime / Schema | 不修改 |
| Existing Observation contract | P7.1 StructureHypothesis schema 不改一个字段 |
| P7.1 决策路径 | 不引入文本证据、不引入 LLM 自动 approve、不自动替代 Human 判断 |

**本基础设施是治理侧建设，不是感知侧建设。** 它消费 P7.1 的 PROPOSED hypothesis，不产生新 Observation，不修改候选生成。

---

## 1. 三个严格分离对象

### A. Observation（= P7.1 StructureHypothesis）

| 属性 | 值 |
|---|---|
| 表示 | "系统观察到/假设了什么" |
| 状态 | `PROPOSED` — **永远不变** |
| 可修改 | **否**（immutable audit record） |
| 来源 | P7.1 StructureHypothesis（hypothesis_id 即 observation_id） |
| 关键字段 | hypothesis_id, document_id, page_number, hypothesis_type, span_ids, region_ids, geometry, confidence, decision_trace, supporting_fact_refs, supporting_relation_ids, construction_method, provenance, coord_origin |

**核心原则**：Observation 是「系统提出了什么」的不可变审计记录。即使 Human REJECT，Observation 仍保留（用于假阳性校准）。即使 Human ACCEPT，Observation 本身仍保持 PROPOSED——裁定状态活在 ValidationRecord 中，不污染 Observation。

### B. ValidationTask

| 属性 | 值 |
|---|---|
| 表示 | "Human 需要审核什么" |
| 可修改 | task_status 可流转（PENDING → IN_REVIEW → RESOLVED） |
| 来源 | 从 Observation **派生**（引用 observation_id，不复制 Observation 本身） |

**必含字段**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | str (deterministic) | sha1(document_id \| page \| observation_id \| "validation_task")[:16] |
| `observation_id` | str | 引用 StructureHypothesis.hypothesis_id（**不复制**） |
| `document_id` | str | 来自 hypothesis |
| `page_reference` | {page_number, bbox} | hypothesis.page_number + hypothesis.geometry.bbox |
| `observation_type` | str | hypothesis.hypothesis_type（HEADING_CANDIDATE 等） |
| `candidate_content` | {text, span_ids, bbox} | **派生展示视图**：从 span_ids 解析 P4 span.text（供 Human 阅读，非复制进 Observation） |
| `visual_reference` | {png_path, bbox_highlight} | 引用 debug PNG + 高亮坐标（如 `tmp/perception/p7/debug/arxiv_toc.png`） |
| `confidence` | str | hypothesis.confidence（HIGH/MEDIUM/LOW） |
| `system_reasoning` | [{step, summary}] | decision_trace 摘要（signals + values + decision reason） |
| `created_time` | ISO 8601 | Task 创建时间 |
| `task_status` | enum | PENDING_HUMAN_REVIEW / IN_REVIEW / RESOLVED |
| `priority` | int | 0=arxiv_toc, 1=rm501, …（按 Evidence Gap Analysis 排序） |

**candidate_content 是派生视图，不是事实复制**：它从 span_ids 引用链解析出文本（P4 span.text），供 Human 阅读。事实的权威来源仍是 P1–P6；ValidationTask 只做展示层解析。

### C. ValidationRecord

| 属性 | 值 |
|---|---|
| 表示 | "Human 做出的裁定" |
| 可修改 | **否**（immutable once created；NEED_REVIEW 会创建新 Record，不修改旧 Record） |
| 来源 | Human 操作产生 |

**必含字段**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `validation_id` | str (deterministic) | sha1(observation_id \| reviewer_id \| timestamp)[:16] |
| `observation_id` | str | 引回 StructureHypothesis |
| `task_id` | str | 引回 ValidationTask |
| `reviewer_decision` | enum | **ACCEPT** / **REJECT** / **NEED_REVIEW** |
| `reviewer_reason` | str | Human 给出的裁定理由（自由文本） |
| `timestamp` | ISO 8601 | 裁定时间 |
| `reviewer_notes` | str | 附加注释（可选） |
| `reviewer_id` | str | 审阅者标识（匿名化） |
| `validation_method` | enum | DIRECT_REVIEW / ESCALATED / BATCH |

**NEED_REVIEW 不修改旧 Record**：它创建一条新 Record（decision=NEED_REVIEW），Task 回到 PENDING 等待升级审阅。所有 Record 留痕（审计链完整）。

### 派生产象：Validated Evidence

**不是第四个手工对象，而是派生记录**。当且仅当 `Observation(存在) + ValidationRecord(reviewer_decision=ACCEPT)` 同时满足时，系统物化一条 Validated Evidence：

| 字段 | 说明 |
|---|---|
| `evidence_id` | sha1(observation_id \| validation_id \| "validated_evidence")[:16] |
| `source_observation_id` | 引用 StructureHypothesis |
| `source_validation_id` | 引用 ACCEPT 的 ValidationRecord |
| `evidence_type` | 从 hypothesis_type 派生（HEADING_CANDIDATE → HEADING） |
| `validated_content` | 从 span_ids 解析的文本 + bbox（与 candidate_content 同源） |
| `validation_provenance` | {reviewer_id, timestamp, reviewer_reason} |
| `status` | VALIDATED |

**Observation ≠ Evidence 的保持**：Observation 保持 PROPOSED（不可变审计记录）；Validated Evidence 是独立派生对象，引用 Observation + Record。两者共存：Observation 回答「系统提出了什么」，Validated Evidence 回答「人工确认后什么可进入下游」。

> **与 P7.1 边界的关系**：P7.1 review 定义了 `Hypothesis → Human Validation → Validated Structure → Evidence Candidate → Evidence`。本设计的 "Validated Evidence" 对应 "Evidence Candidate"（已过人工确认）。是否进入最终 Evidence Store（归属/权重/版本治理）是更下游的独立流程，不在本设计范围。

---

## 2. 最小 Human Review Workflow（状态机）

```
[Observation: PROPOSED]          ← P7.1 创建，永远 PROPOSED（immutable）
        │
        │  ValidationTask 创建（派生）
        ▼
[Task: PENDING_HUMAN_REVIEW]     ← task_status 可流转
        │
        │  Human 打开审阅
        ▼
[Task: IN_REVIEW]
        │
        │  Human 裁定 → 创建 ValidationRecord（immutable）
        │
        ├── ACCEPT ──────────────► [Record: ACCEPT]
        │                              │
        │                              ▼
        │                        物化 Validated Evidence（derived）
        │                              │
        │                              ▼
        │                        Evidence Candidate → 下游 Evidence 治理
        │
        ├── REJECT ──────────────► [Record: REJECTED]
        │                              │
        │                              ▼
        │                        Observation 保留为审计记录
        │                        （假阳性校准数据，不产生 Evidence）
        │
        └── NEED_REVIEW ────────► [Record: NEED_REVIEW]
                                       │
                                       ▼
                                 Task → PENDING_HUMAN_REVIEW（重新排队）
                                 （携带 reviewer_notes 供升级审阅）
```

**不变量（必须强制）**：

1. 任何 PROPOSED Observation **不能**直接进入 Evidence——必须经 Human ACCEPT + ValidationRecord。
2. Observation 永远保持 PROPOSED——裁定状态活在 Record 中。
3. REJECTED 的 Observation **不删除**——它是校准数据（假阳性率计算依据）。
4. NEED_REVIEW 不修改旧 Record——创建新 Record，旧 Record 留痕。
5. Validated Evidence 是**派生**的——不手工创建，系统在 ACCEPT 时自动物化。
6. 不存在「自动 ACCEPT」路径——LLM 自动 approve 被禁止。

---

## 3. 第一个 Validation Target

### Priority 0 — arxiv_toc 33 条 HEADING_CANDIDATE

| 维度 | 值 |
|---|---|
| 来源 | arxiv_bio p2（真实目录页），90 spans → 33 heading 候选（28 LOW + 5 MEDIUM） |
| 为什么选它 | (1) 结构最简单（单页、已知是 TOC）；(2) 能快速验证 Validation Loop 全链路；(3) 不涉及复杂语义（标题 vs 目录条目是明确的二分）；(4) 可证明 Observation→Evidence 链成立；(5) 预期大部分 REJECT → 立即产出校准数据 |
| 预期结果 | "Contents"（MEDIUM, 3 信号）大概率 ACCEPT（是页标题）；其余 32 条大概率 REJECT（是目录条目引用，非文档标题本身） |
| 信号组合分布 | short_line+style_contrast 18 · spatial_separation+style_contrast 10 · short_line+spatial_separation+style_contrast 3 · reading_position+short_line+style_contrast 2 |
| 具体示例 | hypothesis_id=263927b4069ad291, text="Contents", bbox=[83.34, 110.51, 135.86, 122.46], confidence=MEDIUM, signals=[style_contrast, reading_position, short_line] |

**为什么 TOC 条目不是 Heading**：TOC 页的 "Introduction" 是对第 2 页标题的**引用**，不是标题本身。这一区分是语义裁定——几何上 TOC 条目与标题同构（短行+粗体+左对齐），只有 Human 能判。这恰好证明 Human Validation 不可绕过。

### Priority 1 — rm501 21 条 HEADING_CANDIDATE

| 维度 | 值 |
|---|---|
| 来源 | RM501 p2（设备手册），44 spans → 21 heading 候选 |
| 为什么第二 | 比 TOC 复杂（含表格标签窄条误报，需逐条判）；预期 ACCEPT/REJECT 混合 |
| 已知假阳性模式 | 14 条仅靠 short_line+style_contrast，其中含宽 11.1pt 的表格标签窄条（bbox [66, 441.65, 77.12, 469.7]，bold, size 8.0）——非标题，是规格表标签 |
| 预期结果 | 真实章节标题 ACCEPT；表格标签/字段名 REJECT；校准「设备手册 heading 候选 ≈ 50% 假阳性」模式 |

---

## 4. Human Review Interface 原则（只设计，不编码）

### Human 看到的四要素

```
┌─────────────────────────────────────────────┐
│ 1. 系统观察                                   │
│    "这里可能是 Heading"                       │
│    hypothesis_type: HEADING_CANDIDATE         │
│    confidence: MEDIUM                         │
│                                               │
│ 2. 证据                                       │
│    ┌───────────────────────────────┐          │
│    │  [页面图像，bbox 高亮框]        │          │
│    │  visual_reference: debug PNG   │          │
│    └───────────────────────────────┘          │
│    文本: "Contents"                           │
│    bbox: [83.34, 110.51, 135.86, 122.46]      │
│    span_id: 1b7ed02754b7058c                  │
│    page: arxiv_bio p2                         │
│                                               │
│ 3. 系统理由                                   │
│    signals:                                   │
│      • style_contrast: bold=true (vs 页面多数非粗) │
│      • reading_position: 列内首位 (col_0)      │
│      • short_line: width=52.5 ≤ ref×0.80      │
│    decision: ≥2 独立信号 → HEADING_CANDIDATE   │
│    why not final: 候选，非最终结构             │
│                                               │
│ 4. Human 选择                                 │
│    [  ACCEPT  ] [  REJECT  ] [ NEED REVIEW ]  │
│    理由: ___________________________          │
└─────────────────────────────────────────────┘
```

### 禁止事项

| 禁止 | 原因 |
|---|---|
| 让 Human 重新寻找全文 | Human 不是重新做抽取；Human 只确认 Observation |
| 让 Human 重新标注 bbox | bbox 来自 P1–P6 事实，Human 不改事实 |
| 让 Human 输入 heading_level | heading_level 属 Layer D 语义，本阶段不要求 |
| 自动 ACCEPT（LLM/规则） | 禁止自动替代 Human 判断 |
| 隐藏系统理由 | Human 必须看到 WHY 才能裁定（可审计性） |
| 隐藏 confidence | Human 需知道系统自身的置信度 |

### 设计原则

1. **确认界面，非标注界面**：系统已提出候选 + 证据 + 理由；Human 只做 Accept/Reject/Need Review 三选一 + 理由。
2. **批量友好**：33 条 TOC heading 可连续审阅（同类批量），每条预计 5–10 秒。
3. **视觉优先**：页面图像 + bbox 高亮是主要信息源；文本是辅助。
4. **理由必填**：Accept/Reject 都须填理由（校准数据需要归因）。
5. **不可逆标记**：提交后 Record 不可修改（审计完整性）。

---

## 5. 校准反馈环（只读，不自动修改）

ValidationRecord 积累后产生校准数据（**只读分析，不自动改 P7.1**）：

| 校准指标 | 来源 | 用途 |
|---|---|---|
| 假阳性率（按类型） | REJECT 数 / 总候选数 | 衡量 P7.1 候选质量 |
| 假阳性率（按置信桶） | REJECT 数 / 桶内候选数 | 校验 confidence calibration（HIGH 桶应低假阳性） |
| 假阳性模式归因 | reviewer_reason 聚类 | 发现系统性误报源（如「TOC 页 heading 全假」→ 未来 Textual/Symbol Observation 立项证据） |
| 信号组合 × 裁定率 | signals × ACCEPT/REJECT | 发现哪些信号组合最可靠 |

**关键约束**：校准数据只** inform** 未来 P7.x 调优决策，**不自动**修改 P7.1 阈值或决策路径。任何阈值调整须经过独立的 P7.x 评审 + 冻结流程。

---

## 6. 未来 Observation 的复用性

本框架对 observation_type **完全无关**：

| 当前（P7.1） | 未来（P7.2+ 上游扩展后） |
|---|---|
| HEADING_CANDIDATE | FIGURE_CANDIDATE |
| PARAGRAPH_GROUP_CANDIDATE | TABLE_CANDIDATE |
| SECTION_CANDIDATE | TABLE_CELL_CANDIDATE |
| LIST_CANDIDATE | FORMULA_CANDIDATE |
| HEADER_CANDIDATE | CAPTION_CANDIDATE |
| FOOTER_CANDIDATE | FLOWCHART_CANDIDATE |
| MULTI_COLUMN_CONTINUATION_CANDIDATE | … |

**三对象模型（Observation / Task / Record）+ 状态机 + 界面原则完全复用**。未来 Visual Object Observation 产出的 FIGURE_CANDIDATE 会以完全相同的方式：创建 ValidationTask（observation_type=FIGURE_CANDIDATE, candidate_content=图像 bbox + 周围文本, visual_reference=页面图像）→ Human ACCEPT → Validated Evidence。

**唯一差异**：candidate_content 的解析方式（figure 候选的 visual_reference 会更突出图像区域而非文本 span），但数据模型不变。

---

## 7. ID 生成（确定性，无随机 UUID）

| 对象 | ID 公式 |
|---|---|
| ValidationTask | `sha1(f"{document_id}|{page}|{observation_id}|validation_task")[:16]` |
| ValidationRecord | `sha1(f"{observation_id}|{reviewer_id}|{timestamp}")[:16]` |
| Validated Evidence | `sha1(f"{observation_id}|{validation_id}|validated_evidence")[:16]` |

全部确定性——同一输入产生同一 ID，支持可复现审计。

---

## 8. 边界保持总结

| 边界 | 保持方式 |
|---|---|
| Observation ≠ Validated Structure ≠ Evidence | 三对象分离 + Validated Evidence 是派生引用，不替代 Observation |
| P7.1 不改 | 本基础设施不碰 P7.1 代码/schema/输出 |
| 不自动替代 Human | 禁止 LLM 自动 approve；ACCEPT 必须来自 Human |
| 不修改 extractor/heuristic | 本基础设施只消费 PROPOSED hypothesis，不回改生成 |
| Runtime Authority = ZERO | 本基础设施是治理层，不进 Runtime 决策路径 |
| Evidence 需独立治理 | Validated Evidence = Evidence Candidate；最终 Evidence Store 准入是下游独立流程 |

---

**设计完成。不写代码、不修改 HTML/schema/runtime。等待批准后实施。**
