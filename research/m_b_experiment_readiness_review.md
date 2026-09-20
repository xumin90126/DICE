# M-B Experiment Readiness / Mechanism Boundary Review

> **模式: READ-ONLY / NO IMPLEMENTATION / NO EXPERIMENT EXECUTION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `system_reframing_summary.md`（上轮推荐 M-B 为 PRIMARY route）
> 本文件审查 M-B 是否真正具备实验条件。

---

## 1. Executive Summary

```
M-B = NOT_READY

BLOCKING CONDITIONS:
  1. DCE-07 已通过反事实审查关闭 locality 路线 (PLAUSIBLE_BUT_UNSAFE, ROUTE_CLOSED)
  2. DCE-06 的 "local isolation PROVEN" 是合成测试 (手动划定 y-range)，
     证明的是污染机制真实存在，NOT 任何自动方法能安全定位表格边界
  3. L1-correct (纯证据查询，不改 TLD): 0/3 恢复 — band 仍 page-global
  4. 任何能恢复的变体 (L1-modified) 需修改 TLD anchor 逻辑 → TLD_MODIFICATION_REQUIRED = TRUE
  5. Locality ≠ Table: PROVEN UNSAFE — prose-with-citations 与 table 几何性质完全相同

CORRECTION TO PRIOR SUMMARY:
  system_reframing_summary.md 称 M-B "PROVEN local isolation (align 0.23→0.96-1.00)"
  并列为 PRIMARY_NEXT_RESEARCH_ROUTE。该表述基于 DCE-06 的合成测试，
  未充分纳入 DCE-07 的反事实关闭结论。DCE-07 已证明：
  自动 locality 方法无法安全区分 prose 与 table，路线 CLOSED。
  本审查纠正这一过度乐观表述。

VERDICT:
  NEW_OBSERVATION_REQUIRED     = FALSE
  NEW_DETECTOR_REQUIRED        = FALSE
  TLD_MODIFICATION_REQUIRED    = TRUE (if recovery desired; L1-correct alone = 0% recovery)
  FROZEN_ARTIFACT_MODIFICATION = FALSE
  SEMANTIC_LEAP                = TRUE (local cluster → table 是未经验证的语义跳跃)
  AUTHORITY_LEAKAGE            = FALSE
  EXPERIMENT_SCOPE             = READ_ONLY (但实验已在 DCE-07 中执行并被证伪)

  M-B = NOT_READY
```

---

## 2. M-B Research Question

> 冻结的 P2 Geometry / P5 Reading Order 等已有 Evidence，经过局部 Evidence Query /
> Structural Context Organization 后，能否在 TLD 失败页上**稳定定位**真正的小表格区域，
> 从而减少 page-global contamination？

**本审查的关键区分**:

- DCE-06 "local isolation" 回答的是: **如果**手动隔离表格区域，TLD 检查能否通过？
  → 回答: YES (align 0.23→0.96-1.00)。这证明**污染机制真实**。
- M-B 真正要回答的是: 能否**自动**找到表格边界并隔离？
  → DCE-07 已回答: **NO, UNSAFE**。无几何信号能安全区分 prose 与 table。

这两个问题不同。M-B 的问题已被 DCE-07 回答并关闭。

---

## 3. Primary Research Layer

```
PRIMARY   = A (Evidence Organization / Query) — 形式上
SECONDARY = B (Perception Algorithm) — 实质上已跨越边界
```

### 跨界检查: M-B 是否已跨越 Evidence Organization → TLD Decision Logic?

**已跨越 [OBSERVED, DCE-07]**:

M-B 的目标是让 TLD 在失败页上恢复表格检测。DCE-07 测试了 3 种 locality 方法:

| 方法 | 是否改 TLD 逻辑 | 恢复率 | 安全性 |
|------|----------------|--------|--------|
| L1-correct (候选中心，TLD 精确 anchor) | NO | 0/3 (0%) | 安全但无效 |
| L1-modified (is_multicol anchor) | **YES** (改 anchor 定义) | 1/3 (33%) | **UNSAFE** (2 FP on prose) |
| L2 (column-pattern break) | **YES** (改 band formation) | 0/3 (0%) | **UNSAFE** (split success + FP) |

**结论**: 
- 纯 Evidence Organization (L1-correct，不改 TLD): 0% 恢复 — band 仍 page-global
- 任何能恢复的方法 (L1-modified): **已跨越到 TLD Decision Logic** (修改 anchor 定义)
- M-B 如果要保持 "不改 TLD"，则 = L1-correct = 0% 恢复 = 无实验价值
- M-B 如果要恢复失败案例，则 = L1-modified = TLD_MODIFICATION_REQUIRED = TRUE

**边界已跨越**: M-B 无法在不跨越 Evidence Organization → TLD Decision Logic 边界的情况下
产生任何恢复效果。

---

## 4. Existing Evidence Inventory

逐项确认 M-B 所需输入:

| 输入 | 来源 | 状态 |
|------|------|------|
| P1 AtomicTextObservation | atomic_text.py | EXISTING_FROZEN (drift=0) |
| P2 GeometryObservation (same_y_band, h_gap, fragment x/y, center_x) | geometry_engine.py | EXISTING_FROZEN (drift=0) |
| P3 StyleObservation | style_observation.py | EXISTING_FROZEN (drift=0) — M-B 未使用 |
| P4 ExperimentalSpan | span_config.py | EXISTING_FROZEN (drift=0) — M-B 未使用 |
| P5 ReadingOrder (column groups) | reading_order | EXISTING_FROZEN (drift=0) |
| P6 RegionObservation | region_engine.py | EXISTING_FROZEN (drift=0) — M-B 未使用 |
| P7.1 StructureHypothesis (REPEATS_ACROSS_PAGES) | boundary resolution | EXISTING_FROZEN (drift=0) — M-B 未使用 |
| TLD 当前输入 | table_line_detector.py | EXISTING_FROZEN (022f5c21) |
| 其他输入 | — | NONE |

```
NEW_OBSERVATION_REQUIRED = FALSE
```

全部输入来自已有冻结 Evidence。无新增 observation 需求。

---

## 5. New Observation Requirement

```
NEW_OBSERVATION_REQUIRED = FALSE
```

P1/P2/P5 提供全部所需 L1/L2 几何。DCE-07 §16 明确: "NEW_OBSERVATION_NEEDED = NO"。
问题不在 observation 缺失，在于**无几何信号能安全区分 prose 与 table** (DCE-07 §13)。

---

## 6. New Detector Requirement

```
NEW_DETECTOR_REQUIRED = FALSE
```

TLD 已存在并具备表达 different_cell 的能力 (DCE-06 Case B)。问题不在缺 detector，
在 detector 的检测算法在特定页面模式上失败。

但注意: DCE-07 §13 发现 "无几何信号能安全区分 prose 与 table" — 这暗示
**如果要安全区分，可能需要非几何信号 (语义/内容理解)**，但这属于 NEW_OBSERVATION
或 LLM 范畴，均被禁止。这是 M-B 的根本性阻塞，不是 detector 数量问题。

---

## 7. TLD Modification Boundary

逐项检查 M-B 是否会改变 TLD:

| TLD 组件 | L1-correct 是否改变 | L1-modified 是否改变 | L2 是否改变 |
|----------|--------------------|--------------------|------------|
| detector | NO | NO | NO |
| anchor logic (len>=2) | NO | **YES** (→ is_multicol) | NO |
| threshold (0.75/0.45) | NO | NO | NO |
| grouping rule | NO | NO | **YES** (column-pattern break) |
| band formation | NO (band scope 不变) | YES (band scope 变) | YES (band formation 变) |
| decision policy | NO | NO | NO |
| merge/keep logic | NO | NO | NO |
| ranking | NO | NO | NO |
| confidence | NO | NO | NO |
| fallback | NO | NO | NO |
| arbitration | NO | NO | NO |
| consumer semantics | NO | NO | NO |

```
TLD_MODIFICATION_REQUIRED = TRUE
```

**判定依据**:
- L1-correct (不改 TLD): 0/3 恢复 → 无实验价值
- 任何能恢复的方法 (L1-modified / L2): 修改 TLD anchor logic 或 band formation → TRUE
- M-B 要产生恢复效果，必须修改 TLD → 违反当前 "不改 TLD" 约束

---

## 8. Locality ≠ Table Boundary Analysis

这是本审查最重要的一项。

### 必须区分的层次

```
Local geometric concentration   ← P2 可观测
        ≠
Table existence                 ← 需语义判定
        ≠
Table boundary                  ← 需结构判定
        ≠
Table cell structure            ← 需 TLD 检测
        ≠
Table semantics                 ← 需内容理解
```

### M-B 是否隐含 local cluster → table 逻辑?

**YES — DCE-07 PROVEN [OBSERVED]**:

DCE-07 §13 "Locality Safety Analysis" 明确证明:

> Prose with citations has the same geometric properties as table data:
> - same_y_band (multiple fragments on same y)
> - x-gaps ≥ 12pt (citation formatting)
> - stable column alignment (prose has regular x-positions)
> - sufficient text ratio (prose contains text words)
> - y-spacing regularity (some prose regions have regular spacing)
>
> Without semantic content understanding, there is NO geometric signal
> that safely distinguishes "prose with citations" from "table data".

DCE-07 §15 "Success vs Failure Comparison" 量化:

| Metric | Failure (135/262/313) | Success (032/074/346) | Negative (008/042) | 区分? |
|--------|----------------------|----------------------|-------------------|-------|
| MC count | 31/37/31 | 38/41/24 | 29/22 | NO (overlap) |
| Wide text | 1/2/1 | 0/0/1 | 0/0 | NO |
| Band size | 81/79/61 | 86/63/66 | 82/85 | NO (all page-global) |
| Local align | 0.99/1.0/0.96 | N/A (= global) | **0.81/1.0** | **NO (negative also high)** |
| Y-spacing CV | 0.42/0.16/0.39 | N/A | N/A/**0.01** | NO (negative lower CV) |

**负控 AMB-008 (prose) local align=0.805, AMB-042 (prose) local align=1.000**
— 与失败案例的 local align (0.96-1.00) 完全重叠。

```
SEMANTIC_LEAP = TRUE
```

M-B 隐含 "local geometric concentration → table" 逻辑。
DCE-07 已证明此跳跃 **不安全**: prose-with-citations 的局部几何浓度与 table 完全相同。
负控 AMB-008/042 在 local isolation 下 align 高达 0.805-1.000，会被误判为 table。

### 如何在实验中避免?

**无法用纯几何避免 [PROVEN, DCE-07]**:
- y-spacing regularity: AMB-042 (prose) CV=0.01 < AMB-262 (table) CV=0.16 → 反向区分
- column-pattern consistency: prose 与 table 共享 x 位置 (left margin ~55pt, citation ~127pt)
- fragment count consistency: 无清晰区分
- text ratio: 已在 TLD (不能改 threshold)

M-B 只能证明: "局部 Evidence Query 比 page-global query 更能隔离**相关结构区域**"。
但不能证明: "该区域就是 table" — 因为 prose 区域在局部查询下表现完全相同。

---

## 9. Minimal Experiment Object

### 不能定义成 "Page → Table detected" (进入 detector semantics)

M-B 的最小实验对象应为:

```
Page → Existing P2/P5 evidence → Local spatial window → Evidence composition
     → Structural purity / contamination measurement
```

### 具体:

- **不测**: "table 是否被检测到" (这是 TLD detector semantics)
- **只测**: "局部窗口内的 column alignment / contamination ratio 是否优于 page-global"

### 但关键问题:

DCE-07 已执行了这个实验 (L1/L2 counterfactual)。结果:

- L1-correct: 局部窗口 = page-global (band 不变) → 无改善
- L1-modified: 局部窗口改善 align，但负控也改善 → unsafe
- L2: 局部窗口不形成 (prose 与 table 共享 x) → 无改善

**实验已运行，假设已证伪。** 重新运行相同实验不会产生新结论。

---

## 10. Input / Transformation / Output

### Input
- 冻结 P2 geometry: same_y_band, h_gap, fragment x0/y0/x1/y1, center_x
- 冻结 P5: column groups
- 冻结 TLD: VLine list, band formation, column stability, text ratio (只读)
- IS-11 GT: 45 case labels (只读，用于评估)

### Transformation (允许的 read-only)
- 计算 candidate-centered y-window (L1)
- 计算 column-pattern alignment ratio (L2)
- 计算 local vs global column stability 差值
- 计算 contamination ratio (table MC rows / total MC rows in window)

### Observable Output
- local alignment score (per case)
- global alignment score (per case)
- contamination ratio (per case)
- recovery count (failure cases where local align > 0.75)
- regression count (negative controls where local align > 0.75)
- TP preservation count (success cases unchanged)

### 禁止的 Output
- "table detected" (detector semantics)
- "table boundary" (结构判定)
- 任何修改 TLD 输出的结果

---

## 11. Ground Truth

使用已有 IS-11 GT (45 cases, frozen, sha 7349963d):
- 43 KEEP_SEPARATE, 2 MERGE
- 4 adjudicated (AMB-005/375/418/519)
- Machine eval: TN=26, ABSTAIN=18, FP=1, FN=0

DCE-07 额外使用:
- 3 negative controls (AMB-008/042/397 — prose pages, 0 wide_text breakers)
- 2 partial (AMB-519/414)

GT 不修改，只读使用。

---

## 12. Direct Cases

6 DIRECT failure cases (DCE-06/07):

| Case | Doc | Page | Mechanism | Actual TLD | Local Isolation (DCE-06) |
|------|-----|------|-----------|-----------|--------------------------|
| AMB-135 | efficientnet | 5 | M1+M2 | 0 tables | align 0.991 (PASS), text_ratio 0.195 (FAIL) |
| AMB-262 | efficientnet | 7 | M1 | 0 tables | align 1.000 (PASS), text_ratio 0.822 (PASS) |
| AMB-313 | efficientnet | 8 | M1 | 0 tables | align 0.958 (PASS), text_ratio 0.516 (PASS) |
| AMB-462 | cs_001 | 3 | M2 | 1 (wrong) | text_ratio 0.163 (FAIL, inherent) |
| eff p5-p8 | efficientnet | 5-8 | M1 | 0 tables | (subset of above) |

**注意**: DCE-06 local isolation 是**合成测试** (手动划定 y-range)。
DCE-07 L1-correct (自动 candidate-centered): 0/3 恢复 (AMB-135/262/313 全部仍 fail)。

---

## 13. Control Cases

8 CONTROL cases (DCE-06/07):

| Case | Role | Actual TLD | L1-correct | L1-modified | L2 |
|------|------|-----------|-----------|-------------|-----|
| AMB-032 | SUCCESS | 1 table ✓ | 1 ✓ | 1 ✓ | **3 (split)** ✗ |
| AMB-074 | SUCCESS | 1 table ✓ | 1 ✓ | 1 ✓ | 1 ✓ |
| AMB-346 | SUCCESS | 1 table ✓ | 1 ✓ | 1 ✓ | **2 (split)** ✗ |
| AMB-008 | NEGATIVE (prose) | 0 ✓ | 0 ✓ | **1 FP** ✗ | **2 FP** ✗ |
| AMB-042 | NEGATIVE (prose) | 0 ✓ | 0 ✓ | **1 FP** ✗ | **1 FP** ✗ |
| AMB-397 | NEGATIVE (formula) | 0 ✓ | 0 ✓ | 0 ✓ | 0 ✓ |
| AMB-519 | PARTIAL | 1 (FP on prose) | 1 | 1 | 1 |
| AMB-414 | PARTIAL (figure) | 0 | 0 | 0 | 0 |

### Controls 是否足够区分 "locality genuinely useful" vs "locality simply works on these pages"?

**足够 [OBSERVED, DCE-07]**:

负控 AMB-008/042 是**最难的测试** — 它们有 0 wide_text breakers (与失败案例相同条件)，
高 multicol count (29/22)，page-global band。如果 locality 在这些页上也提高 align，
则 locality **不能区分 table 与 prose**。

DCE-07 结果: L1-modified 在 AMB-008 (align 0.805) 和 AMB-042 (align 1.000) 上
**创造了 false positive** — 证明 locality 无法区分。

```
CONTROLS_SUFFICIENT = TRUE (DCE-07 已用 3 negative + 3 success + 2 partial)
```

但注意: 实验已运行。controls 已证明 locality unsafe。不需要补造数据。

---

## 14. Falsifiability

### 什么结果会导致 M-B 假设不成立?

M-B 假设: "局部 Evidence Query 能稳定定位表格区域，减少 contamination"

**已被 DCE-07 证伪 [OBSERVED]**:

1. **L1-correct (纯证据查询，不改 TLD)**: local isolation 不形成 — band 仍 page-global
   → "局部查询比全局查询更好" **不成立** (局部查询 = 全局查询，因为 band scope 不变)

2. **L1-modified (改 anchor)**: local isolation 改善 align，但负控也改善
   → "局部查询能定位表格" **不成立** (prose 也被定位为 table)

3. **L2 (column-pattern break)**: 不形成局部 band (prose 与 table 共享 x)
   → "column-pattern 能隔离表格" **不成立**

4. **Success only on known 6 DIRECT**: DCE-07 在 3 negative controls 上创造 FP
   → locality 不是 "只在这些页上有效"，而是 "无法区分有效与无效"

```
FALSIFIABILITY = SUFFICIENT (DCE-07 已证伪)
HYPOTHESIS_STATUS = FALSIFIED
```

假设已被反事实审查证伪。重新运行相同实验不会改变结论。

---

## 15. Success Criteria

假设 M-B 能成功的结果 (理论):

- local-isolation align > 0.75 on ≥4/6 DIRECT cases
- 0 false region on 8 controls
- AMB-135 FP → KEEP_SEPARATE
- 不触碰 TLD/IS-11/GT

**实际结果 (DCE-07)**:

| Criterion | L1-correct | L1-modified | L2 |
|-----------|-----------|-------------|-----|
| local align > 0.75 on DIRECT | 0/3 (band 不变) | 1/3 (AMB-262) | 0/3 |
| 0 false region on controls | ✓ (0 FP) | **✗ (2 FP)** | **✗ (2 FP + 2 split)** |
| AMB-135 FP → KEEP | NO (still fail) | NO (still fail) | NO |

**无任何方法同时满足全部 success criteria。**

---

## 16. Failure Criteria

什么结果否定或削弱 M-B:

1. ✅ **Local isolation improvement disappears** (L1-correct): band 不变，0% 恢复 — **已发生**
2. ✅ **Local isolation improves geometry purity but not TLD-required Evidence** (L1-modified):
   align 改善但负控也改善 → 不能安全用于 TLD — **已发生**
3. ✅ **Local isolation introduces comparable contamination** (AMB-008/042 FP):
   prose 在 local isolation 下 align 0.805-1.000 — **已发生**
4. ✅ **Success only on already-known 6 DIRECT** (L1-modified):
   仅 AMB-262 恢复 (1/3)，且伴随 2 FP — **已发生**

**全部 failure criteria 已被 DCE-07 触发。M-B 假设已被证伪。**

---

## 17. Frozen Baseline Safety

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
TLD_MODIFICATION                    = NO (审查未修改; 但 recovery 需要 = TRUE)
GT_MODIFICATION                     = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_ARTIFACT_MODIFICATION        = FALSE
```

本审查为 READ-ONLY，未修改任何冻结文件。
但: 如果 M-B 要进入实验并产生恢复效果，TLD_MODIFICATION_REQUIRED = TRUE (§7)。
这与 "不改 TLD" 约束冲突 → 阻塞。

---

## 18. VGA Downstream Impact

```
DOWNSTREAM_IMPACT = UNVERIFIED
```

DICE 无真实 VGA evaluation。M-B 即使成功 (假设) 也只能建立:

```
M-B → structural evidence isolation → possible improvement of downstream table evidence
    → VGA impact = UNVERIFIED
```

禁止写成 "M-B → VGA improvement"。

当前 M-B = NOT_READY，因此 VGA 影响讨论为假设性，无实际意义。

---

## 19. Final Readiness Decision

```
M-B = NOT_READY
```

### 阻塞条件

| 条件 | 状态 | 证据 |
|------|------|------|
| DCE-07 已关闭 locality 路线 | **BLOCKING** | DCE-07: ROUTE_CLOSED, PLAUSIBLE_BUT_UNSAFE |
| DCE-06 local isolation 是合成测试 | **BLOCKING** | DCE-06 §20: "synthetic, manually identified y-ranges, proves mechanism not solution" |
| L1-correct (不改 TLD): 0% 恢复 | **BLOCKING** | DCE-07 §10: RECOVERY_COUNT = 0/3 |
| Recovery 需改 TLD anchor | **BLOCKING** | DCE-07 §7: L1-modified changes anchor definition → TLD_MODIFICATION_REQUIRED = TRUE |
| Locality ≠ Table (SEMANTIC_LEAP) | **BLOCKING** | DCE-07 §13: prose geometrically = table; no geometric signal distinguishes |
| 实验已运行并被证伪 | **BLOCKING** | DCE-07 = counterfactual audit = 已执行的实验 |

### Readiness 证明 (NOT_READY 不需要全部 FALSE，但列出当前状态)

```
NEW_OBSERVATION_REQUIRED     = FALSE
NEW_DETECTOR_REQUIRED        = FALSE
TLD_MODIFICATION_REQUIRED    = TRUE   ← 阻塞 (recovery 需要)
FROZEN_ARTIFACT_MODIFICATION = FALSE
SEMANTIC_LEAP                = TRUE   ← 阻塞 (local cluster ≠ table)
AUTHORITY_LEAKAGE            = FALSE
EXPERIMENT_SCOPE             = READ_ONLY (但实验已在 DCE-07 执行)
```

---

## 20. Recommended Next Action

### 最小补充工作 (不授权执行，仅指出方向)

M-B locality 路线已被 DCE-07 关闭。要重新打开需要以下**之一**:

1. **找到一个非几何的 table/prose 区分信号** (不依赖 local alignment / y-spacing / column-pattern)
   - 当前状态: DCE-07 测试了全部已知几何信号，均不安全
   - 阻塞: 非几何信号 = 新 observation 或语义理解 = 均禁止
   - → **当前不可行**

2. **接受 M-B 的 Mechanism 2 子分支 (AMB-462 text_ratio) 作为独立研究**
   - AMB-462: band 已正确隔离，失败在 text_ratio=0.163 (inherent numeric)
   - 但: text_ratio threshold tuning = FORBIDDEN
   - → **当前不可行**

3. **重新定义 M-B 为 "contamination measurement only" (不追求 recovery)**
   - 只测量 local vs global contamination ratio，不尝试恢复
   - 价值: 量化 contamination 严重程度 (学术/论文价值)
   - 但: 不产生 slicing 改善 → 低优先级
   - → **可行但低价值**

4. **转向 M-A (caption association) 作为替代 PRIMARY route**
   - M-A: EXPRESSIBLE=YES, 2 MERGE cases, cross-framework 6.08%
   - 未被反事实关闭 (无 DCE-07 等效审查)
   - 但: 需预注册负例集
   - → **值得下一步审查 (非本文件范围)**

### 不应做

- 重新运行 DCE-07 已执行的 locality counterfactual (不会产生新结论)
- 修改 TLD anchor / band formation / threshold (FORBIDDEN)
- 引入 LLM / 语义理解区分 prose 与 table (FORBIDDEN)
- 把合成 local isolation (DCE-06) 包装为 "已验证的自动方法"

### 对上轮 summary 的纠正

`system_reframing_summary.md` 将 M-B 列为 PRIMARY_NEXT_RESEARCH_ROUTE，引用
"PROVEN local isolation (align 0.23→0.96-1.00)"。该引用来自 DCE-06 合成测试，
未充分纳入 DCE-07 反事实关闭结论。建议在下一轮授权时:
- 将 M-B 从 PRIMARY 降级
- 将 M-A (caption) 列为待审查的替代 PRIMARY 候选
- 或接受 "当前无 safe algorithm route" 的结论

---

## 最终状态

```text
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED      = FALSE
FROZEN_BASELINE            = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
DICE_CORE_DRIFT            = 0
PRODUCTION                 = FALSE
RUNTIME_AUTHORITY          = ZERO
STOP                       = TRUE
```

M-B = NOT_READY。等待下一条明确授权。

`STOP = TRUE`。
