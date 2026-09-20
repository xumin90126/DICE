# P7 Uncertainty Propagation Contract

> 核心原则：**Downstream cannot silently erase upstream uncertainty.**
> 允许：新增独立证据可提高置信，但必须可解释、可追踪、写入 decision_trace。

## 1. 上游置信度的输入集合

P7 的每个 StructureHypothesis 引用上游证据时，可能读到以下置信度来源：

| 上游置信度 | 来源 | 取值 |
|---|---|---|
| span 置信度 | P4（构造方法确定性） | 隐式 HIGH（纯几何规则） |
| reading order 置信度 | P5 `pro.confidence` | HIGH / MEDIUM / LOW / UNKNOWN |
| column 置信度 | P5 ColumnGroup.confidence | HIGH / MEDIUM / LOW / UNKNOWN |
| region 置信度 | P6 RegionObservation.confidence | HIGH / MEDIUM / LOW / UNKNOWN（已 min 合并 overlap 歧义） |

## 2. 置信度归一化（P7 内部）

P7 定义统一五级：

```
UPSTREAM_HIGH    ← 上游 HIGH
UPSTREAM_MEDIUM  ← 上游 MEDIUM
UPSTREAM_LOW     ← 上游 LOW
AMBIGUOUS        ← 上游存在 overlap/列歧义，或证据互相冲突
UNKNOWN          ← 上游 UNKNOWN，或证据不足以计算
```

## 3. 传播规则（固定契约）

1. **基线规则**：`StructureHypothesis.confidence = min(所有被引用上游证据的 confidence)`。
   - 例：region=HIGH 但 reading_order=LOW → hypothesis 基线 = LOW。
2. **禁止静默提升**：P7 不得在未提供新独立证据时，把 LOW/AMBIGUOUS/UNKNOWN 直接写成 HIGH。
3. **允许可解释提升**：新增**独立**证据（来自不同证据类别：Geometry/Style/Order/Region）可提升置信。提升必须：
   - 在 `decision_trace` 记录「新增证据 X，类别 Y，为何提升」；
   - 提升幅度有界（单条新证据至多提升一级：UNKNOWN→LOW→MEDIUM→HIGH）。
   - 多类证据叠加才可跨多级，且每级都在 trace 中可解释。
4. **AMBIGUOUS 的语义**：证据互相冲突（如 style 指向 heading、但 position 指向 body）→ 置信标 AMBIGUOUS，**绝不**用「多数票」强行消歧。冲突证据双方都写入 `conflicting_evidence`。
5. **UNKNOWN 的语义**：证据不足（如只有 1 类弱信号）→ 置信 UNKNOWN，且 hypothesis 进入 Human Validation，**不**进入自动结构。
6. **溯源保留**：hypothesis.provenance 必须记录所有被引用证据的 `(source_layer, observation_id/span_id/region_id, 原始 confidence)`，保证逐条可回查。

## 4. 判定示例

| 上游事实 | 传播结果 | 说明 |
|---|---|---|
| region=HIGH, order=HIGH, style=bold+size18 | heading hypothesis 可 MEDIUM/HIGH | 多类独立证据可解释提升 |
| region=HIGH, order=LOW（overlap 歧义） | hypothesis 基线 LOW | 不静默提升 |
| style 指向 heading，position 指向 body | hypothesis=AMBIGUOUS | 冲突证据，不强行消歧 |
| 仅 1 类弱信号（如仅 bold） | hypothesis=UNKNOWN | 证据不足，不产出结论 |

## 5. 违规即回归失败

P7 验证必须包含「不确定性传播」断言：对任一 hypothesis，`hypothesis.confidence > min(upstream confidences)` 且无 decision_trace 解释 → 判为 **No Semantic Leakage / 静默提升违规**，回归失败。
