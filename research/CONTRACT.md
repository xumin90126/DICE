# CONTRACT.md — Atomic Observation Layer v1

> 实现者唯一权威规范。上层合约: `tmp/atomic_observation_implementation_contract.md` (ACCEPTED, 不可重释)。
> 授权: IMPLEMENTATION = AUTHORIZED (scope = 本层 v1 only); EVALUATION / GT / P7.3 / FROZEN MODIFICATION = NOT AUTHORIZED。

## Declarations (不可协商)

```text
Observation ≠ Interpretation
Observation ≠ Decision
Observation ≠ Capability
Observation Layer does not own Runtime Authority.
```

## 1. Layer purpose

把已冻结的 P1-P6 事实 **read-only 暴露**为可查询的原子观测 (expose-first), 加上最小的新增面
(NON_TEXT_BLOCK 枚举 / IN_REGION / GAP_SEQUENCE_v1), 使未来 hypothesis 能以
`required_atoms / required_relations / required_regions` 声明制接入 — 而不需要
detector/feature 的累积。它不是 parser replacement / semantic classifier / detector
arbitration layer / decision engine / Evidence Admission / Capability layer / Runtime / P7.3。

## 2. Atom contract

- **TEXT_ATOM**: P1 `AtomicTextObservation` (span layer) 逐字段透传; `atom_id = P1 observation_id`
  (禁止重新生成); bbox/text verbatim; 禁 normalize/rewrite/semantic classify/merge。
- **NON_TEXT_BLOCK_ATOM**: `atom_id = NTB|{doc}|p{page}|{block_index}` (纯函数);
  bbox/pdf_block_type verbatim; **content = null 永久**; 禁 OCR/视觉解释/去重/仲裁;
  禁 image/figure/chart/caption/axis/table/diagram 等任何语义命名。
  矢量绘图不覆盖 (documented limitation)。

## 3. RegionFact contract

字段封闭: `region_id` (纯函数 `{source_short}|{doc}|p{page}|{seq}`) / `source_detector` (注册) /
`source_sha` (detector 代码 sha) / `params_hash` / `bbox` (verbatim) / `coordinate_system`。
唯一进入通道 = 注册表。多 detector 共存, **层不仲裁真伪**; 禁 TABLE_REGION/GRAPHIC_REGION 等
语义类型名; P6 region_type/confidence/decision_trace 一律不复制。

## 4. Relation contract

- **IN_REGION** (`bbox_containment_v1`): atom bbox 中心 ∈ region bbox (注册的平凡谓词例外)。
  输出封闭: `{atom_id, region_id, contained, relation_def, params_hash, geometry_source, document_id, page_reference}`。
  禁一切 `is_table_cell / is_figure / is_caption / ...`。
- **GAP_SEQUENCE_v1** (**measurement, 不是 classifier**):
  - grouping = 冻结 P2 `same_y_band` 邻接集消费 (anchor ∪ members, 唯一 frozenset)
  - gap = 冻结 `compute_pairwise().horizontal_distance` **原值透传** (层零 gap 数学)
  - ordering = sort_key_v1 `(center_x, center_y, atom_id)`
  - **零阈值**: 均匀性/CV/等距判断全部 hypothesis 侧
  - 输出仅 `{seq, a_id, b_id, gap}` 记录; **禁** `is_uniform_run / is_tick_run / ...` 任何布尔
  - gap 定义/分组/排序任何变化 ⇒ `measurement_identity_version++`, 禁止静默更新 v1

## 5. Provenance

每个 observation 受 7 字段约束: `source_sha / params_hash / schema_version /
coordinate_system / document_id / page_reference / pymupdf_version`。
timestamp/host/author 禁入 identity (仅 build 段, 且本实现完全不使用 timestamp)。

## 6. Determinism (验收已执行)

同 document + source version + params + query ⇒ **逐字节一致** (Case B 重建、Case A 暴露、
GAP_SEQUENCE 查询三方验证)。固定 key 序 serialization (`sort_keys=True`); 禁 random UUID /
timestamp identity / runtime iteration order / 新浮点运算 (gap 值为冻结函数原值)。

## 7. Versioning (四版本正交)

`observation_schema_version` (结构) / `measurement_identity_version` (GAP_SEQUENCE_v1,
bbox_containment_v1) / `detector_version` (每 RegionFact 携带自身 sha) / `query_version`
(hypothesis 侧, 层不感知)。

## 8. Geometry source (single source of truth)

一切几何事实携带 `geometry_source`, 枚举封闭 (registry.geometry_sources):
`p1/p2/p6_artifact:{sha}` | `frozen:atomic_text.py@74d23ec7…` |
`frozen:geometry_engine.py@388e7939…@cfg:geometry_config.py@7ef3629e…` |
`serialized-shape:geometry_observation.py@7731377c…` | `frozen:span_config.py@55b9a238… (仅引用)` |
`layer:relation_def@bbox_containment_v1` / `layer:measurement_identity@GAP_SEQUENCE_v1`。
**层不重写任何几何数学**; 需求无法由冻结原语表达时 → `GEOMETRIC_PRIMITIVE_GAP`, 停止该部分。

## 9. Frozen dependency (白名单, 只读)

`extract_pdf_observations` / `extract_page_observations` / `compute_single` /
`compute_pairwise` / `compute_page_bundle` (**必须 max_pairwise=None**) / `_round_bbox` /
`pymupdf_version` — 全部 sha 锚定于 `layer_registry.json.frozen_sources`。
截断 P2 artifact 只暴露 singles 并标记 `truncated: true`, GAP_SEQUENCE 拒绝之。

## 10. Hypothesis boundary

可声明 `required_atoms / required_relations / required_regions` (闭集内)。
不可: 改 schema / 改 semantics / 私改测量定义 / 改 frozen geometry / 注册 semantic label /
向层写任何对象。新测量 → `NEW_OBSERVATION_MEASUREMENT_REQUEST` → governance → design →
experiment → versioned promotion (GT 冻结前)。

## 11. Human Feedback boundary

Human = 1-click boundary judgment (不变)。禁止 reason_category / technical diagnosis /
detector choice / feature selection。

## 12. Explicit forbidden semantics

`is_table_cell / is_table / is_figure / is_caption / is_axis / is_chart / is_tick_run /
is_uniform_run / is_caption_group / is_table_row / MERGE / KEEP / REJECT / score /
confidence / ranking / routing / recommendation / execution_plan / fallback / retry /
override / correction` — 进入 schema / registry / relation output 任一 = 验收 FAIL
(verify_determinism.py §K 强制扫描)。

## 13. Known limitations

1. 矢量绘图 (`get_drawings`) 不覆盖 — 与冻结 P1 block 层同一 surface 限制。
2. raster 内容不可达 (无 OCR) — 仅 presence/bbox。
3. P3 style_signature 未暴露 (P3 函数不在冻结白名单)。
4. 截断 P2 artifact 只暴露 singles; GAP_SEQUENCE 拒绝截断数据。
5. 层不调用任何 detector (registered_but_never_invoked); RegionFact 数据来自 detector
   既有 artifact 的 Case A 暴露。
