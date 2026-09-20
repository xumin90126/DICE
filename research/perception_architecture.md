# Perception Architecture — Dual-Track Design

> 只读设计文档。未修改任何代码/数据/annotation/manifest。
> 核心原则：**冻结的是实例和证据基线，而不是未来 Span 技术的发展能力。**

---

## 1. 设计原则

1. **三概念分离**：Schema（契约）、Generator（算法）、Pool（实例）三者冻结性不同。
2. **实例冻结 ≠ 技术冻结**：730 Pool 冻结不阻止新 Generator 算法的开发。
3. **物理隔离**：TRACK A 与 TRACK B 的存储、数据流、校验完全分离，TRACK B 不得自动覆盖 TRACK A。
4. **零权威性保持**：无论 v1/v2，Span Construction 不得引入 span_type/capability/decision（T-7 约束不变）。
5. **晋升需显式批准**：TRACK B 结果晋升为新 baseline 必须经过 Human Validation + 显式 Unfreeze 审批。

---

## 2. TRACK A — Frozen Evidence Baseline（完全不变）

```
Raw Document (PDF)
    │
    │  PyMuPDF get_text("blocks")  [旧版本聚类行为，已固化在 pool 文件中]
    ▼
Legacy CandidateSpanGenerator  [candidate_span.py:126, 不修改]
    │  1 block = 1 CandidateSpan (1:1)
    ▼
Frozen 730 CandidateSpan Pool  [phase48 JSON, 不可复现快照]
    │  candidate_key = f"{doc}::p{page}::{span_text.strip()}"
    ▼
Existing Human Annotation  [phase52_1/workbench, 不修改]
    │  HumanValidationGate.promote(candidate, annotation)
    ▼
DocumentSpan  [frozen schema, Phase 16.1]
    │
    ▼
Existing Evidence Baseline  [Evidence Store, 不修改]
    │
    ▼
Capability Registry  [frozen, 不修改]
```

**TRACK A 规则**：
- 整条链完全保持不变，不修改任何环节
- Frozen 730 Pool 是不可复现快照（旧 PyMuPDF 版本产物），保护 JSON 文件本身
- 不得用当前 PyMuPDF 重跑 Generator 覆盖 pool（会产 185≠201，破坏冻结）
- 此链继续作为当前 Evidence Baseline 的唯一来源

---

## 3. TRACK B — Perception Development Sandbox（独立开发）

```
Raw Document (PDF)  [同一份源文档]
    │
    │  PyMuPDF get_text("dict")   → spans (含 size/font/flags)
    │  PyMuPDF get_text("words")  → words (含 bbox)
    │  PyMuPDF get_text("rawdict")→ chars (含逐字 bbox)
    ▼
┌─────────────────────────────────────────────┐
│  Atomic Observation Layer (NEW)             │
│                                             │
│  AtomicTextObservation                      │
│    - word/span 级原子，含 text + bbox       │
│    - 不依赖 CandidateSpan                   │
│    - 直接来自 PyMuPDF word/span 层           │
│                                             │
│  GeometryObservation                        │
│    - x/y 坐标、列归属、间距、行高            │
│    - 由 AtomicText 的 bbox 派生             │
│                                             │
│  StyleObservation                           │
│    - 字号/字体/bold/flags                    │
│    - 来自 dict span 层                       │
│                                             │
│  RegionObservation                          │
│    - 表格区/图区/正文区/页眉页脚区            │
│    - 由 Geometry + Style 综合判定            │
│    - 标记为 UNKNOWN/DEFER 时不猜             │
└─────────────────────────────────────────────┘
    │
    │  基于 Observations 重新聚合
    ▼
Experimental Span Construction (NEW)
    │
    │  - 不用 block 层（避免聚类腐败）
    │  - 用 Geometry 判断列边界（x 距离 > 阈值 → 不同列 → 不同 span）
    │  - 用 Region 判断表格/图区（区域内的原子归一组）
    │  - 用 Style 辅助（同字号/字体的连续原子倾向同 span）
    │  - 产出 ExperimentalSpan（复用 Schema 4-field 定义，独立实例）
    ▼
Experimental CandidateSpan Pool (NEW, 独立存储)
    │
    │  - 存储路径与 frozen pool 物理分离
    │  - 可自由修改、重跑、迭代
    │  - 不得写入 tmp/phase48/ 或任何 frozen 路径
    ▼
Evaluation (NEW)
    │
    │  - Legacy vs Experimental Span 对比
    │  - Boundary Violation 检测
    │  - 碎片率/合并率/列跨越统计
    ▼
Human Validation (NEW, 独立于现有 annotation)
    │
    │  - 对 Experimental Span 做人工标注
    │  - 不触碰现有 730 pool 的 annotation
    ▼
Candidate Evidence (NEW)
    │
    │  - 达到晋升条件后，候选为新 baseline
    │  - 晋升需 EXPLICIT UNFREEZE APPROVAL
```

**TRACK B 规则**：
- 可独立开发和修改，任何结果不得自动覆盖 TRACK A
- Atomic Observation 层是全新抽象，不依赖 CandidateSpan
- ExperimentalSpan 复用 Schema 字段定义（4-field），但实例与 frozen pool 隔离
- Experimental Pool 存储在独立路径（如 `tmp/perception/experimental_pool/`）
- 评估与人工验证独立于现有 annotation 体系

---

## 4. 双轨隔离机制

### 4.1 存储隔离

| 对象 | TRACK A 路径 | TRACK B 路径 |
|---|---|---|
| Span Pool | `tmp/phase48/phase48_l1_candidate_presentation.json`（只读） | `tmp/perception/experimental_pool/`（读写） |
| Annotation | `tmp/phase52_1/workbench/`（只读） | `tmp/perception/experimental_annotation/`（读写） |
| Generator | `candidate_span.py:126`（不修改） | `tmp/perception/experimental_generator/`（新建） |

**硬规则**：TRACK B 代码不得写入任何 `tmp/phase48/`、`tmp/phase52_1/`、`dice/` 路径。

### 4.2 数据流隔离

```
TRACK A: PDF → [frozen pipeline] → 730 Pool → [frozen annotation] → Evidence Baseline
                                                                    ↕ (只读对比，不写回)
TRACK B: PDF → [atomic observations] → [experimental generator] → Experimental Pool → [eval] → [validation]
```

两条 track 共享的唯一输入是 **Raw Document（PDF 源文件）**。输出完全分离。

### 4.3 对比桥（只读）

TRACK B 的 Evaluation 阶段可以**只读** TRACK A 的 frozen pool 做对比：
- 同一 PDF 的同一区域：Legacy span_text vs Experimental span_text
- 统计：哪些 candidate 被正确拆分、哪些被正确合并、哪些新增、哪些消失
- 对比结果写入 `tmp/perception/evaluation/`，不写回 TRACK A

---

## 5. Atomic Observation 层设计

### 5.1 AtomicTextObservation

```
AtomicTextObservation:
    document_id: str          # 源文档
    page: int                 # 页码
    text: str                 # 文本内容（word 或 span 级）
    bbox: [x0, y0, x1, y1]   # 精确坐标
    size: float               # 字号（来自 dict span）
    font: str                 # 字体（来自 dict span）
    flags: int                # 排版 flags（来自 dict span）
    source_layer: str         # "word" | "span"（标记来源层）
```

**不依赖 CandidateSpan**。直接来自 PyMuPDF word/span 层。一个 word 或 span = 一个 AtomicTextObservation。

### 5.2 GeometryObservation

由 AtomicTextObservation 的 bbox 派生：
- 列归属（x 聚类）
- 列间距（相邻 x 差）
- 行归属（y 聚类）
- 区域边界（表格/图区 bbox）

### 5.3 StyleObservation

由 dict span 层的 size/font/flags 派生：
- 字号分组（标题/正文/表头/脚注）
- bold 检测
- 字体一致性

### 5.4 RegionObservation

由 Geometry + Style 综合判定：
- 表格区（多列对齐 + 表头字号特征）
- 图区（矢量绘图密集区 + 文字稀疏）
- 正文区（单/双栏 + 连续段落）
- 页眉页脚区（y 在页面顶/底边界 + 重复模式）
- **UNKNOWN/DEFER**：信息不足时不猜，标记待定

---

## 6. Experimental Span Construction 设计

### 6.1 核心算法思路（本轮不实现，仅设计）

```
输入: List[AtomicTextObservation] + Geometry/Style/Region Observations
输出: List[ExperimentalSpan]  (复用 Schema 4-field)

步骤:
1. 按 Region 分组原子（表格区原子 → 表格 span 候选；正文区 → 段落 span）
2. 在每个 Region 内按 Geometry 分列（x 距离 > 列间距阈值 → 不同列）
3. 在每列内按行（y）聚合成 span
4. 用 Style 辅助（同字号连续原子优先聚合）
5. 产出 ExperimentalSpan(span_text, position_metadata={bbox, ...})
```

### 6.2 与 Legacy Generator 的区别

| 维度 | Legacy (v1) | Experimental (v2) |
|---|---|---|
| 数据源 | block 层（1 层） | word/span/line 层（多层） |
| 聚类依据 | PyMuPDF block 聚类（不透明） | DICE 自控 Geometry + Style + Region |
| 跨列腐败 | ❌ 有（'Position'+'Step' 归一） | ✅ 避免（x 距离检测） |
| 版本稳定 | ❌ 不稳定 | ✅ 稳定（word/span 层跨版本一致） |
| style 信息 | 丢失 | 保留 |
| 零权威性 | ✅ | ✅（保持） |

### 6.3 row 104 拆分验证（设计层面）

```
Atomic Observations (RM501-P4 p2 表头区):
  - 'Position' (x513, y548, size7.3, bold)   ← 来自 dict span
  - 'Step'     (x77,  y539, size7.0, bold)   ← 来自 dict span
  - ... 其他表头原子

Geometry Observation:
  - x_distance(Position, Step) = 436pt > column_gap_threshold
  - → 判定属于不同列

Experimental Span Construction:
  → ExperimentalSpan_1(span_text="Position", bbox=[513,...])
  → ExperimentalSpan_2(span_text="Step",     bbox=[77,...])
  （不修改 frozen 730 row 104）
```

---

## 7. 版本兼容与 Schema 复用

### 7.1 Schema 复用策略

ExperimentalSpan **复用** CandidateSpan Schema 的 4-field 定义（document_id / page_reference / span_text / position_metadata），但：
- **不共享实例**：ExperimentalSpan 实例与 frozen pool 实例物理隔离
- **position_metadata 扩展**：v2 可在 position_metadata 中增加字段（如 `source_layer`、`column_index`、`region_type`），不破坏 4-field 契约（position_metadata 本身是 Dict，可扩展）
- **禁止字段不变**：v2 不得引入 span_type/capability/decision（T-7 保持）

### 7.2 版本标识

每个 Span 实例在 position_metadata 中携带 `span_version`：
- v1（frozen）：`span_version: "v1"`（已存在于 frozen pool 的隐含版本）
- v2（experimental）：`span_version: "v2"`
- validated：`span_version: "v2-validated"`

---

## 8. 晋升机制（TRACK B → 新 Baseline）

```
Experimental Pool (v2)
    │
    │  1. Evaluation: boundary violation = 0 on audit set
    │  2. Human Validation: validation rate ≥ v1 baseline
    │  3. row 104 class split verified
    │  4. Full regression (6 docs) passes
    │  5. No C1/C2/C3/C4 regression
    ▼
Validated Pool (v2-validated)  [候选新 baseline]
    │
    │  EXPLICIT UNFREEZE APPROVAL (人工治理决策)
    ▼
New Baseline Migration:
    - 重新生成 pool（在新 PyMuPDF 版本下）
    - 重新标注 annotation（新 span_text → 新 candidate_key）
    - 旧 730 pool 归档（不删除，保留为历史 baseline）
```

**晋升条件必须全部满足**，缺一不可。详见 `span_versioning_strategy.md`。

---

## 9. 不变式（Invariants）

1. **TRACK A 不可写**：任何 TRACK B 操作不得修改 frozen pool / annotation / Evidence Store / Capability。
2. **Schema 4-field 不变**：v1/v2/validated 均保持 4-field，禁止字段不变。
3. **零权威性不变**：Span Construction 不得引入分类/评分/决策。
4. **不自动晋升**：TRACK B → TRACK A 的迁移必须经显式人工批准。
5. **源文档共享**：两条 track 共享 PDF 源文件，但输出隔离。
