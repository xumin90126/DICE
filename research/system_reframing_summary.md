# DICE System Reframing Summary

> **模式: READ-ONLY / AUDIT / RESEARCH ONLY。零代码修改、零冻结接触、零 GT 修改、零实验。**
> 日期: 2026-09-14（系统级重审阶段）
> 前置: HVA-09/10/11 暂停; L3→L5 Learning Engine 设计暂停。
> 本文件是 `tmp/dice_system_reframing/` 四份审计文件的最终综合判断。

---

## 一、审计结论速览

| 维度 | 判定 | 一句话依据 |
|------|------|-----------|
| Document Perception 现状 | **PARTIAL** | Text/Geometry/Style 强；Table 71% miss；Figure/Caption/Flowchart/Equation 完全缺失 |
| 失败根因分布 | **D (证据组织) 为主** | 不是 observation 缺失，是"证据查询缺口"；4 份审计一致 |
| Human Case 价值 | **87% 低价值** | 53% Type A 浪费 + 33% Type D_LOW 临时；仅 11% 真边界 |
| L3→L5 链条 | **NOT_DEMONSTRATED** | L3 停滞；L4/L5/L6 全 NOT_ACHIEVED；91% feedback 无新信息 |
| TLD 定位 | **局部节点** | TLD 是 Layout 分支下表格检测一个节点，非 DICE 全部问题 |
| VGA 下游影响 | **DOWNSTREAM_IMPACT_UNVERIFIED** | 无真实 VGA evaluation；推理链合理但未观测 |

---

## 二、Q14.1 — 如果只允许做 ONE Document Perception Algorithm Experiment

### Research Question
> 在 TLD 检测失败的页面（小表格 + 混合内容页）上，冻结 P2/P5 几何（same_y_band、
> h_gap、fragment 位置、column groups）能否可靠地**局部定位**表格区域，
> 使被 page-global contamination 污染的 column stability 恢复到 ≥0.75？

### Failure Mechanism
**M-B — 表格区域证据不可用 / page-global contamination**（mechanism B_perception_incorrect
+ D_evidence_organization_failure）。这是当前唯一同时满足"消除真实 FP + 扩展已证明 8/8 正确
通道 + DIRECT 影响最大 + 跨文档重复"的机制。

### Hypothesis
> 一个 locality-constrained multicol cluster（same_y_band + ≥3 fragments + gaps +
> x-cluster stability within a y-window）能隔离 TLD page-global band 所污染的表格区域，
> 使 local-isolation column stability > 0.75 且不引入伪区域。

### Existing Evidence
- DCE-06 local isolation test: align 0.23–0.27 (global) → 0.96–1.00 (local) — **PROVEN**
- P2 geometry 45/45 = 100% sufficient
- IS-11 channel 8/8 correctness when table detected
- 6 DIRECT cases (AMB-135/262/313/462 + eff p5-p8)
- 8 success controls (table dominates page, 0 contamination → local=global)

### Minimal Experiment (READ-ONLY, no code mod)
在 6 个 DIRECT 失败案例 + 8 个 success control 上**只读重放**:
1. 读取冻结 P2 几何（same_y_band, h_gap, fragment x/y, center_x）
2. 计算 locality-constrained column stability（在 target table 的 y-window 内）
3. 比较 local align vs TLD global align
4. 检查 local align > 0.75 AND text_ratio 通过（AMB-262/313 预期 PASS；AMB-135 预期 Stage F 仍 fail 但 Stage E 修复）
5. 在 8 个 control 上验证不引入伪区域（local=global，0 contamination）

### Success Criteria
- local-isolation align > 0.75 on ≥4/6 DIRECT cases
- 0 false region on 8 success controls
- AMB-135 FP → KEEP_SEPARATE (via different_cell, not via predicate)
- 不触碰 TLD/IS-11/GT/P1-P7 任何冻结文件

### Regression Risk
- **LOW**: success cases table dominates page → local=global → 0 contamination → locality constraint 无害
- 风险: locality window 划定若依赖启发式 → 可能引入伪区域（需预注册 y-window 规则）
- KEEP 单向抑制（different_cell→KEEP）→ regression 面小

### Regression Risk Mitigation
预注册 locality window 规则（基于 P2 fragment 密度 + gap pattern，非任意阈值）；
8 control 必须全部 PASS；AMB-414/422 figure canary 必须保持 ABSTAIN。

### Frozen Impact
**NONE** — 只读冻结 P2；不改 TLD；不触 IS-11/GT/P1-P7。

---

## 三、Q14.2 — 如果允许做 TWO，第二个是什么

### Research Question
> 冻结 pairwise（same_y_band, h_gap ∈ (8,50]）+ left_alignment（列首对齐 x≈85.04）
> + FIG-prefix 词法（hypothesis 侧）能否隔离 caption label↔continuation 关联对，
> 修复当前唯一 MERGE 类缺口（图注过切）？

### Failure Mechanism
**M-A — Caption 空间关联断裂**（mechanism A_perception_missing +
E_interpretation）。这是唯一 MERGE-class GT 缺口；图注语境整体丢失。

### Hypothesis
> 同 y-band 内、h_gap ∈ (8,50]、列首对齐、且 text_a 匹配 "FIG N:" 词法的对，
> 可关联为同一图注单元——无需新 observation，仅查询已有 P1/P2。

### Existing Evidence
- CC-01 microscope: gap 10.5–18.1pt > P4 frozen 8pt → AMBIGUOUS；EXPRESSIBLE=YES
- Phase3 prevalence 6.08% (79/1299) cross-framework
- 2 DIRECT MERGE cases (AMB-414/422)

### Minimal Experiment
1. 预注册负例集（Table label "Table 3" + 表格首行；figure axis label）
2. 在 2 MERGE case + 负例上只读查询 pairwise + left_alignment + FIG-prefix
3. 检查关联召回提升且负例不误关联

### Success Criteria
- 2/2 MERGE case 正确关联
- 负例集 0 false-associate
- 词法 "FIG N:" 必须留 hypothesis 侧（不得词法化进层）

### Why Second (not First)
- DIRECT impact = 2（vs M-B 的 6）；single-doc concentrated in IS-11
- 但 cross-framework 6.08% prevalence 给了可重复性背书
- 是 MERGE 类唯一缺口，结构性价值高

---

## 四、Q14.3 — 哪些事情现在明确不应该做

| 不应做 | 理由（证据） |
|--------|-------------|
| **全面重写 Parser** | block 层腐败已知但 word/span 层已充分（P1/P2）；重写破坏冻结 730 pool + annotation binding；不可复现（185≠201） |
| **继续无限优化 TLD** | TLD frozen；DCE-07 已在 TLD 内部关闭 locality route；M-C 判据路线 15/15 REJECTED；patch accumulation HIGH |
| **新建 Learning Engine** | L3→L5 链 NOT_DEMONSTRATED；L4/L5/L6 全 NOT_ACHIEVED；91% feedback 无新信息；stability-novelty paradox 结构性障碍 |
| **新建 Pattern Engine** | 同上；3 signal candidates 全 TEMPORARY_MACHINE_GAP；features 已在 P1/P2 |
| **新建 Case Selector** | 未授权；但当前 selection 优化 geometric ambiguity 非 learning value——需重设计而非新建 engine |
| **L3→L5 Runtime** | 链条在 L3 停滞；无 L4 validated signal 可 runtime 化 |
| **LLM semantic classifier** | DCE-06: LLM_NEEDED=NO（all failures deterministic/structural）；4 份审计一致禁止 |
| **直接调 threshold** | 禁止；P4 8pt / TLD 0.75 / 0.45 均冻结；threshold tuning = FORBIDDEN |
| **直接修 bug / 写补丁** | 禁止；先 Failure→Mechanism→Capability Gap→Algorithm Hypothesis |
| **把 HVA-09 非真人测试当 Human Evidence** | 已纠正；fabricated data 已删除；HVA-09 = INSUFFICIENT_EVIDENCE |

---

## 五、TLD 在能力图中的位置（重审）

```
                 Document Perception
                        │
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
     Text            Layout          Visual  ← 完全缺失
    (P1 强)         (P2/P5/P6)      (Figure/Caption/
       │                │            Flowchart/Equation)
       ↓                ↓
 Reading Order      Table/List       ← TLD 在这里（局部节点）
 Numbering(部分)    Columns(P5)        TLD 71% miss = 这个节点坏了
 Cross-page(空白)   Region(P6)         但 Visual 分支整个不存在
                    TLD(表格)
```

**判断**: TLD 失败是 Document Perception 能力图中**一个局部节点的局部失败**。
DICE 下一阶段**不应定义成"继续优化 TLD"**。
更根本的缺口是 Visual 分支（Figure/Caption/Flowchart/Equation）完全缺失——
只是因为没有真实案例暴露而被低估。

但按"先发现 Failure Mechanism 再决定 Algorithm"原则：
- M-B（TLD 失败）是当前**唯一被真实数据量化**且**已 PROVEN local isolation** 的机制 → 第一个实验
- M-A（caption）是唯一 MERGE 缺口 → 第二个实验
- Visual 分支其余项（flowchart/equation）= INSUFFICIENT_EVIDENCE，先补案例

---

## 六、VGA Evidence Dependency 视角

DICE 最终存在的原因是为 VGA 提供更可靠的 Evidence。本审计增加这一层:

```
Document Structure → Evidence Failure → Knowledge Retrieval/Chunking 影响 → VGA Answer 影响
```

**状态: DOWNSTREAM_IMPACT_UNVERIFIED** — DICE 无真实 VGA evaluation。
以下为 INFERRED 推理链，非观测:

| Document Structure | Evidence Failure | Retrieval 影响 | VGA 影响（INFERRED） |
|---|---|---|---|
| Table lost (M-B) | row/column关系丢失 | cell级事实关联断裂 | 可能检索到错误事实关联（'4'关联'MBConv6'） |
| Reading order broken (M-E) | 句/段含义扭曲 | retrieved evidence 扭曲 | 答案可靠性受影响 |
| Caption over-split (M-A) | 图注主体与label断开 | figure context 丢失 | 无法关联图与说明 |
| Header contamination (M-D) | header 进入 body | chunk 噪声 | 可能引用 header 为内容 |

**不得声称 VGA 已受影响** — 推理合理但 UNVERIFIED。需真实 VGA evaluation 才能确认。

---

## 七、Human 介入位置重定义

### 当前问题
Human 做了大量普通判断（87% 低价值）。69% decisions <3s，96% no expansion。
Human 用 page visual 而非 machine evidence（image confound）→ feedback 不 evidence-grounded
→ 无法改进 machine evidence path。

### Human 真正应该介入的位置
1. **Genuine Semantic Boundary (F)**: reference/citation continuation（IS-10 HUMAN_OWNED）；
   reviewer-disagreement adjudicated cases（AMB-375 类）
2. **"When should system abstain" boundary (E)**: 机器不确定且 Human 也不确定 → UNKNOWN
   → 定义 abstain 边界
3. **高价值 Failure 确认**: M-B locality 修复后的 canary 验证（AMB-414/422 保持 ABSTAIN）

### Human 不应做的
- Type A（机器已正确）的批量确认（53% 浪费）
- 用 page visual 替代 machine evidence 做 snap judgment（83% TLD failure）
- 替机器做 case-specific correction 但无 reusable pattern（Case B）

### 前提条件
Human scaling 前必须先解决:
- L2 Case Selection（优化 learning value 非 geometric ambiguity）
- L3 Evidence Distillation（B2 比 A 更慢 → distillation 加认知负荷；AMB-032 B2 UNKNOWN 因未暴露 TLD cell info）

---

## 八、最终判断

```text
DOCUMENT_PERCEPTION_STATUS    = PARTIAL
  # Text/Geometry/Style 强; Table 71% miss; Figure/Caption/Flowchart/Equation 完全缺失;
  # Reading order 列级 partial; Cross-page 观察空白

ALGORITHM_INVESTMENT          = MEDIUM
  # ONE focused experiment (M-B locality) justified + PROVEN;
  # SECOND (M-A caption) conditional;
  # NOT broad parser rewrite / NOT infinite TLD optimization

HUMAN_VALIDATION_PRIORITY     = LOW (current) / MEDIUM (after redesign)
  # 87% low-value currently; needs L2+L3 redesign before scaling;
  # genuine boundary types (F/E) underrepresented

L3_TO_L5_PRIORITY             = NOT_YET
  # chain NOT_DEMONSTRATED; L3 stalled; L4/L5/L6 NOT_ACHIEVED;
  # stability-novelty paradox = structural barrier;
  # do NOT build Learning/Pattern Engine now

PRIMARY_NEXT_RESEARCH_ROUTE   = M-B locality-constrained table region isolation
  # READ-ONLY replay on 6 DIRECT + 8 control;
  # frozen P2 only; no TLD/IS-11/GT modification;
  # PROVEN local isolation (align 0.23→0.96-1.00)

SECONDARY_ROUTE               = M-A caption association evidence query
  # needs pre-registered negative set; FIG-prefix stays hypothesis-side;
  # 2 MERGE cases + Phase3 6.08% prevalence

DO_NOT_DO                     =
  - 全面重写 Parser (breaks frozen pool; word/span层已充分)
  - 继续无限优化 TLD (frozen; DCE-07 closed; PH-02 REJECTED)
  - 新建 Learning Engine / Pattern Engine (L3→L5 NOT_DEMONSTRATED)
  - 新建 Case Selector / L3→L5 Runtime (not authorized; no L4 signal)
  - LLM semantic classifier (all failures deterministic/structural)
  - 直接调 threshold / 修 bug / 写补丁 (FORBIDDEN)
  - 把 HVA-09 非真人测试当 Human Evidence (fabricated; deleted)

IMPLEMENTATION_AUTHORIZED     = FALSE
EXPERIMENT_AUTHORIZED         = FALSE
FROZEN_BASELINE               = INTACT
DICE_CORE_DRIFT               = 0
  # TLD=022f5c21e872ad9e, GT=7349963d0d23b5ef, drift=0/7 (verified this round)
STOP                          = TRUE
```

---

## 九、研究原则遵守确认

- ✅ 先发现 Failure Mechanism，再决定 Algorithm（M-B 先于"优化 TLD"）
- ✅ 不先决定优化 Table/TLD/Reading Order 再找证据
- ✅ Human 不应替机器做大量普通判断（87% 低价值已量化）
- ✅ Human 价值 = 确认高价值 Failure/Boundary（genuine F/E boundary）
- ✅ 目标 = Human Review Cost ↓ + Evidence Quality ↑ + Reusable Improvement ↑ + Future Failure ↓ + VGA Evidence Reliability ↑
- ✅ 不虚构能力（Figure/Caption/Flowchart/Equation 标 MISSING/INSUFFICIENT）
- ✅ 不补数据（CROSS_PAGE/LIST/EQUATION 标 INSUFFICIENT_EVIDENCE）
- ✅ 不综合打分（matrix 只用 LOW/MEDIUM/HIGH/UNKNOWN）
- ✅ 不把 SignalCandidate 文件当作 Learning 已发生（L3→L5 chain NOT_DEMONSTRATED）

---

## 十、输出文件清单

```
tmp/dice_system_reframing/
    document_perception_capability_audit.md      ← Q1 能力边界表 (14类结构)
    document_perception_failure_taxonomy.json    ← 13类结构 × 机制A-G 分类
    algorithm_improvement_candidate_matrix.json  ← M-A..M-I 候选矩阵 (无综合分)
    human_case_value_reassessment.json           ← Case A-E 重估 + Q11/Q12
    system_reframing_summary.md                  ← 本文件 (Q14.1/Q14.2/Q14.3 + 终判)
```

未修改任何生产代码、frozen artifacts、GT、实验结果、旧报告。

`STOP = TRUE`。等待下一条明确授权。
