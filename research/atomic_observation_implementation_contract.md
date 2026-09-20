# Atomic Observation Layer — Pre-Implementation Contract

> **本 define-only 轮**: 不实现、不创建 production code、不修改 Frozen Baseline / P1-P6 /
> CandidateSpan / P4 / P7.1 / P7.2、不运行 IS-14 evaluation、不收集 GT、不进入 P7.3、不修改 MAP。
> 目标: 把已通过 Architecture Challenge 的设计收敛为**可安全实现、最小、可验收**的
> Implementation Contract — 使未来获授权的实现者**没有任何重新解释空间**。
>
> 设计基线: `tmp/phase4_research_object_design.md` (DESIGN_SUPPORTED_WITH_LIMITATIONS)
> + `tmp/atomic_observation_architecture_challenge.md` (B_SUPPORTED_WITH_REFINEMENT, R1–R6)。
> 证据标签: **OBSERVED** (本轮 SHA/代码核实) / **INFERRED** / **CONTRACT** (本文件定义的规范条款)。

---

## 1. CURRENT DESIGN BASELINE

**Candidate B — B_SUPPORTED_WITH_REFINEMENT** (固定, 不可在本轮重释)。

最终 abstraction [CONTRACT]:
1. Frozen P1-P6 事实的 **read-only exposure** (expose-first)
2. `TEXT_ATOM` + `NON_TEXT_BLOCK_ATOM`
3. `RegionFact` (无语义类型名, 共存不仲裁)
4. 闭集 Relation: **IN_REGION + GAP_SEQUENCE** (仅此两个 layer-level 新增面)
5. frozen geometry single-source-of-truth
6. provenance / params_hash / version discipline
7. lazy query

明确禁止 [CONTRACT, 实现者无解释权]: semantic labels / decision / MERGE / KEEP / REJECT /
score / confidence / ranking / routing / recommendation / capability registration / runtime authority /
content 解读 (数值解析、等差、词法模式) / 任何 `is_*` 类别谓词输出。

---

## 2. ATOM CONTRACT

### 2.1 TEXT_ATOM [CONTRACT]

| 字段 | 定义 | 来源 |
|------|------|------|
| `atom_id` | `P1 AtomicTextObservation.obs_id` (frozen `_make_obs_id(doc,page,source,index)`), **不改名不重造** | P1 frozen |
| `atom_kind` | `"TEXT_ATOM"` (常量) | layer |
| `document_id` | P1 原值 | P1 |
| `page_reference` | P1 `page_number` (1-based, P1 既有约定) | P1 |
| `bbox` | P1 原值 (frozen `_round_bbox` 约定, 2pt→2位小数) | P1 |
| `content` | P1 `text` 原值 (未变换; 层不做 strip/normalize 超出 P1 已做部分) | P1 |
| `style_signature` | P3 `StyleObservation.signature` (可选暴露; 引用 P3 sha) | P3 frozen |
| `coordinate_system` | `"pymupdf_page_1.26.x_y_down"` (显式常量) | layer |
| `source_provenance` | `p1_artifact_sha` 或 `frozen_p1_function_sha` + `pymupdf_version` | layer |
| `deterministic identity` | = atom_id 本身 (纯函数 of content/position) — **禁 timestamp/random/runtime 序** | CONTRACT |

### 2.2 NON_TEXT_BLOCK_ATOM [CONTRACT — 唯一新枚举面]

| 允许字段 | 禁止字段 |
|----------|----------|
| `atom_id` = `NTB|{doc}|p{page}|{block_index}` (纯函数) | 任何 "image/figure/chart" 词汇或语义 |
| `atom_kind` = `"NON_TEXT_BLOCK_ATOM"` | OCR / content 任何非 null 值 |
| `document_id`, `page_reference` | semantic role / region 归属预设 |
| `bbox` (PyMuPDF block 原值, 同 `_round_bbox` 约定) | 去重/合并裁决 (重叠块全部保留) |
| `pdf_block_type` (PDF 自身声明, 如 `1`) | "这是图形" 类判断 |
| `content = null` (**永久**) | — |
| `coordinate_system`, `source_provenance` | — |

枚举来源 [OBSERVED]: P1 `_extract_block_observations` **显式跳过** `block_type != 0`
(atomic_text.py:256, sha `74d23ec7…`); P6 冻结裁决 "『这是 Image』 is forbidden"。
因此本枚举 = 层内**唯一**新提取代码: 读与 P1 **同一个** `page.get_text("dict")` 结构,
取 `type != 0` 块, 仅记录结构字段。**矢量绘图 (`get_drawings`) 不在覆盖范围** — 声明为
documented limitation (与 G-C3 披露一致)。

**稳定性声明**: 若未来任何字段无法证明 generic → 删字段, 不加字段 (challenge R3 延续)。

---

## 3. REGION CONTRACT

[CONTRACT] Region **不得**携带语义类型名 (`TABLE_REGION`/`GRAPHIC_REGION`/`FIGURE_REGION` 禁止)。
只有一种合法形态: **"detector/source 在参数 P 下输出 bbox B" 的 claim-fact**。

```text
RegionFact:
  region_id        = "{source_short}|{doc}|p{page}|{seq}" (纯函数)
  source_detector  = 注册身份字符串 (如 "p6_region_engine", "table_line_detector")
  source_sha       = 产生该 region 的代码 sha256 (全 hash)
  params_hash      = config_snapshot 的 sha256
  bbox             = detector 原值 (不变换)
  coordinate_system = 同 §2.1 常量
```

**共存不仲裁** [CONTRACT]: 同页可有 N 个来自不同 (或相同) detector 的 RegionFact;
层不输出 "哪个是真的"; 任何 selection/采信 = hypothesis/experiment 层职责。
`IN_REGION` 引用**具体** region_id → provenance 随查询结果天然可见。
RegionFact 进入层的唯一通道 = **注册表** (source_detector + sha + params_hash 登记);
未注册来源不得产生 RegionFact。

---

## 4. RELATION CONTRACT

### 4.1 IN_REGION [CONTRACT]

- 输入: `atom (任一 kind) + region_id (已注册 RegionFact)`
- 输出: **纯几何包含事实**: `{atom_id, region_id, contained: true/false, relation_def: "bbox_containment_v1", params_hash}`
  (contained = atom bbox 中心 ∈ region bbox, 或 bbox 交叠 — **二选一注册为 relation_def,
  本合约注册中心点包含 v1**; 不得输出 is_table_cell / is_figure / is_caption)
- 数学来源: 中心点计算与区间比较 = 对**冻结输出坐标**的平凡谓词 (非几何语义),
  定义冻结于 `relation_def` 版本 — 不构成第二套几何 (见 §6)

### 4.2 GAP_SEQUENCE [CONTRACT — 按 challenge R1 定义为测量, 非分类器]

| 问 | 定案 |
|----|------|
| 输入 | 一个 page 的 TEXT_ATOM 集合 (来自 P1/P2 expose) |
| 输出 | `[{seq: i, a_id, b_id, gap: <frozen horizontal_distance>, …}]` + **无任何类别判断** |
| gap 定义 | **冻结 `compute_pairwise(a,b).horizontal_distance`** (edge-gap, 重叠=0) — 层**零 gap 数学** |
| coordinate source | 冻结 P2 输出 (geometry sha 见 §6); PyMuPDF 页面坐标系 |
| ordering | **注册 sort key**: band 内按 `center_x` 升序, tie-break `(center_y, atom_id)` — 排序是确定性遍历, 定义冻结于 `measurement_identity` |
| threshold | **测量内零阈值**。均匀性/CV/等距判断全部 = hypothesis 侧对 gap 序列的计算 |
| grouping | **复用冻结 P2 `same_y_band`** (y_center 差 ≤ 3.0, `GeometryConfig(frozen=True)`) — 内容盲、确定性、通用几何构造, **非语义分类** → 证明成立, grouping 保留 |
| grouping 与 identity | band 容差是**冻结 config 的一部分** (config_snapshot 随输出持久化) → grouping **不**构成新测量身份; 测量身份 = `GAP_SEQUENCE_v1 = (frozen band @geometry_config sha) + (frozen edge-gap @geometry_engine sha) + (registered sort key v1)` |
| 禁止输出 | `is_uniform_run / is_tick_run / is_caption_group / is_table_row / is_*` — 任何形式 |

---

## 5. P1/P2 EXPOSURE CONTRACT (expose-first)

### Case A — 已有 artifact [CONTRACT]

条件: 目标 document 存在 P1/P2 artifact 且 sha 验证通过 (layer registry 登记 artifact 路径+sha)。
动作: **直接暴露** — 不重新计算、sha intact、provenance = `artifact_sha`、
**零几何变换** (原值透传)。现状 [OBSERVED]: 既有 P1/P2 artifact 覆盖验证文档集
(RM501/DC201 等, 报告导向, P2 pairwise 有 2000 截断) — registry 必须记录截断参数,
截断 artifact 不得冒充全量事实。

### Case B — 无 artifact [CONTRACT: 允许调用的冻结函数白名单]

| function | source file | sha256 | 输入 | 输出 | 确定性 |
|----------|------------|--------|------|------|--------|
| `extract_page_observations` | `perception/sandbox/observations/atomic_text.py` | `74d23ec784d657825780b35627f1b766ad87bd4dd74d88bbe4d560941f3b724a` | fitz page, page_no, doc_id, layers | AtomicTextObservation list | obs_id 纯函数 of (doc,page,source,index); 同 fitz 版本同 PDF → 逐字节同 |
| `extract_pdf_observations` | 同上 | 同上 | pdf_path, doc_id, layers | 全文档 obs | 同上 |
| `compute_single` | `perception/sandbox/geometry/geometry_engine.py` | `388e7939d334458e194dd4d805f6cafa0b975ce4f78d6b1137a965dd13d5554c` | obs dict, page w/h, cfg | SingleObservationGeometry | 纯函数; cfg frozen dataclass (`7ef3629e5a9b819c59724b8e94a831d10a94e875c8b9534d750a7dcfa849196b`) |
| `compute_pairwise` | 同上 | 同上 | obs a, obs b, cfg | PairwiseRelation | 纯函数, 对称可验证 (`verify_symmetry` frozen) |
| `compute_page_bundle` | 同上 | 同上 | obs list, w/h, cfg, max_pairwise | PageGeometryBundle (含 band/对齐组) | 纯函数; **层调用必须 `max_pairwise=None`** (禁止截断冒充全量) |
| `_round_bbox` (只读复用) | `atomic_text.py` | 同上 | bbox | rounded bbox | 纯函数 (NON_TEXT_BLOCK bbox 采用同一舍入约定) |
| `pymupdf_version` | `atomic_text.py` | 同上 | — | 版本字符串 | 环境函数, 仅入 provenance |

流程: `frozen function → layer artifact (持久化, 含 sha/config_snapshot/fitz version) → observation`。
**下次访问同一 document = 读 layer artifact (Case A)**。验收条件 (未来实现时执行, 本轮不运行):
同一 document 二次构建 → 新 artifact 与 persisted artifact **逐字节相同**; 不等 = 实现验收失败。

### Case C — 非相邻 / query-scoped 计算 [CONTRACT]

- 层内计算: **仅允许调用上表白名单冻结函数** (`compute_pairwise` 直接用于任意查询对,
  无截断问题) — **不重新实现任何几何数学**
- 层内**禁止**: 自写 gap/alignment/same_line/containment 几何 (IN_REGION 中心点谓词与
  GAP_SEQUENCE 排序键为唯一注册例外, 定义冻结于 relation_def/measurement_identity)
- hypothesis 侧: 可对层输出做任意算术 (如由冻结 `center` 值求 center-distance) — 这是
  **query-side 计算**, 不入层、不入测量身份
- 第二套 coordinate truth: **无** (见 §6)

---

## 6. GEOMETRIC SOURCE CONTRACT (single source of geometric truth)

[CONTRACT] 层产出的每一个几何事实必须携带 `geometry_source`, 取值仅为:

```text
geometry_source ∈ {
  "p1_artifact:<sha>", "p2_artifact:<sha>",            # Case A
  "frozen:atomic_text.py@74d23ec7…",                    # Case B (P1 函数)
  "frozen:geometry_engine.py@388e7939d334458e194dd4d805f6cafa0b975ce4f78d6b1137a965dd13d5554c@cfg:geometry_config.py@7ef3629e5a9b819c59724b8e94a831d10a94e875c8b9534d750a7dcfa849196b",
  "serialized-shape:geometry_observation.py@7731377cb8468c9171efdc89f03c1d60f11e1372e3671c64c80c77d6da7524da",  # 数据类 to_dict 形状锚 (serialization determinism)
  "frozen:span_config.py@55b9a23850398acc7a89d9164ada6a5788a0bd1777b3f2f520960db2febbb2b2 (仅引用, 不调用)",  # P4 语义引用 (same_line_tolerance 等)
  "layer:relation_def@v1 / layer:measurement_identity@v1"  # §4 两项注册例外
}
```

[OBSERVED] 可复用性核查结论: P1/P2 已提供**足够**的冻结原语
(提取 / single / pairwise / band 组群全部 frozen, GeometryConfig 为 `frozen=True` dataclass)
→ **无 `GEOMETRIC_PRIMITIVE_GAP`**。P4 的 same_line (3.0) 仅作语义引用对照 (层不做 P4 合并,
不调用 P4 函数); 若未来需要与 P4 语义对齐的谓词 → 走 §10 升级路径, **不私下补数学**。

---

## 7. PROVENANCE CONTRACT

每个 observation 必须可回答: **"由哪个 frozen/registered source 在什么参数下产生"**。

| 字段 | 必要性 | 理由 |
|------|--------|------|
| `source_sha` (artifact 或 frozen function) | **必要** | 可追溯性核心 |
| `params_hash` | **必要** | 几何 cfg / detector params 身份 |
| `schema_version` | **必要** | 层结构演进 |
| `coordinate_system` | **必要** | 几何可解释性前提 |
| `document_id` + `page_reference` | **必要** | 事实定位 |
| `pymupdf_version` | **必要** | Case B 重放确定性依赖环境版本 (现值 1.26.5) |
| ~~timestamp / host / author / tool 链路~~ | **删除** | "看起来完整" 但违反 determinism (§8); 仅允许出现在层 artifact 的 **build 段** (非 observation identity) |

---

## 8. DETERMINISM CONTRACT (验收条件, 本轮不运行)

同一 `document + source version + params + query` ⇒ **完全相同 observation**。

| 维度 | 验收条件 |
|------|---------|
| identity determinism | 所有 id (atom_id/region_id) = 纯函数 of 内容坐标; **禁** timestamp/random UUID/runtime 序 |
| ordering determinism | 一切列表输出使用注册 sort key + 显式 tie-break (§4.2); 禁依赖 dict 迭代序/文件系统序 |
| geometry determinism | 仅白名单冻结函数 (§5); cfg frozen; fitz version 入 provenance; 版本变更 ⇒ 重放失效并强制重建 (不静默混用) |
| serialization determinism | 固定 key 序、固定浮点舍入 (冻结 `_round_bbox` 约定; 测量输出**不引入新舍入**)、UTF-8、无换行差异 |
| 浮点 | 层不做新浮点运算 (gap 值 = 冻结函数原值透传) |

---

## 9. VERSIONING CONTRACT (四版本正交, 不得混合)

| Version | 定义 | 变更示例 | 规则 |
|---------|------|---------|------|
| `observation_schema_version` | 字段/数据结构 | 加字段/改字段名 | 破坏性 → major++, 兼容 → minor++ |
| `measurement_identity_version` | **几何测量定义** | gap 定义 center↔edge、sort key、band 来源更换 | **任何变更 → 必须 ++, 禁止静默更新**; 新身份并行共存, 旧身份按注册表保留 |
| `detector_version` | source detector | table_line_detector 更换/升级 → 新 RegionFact source_sha | RegionFact 永远携带自己的 sha; 层不合并不同 detector 输出 |
| `query_version` | hypothesis 自身查询逻辑 | 任何 hypothesis 内部变化 | **完全在 hypothesis 侧**, 层不感知不记录 |

`GAP_SEQUENCE_v1 = frozen edge-gap + frozen band(3.0) + sort_key_v1` — 以上任一构成变化即
`measurement_identity_version++`。

---

## 10. HYPOTHESIS BOUNDARY

Hypothesis **可以声明**: `required_atoms` / `required_relations` / `required_regions` (闭集内) +
自带词法/统计解释。
Hypothesis **不可以**: 修改 observation schema / 修改 observation semantics / 私改测量定义 /
修改 frozen geometry / 在层注册 semantic label / 在层写入任何对象。

需要真正新的 measurement → **`NEW_OBSERVATION_MEASUREMENT_REQUEST`**
→ governance → design → experiment → `measurement_identity_version++` promotion。
**GT 冻结前完成, 严禁 seeing-results 后扩层** (§9 challenge 延续)。

---

## 11. HUMAN FEEDBACK INTERFACE

不变 (Phase 1/Phase 4 已定): Human = **1-click boundary judgment**;
机器链 = Human Feedback → failure pattern (只读分析) → hypothesis → required observables → 层查询。
**禁止增加**: reason_category / technical diagnosis / detector choice / feature selection
(任何要求人类填写技术字段的接口设计 = 违约)。

---

## 12. IS-11 COMPATIBILITY (设计级, 不运行)

| IS-11 所需信息 | 层表达 |
|---------------|--------|
| 表格区域归属 | RegionFact (`table_line_detector@022f5c21e872ad9e737ddadb10a3f9eb8ff0ddd31333dacd6f30610cfbd8d79b`, params_hash) + IN_REGION |
| cell 相邻/对齐 | TEXT_ATOM + P2 `same_y_band` / ALIGNED_X / `compute_pairwise` (冻结) |
| 语义判定 (cell column 等) | hypothesis 侧 — **不需要 `TableCellObservation`** |

✅ PASS — 仅 Atom + Region + IN_REGION + 既有 P2 几何即可表达。

## 13. IS-14 COMPATIBILITY (设计级, 不运行)

| IS-14 所需信息 | 层表达 |
|---------------|--------|
| caption 上下文 | TEXT_ATOM (P4 合并前原子仍可查) + P2 pairwise gap — 词法模式在 hypothesis 侧 |
| axis tick 结构 | TEXT_ATOM + P2 `same_y_band` + `GAP_SEQUENCE_v1` (纯测量; 均匀性判断 = hypothesis; 冻结 OBS-C 不回改) |
| raster 图形 | `NON_TEXT_BLOCK_ATOM` (presence/bbox; content 不可达 = documented limitation) |
| image context | NON_TEXT_BLOCK_ATOM 邻近查询 (P2 pairwise, 冻结) |

✅ PASS — **不需要** `FigureCaptionObservation` / `AxisTickObservation` / `TableCellObservation`
(若需要 = 架构 FAIL, 本合约判定未触发)。

---

## 14. ANTI-OVERENGINEERING GATE

| Gate | 结论 |
|------|------|
| Schema Growth (IS-15..18 需新 semantic atom/relation?) | **否** — 闭集覆盖; 新测量走 §10 请求路径 |
| Detector Growth | **仅增加 provenance-backed RegionFact 数据**, schema 不动 (注册表治理) |
| Decision Leakage | **零** — 层输出无 is_*/score/decision; §4 两例外均为无类别几何事实 |
| Frozen Impact | **零** — 新文件全部在 `tmp/perception/atomic_observation/`; 冻结函数只读调用 |
| Duplication | **无第二套几何** — 白名单制 (§5) + geometry_source 强制 (§6); 唯一新代码 = NON_TEXT_BLOCK 枚举 + IN_REGION 谓词 + 排序键 (均注册定义, 非几何语义) |

---

## 15. IMPLEMENTATION SCOPE (未来授权时的最大允许范围)

### 允许创建 (全部限于 `tmp/perception/atomic_observation/`)

```text
tmp/perception/atomic_observation/
├── atomic_observation_schema.json      # Atom/RegionFact/Relation schema (本文档 §2-§4 的机器可读形式)
├── layer_registry.json                 # 冻结函数白名单 sha + RegionFact detector 注册表 + 版本表 (§5/§6/§9)
├── adapter.py                          # expose-first adapter: registry 查表 → Case A expose / Case B 白名单调用
├── non_text_block.py                   # 唯一新枚举 (§2.2: 同 fitz dict 结构, type!=0, 结构字段)
├── relations.py                        # IN_REGION (relation_def v1) + GAP_SEQUENCE (measurement_identity v1) — 仅白名单函数 + 注册谓词
├── verify_determinism.py               # §8 验收测试: 二次构建逐字节相同 / expose-first 相等 / frozen 完好复查
└── CONTRACT.md                         # 本文档副本 (实现者唯一权威规范)
```

### 绝对不能碰 (无例外)

```text
perception/sandbox/**                    (P1-P7 全部现有代码, 含 geometry/observations/span/structure/validation/region)
chunker/**                               (table_line_detector @022f5c21e872ad9e737ddadb10a3f9eb8ff0ddd31333dacd6f30610cfbd8d79b)
tmp/perception/p1..p7/**                 (全部既有 artifact — 只读)
tmp/is11_* / tmp/phase3_* / tmp/phase4_* (冻结实验 artifact — 只读)
tmp/is11_semantic_ground_truth.json      (GT)
P7.1/P7.2 冻结清单所列 6+ 文件           (structure/**, p7_runner.py 等)
MAP 文档 / roadmap                       (不得修改)
```

Scope 判定: **明确** (无 `IMPLEMENTATION_SCOPE_UNRESOLVED`)。
任何超出上表的新增/修改 = 违约, 验收测试 (verify_determinism.py 的 frozen 复查) 必须失败该实现。

---

## 16. FINAL GATE

| 阻塞条件 (§十五) | 状态 |
|------------------|------|
| GAP_SEQUENCE semantics 不清 | **已解决** — 纯测量定义完备 (§4.2): 冻结 gap + 冻结 band + 注册 sort key, 零阈值零类别 |
| P1/P2 reusable primitive 不足 | **已解决** — 白名单 6 函数 + frozen cfg 覆盖全部需求; 无 GEOMETRIC_PRIMITIVE_GAP |
| provenance 不完整 | **已解决** — §7 最小必要字段集 (含 pymupdf_version), 装饰字段删除 |
| geometry source 不统一 | **已解决** — §6 geometry_source 枚举封闭, 白名单禁平行数学 |
| NON_TEXT_BLOCK_ATOM contract 不稳定 | **已解决** — §2.2 四字段封闭 + content=null 永久 + 命名合规冻结裁决 |

```text
╔══════════════════════════════════════════════════════════════╗
║  FINAL GATE = IMPLEMENTATION_CONTRACT_READY                  ║
║  (READY ≠ 授权实现; 仅为 "可被安全实现" 的合约就绪声明)        ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 17. 最终治理

```text
PRE-IMPLEMENTATION CONTRACT REVIEW = COMPLETE
IMPLEMENTATION_CONTRACT = READY (未激活 — 激活需显式 IMPLEMENTATION AUTHORIZATION)
IMPLEMENTATION = NOT AUTHORIZED
EVALUATION = NOT AUTHORIZED
GT = NOT AUTHORIZED
FROZEN MODIFICATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
PRODUCTION = FALSE
CAPABILITY REGISTRATION = NOT AUTHORIZED
RUNTIME INTEGRATION = NOT AUTHORIZED

NO CODE CREATED THIS ROUND
NO EXISTING CODE MODIFIED
NO NEW EXPERIMENT
NO MAP MODIFICATION
FROZEN BASELINE = INTACT

STOP = TRUE
WAIT FOR EXPLICIT AUTHORIZATION
```
