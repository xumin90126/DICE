# Phase 3 — MAP Gap Report

## MAP GAP IDENTIFIED

### 缺口描述

对项目现有全部 MAP/治理文档的 READ-ONLY 检索 (OBSERVED):

| 文档 | 节点类型 | 是否定义 "实验 BLOCKED 后" 的节点 |
|------|---------|--------------------------------|
| `tmp/perception/perception_development_roadmap.md` | 阶段 0-6 (TRACK B perception 层) | ❌ 无 BLOCKED 状态; 阶段均为 完成/未来需批准 二态 |
| `tmp/stage5_next_information_source_decision.md` §10.5/§12/§13 | IS-Experiment 链: Phase 1→2→3 | ❌ §13 仅有 STOP 条件 ("user does not authorize next phase" 等), 无 BLOCK 后节点定义 |
| `tmp/perception/p7/is11_table_cell_context_experiment_design.md` §17 | IS-11 失败路径 | ⚠️ 有失败路径**词汇** (HUMAN_OWNED / 重新评估 boundary class / DEFER) 但仅针对 IS-11, 未形式化为通用 MAP 节点 |
| 各阶段实践 (closure notes / decision enums) | closure node / decision gate | ⚠️ 形态存在 (Stage 4 closure, 各阶段 final decision), 但未写入任何 MAP 文档作为标准节点 |

### 缺口的实际影响

1. Phase 3 BLOCKED 后, 治理上**没有预先定义的下一步节点** — 本次 "Sampling Strategy Diagnostic"
   是以复用已有节点形态 (closure + diagnostic + decision gate) 的方式执行的, 属于**实践存在、MAP 未形式化**。
2. 若不补齐, 未来任何实验 BLOCK 都会重新面临同样的定位真空。

### 处置 (遵守 "不擅自扩展 MAP")

- 本诊断**不**修改任何 MAP/roadmap 文档, **不**创建平行路线。
- 正式记录 GAP, 并给出**供治理决策的形式化建议** (建议本身不生效, 需显式批准):

```text
建议 (非生效): 在 IS-Experiment 链中增加标准节点 —

  EXPERIMENT PHASE
      ├── PASS  → 下一授权决策
      ├── FAIL_UTILITY / FAIL_SAFETY → failure diagnosis (已有 §38 实践)
      ├── INVALID → protocol audit
      └── BLOCKED (pre-condition) → CLOSURE & DIAGNOSTIC NODE
              ├── 输入: BLOCK 原因 + 冻结 artifact (无重抽样/无 tuning)
              ├── 动作: 假设对比诊断 (H1/H2/H3 类) + prevalence/representation 测量
              ├── 输出: DIAGNOSTIC STATUS + NEXT MAP ACTION (受控枚举)
              └── 边界: 任何实施/评估/GT/语料变更均需新的显式授权
```

- 该建议若被采纳, 应写入相应 MAP 文档 (本诊断未执行该写入)。
