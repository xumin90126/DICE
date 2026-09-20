# Perception Development Roadmap

> 只读规划文档。未修改任何代码/数据/annotation/manifest。
> 本文档描述 TRACK B（Perception Development Sandbox）的阶段性开发路线。
> 所有阶段均不触碰 TRACK A（Frozen Evidence Baseline）。

---

## 总原则

- **TRACK A 全程不动**：730 pool / annotation / Evidence Store / Capability 保持冻结。
- **TRACK B 独立迭代**：在 `tmp/perception/` 下建立实验代码与数据，不写入任何 frozen 路径。
- **不实现识别算法**：本轮只做 Architecture / Dependency / Versioning Audit。Roadmap 是规划，不是实现。
- **零权威性贯穿**：所有阶段保持 T-7 约束（不分类、不评分、不决策）。

---

## 阶段 0：Audit & Design（本轮，已完成）

| 项 | 状态 |
|---|---|
| 三概念区分（Schema / Generator / Pool） | ✅ 完成 |
| PyMuPDF 数据层分析（char/word/span/line/block） | ✅ 完成 |
| 版本漂移发现（frozen pool 不可复现） | ✅ 完成 |
| row 104 全链确认 + 拆分可行性判断 | ✅ 完成 |
| DC201 p5 "Plate Position Step" 归属 C3 确认 | ✅ 完成 |
| 双轨架构设计（TRACK A / TRACK B） | ✅ 完成 |
| 版本化策略（v1/v2/validated + 三 pool） | ✅ 完成 |
| 依赖矩阵 | ✅ 完成 |

**产出**：`perception_dependency_audit.md`、`perception_dependency_matrix.json`、`perception_architecture.md`、`perception_development_roadmap.md`、`span_versioning_strategy.md`

---

## 阶段 1：Atomic Observation Layer（未来，需批准后启动）

**目标**：建立 PDF → Atomic Observation 的提取层，不依赖 CandidateSpan。

**范围**：
- 建立 AtomicTextObservation 提取器（基于 PyMuPDF word/span 层）
- 建立 GeometryObservation 派生（列/行/间距）
- 建立 StyleObservation 派生（字号/字体/bold）
- 建立 RegionObservation 派生（表格/图/正文/页眉页脚，含 UNKNOWN/DEFER）

**不变式**：
- 不修改 CandidateSpanGenerator
- 不修改 frozen 730 pool
- 不引入 span_type / capability / decision
- RegionObservation 不确定时标记 UNKNOWN，不猜

**验证**：
- RM501-P4 p2：Atomic Observation 能正确区分 'Position'(x513) 与 'Step'(x77) 为两个独立原子
- 跨版本稳定性：word/span 层在 PyMuPDF 版本间一致（block 层不一致，不使用）

**产出**：`tmp/perception/atomic_observation/`（提取器 + 观测数据）

---

## 阶段 2：Experimental Span Construction（未来，依赖阶段 1）

**目标**：基于 Atomic Observations 重新聚合为 ExperimentalSpan。

**范围**：
- Span Construction 算法（Geometry 分列 + Region 分区 + Style 辅助）
- 产出 ExperimentalSpan（复用 Schema 4-field，position_metadata 扩展 source_layer/column_index/region_type）
- 写入 Experimental Pool（独立存储）

**不变式**：
- 不写入 `tmp/phase48/` 或任何 frozen 路径
- 不自动覆盖 frozen pool
- 保持零权威性

**验证**：
- row 104 拆分：Experimental Pool 中 'Position' 与 'Step' 是两个独立 ExperimentalSpan
- Boundary Violation = 0（不跨越列/表格/图区边界）
- 不产生跨列腐败 span

**产出**：`tmp/perception/experimental_pool/`、`tmp/perception/experimental_generator/`

---

## 阶段 3：Evaluation & Comparison（未来，依赖阶段 2）

**目标**：对比 Legacy Span (v1) 与 Experimental Span (v2)。

**范围**：
- 只读对比桥：读 frozen pool + experimental pool，按同 PDF 同区域对齐
- 统计指标：
  - 正确拆分（v1 一个 → v2 多个，且 v2 更忠实）
  - 正确合并（v1 多个 → v2 一个，且合理）
  - 新增/消失 candidate
  - Boundary Violation Rate
  - bbox 忠实度（span_text 与 bbox 的视觉一致性）

**不变式**：
- 只读 frozen pool，不写回
- 对比结果写入 `tmp/perception/evaluation/`

**验证**：
- row 104：v1 `"Position\nStep"` (bbox x跨463pt) → v2 两个独立 span（bbox 各自忠实）✅
- DC201 p5 "Plate Position Step"：此 case 在 dice2 侧，属 C3，不在此 track 评估（除非 dice2 也接入 experimental perception）

**产出**：`tmp/perception/evaluation/comparison_report.md`

---

## 阶段 4：Human Validation（未来，依赖阶段 3）

**目标**：对 Experimental Span 做人工验证，独立于现有 annotation。

**范围**：
- 建立 experimental annotation workbench（独立于 phase52_1）
- 人工标注 ExperimentalSpan 的质量（忠实度/边界正确性）
- 不触碰现有 730 pool 的 annotation

**不变式**：
- 独立 annotation 存储
- 不修改现有 annotation protocol / 数据

**验证**：
- 验证率 ≥ v1 baseline（人工判断 v2 不劣于 v1）
- row 104 拆分被人工确认为正确

**产出**：`tmp/perception/experimental_annotation/`

---

## 阶段 5：Promotion Assessment（未来，依赖阶段 4）

**目标**：评估 Experimental Span 是否达到晋升为新 baseline 的条件。

**晋升条件（全部满足）**：
1. Boundary Violation = 0 on audit set（6 docs）
2. Human Validation rate ≥ v1 baseline
3. row 104 class split verified（'Position'/'Step' 正确拆分）
4. Full regression passes（碎片率/bbox 忠实度不退化）
5. No C1/C2/C3/C4 regression
6. 跨版本稳定性验证（新 PyMuPDF 版本下可复现）

**不变式**：
- 不自动执行 unfreeze
- 晋升需 EXPLICIT UNFREEZE APPROVAL（治理决策）

**产出**：`tmp/perception/promotion_assessment.md`

---

## 阶段 6：Baseline Migration（未来，需显式解冻批准后）

**目标**：将 validated Experimental Pool 迁移为新 baseline。

**范围**：
- 在新 PyMuPDF 版本下重新生成 pool（全部 4 份 frozen 文档 + 扩展文档）
- 重新标注 annotation（新 span_text → 新 candidate_key）
- 旧 730 pool 归档（保留为历史 baseline，不删除）
- 更新 EXPECTED_TOTAL（从 730 → 新值）

**前置条件**：阶段 5 全部通过 + 显式解冻批准

**不变式**：
- 旧 pool 不删除（归档为 v1-historical）
- annotation 迁移需人工逐条确认（不自动映射）

---

## 阶段依赖图

```
阶段 0 (Audit) ✅
    │
    ▼
阶段 1 (Atomic Observation)  ← 需批准启动
    │
    ▼
阶段 2 (Experimental Span Construction)
    │
    ▼
阶段 3 (Evaluation & Comparison)
    │
    ▼
阶段 4 (Human Validation)
    │
    ▼
阶段 5 (Promotion Assessment)
    │
    │  EXPLICIT UNFREEZE APPROVAL
    ▼
阶段 6 (Baseline Migration)
```

**当前状态**：阶段 0 完成。阶段 1-6 均为未来工作，需逐阶段批准。

---

## 与 DICE 2.0 C1-C4 的关系

| DICE 2.0 层 | 与 TRACK B 的关系 |
|---|---|
| C1（行级文本重建） | 独立。C1 在 dice2 用 dict 层自建 VLine，不产 CandidateSpan。TRACK B 的 Atomic Observation 层与 C1 的 rebuild 思路类似但目标不同（C1 产 chunk 元素，TRACK B 产 ExperimentalSpan）。 |
| C2（语义边界约束） | PAUSED。C2 的 boundary 概念可反哺 TRACK B 的 RegionObservation，但本轮不建立依赖。 |
| C3（表格二维重建） | 独立。DC201 "Plate Position Step" 是 C3 问题，不在 TRACK B 范围。TRACK B 的 RegionObservation 可标记表格区，但不做表格内部二维结构。 |
| C4（矢量图识别） | 独立。TRACK B 的 RegionObservation 可标记图区为 UNKNOWN/DEFER，交给 C4 处理。 |

**TRACK B 不阻塞 C1-C4，也不被 C1-C4 阻塞**——两者可并行（各自由各自批准触发）。
