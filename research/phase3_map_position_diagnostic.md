# Phase 3 — MAP Position Diagnostic

> READ-ONLY 定位诊断。未修改任何 Frozen 文件、未修改任何 MAP/roadmap 文档。
> 结论标签: OBSERVED (文档可查) / INFERRED (由文档推导) / HYPOTHESIS / NOT ESTABLISHED。

---

## 1. MAP 文档定位 (READ-ONLY 检索结果)

项目中存在**两层已文档化的 MAP/治理结构** (无单一统一 MAP 文件):

### 层 1 — Perception Development Roadmap (`tmp/perception/perception_development_roadmap.md`) [OBSERVED]

```text
阶段 0 (Audit & Design) ✅ 完成
    ↓
阶段 1 (Atomic Observation Layer)   ← 未来, 需批准启动
    ↓
阶段 2 (Experimental Span Construction)
    ↓
阶段 3 (Evaluation & Comparison)
    ↓
阶段 4 (Human Validation)
    ↓
阶段 5 (Promotion Assessment)      ← 晋升需全部条件 + EXPLICIT UNFREEZE APPROVAL
    ↓
阶段 6 (Baseline Migration)        ← 需显式解冻批准
```

节点类型: 阶段 (stage), 状态: 完成 / 未来需批准。**无 BLOCKED 状态, 无实验后诊断节点。**
该 roadmap 是 TRACK B perception 表示层的路线, 与 IS 信息源实验不属同一序列 (两者按文档声明互不阻塞)。

### 层 2 — IS-Experiment 阶段链 (Stage 5 decision §10.5/§12 + 各阶段任务门控) [OBSERVED]

```text
Stage 0-5 (IS-11 实验: corpus → 盲审 → GT → 机器评估 → closure → 下一信息源决策)
    ↓
Phase 1 (Human Feedback → Machine Improvement Diagnostic) = COMPLETE / LOOP_SUPPORTED
    ↓
Phase 2 (IS-14 Experiment Design) = COMPLETE / DESIGN_READY
    ↓
Phase 3 (IS-14 Machine Evaluation) = BLOCKED (G-C1 FAIL)
    ↓
[当前待定位节点]
```

该文档 §13 预注册了 Stop Conditions (含 "IS-14 cannot be stably observed" / "User does not authorize
next phase"), 但**没有定义 BLOCK 之后存在什么节点**。
IS-11 design §17 提供了失败路径词汇 ("转为 HUMAN_OWNED / 重新评估 boundary class / DEFER") [OBSERVED],
各阶段实践已有 closure note / decision gate 形态 [OBSERVED: is11_stage4_closure_final_report.md 等]。

---

## 2. 定位输出 (按任务要求字段)

### CURRENT_MAP_NODE

```text
层 2 (IS-Experiment 链): "Phase 3 — IS-14 GRAPHIC_TEXT_CONTEXT Controlled Experiment"
                          — 已进入, 终止于 pre-condition gate (G-C1)
层 1 (Perception Roadmap): 不适用 (IS 实验不在该链上; 其 阶段 1-6 为未来节点)
```

### CURRENT_STATUS

```text
Phase 3 = BLOCKED
IS-14 = GRAPHIC_TEXT_CONTEXT / HYPOTHESIS ONLY (未评估, 未证伪, 未证实)
Phase 2 = DESIGN_READY / ACCEPTED (其 G-C1 pre-condition 在本次 corpus 实例化中未达成)
```

### BLOCK_REASON

```text
G-C1 FAIL: 冻结样本 (n=54) 中 figure-context cases = 3 < 15 (要求 ≥15)
(G-C2 = PASS, G-C3 = PASS; 未进入 GT collection / Baseline B vs C / 任何评估)
```

### ALLOWED_NEXT_ACTIONS (依现有文档可推导) [INFERRED]

1. **closure / diagnostic 类节点** (形态已存在于实践: Stage 4 closure note、Stage 5 diagnostic) — 即本诊断
2. **decision gate** (每阶段已有 final-decision-enum 实践)
3. 若证据支持: 提交**新的设计文档** (design-only), 等待显式授权
4. 若走表示层变更: 层 1 roadmap 的 **阶段 1-2** (Atomic Observation / Experimental Span) — 已有节点, 需批准启动
5. DEFER (IS-11 design §17 词汇: "DEFER — 等待更好的技术")

### FORBIDDEN_ACTIONS [OBSERVED — 由本任务边界 + 既有文档]

re-sampling / corpus substitution / GT collection / 评估运行 / threshold·regex·observer tuning /
Frozen Baseline 修改 (P1-P6, P4, IS-01/02, table_line_detector, P7.1/P7.2, GT) /
P7.3 / Production / Capability Registration / Runtime Integration

### PROPOSED_DIAGNOSTIC_POSITION

```text
"Phase 3 Closure / Sampling Strategy Diagnostic"
  = closure node (阶段收尾记录, 复用 Stage 4 closure 实践)
  + diagnostic node (READ-ONLY 假设对比, 复用 Stage 5 Phase 1 诊断形态)
  + decision gate (输出 DIAGNOSTIC STATUS + NEXT MAP ACTION, 复用每阶段 decision-enum 实践)
```

不创建平行路线; 全部复用已有节点形态与词汇。

### MAP_EXISTING_OR_GAP

**MAP GAP IDENTIFIED** — 详见 `tmp/phase3_map_gap_report.md`。

要点 [OBSERVED]: 现有两层 MAP 均**没有**为 "实验 BLOCKED 之后的 closure/diagnostic 节点" 提供正式定义:
- 层 1 roadmap: 无 BLOCKED 状态, 无实验后节点;
- 层 2 阶段链: §13 只有 STOP 条件, 无 BLOCK 后节点;
- IS-11 design §17: 有失败路径词汇但只针对 IS-11 实验本身, 未形式化为通用节点。

处置: **不擅自扩展 MAP**。本诊断以 "复用已有节点形态" 的方式执行, 并将 GAP 正式记录,
留待治理决策 (是否把 closure/diagnostic-after-BLOCK 形式化为 MAP 标准节点)。

### REQUIRED_EXIT_GATE

```text
本诊断自身的退出条件 = 产出明确的:
  1. DIAGNOSTIC STATUS ∈ {GENUINE_SPARSITY, SAMPLING_FRAME_MISMATCH,
                          RESEARCH_OBJECT_MISMATCH, MIXED_CAUSE, INSUFFICIENT_EVIDENCE}
  2. NEXT MAP ACTION ∈ {REDESIGN_SAMPLING_FRAME, DESIGN_RESEARCH_OBJECT,
                        DEFER_IS14, COLLECT_MORE_EVIDENCE, NO_FURTHER_ACTION}
  3. 任何后续 implementation / evaluation / GT 均需新的显式授权 (本诊断不授予)
  4. 若 NEXT MAP ACTION 涉及表示层变更 → 必须走层 1 roadmap 阶段 1-2 批准,
     且任何 Frozen 影响必须经 阶段 5-6 promotion/unfreeze gates
```

---

## 3. 证据标签汇总

| 陈述 | 标签 |
|------|------|
| 两层 MAP 文档的内容与节点 | OBSERVED |
| Phase 3 = BLOCKED / G-C1 FAIL / G-C2·C3 PASS | OBSERVED (Phase 3 artifacts) |
| "无 BLOCK 后节点" → MAP GAP | OBSERVED (检索) + INFERRED (定性为 gap) |
| 本诊断的节点归属 (closure+diagnostic+decision gate 复用) | INFERRED |
| 表示层变更应走 roadmap 阶段 1-2 | INFERRED (节点存在性 OBSERVED) |
