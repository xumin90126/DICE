# P7.2 Implementation Precheck — Read-only

> 在写任何 P7.2 代码之前，检查 design 中的四对象与现有仓库的关系。
> 优先复用，不重复定义。

## 1. StructureHypothesis 是否已是现有 Observation 对象？

**是。** P7.1 `StructureHypothesis`（`perception/sandbox/structure/structure_hypothesis.py`）已具备 Observation 所需全部语义：
- `hypothesis_id`（确定性 sha1[:16]）→ 可直接作 observation_id
- `status`（= `PROPOSED`，P7.1 永不离开）→ Observation 不可变语义已满足
- `provenance` / `decision_trace` / `coord_origin` / `construction_version` → 审计能力已具备
- `document_id` / `page_number` / `span_ids` / `region_ids` / `geometry` / `confidence` → source reference 已具备

**结论**：Observation = StructureHypothesis，**直接引用 hypothesis_id 作 observation_id，不新建对象、不复制内容**。

## 2. 是否已有 ID？

是。`hypothesis_id = sha1(doc|page|type|sorted span_ids)[:16]`，确定性。P7.2 的 ValidationTask / ValidationRecord / ValidatedEvidence 各自的 ID 按 design §7 公式生成（确定性，无随机 UUID）。

## 3. 是否存在现有 evidence object，避免重复定义？

**无。** `src/schemas.py` 仅含 datasheet 提取 schema（StorageCondition/Component/Specification），是不同领域的提取目标结构，非 Evidence governance 对象。restore 区 `tmp/phase52_1/` 是标注 fixture（非 Evidence 对象）。**无冲突，可安全新建 ValidatedEvidence。**

## 4. 是否已有 audit/trace 能力可复用？

是。StructureHypothesis.decision_trace（4 步：input/signals/decision/confidence）+ provenance（source_layers + upstream_confidence）已是完整审计链。P7.2 不重建 audit，只在其上追加 ValidationRecord 这一层裁定审计。

## 5. 是否已有 timestamp / provenance / source reference？

是。provenance（dict）+ coord_origin + decision_trace 已含 source reference。**timestamp 是 P7.2 新增**——StructureHypothesis 无 timestamp（它是确定性产物，时间无关），ValidationTask/Record 需 created_time/timestamp（来自真实 Human interaction）。

## 6. 是否已有状态字段？

是。`status = PROPOSED`。P7.2 **不改这个字段**（Observation 保持 PROPOSED 永不可变）；ValidationTask 有独立的 `task_status`（PENDING_HUMAN_REVIEW / IN_REVIEW / RESOLVED），ValidationRecord 有 `reviewer_decision`（ACCEPT/REJECT/NEED_REVIEW）。三套状态独立。

## 结论：无冲突，可实施

- Observation = 引用 StructureHypothesis（不新建、不复制、不改）
- ValidationTask / ValidationRecord / ValidatedEvidence = 三个新对象（无现有重复）
- 新增 `perception/sandbox/validation/` 包，不碰 P1–P7.1 任何文件
- timestamp / duration_seconds = P7.2 新增（来自真实 Human interaction）

**无 STOP 条件触发。设计与现有代码无冲突。可进入实施。**
