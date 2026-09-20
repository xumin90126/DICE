# DICE Future Paper Materials Library

> 层 2: 未来论文素材库。与工程验收报告严格分离。保留**过程**, 不仅保留结果。
> 失败假设、研究对象修正、负例、安全机制 = 论文最有价值的研究证据。
>
> 标注: PAPER_VALUE = HIGH/MEDIUM/LOW; EVIDENCE_LEVEL = Observed / Mechanism-supported /
> Experimentally-supported / Hypothesis。区分 Engineering Fact / Research Interpretation /
> Potential Paper Claim。

---

## TYPE A — Research Question

| # | 研究问题 | STATUS |
|---|---------|--------|
| A1 | Evidence Quality 是否比 raw accuracy 更适合作为优化目标? | partially answered (机制验证, 非 generalization) |
| A2 | Geometry Evidence 能否支持 slicing failure diagnosis? | answered (EXPRESSIBLE + replay PASS) |
| A3 | Structural Object 应该如何定义? | answered (LSP = membership/scope/relation/continuity/provenance; 零语义) |
| A4 | Evidence 与 Interpretation 的边界在哪里? | answered (EIC-1 = 唯一闸门; No Semantic Closure) |
| A5 | Human Validation 应验证 instance 还是 reusable pattern? | answered (reusable pattern 级 + 边界/负例) |
| A6 | Consumer Integration 能否解决已有 evidence 无法进入下游? | answered (REPLAY_PASS, 决策函数不变) |
| A7 | 如何避免 if/else patch accumulation? | answered (precommitment 禁 M6/M7/M8; 失败归因不堆规则) |
| A8 | 如何通过 safety canary 控制错误传播? | answered (caption canary = HARD GATE, flip=SAFETY FAILURE) |

PAPER_VALUE: A3/A4/A5/A6/A8 = HIGH; A1/A7 = MEDIUM; A2 = HIGH。

## TYPE B — Failed Hypothesis

### PH-02 (HIGH)
- **Hypothesis**: frozen left_alignment_group geometry 可直接作 column-membership signal,
  通过 whole-group equidistance predicate 修复 AMB-135 FP。
- **Motivation**: FP 的 '4' 有 lag=10 对齐组, 似可用等距谓词识别 in-column。
- **Preregistration**: 15 参数组合 × 45 案例; A=1∧B=0∧C=0 = PASS; 否则 REJECTED 无补救。
- **Experiment**: 15/15 全矩阵; A=0/1 (FP 未移除任一组合); 7/13 anchors firing (specificity)。
- **Observed result**: whole-group 谓词无法区分目标列与正文 margin 组 (共享对齐关系)。
- **Falsification**: A=0 触发预注册 REJECTED 规则。
- **Rejection reason**: research object (whole group) 结构上无法承担 column-membership 语义;
  page-wide 几何对象 ≠ 局部结构列。
- **What changed afterward**: research object revision (whole group → candidate segment →
  LSP); 不堆 M6/M7/M8; 转 mechanism redesign。
- EVIDENCE_LEVEL: Experimentally-supported (rejected)。PAPER_VALUE: **HIGH** (失败假设本身是研究证据)。

### C2 coverage insufficiency (MEDIUM-HIGH)
- **Hypothesis**: candidate-column-segment (成员级) 可提高正例覆盖。
- **Result**: positive GT-confirmed 维持=1, 新增=0; POSITIVE_COVERAGE=INSUFFICIENT。
- **Falsification**: coverage 不足独立阻塞; M5 簇级自斥。
- **What changed**: 不调 predicate; corpus expansion + mechanism redesign (M-B)。
- EVIDENCE_LEVEL: Experimentally-supported。PAPER_VALUE: HIGH。

## TYPE C — Research Object Revision (HIGH — "研究对象逐步收敛")

| 阶段 | 对象 | 为何不成立 | 新对象 | 解决了什么 | 未验证部分 |
|---|---|---|---|---|---|
| PH-02 | whole left_alignment_group | page-wide margin 污染; 整组 ≠ 局部列 | candidate-column-segment | 局部化 | coverage 不足 |
| C2 | candidate-column-segment | positive diversity=1; M5 自斥 | (转向 M-B, 非列段对象) | — | — |
| M-B | Local Structural Partition (LSP) | (成立) | LSP + RSC + EIC-1 | 局部分区 + 语义闸门 + 复用既有契约 | L5 人审未发生; conflict 自然案例=0 |

收敛轨迹: **whole group (page-wide) → column segment (局部但 coverage 不足) → LSP (局部 + 结构 + 非语义, 经 EIC 解释)**。
关键洞察: 每次 revision 不是加谓词, 而是改变**对象的层与语义边界**。

## TYPE D — Negative Evidence Catalog (HIGH — 不只存正例)

| CASE / 结构 | STRUCTURAL OBSERVATION | HYPOTHESIS IT CHALLENGED | RESULT | RULES OUT | DOES NOT RULE OUT |
|---|---|---|---|---|---|
| VALUE_COLUMN (resnet p6 '21.59') | 对齐数值列, lag6 band2 | "对齐数值列 = row-index" | Level-2 同构不区分 | L2 角色区分 | 角色需 L5 |
| AXIS_TICK | 单列重复数字堆 | "重复数字 = 表格列" | sib=0, 无第二分区 | 单列=表列 | — |
| DIGIT_GRID | 网格数字 | "网格结构 = table" | (corpus discovery 边界) | — | — |
| MIXED_ARTIFACT (AMB-005 跨栏正文) | margin lag30 × 右列 | "同带异 x = 不同 cell" | 双栏正文同构 | L2 区分正文/表 | — |
| CODE_LINE_NUMBER (LLaMA p19) | 连续整数列 | "整数序列 = row-index" | 单列 sib=0 | — | L5 角色区分 |
| TOC (2212 p15) | 3 x-zone 共结构 | "3-zone 共结构 = table" | 点列 x-center 不稳 | (最难混淆) | 需 L5 负例 |
| page-wide body margin | n=15-24, y_ext 293-393pt | "alignment group = 列" | 污染每一页 | 整组=列 | localization 修正 |
| caption pseudo-cell (med p20) | band 含 4 伪 cell 片段 | "同带多分区 = table row" | caption 不可区分 | L2 区分 caption/表 | localization + canary |
| prose contamination (AMB-519) | band=1 margin lag24 | "同带 = 表行" | 正文双栏 | — | — |
| lag=0 (AMB-313 'Test Size') | 无对齐组成员 | "所有 atom 可分区" | 分区不可解 | 全 atom 可分区 | honest ABSTAIN |
| lag=1 (AMB-462 'WGe') | 单成员 | "弱成员可分区" | 弱 | — | honest ABSTAIN |

PAPER_VALUE: 全部 HIGH (负例是边界发现的核心)。

## TYPE E — Safety / Error Containment (HIGH)

| 机制 | 案例 | 为什么"拒答/ABSTAIN"是正确结果 |
|---|---|---|
| AMB-135 FP 修复 | MERGE→KEEP | 经契约链, 非新规则; 证据已存在 |
| AMB-414/422 caption canary | ABSTAIN 保留 | geometry ≠ table semantics; localization 保护; flip=SAFETY FAILURE |
| honest ABSTAIN (313/462) | 分区不可解 | coverage ≠ forced decision; 拒答优于猜 |
| conflict contract | EVIDENCE_CONFLICT | 不做 winner; 冲突 observable + provenance |
| frozen decision function | hash 不变 | 架构变更 ≠ 决策政策变更 |
| OFF isolation | byte-identical | 关闭即回退 baseline |
| provenance 1.0 | 11/11 四元组 | 可追溯 |
| deterministic replay | 21/21 双跑 | 可重复 |
| frozen baseline drift 0 | anchors/GT/TLD 不变 | 冻结纪律 |

核心思想: **错误不向下游传播**; ABSTAIN 是 Evidence Quality 的合法结果, 不是失败。

## TYPE F — Engineering Decision Records (HIGH)

| DECISION | ALTERNATIVES | WHY REJECTED | WHY SELECTED | EVIDENCE | RISK | STATUS |
|---|---|---|---|---|---|---|
| 不修改 frozen harness | 改 harness | 破坏冻结 | importlib 导入未改 | hash 验证 | 低 | 执行 |
| 不修改 decision function | 加 if/else | 决策政策变更 (F2) | EIC 复用既有契约 | 行为 10/10 | 低 | 执行 |
| 不修改 TLD | 改 TLD | 破坏既有 8/8 通道 | 第二生产者并存 | agree 3 例 | 低 | 执行 |
| 不修改 Atomic Observation | 加 drawings | NEW_OBSERVATION request | Type C 不需要 | EXPRESSIBLE | 低 | 执行 |
| 不直接 LSP→different_cell | 直连 | semantic leakage (F1) | 经 EIC-1 闸门 | 代码级证 | 低 | 执行 |
| 引入 EIC-1 | 无闸门 | 语义升级失控 | 唯一解释 authority | Phase 2.1 发现 | 中 | 执行 |
| conflict 不做 winner | trust TLD/Geometry | hidden arbitration | EVIDENCE_CONFLICT | — | 中 | 执行 |
| Human Validation 在 pattern 级 | instance 级 | annotation tool 退化 | reusable abstraction | Phase 2.2 | 中 | 设计 |
| localization 入 prerequisite | 无 | canary 必 FIRE | 排除 page-wide 组 | LOCALIZATION GAP | 低 | 执行 |
| 不继续 M6/M7/M8 | 堆谓词 | patch accumulation | 失败归因/契约修订 | PH-02 教训 | 低 | precommit |
| implementation isolated+flag-gated+non-production | 直接 production | 未授权/回归风险 | OFF 可回退 | S9 | 低 | 执行 |

## TYPE G — Quantitative Evidence (统一登记, 不补数字)

| 数量 | 值 | 出处 | EVIDENCE_LEVEL |
|---|---|---|---|
| adjudicated cases | 45 | machine eval | Observed |
| TCC cases | 26 (3 docs/10 页) | independence audit | Observed |
| 545-universe | 545 | C2 coverage audit | Observed |
| corpus discovery clusters | 709 / 10 docs | corpus_discovery | Observed |
| numeric x0-clusters | 138 | C2 | Observed |
| negative clusters | 137 | C2 | Observed |
| corpus acquisition | 4 docs / 80 pages / 131 clusters | corpus_acquisition | Observed |
| positive GT-confirmed | 1 (全程) | 各阶段 | Observed |
| PH-02 param combos | 15/15 (A=0/1) | ph02_results | Experimentally-supported |
| M-B replay matrix | 21 decision + 4 descriptive | phase3 design | Design |
| S1-S10 | ALL PASS | phase3.2 | Experimentally-supported |
| F1-F10 | 0 | phase3.2 | Experimentally-supported |
| DIRECT recovery | 6/8 | phase3.2 | Experimentally-supported |
| honest ABSTAIN | 2/8 (313/462) | phase3.2 | Experimentally-supported |
| collateral | 0 | phase3.2 | Experimentally-supported |
| unsafe flip | 0 | phase3.2 | Experimentally-supported |
| provenance completeness | 1.0 (11/11) | phase3.2 | Experimentally-supported |
| determinism | 21/21 | phase3.2 | Experimentally-supported |
| frozen drift | 0 | 全程复验 | Observed |
| AMB-135 pair-band density | 30 | phase3.1 | Experimentally-supported |
| canary pair-band density | 0 (100/150/200pt) | phase3.1 | Experimentally-supported |
| localization robustness | [100,200]pt | phase3.1 | Experimentally-supported |
| 7/13 anchors firing (PH-02) | 7/13 | ph02_report | Experimentally-supported |

discrepancy 见 `dice_evidence_discrepancy_log.md` (DIRECT 6→8→9; eff/cs 5+3→3+7; AMB-262 分类;
OFF 伪 mismatch; FP 3→1)。

## TYPE H — Case Studies (HIGH)

### H1. AMB-135 (FP → 修复)
- initial FP: IS-01∧IS-02 → MERGE (GT=KEEP_SEPARATE);
- PH-02 failure: whole-group 谓词 15/15 A=0;
- research-object diagnosis: whole group 误用 → LSP 局部分区;
- M-B recovery: Geometry→LSP→RSC→EIC-1→既有契约→KEEP (eic1_single_source, density=30);
- final: KEEP_SEPARATE (GT-consistent), 契约链完整, candidate 状态。

### H2. AMB-414 / AMB-422 (caption safety canary)
- caption band 含伪 cell 片段 (med p20: Left:/BIC values/Right:/Learning);
- geometry ≠ table semantics — 纯 Level-2 不可区分;
- localization 保护 (pair-band density=0);
- ABSTAIN 保留 (flip=SAFETY FAILURE)。

### H3. AMB-313 / AMB-462 (honest ABSTAIN)
- 313 'Test Size' lag=0 (无对齐组成员); 462 'WGe' lag=1 (弱);
- 分区不可解 → honest ABSTAIN;
- coverage ≠ forced decision — 拒答优于猜。

### H4. AMB-262 (分类修正)
- early: 标 "different_band" (早期 atom 测量 same_y_band=False);
- replay: 实际案例对同带+不同 x0 (co_density=41) → EIC-1 发射 → GT-consistent;
- discrepancy reconciliation (见 D3)。

### H5. VALUE_COLUMN / CODE_LINE / TOC (negative lookalikes)
- 几何相似不蕴含语义等价; Level-2 不区分角色; 角色语义留 L5 pattern 级 (含负例集)。

## TYPE I — Research Insights ("What We Learned")

| # | Insight | EVIDENCE_LEVEL |
|---|---------|----------------|
| I1 | Geometry Fact ≠ Structural Object | Experimentally-supported (PH-02) |
| I2 | Structural Evidence 不应自动获得 Semantic Authority | Mechanism-supported (Phase 2.1/2.2) |
| I3 | Evidence Integration Gap 与 Observation Gap 必须区分 | Experimentally-supported (M-B audit) |
| I4 | Human Validation 应作用于 reusable pattern, 非 instance annotation | Hypothesis (设计, L5 未发生) |
| I5 | Honest ABSTAIN 是 Evidence Quality / Error Containment 的合法结果 | Experimentally-supported (313/462) |
| I6 | Safety canary 可作 semantic-boundary regression gate | Experimentally-supported (414/422) |
| I7 | Frozen baseline + isolated replay 可分离 architecture change 与 decision-policy change | Experimentally-supported (S6/S9) |
| I8 | 失败假设本身是研究证据, 不应删除 | Observed (PH-02/C2 保留) |
| I9 | evidence 已存在时优先修复 consumer integration, 非扩张 observation | Experimentally-supported (NEW_OBSERVATION=NONE) |
| I10 | positive diversity 不足时应停调参 + 扩 corpus / revise object, 非堆 predicate | Experimentally-supported (C2) |
| I11 | L5 Human Validation 最小对象 = Interpretation Pattern (非 instance/非 capability); 当前架构无 pattern 抽象层 (grep 0), ValidationTask 结构性实例级; pattern 成分 5/10 已备, 5/10 需设计 | DESIGN REVIEW (L5 readiness) |
| I12 | pattern validation ≠ capability registration; FROZEN_CAPABILITY_TABLE 静态人控, 非自动派生; 新 capability 需 human registration decision | Observed (架构) |
| I13 | Naive Pattern Validation = burden transfer (非 reduction): evidence_exposure 30-60 > instance 21; Human 承担 8/10 abstraction 子任务; validation count↓ 但 per-validation load↑; 违反 "validate not reconstruct" | Inferred (L5.1 simulation) |
| I14 | Human Validation 最小单位 = Semantic Claim (非 Instance 非 Pattern); Pattern = evidence organization/reuse layer (Model 2, 透明于 Human); System 承担 aggregation/compression; Human 仅 semantic authorization | Design (L5.1) |
| I15 | Evidence visibility ≠ Evidence authority: 不默认展示 ≠ 不存在; Progressive Disclosure (Level 0 default→Level 4 on-demand) + 诚实 summary + auditable provenance = 降低默认 cognitive load 同时保留可审计性 | Design (L5.1) |
| I16 | Evidence Compression 当前 MISSING (8/15 allocation MISSING, 6/9 abstraction capability MISSING); Workflow C 设计上成立但**不可立即实现**; gap=Pattern abstraction layer (新抽象层), 非 observation gap 非 consumer gap | Observed (L5.2 code audit) |
| I17 | Structural Abstraction (System, authority=0) vs Semantic Abstraction (Human, sole authority): Compression Layer authority=0, 只改证据组织不改语义; System 产 Semantic Claim **Candidate** 非 Conclusion | Design (L5.2) |
| I18 | Compression Fidelity 硬约束: High Compression + High Fidelity (非 Maximum); 关键证据 positive/negative/boundary/UNKNOWN/conflict/provenance 压缩后可恢复/追溯/审查; System 提议 structural role, Human 确认, 不得单方删除 | Design (L5.2) |
| I19 | Minimum System Capability = 2 primitive (Aggregation + Evidence Compression); L5.2 的 7 项经 Deletion Test 压缩为 2 真正 primitive + 6 fidelity constraints; 5 项为派生/合并/复用 (commonality=grouping criterion / negative=其他 group 保留 / conflict+UNKNOWN+coverage=保真约束 / provenance+EIC-1+UNKNOWN=EXISTS 复用); 删任一 primitive → Workflow C 崩 (burden transfer) | Design (L5.3 minimality proof) |
| I20 | "Compress evidence, not meaning": compression 报告已有 EIC-1 candidate (status=candidate, governed), 不创建新语义; Semantic Claim Candidate = aggregated per-instance EIC-1 candidates (模板陈述), 非 new interpretation; compression authority=0 | Design (L5.3) |
| I21 | Primitive Contract 正式化: Aggregation MUST/MAY/MUST NOT (group by structural signature, no semantic label, no representative/ranking/decision) + Compression MUST/MAY/MUST NOT (count+aggregate existing EIC-1 candidate, no new interpretation, no conclusion/judgment); F1-F7 fidelity 硬约束; CONTRACT_STATUS=READY but IMPLEMENTATION NOT AUTHORIZED | Design (L5.4) |
| I22 | "不得丢失" ≠ "必须自动判断": negative/UNKNOWN/conflict 必须保留 (F2/F4/F5) 但 System 不得自动判断 semantic role; "这是 negative" = Human 验证后 label; System 标 negative role = Semantic Closure | Design (L5.4) |
| I23 | L5.3 最小性证明得到 implementation-level support: 2 primitive (Aggregation+Compression) 在 tmp/ 隔离实现, C1-C10+R1-R8+F1-F7 全 PASS, 无第三 primitive 需求 (minimality_falsified=False), 无 semantic closure, 无 decision leakage, 无 burden transfer (3/21); 未长成 Pattern Engine | Experimentally verified (L5.5) |
| I24 | Semantic Claim Candidate 工程实现验证: claim = aggregation_of_existing_governed_candidates (template); is_new_semantic_interpretation=False; source=different_cell_candidate from EIC-1 governed mapping (EXISTING frozen); "Compress evidence not meaning" 在代码层面可证伪 | Experimentally verified (L5.5) |
| I25 | L5.3 minimality 存在 LIMITED circular reasoning: L5.1 定义 Workflow C (design hypothesis) → L5.3 以其为 deletion test 前提 → L5.5 验证; L5.3 证明的是 B ("Workflow C 下最小") 非 A ("DICE 普适最小"); 需 human-subject experiment 消除; claim 已降级为 B | Inferred (L5.6 audit) |
| I26 | L5.5 的 3/21 compression = Engineering Proxy (B 类), 非 Human Subject Evidence (A 类); "Workflow C 工程可实现" 的证据, 非 "Human cognitive load 下降" 的证据; Over-Design Risk=LOW (L5.3 收敛, L5.5 退出 design); NO FURTHER DESIGN REQUIRED | Inferred (L5.6 audit) |
| I27 | L5.7 Material Audit: 21 cases GT=19:2 SEVERELY IMBALANCED; 0 conflict cases; 0 System≠GT cases (automation bias coverage LIMITED); System candidate 全正确 (11 admitted 全 KEEP_SEPARATE); n=21 → pilot/exploratory only 非 confirmatory; limitations recorded NOT designed-away; 不扩大 Pattern/Primitive/系统弥补 | Observed (L5.7 material audit) |
| I28 | L5.8 Readiness: Pilot 已 READY (0 blocker, 8 non-blocking limitations); F1-F7 re-verified ALL PASS; C claim=CANDIDATE (0 answer leak, candidate wording 非 assertion); UNKNOWN preserved; negative visible; provenance=1.0; A/B/C all READY + fair; PRODUCTION=FALSE, FROZEN_BASELINE=INTACT; 不自行执行, 需 Human Experiment Authorization | Experimentally verified (L5.8 readiness check) |
| I29 | L5.7 Harness: A/B/C materials 从 frozen L5.5 生成 (A=21/B=3/C=3); 7/7 validation PASS; recording schema + behavioral indicators (ABSTRACTION/REVISIT/EXPANSION) + progressive disclosure (Level 0→4) + workload proxy warning (≠cognitive_load) 全定义; NO human judgments (不模拟不伪造); 允许 C 失败 (不修改 to "fix"); 为真实 Human 执行做好一切准备 | Experimentally verified (code-level) |
| I30 | L5 Authorization Prep: 全部执行条件 READY (Protocol + UI standalone HTML + Recording + Counterbalancing + Privacy + Consent template + Observation plan + Failure rules); A/B/C fairness PASS; UI GT stripped + no recommend/score/predict; 3 blockers 全 authorization-related (ethics/IRB + recruitment + execution); 0 simulated/fabricated data; 需 Human Experiment Authorization 后可直接执行 | Experimentally verified (code-level) + Design |

PAPER_VALUE: I1/I2/I3/I6/I7/I9 = HIGH; I4/I5/I8/I10 = HIGH; I11/I12 = HIGH; I13/I14/I15 = HIGH; I16/I17/I18 = HIGH; I19/I20 = HIGH; I21/I22 = HIGH; I23/I24 = HIGH; I25/I26 = HIGH; I27 = HIGH; I28 = HIGH; I29 = HIGH; I30 = HIGH。

---

## TYPE K — L5.1 Cognitive Load & Burden Transfer Findings (DESIGN REVIEW, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Naive Pattern burden transfer | B 的 evidence_exposure (30-60) > A (21); validation count↓ 但 total load 可能↑ | Inferred (simulation) |
| Human Abstraction Burden (B) | Human 承担 8/10 abstraction (commonality/prototype/boundary/negative/UNKNOWN/scope/provenance/construction) | Inferred |
| Minimal Semantic (C) design | System 承担 abstraction; Human 仅 semantic judgment; default exposure 最低 (3-4) | Design |
| Pattern concept redesign | Model 1 (Human validates Pattern) REJECTED → Model 2 (Pattern=evidence-org layer, Human validates Semantic Claim) | Design conclusion |
| Validation unit | Semantic Claim (非 Instance 非 Pattern) | Design |
| Progressive Disclosure | Level 0-4; default minimal; risk=hidden evidence; mitigation=honest summary+on-demand+auditable provenance | Design |
| Burden transfer mitigation | 诚实 summary (conflict/UNKNOWN count) + on-demand audit + auditable provenance; 残余风险=silent suppression (未验证) | Design / Hypothesis |
| HVC cost model | 8 变量 (review_count/exposure/switching/comparison/abstraction/interaction/complexity/error/fatigue); 无伪权重; 可观测=5, 设计变量=2, 未来实验=3 | Design |
| Long-term sustainability | A/B unsustainable @1000+ [I]; C potentially sustainable @10000 [H unverified] | Inferred / Hypothesis |
| NEW_OBSERVATION_REQUEST | NONE (gap=aggregation/compression layer, 非 measurement) | Experimentally-supported (M-B audit) |
| Pattern REDESIGN verdict | KEEP + REDESIGN (Model 1→Model 2); 不因之前认可默认 KEEP | Design conclusion |

---

## TYPE L — L5.2 Evidence Compression Feasibility Findings (DESIGN REVIEW, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Current System capability | EXISTS=2 (provenance/human-auth), PARTIAL=3 (pairwise/UNKNOWN-instance/conflict-tmp), MISSING=8 (aggregation/commonality/prototype/boundary/negative/summarization/compression/coverage) | Observed (code audit) |
| System Abstraction Capability Test | 9 项: MISSING=6, PARTIAL=3, SUPPORTED=0 | Observed |
| Workflow C implementable now | NO (6/9 MISSING → Human 补 = burden transfer) | Inferred |
| Gap classification | Pattern abstraction layer (新抽象层); 非 observation gap [EV M-B], 非 consumer gap [EV M-B] | Observed + Experimentally-supported |
| Pattern redefinition | Evidence Compression + Reuse Layer (transparent, no runtime authority); KEEP 但不可立即实现 | Design |
| Compression Fidelity | 7 指标 (positive/negative/boundary/UNKNOWN/conflict/provenance/claim-traceable); System 提议 structural role, Human 确认 | Design |
| Semantic Authority Boundary | Compression Layer authority=0; System=Structural Abstraction (L1/L2), Human=Semantic Abstraction (L3); Candidate 非 Conclusion | Design |
| Three-layer model | L1 Organization (provenance EXISTS rest MISSING) / L2 Compression (all MISSING) / L3 Semantic (Human, object MISSING) | Design |
| Burden Transfer Red-Team | 6 反例全 PRESENT (R1 silent-suppression/R2 prototype-bias/R3 over-trust/R4 semantic-closure-in-negative/R5 candidate-vs-conclusion/R6 automation-bias); 缓解设计有, 残余未验证 | Inferred / Hypothesis |
| Minimum required capability | aggregation+compression+provenance+conflict+UNKNOWN+commonality(structural)+negative(structural); boundary deferrable | Design |
| Semantic Claim suitability | 10/10 维度通过 (4 需实现); 反证未推翻 | Design |
| NEW_OBSERVATION_REQUEST | NONE (frozen observation 足够; gap=abstraction layer) | Experimentally-supported |
| Long-term sustainability | @100 design-feasible; @1000 design-sustainable [H]; @10000 theoretically [H]; theoretical≠empirical | Hypothesis |
| 名字类似≠能力 | REPEATS_ACROSS_PAGES=instance-pair 非 pattern; region clustering=page-internal 非 cross-instance; audit_chain=single-trace 非 compressed-multi | Observed |

---

## TYPE M — L5.3 Minimum Capability Boundary Findings (DESIGN REVIEW, 最小性证明, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Minimum System Capability Set | **{Aggregation, Evidence Compression}** — 2 primitive; L5.2 的 7 项经 Deletion Test 压缩 | Design (minimality proof) |
| Minimality proof | 删 Aggregation → 无 group → Human 手动 group → burden transfer; 删 Compression → Human 读全部 N → burden transfer; 两者不可合并/派生彼此 | Design + Inferred |
| Compression Fidelity Constraints (6) | conflict_count / UNKNOWN_count / coverage / provenance-ref / non-positive-groups / claim=candidate — 非独立能力, 是 compression 硬约束 | Design |
| Derived from Aggregation | Commonality(=grouping criterion) / Negative Set(=其他 group 保留非发现) / Structural Signature(=frozen features 作 key) / Structural Comparison(=读 frozen pairwise) | Design |
| Merged into Compression | Summarization(=输出格式) / Conflict(=count 保真) / UNKNOWN(=count 保真) / Coverage(=N/M/K/L) / Semantic Claim Candidate(=aggregated EIC-1 candidates) | Design |
| Deferred | Prototype(L0 不需, 智能=bias R2) / Boundary(grouping criteria=boundary, edge=优化) | Design |
| EXISTS Reused | Provenance / EIC-1 Governed Mapping(candidate) / IS-11 INSUFFICIENT_EVIDENCE / EIC-1 EVIDENCE_CONFLICT | Observed |
| HUMAN Only (System 不得接管) | Semantic Interpretation / Claim Validation / **Negative Semantic Role**(System 标=Semantic Closure) / Boundary Adequacy / Final Authorization / Capability Registration | Design |
| Authority=0 保证 | Aggregation: signature=structural-only frozen; Compression: 报告已有 candidate 不创建新语义; "Compress evidence not meaning" | Design |
| 无 Semantic Closure | 极端 B 检查: System 不形成 semantic pattern / 不判 negative role / 不自动 boundary / 不输出 conclusion | Design + Inferred |
| 无 burden transfer | 极端 A 检查 (若 minimum 实现): Human 不 group/compare/find-commonality/negative/boundary/UNKNOWN/provenance | Inferred |
| NEW_OBSERVATION_REQUEST | NONE (2 primitive 输入全来自 frozen evidence [EV M-B]) | Experimentally-supported |
| 21-case simulation | 4 judgments vs 21; 0 abstraction by Human; default exposure=4 claims (not 21 instances) | Design (based on Observed) |
| L5.2→L5.3 压缩 | 7 items → 2 primitives + 6 constraints; 5 items = derived/merged/reused | Design |

---

## TYPE N — L5.4 Primitive Contract Boundary Findings (DESIGN REVIEW, Contract 正式化, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Aggregation Contract | MUST: read frozen features / group by structural signature / output {group_id,signature,member_refs} / preserve provenance / mark UNKNOWN+CONFLICT / preserve non-positive / declare criteria / enforce forbidden-field [O]; MAY: cross-doc/page / use frozen relations; MUST NOT: semantic label / infer equivalence / select representative / rank/score/decide / infer boundary/scope | Design |
| Compression Contract | MUST: take aggregation+EIC-1+provenance+INSUFFICIENT [O] / output summary(counts)+Claim Candidate(status=candidate,template) / preserve F1-F7 / declare criteria / support L4 / enforce forbidden-field; MAY: aggregate existing candidate wording / compress detail; MUST NOT: create new interpretation / generate conclusion / close boundary / judge SUPPORTED / silently remove conflict/UNKNOWN/negative / score/rank/override / runtime action / weight by volume | Design |
| F1-F7 Fidelity | F1 positive / F2 negative / F3 boundary / F4 UNKNOWN(IS-11 [O]) / F5 conflict(EIC-1 [O]) / F6 provenance(L4) / F7 claim-traceability (Claim→Compressed→Group→Evidence→Observation; break=Failure) | Design + Observed |
| Semantic Claim Candidate | Aggregation 不产 claim; Compression 只 aggregate 已有 EIC-1 candidate; System 凭 structural similarity 创 claim = semantic leakage FORBIDDEN; Template of Existing Claims (ALLOWED) ≠ New Interpretation (FORBIDDEN) | Design |
| "不得丢失"≠"必须自动判断" | negative/UNKNOWN/conflict 保留 (F2/F4/F5) 但 System 不判 semantic role; "这是 negative"=Human label; System 标=Semantic Closure | Design |
| Red-Team 8 场景 | R1 structural≠semantic误读 / R2 conflict隐藏(F5) / R3 UNKNOWN隐藏(F4) / R4 negative隐藏(F2) / R5 semantic-equivalence(System不做) / R6 role越权(FORBIDDEN) / R7 new-claim越权(F7) / R8 volume-weighting(count≠weight); 全 SAFE by contract; 残余=System不诚实→audit [H] | Design + Inferred |
| Authority Gradient | 无 forbidden transition; System=0 structural; Human=sole semantic; Capability=Human-controlled; Runtime=0 | Design |
| 不引入新 Capability | Representative/Boundary/Negative/Conflict/Coverage=derived/constraint/view; Pattern Miner/Classifier=FORBIDDEN; Minimum Set 不变 | Design |
| CONTRACT_STATUS | READY (完整/可证伪/authority=0/fidelity正式化/red-team全覆盖); 但 IMPLEMENTATION NOT AUTHORIZED | Design |

---

## TYPE O — L5.5 Implementation Realizability Findings (ISOLATED EXPERIMENTAL, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Implementation result | 21 cases → 3 groups → 3 claims; exposure 3/21; C1-C10+R1-R8+F1-F7 ALL PASS | Experimentally verified |
| Aggregation realizability | YES (group by structural signature, 0 semantic, 0 forbidden, deterministic) | Experimentally verified |
| Compression realizability | YES (count + aggregate existing EIC-1 candidate, 0 new interpretation, 0 conclusion) | Experimentally verified |
| F1-F7 engineering feasibility | ALL PASS (7/7; positive/negative/boundary/UNKNOWN/conflict/provenance/claim-traceable) | Experimentally verified |
| Level 4 provenance recovery | YES (provenance_coverage=1.0, 21/21, Level 0→4 full chain) | Experimentally verified |
| Third primitive required | NO (minimality_falsified=False; L5.3 proof supported at implementation level) | Experimentally verified |
| Semantic closure | NONE (R1-R8 all PASS; 0 semantic role; 0 new interpretation; 0 conclusion) | Experimentally verified |
| Decision authority leakage | NONE (0 decision/ranking/score/confidence/recommendation; C9 recursive scan=0) | Experimentally verified |
| Determinism | YES (C1 byte-identical double-run) | Experimentally verified |
| Frozen baseline | INTACT (drift=0; 0 production modifications) | Observed |
| Burden transfer proxy | PASS (Human 3 claims vs 21 instances; 0 abstraction work by Human) | Experimentally verified |
| Not a Pattern Engine | YES (no pattern discovery/mining/classification; Pattern=Human validation concept) | Experimentally verified |
| Semantic Claim Candidate source | aggregation_of_existing_governed_candidates; is_new_semantic_interpretation=False; source=different_cell_candidate from EIC-1 | Experimentally verified |
| Claim boundary | "在当前冻结测试框架和 L5.4 Contract 下, 2 primitive 具有可实现性" (非 generalization/非 production) | Experimentally verified |

---

## TYPE P — L5.6 Research Checkpoint Findings (READ-ONLY AUDIT, 收口, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Logic chain | L5.0-L5.5 成立 (每环可验证, 无断裂) | Inferred |
| Circular reasoning | LIMITED (L5.1 defines Workflow C → L5.3 uses as precondition → L5.5 verifies; L5.3 proves B not A) | Inferred |
| L5.3 claim correction | 降级为 B: "Workflow C 下最小" 非 "DICE 普适最小" | Design |
| Over-design risk | LOW (L5.3 converged 7→2, L5.5 exited design; no recursion) | Inferred |
| L5.4 Contract sufficiency | Sufficient (F1-F7+R1-R8 verified; no observed failure; no v2) | Design + Experimentally verified |
| L5.5 completion | Complete (C1-C10+R1-R8+F1-F7 ALL PASS; no L5.5.x) | Experimentally verified |
| 3/21 evidence level | Engineering Proxy (B), NOT Human Subject Evidence (A) | Experimentally verified (engineering) / Hypothesis (human benefit) |
| Max unknown | C-class: cognitive load / decision quality / automation bias / Workflow C vs A/B / generalization | Hypothesis |
| Over-design audit | 6 undeletable / 2 scaffolding / 4 FORBIDDEN; all either verified or closed | Design + Observed |
| NO FURTHER DESIGN REQUIRED | YES (no observed failure forcing new design) | Observed |
| Next step | OPTION A: Human Validation Experiment (需单独授权) | Design |
| L5 architecture status | CLOSED (no new Primitive/Contract/Design) | Design |

---

## TYPE Q — L5.7 Experiment Design Findings (DESIGN-READY, 最小实验, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| RQ answerable | YES (with material limitations); core (cost+burden transfer) answerable; automation bias/false-acceptance/conflict LIMITED | Inferred |
| Design minimality | PASS (3 conditions = RQ minimum; 3 primary outcomes = minimum; no new architecture) | Design + Inferred |
| Material sufficiency | 21 cases sufficient for pilot; NOT sufficient for confirmatory (GT 19:2 imbalance) | Observed |
| GT balance | SEVERELY IMBALANCED (19 KEEP_SEPARATE : 2 MERGE) | Observed |
| Conflict material | 0 cases (missing; cannot test conflict-preservation Human judgment) | Observed |
| Automation bias material | 0 System≠GT cases (LIMITED; System candidate all correct; cannot test misleading claim acceptance) | Observed |
| Positive scope | All positive=KEEP_SEPARATE (C false-acceptance not testable) | Observed |
| Burden transfer detection | B vs C same count(3), compare time+difficulty → detect Naive Pattern abstraction burden transfer | Design |
| UNKNOWN handling | UNKNOWN = legal judgment; over-compression risk = Human all UNKNOWN for region_not_formed (correctness drop) | Design |
| Negative preservation | C must show Group 2+3 (no candidate); not only Group 1 (admitted) | Design |
| Authority boundary | Preserved (System=0, claim=candidate, Human=authority) | Design |
| Data supplement plan | PROPOSED (+5-8 MERGE + 2-3 conflict + 3-5 System≠GT; requires separate authorization) | Design |
| Recommended path | PATH 1 (PILOT NOW, LIMITED SCOPE): use current 21 cases; answer cost+burden+descriptive quality; mark PILOT/EXPLORATORY | Design |
| No new architecture | YES (L5.5 frozen direct use; no new Primitive/Contract/Pattern) | Observed |
| No experiment execution | YES (design+audit+authorization request only; no recruitment, no execution) | Design |

---

## TYPE R — L5.8 Pilot Execution Readiness Findings (READINESS CHECK, READY, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Execution readiness | PASS (READY; no blocker) | Experimentally verified (re-checked this phase) |
| Core material | READY (21 cases: 11/6/4/2/0; usable for A/B/C) | Observed |
| Workflow A | READY (instance-level, 21 judgments, 0 abstraction) | Design + Observed |
| Workflow B | READY (group-level, 3 judgments, HIGH abstraction; not preset worse) | Design + Observed |
| Workflow C | READY (claim-level, 3 judgments, 0 abstraction; System did grouping+compression) | Design + Observed |
| A/B/C fairness | PASS (same task/material/GT/options; C claim=CANDIDATE not conclusion; 0 answer leak) | Experimentally verified |
| UNKNOWN preservation | PASS (F4; all 3 workflows allow UNKNOWN; compression does not delete UNKNOWN) | Experimentally verified |
| Negative visibility | PASS (C shows 2 negative + 1 positive groups) | Observed |
| Conflict coverage | 0 (LIMITATION, not blocker; not artificially increased) | Observed |
| F1-F7 | ALL PASS (re-verified this phase) | Experimentally verified |
| Provenance | 1.0 (21/21, Level 4 recoverable) | Experimentally verified |
| Recording | READY (case_id+workflow+decision+time; optional difficulty+confidence; proxy≠cognitive_load) | Design |
| Blocker count | 0 | Inferred |
| Limitation count | 8 (all non-blocking; honestly retained) | Observed |
| Future question count | 5 (not addressed in pilot) | Design |
| Artifact boundary | PRODUCTION=FALSE, 0 mods, FROZEN_BASELINE=INTACT, L5.5 tmp/ only | Observed |
| Anti-overdesign | NEW_PRIMITIVE/CONTRACT/ARCHITECTURE/DESIGN=0; no L5.8.1/8.2; no Pattern Engine/etc | Inferred |
| Pilot scope | LIMITED / EXPLORATORY (non-confirmatory, non-generalization) | Design |
| Not self-executed | YES (readiness + authorization request only; no Pilot execution) | Design |

---

## TYPE S — L5.7 Pilot Harness Preparation Findings (HARNESS-READY, tmp/ only, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Harness complete | YES (generate/validate/schema; reads frozen L5.5, produces A/B/C materials) | Experimentally verified (code-level) |
| Materials A | 21 per-instance items (structural context, no semantic label, GT hidden) | Observed |
| Materials B | 3 per-group items (all members shown, no compression, no claim) | Observed |
| Materials C | 3 per-claim items (compressed candidate + summary + progressive disclosure) | Observed |
| Material validation | 7/7 PASS (same options, no answer leak, candidate, all members, L4 recoverable, negative shown) | Experimentally verified |
| Recording schema | Complete (required: id+workflow+decision+time; optional: difficulty+confidence+expansion+behavior) | Design |
| Behavioral indicators | ABSTRACTION_BEHAVIOR / REVISIT_BEHAVIOR / EXPANSION_BEHAVIOR defined | Design |
| Progressive disclosure | C: Level 0→4 (claim→summary→members→boundary/negative→full provenance); track expansion_count | Design |
| Workload proxy warning | review_count/evidence_exposure ≠ cognitive_load; true burden = time+difficulty+abstraction+behavior | Design |
| No human judgments | YES (no simulation, no fabricated results, no synthetic data) | Observed |
| Frozen baseline | INTACT (drift=0, L5.5 not modified, 0 production mods) | Observed |
| Allowed C failure | YES (if C fails, record as observed failure; do not modify to "fix") | Design |

---

## TYPE T — L5 Human Experiment Authorization Preparation (READY, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| Preparation status | READY (all execution conditions prepared) | Design + Observed |
| Protocol | READY (RQ + non-directional hypothesis + participants + A/B/C + materials + counterbalancing + recording + limitations) | Design |
| A/B/C fairness | PASS (same task/material/GT/options; C=CANDIDATE; 0 answer leak; UI no recommend/score) | Experimentally verified |
| Pilot UI | READY (standalone HTML 45.8KB; display+record; GT stripped; no answer/recommend/rank/score/predict) | Experimentally verified (code-level) |
| Recording | READY (schema L5.7_v1; required+optional+behavioral; JSON export per participant) | Design + Observed |
| Counterbalancing | READY (Latin square 3 orders, auto-assigned by participant number) | Design |
| Privacy | READY (anonymous ID; no personal data; offline; no cloud upload) | Design |
| Consent | TEMPLATE READY (ethics/IRB = institutional requirement identified, not yet obtained) | Design |
| Observation plan | READY (4-layer: operational/cognitive-behavior/quality/reusability; H1-H4; N→claims→work) | Design |
| Failure rules | READY (C failure allowed; BURDEN_TRANSFER if count↓ but time/abstraction↑; no modification to "fix") | Design |
| Remaining blockers | 3 (all authorization-related: ethics/IRB + recruitment + execution; NOT design/technical) | Inferred |
| No simulated data | YES (0 simulated, 0 fabricated, 0 AI-as-human) | Observed |
| Frozen baseline | INTACT (drift=0, L5.5 unchanged, 0 production mods) | Observed |

---

## TYPE J — L5 Human Validation Readiness (DESIGN REVIEW, HIGH)

| 维度 | 发现 | EVIDENCE_LEVEL |
|---|---|---|
| 当前 validation 对象 | 实例级 (ValidationTask per document/page/observation) | Observed (code) |
| reusable-pattern 抽象 | ABSENT (grep 0 命中: interpretation_pattern/reusable_pattern/capability_candidate/document_span) | Observed (code) |
| ValidationRecord 字段 | verdict+reason+notes+timestamp+duration+reviewer+revision+provenance; **无** pattern/negative-set/boundary/scope | Observed (code) |
| FROZEN_CAPABILITY_TABLE | 22 静态 DICE 1.0 人控; L3_SKILL_ROUTES 非自动学习 | Observed (code) |
| TABLE/TABLE_CELL in P7.1 | BLOCKED ("waits for Table Cell Geometry") — EIC-1 candidate 无架构归宿 | Observed (code) |
| instance-level bias 位置 | ValidationTask key 构造 + review_interface 逐案呈现循环 | Observed (code) |
| 推荐对象 | Interpretation Pattern (D); 5/10 成分已备 (positive/negative/provenance/interpretation/UNKNOWN), 5/10 需设计 (scope/boundary/human-decision/record/reuse) | Design conclusion |
| 反模式风险 PRESENT | 4 项: instance-labeling / positive-only / no-negative-set / no-boundary | Observed |
| L5 DESIGN READINESS | CONDITIONAL READY (成分有, 抽象层/schema 无) | Design conclusion |
| NEW_OBSERVATION_REQUEST | NONE (现有 frozen Observation 足以表达 pattern prerequisites) | Experimentally-supported (M-B audit) |
| pattern↔capability | ≠ ; pattern validation → validated knowledge → capability candidate → human controlled registration → capability | Design |

---

## Engineering Fact / Research Interpretation / Potential Paper Claim 分离示例

- **Engineering Fact**: AMB-135 MERGE→KEEP_SEPARATE (Phase 3.2 实测)。
- **Research Interpretation**: existing frozen geometry evidence was sufficient to express
  the failure mechanism through a governed integration layer (EIC-1) without modifying
  the decision policy.
- **Potential Paper Claim**: "在当前冻结测试框架中, 该 minimal Consumer Integration 机制得到验证。"
- **禁止写成**: "DICE 解决了 table slicing" / "实现了通用 table detection" / "跨文档泛化"。

## 价值排序原则
- HIGH: PH-02 failed hypothesis · research-object correction · localization gap ·
  M-B expressability · semantic leakage · EIC-1 boundary · safety canary · honest
  ABSTAIN · frozen decision invariant · isolated replay · evidence integration vs
  observation gap · negative examples · discrepancy correction。
- **不因最终成功而把失败过程标 LOW** — 失败过程是论文最有价值的部分。
