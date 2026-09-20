# DICE Engineering / Research Evidence Index

> 层 1 索引: 近期 DICE 研究过程的工程/研究证据总目录。每条标注 EVIDENCE_LEVEL 与文件出处。
> 目的: 可追溯、可审计的证据沉淀, 非宣传材料。

## 索引体例

每条: **主题** | EVIDENCE_LEVEL | 关键文件 | 一句话事实。

---

## 1. 独立性审计 / 失败分析基础
- **45-case independence audit** | OBSERVED | `tmp/is11_human_review_report.md`,
  `tmp/is11_independent_sampling_frame.json` | 45 案例逐案冻结, machine eval 顶层 dict,
  `case_results` 字段; GT sha=7349963d0d23b5ef。
- **TCC 26 例 = 3 docs / 10 页设置** | OBSERVED | 同上 | top1 doc 57%, med_001 抽样加权 1.86×。

## 2. PH-02 (REJECTED)
- **PH-02 column-membership experiment** | EXPERIMENTALLY VERIFIED |
  `tmp/ph02_column_membership_experiment_contract.md`, `_report.md`, `_results.json` |
  15/15 参数组合 × 45 案例; A=0/1 (FP 未移除); 7/13 anchors firing (specificity risk);
  REJECTED (预注册规则, 无补救)。
- **research object 错误诊断** | INFERRED | `_report.md` | whole left_alignment_group
  被误当作 research object; page-wide 几何对象 ≠ 局部结构列。

## 3. C2 Necessity Review (REQUIRES_REDESIGN)
- **C2 necessity + positive coverage audit** | EXPERIMENTALLY VERIFIED |
  `tmp/c2_necessity_review.{md,json}` | 545-universe; 138 numeric clusters; 137 negative;
  positive GT-confirmed=1; POSITIVE_COVERAGE=INSUFFICIENT; 双重阻塞 (redesign × coverage)。
- **research-object design** | DESIGN | `tmp/candidate_column_segment_research_object_design.{md,json}` |
  candidate-column-segment; M3 POSSIBLY_REDUNDANT; M5 簇级自斥。

## 4. Corpus Discovery / Acquisition
- **corpus discovery** | OBSERVED | `tmp/candidate_column_segment_corpus_discovery.{md,json}`,
  `tmp/corpus_discovery/*` | 709 簇 / 10 文档; 新边界族 INDEX_LIST; GT_CONFIRMED=1。
- **corpus acquisition** | OBSERVED | `tmp/candidate_column_segment_corpus_acquisition.{md,json}`,
  `tmp/corpus_acquisition/*` | 4 arXiv 文档 (T5/LLaMA/BERT/MMLU) / 80 页 / 131 簇;
  新边界 CODE_LINE_NUMBER (NM-06); M4 第二独立佐证; positive 新增=0。

## 5. Slicing Failure Impact Ranking
- **impact ranking** | INFERRED + OBSERVED | `tmp/slicing_failure_impact_ranking.{md,json}` |
  M-B = TOP1 (表格区域证据不可用); 6 DIRECT + 3 INDIRECT; 唯一真实 FP=AMB-135;
  通道 8/8 已证; RESEARCH_HYPOTHESIS=NOT_READY。

## 6. M-B Expressability Audit (EXPRESSIBLE)
- **expressability audit** | EXPERIMENTALLY VERIFIED |
  `tmp/mb_table_region_evidence_expressability_audit.{md,json}` | 冻结证据已存在;
  correct-vs-blind 无 Level-1 差异; primary gap=Consumer/Integration; drawings 缺席非承重;
  verdict=EXPRESSIBLE。
- **逐案显微镜事实** | OBSERVED | `/tmp/mb_case_facts.json`, `/tmp/mb_fp_precise.py` |
  19 focus case 逐案 lag/band/pairwise; FP 对 lag10×lag6 h_gap=30.02; p5 表区 12 列簇。

## 7. M-B Phase 2 (Consumer Integration Design)
- **Phase 2 design** | DESIGN | `tmp/mb_phase2_minimal_consumer_integration_design.{md,json}` |
  Design B (Structural Context Adapter) 推荐; 3 设计比较; TLD 共存契约; AMB-135 walkthrough;
  caption canary M3。

## 8. M-B Phase 2.1 (Integration Contract Review, CONDITIONAL_PASS)
- **Phase 2.1 review** | DESIGN REVIEW + OBSERVED |
  `tmp/mb_phase2_1_integration_contract_review.{md,json}` | 代码级证 SEMANTIC_MAPPING_GAP=TRUE
  (TLD different_cell 以 detected table 为前提); 1 处语义泄漏 (is11_obs 形状发射);
  canonical DIRECT=9 (修正 8); canary 事实确认; CONFLICT_CONTRACT_UNRESOLVED。

## 9. M-B Phase 2.2 (Evidence Interpretation Contract, PASS)
- **Phase 2.2 review** | DESIGN | `tmp/mb_phase2_2_evidence_interpretation_contract_review.{md,json}` |
  EIC-1 十要素; Authority Gradient L0-L6; No Semantic Closure; Cell Context=B(interpretation,
  candidate); DECISION_POLICY_CHANGE_REQUIRED=FALSE; Gate A-O 全满足。

## 10. M-B Phase 3 (Isolated Replay Design, DESIGN-READY)
- **Phase 3 design** | DESIGN | `tmp/mb_phase3_isolated_replay_design.{md,json}` |
  25 行冻结矩阵 (21 决策 + 4 描述); S1-S10; F1-F10; patch-accumulation precommitment;
  scientific claim boundary。

## 11. M-B Phase 3.1 (Preregistration Parameter Fixation, COMPLETE)
- **Phase 3.1** | EXPERIMENTALLY VERIFIED |
  `tmp/mb_phase3_1_preregistration_parameter_fixation.{md,json}` | LOCALIZATION GAP 发现;
  P_localization=150pt; canary density=0 vs target=30; 鲁棒性 [100,200]pt; MISSING_PARAMETER=0。

## 12. M-B Phase 3.2 (Implementation + Isolated Replay, REPLAY_PASS)
- **Phase 3.2 implementation** | EXPERIMENTALLY VERIFIED |
  `tmp/mb_phase3_2_implementation_report.{md,json}`,
  `tmp/mb_phase3_2_isolated_replay_results.json`,
  `tmp/mb_phase3_2_implementation_baseline.json` | S1-S10 ALL PASS; F1-F10=0;
  FP 修复 + 6/8 recovery + 2/8 honest ABSTAIN; 0 语义泄漏; 决策函数 hash 不变。
- **adapter / runner 代码** | IMPLEMENTATION (isolated, non-production) |
  `tmp/mb_eic1_adapter.py`, `tmp/mb_phase3_2_replay.py` | harness 通过 importlib 导入未改;
  forbidden-field assertions; 三案例共存契约。

## 13. 冻结完整性 (全程)
- **frozen baseline** | OBSERVED (每轮复验) | `tmp/perception/atomic_observation/layer_registry.json` |
  7 frozen sources; anchors_drift=0 (全程); GT sha=7349963d0d23b5ef; TLD sha=022f5c21e872ad9e;
  harness sha=b41494020b491b92 (Phase 3.2 前后一致)。

## 14. 治理状态 (整链继承)
- **governance gate 历史** | DESIGN | 各阶段报告 §Gate | PH02=REJECTED; PH02B=NOT AUTHORIZED;
  C2=REQUIRES_REDESIGN; DESIGN_STATUS=INSUFFICIENT_COVERAGE; CORPUS_LIMITATION=CONFIRMED;
  GT_CONFIRMED_POSITIVE=1; M-B Phase2=CONDITIONAL; 2.1=CONDITIONAL_PASS; 2.2=PASS;
  3=DESIGN-READY; 3.1=COMPLETE; 3.2=REPLAY_PASS; 全程 IMPLEMENTATION/EXPERIMENT 从 NOT
  AUTHORIZED 到 3.2 授权执行; GT/层/TLD/IS-11决策/production 全程未改; FROZEN_BASELINE=INTACT。

## 15. L5 Human Validation Readiness Review (DESIGN/ARCHITECTURE REVIEW)
- **L5 readiness review** | DESIGN REVIEW | `tmp/l5_human_validation_readiness_review.{md,json}` |
  CONDITIONAL READY; 当前 ValidationTask = instance-level (per document/page/observation);
  reusable-pattern abstraction ABSENT (grep 0); FROZEN_CAPABILITY_TABLE = static 人控 (非自动派生);
  TABLE/TABLE_CELL 在 P7.1 BLOCKED (EIC-1 candidate 无架构归宿); 推荐对象 = Interpretation
  Pattern (Candidate D, 5/10 成分已备); 4 反模式风险 PRESENT (instance-labeling/no-negative-set/
  no-boundary/positive-only); NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE; 不实施。
- **architecture inventory** | OBSERVED | `perception/sandbox/validation/validation_models.py`,
  `review_interface.py`, `assets/frozen_capabilities.py`, `structure/structure_hypothesis.py` |
  ValidationRecord 无 pattern/negative/boundary/scope 字段; review_interface 逐案确认;
  StructureHypothesis per-instance (document|page|type|source_ids)。

## 16. L5.1 Human Validation Cognitive Load Review (DESIGN-ONLY)
- **L5.1 cognitive load review** | DESIGN REVIEW | `tmp/l5_1_human_validation_cognitive_load_review.{md,json}` |
  CONDITIONAL PASS; RQ=Pattern 是否降低 total cognitive cost 还是 burden transfer;
  三 Workflow 分析 (A=instance/B=naive pattern/C=minimal semantic); B 的 evidence_exposure
  (30-60) > A (21) = burden transfer 直接证据 [I]; C 默认 exposure (3-4) 最低但依赖未实现
  System aggregation [H]; Human Abstraction Burden Test: B=8/10 abstraction 在 Human, C=System
  承担; 核心结论: Model 1 (Human validates Pattern) REJECTED; Model 2 (Pattern=evidence-org
  layer, Human validates Semantic Claim) RETAINED; validation unit = Semantic Claim (非 Instance
  非 Pattern); Progressive Disclosure (Level 0-4) + Evidence visibility≠authority; HVC 成本模型
  (8 变量无伪权重); burden transfer 缓解=诚实 summary+on-demand audit+auditable provenance
  (残余风险=silent suppression, 未验证); NEW_OBSERVATION_REQUEST=NONE; 不实施不实验。
- **design principles fixed (L5.1)** | DESIGN | 同上 | (1) Human validates not reconstruct;
  (2) Pattern compresses evidence not transfers abstraction; (3) validation unit=Semantic Claim;
  (4) System owns aggregation/compression/boundary/negative/UNKNOWN/provenance; (5) Human owns
  semantic interpretation+final authorization; (6) Evidence visibility≠authority; (7) Progressive
  Disclosure; (8) honest summary+auditable provenance; (9) Pattern 无 runtime authority;
  (10) 成功标准=更少更简单语义判断+足够证据+abstraction 不转嫁。
- **simulation (21 cases)** | DESIGN SIMULATION (基于 O 案例) | A=21 judgments/B=3-4 patterns
  exposure 30-60/C=3-4 claims exposure 3-4; @10000: A/B unsustainable, C potentially sustainable
  [H unverified]。

## 17. L5.2 Evidence Compression Feasibility Review (DESIGN-ONLY)
- **L5.2 compression feasibility** | DESIGN REVIEW | `tmp/l5_2_evidence_compression_feasibility_review.{md,json}` |
  CONDITIONAL PASS; RQ=现有能力是否足以支撑 Workflow C (System 自动 aggregation/compression/
  coverage/conflict+UNKNOWN preservation → Human 仅验证 Semantic Claim); **核心发现 [O]**: 15 项
  allocation 中 EXISTS=2 (provenance/human-auth), PARTIAL=3 (pairwise-comparison/UNKNOWN-instance/
  conflict-tmp), **MISSING=8** (aggregation/commonality/prototype/boundary/negative/summarization/
  compression/coverage); System Abstraction Capability Test: 9 项 MISSING=6/PARTIAL=3/SUPPORTED=0;
  Workflow C **当前不可实现** (6/9 MISSING → 若强行用 Human 补 = HUMAN_ABSTRACTION_BURDEN);
  gap=Pattern abstraction layer (新抽象层, 非 observation gap [EV M-B], 非 consumer gap [EV M-B]);
  Compression Fidelity 定义 (7 指标: positive/negative/boundary/UNKNOWN/conflict/provenance/
  claim-traceable; System 提议 structural role, Human 确认, 不得单方删除); Semantic Authority
  Boundary: Compression Layer authority=0 (只改组织不改语义); System=Structural Abstraction
  (L1/L2), Human=Semantic Abstraction (L3); Pattern=Evidence Compression+Reuse Layer (KEEP 但
  不可立即实现); Semantic Claim 10/10 维度通过 (4 需实现); Burden Transfer Red-Team 6 反例全
  PRESENT (R1 silent-suppression/R2 prototype-bias/R3 over-trust/R4 semantic-closure-in-negative/
  R5 candidate-vs-conclusion/R6 automation-bias) + 设计缓解 + 残余风险未验证 [H]; NEW_OBSERVATION
  _REQUEST=NONE; 不实施不实验。
- **current capability inventory [O]** | OBSERVED (代码核查) | `perception/sandbox/structure/
  structure_relation.py` (8 REL types, instance-pair per doc/page/src/tgt); `region/region_engine.py`
  (page-internal clustering); `validation/validation_models.py` (ValidationRecord instance-level);
  `assets/frozen_capabilities.py` (22 static human-controlled); grep 0 for aggregation/commonality/
  common_structure/repeated_pattern/evidence_summary/compress/coverage/prototype/boundary_discovery/
  negative_discovery; 33 validation_records (1 ACCEPT/32 REJECT, all instance-level); 名字类似≠能力
  (REPEATS_ACROSS_PAGES=instance-pair 非 pattern; region clustering=page-internal 非 cross-instance)。
- **three-layer capability model [D]** | DESIGN | L1 Evidence Organization (group/aggregate/link/
  provenance: provenance EXISTS, rest MISSING) / L2 Evidence Compression (summarize/compress/
  preserve contradiction+UNKNOWN/progressive disclosure: all MISSING) / L3 Semantic Abstraction
  (semantic pattern/claim/scope/boundary: Human, System produces Candidate only; object MISSING)。
- **minimum required system capability [D]** | DESIGN | aggregation+compression+provenance-preserved
  +conflict-preserved+UNKNOWN-preserved+commonality(structural)+negative(structural); boundary
  deferrable (不过度设计)。

## 18. L5.3 Minimum System Abstraction Boundary Review (DESIGN-ONLY, 最小性证明)
- **L5.3 minimum capability boundary** | DESIGN REVIEW (Deletion Test) | `tmp/l5_3_minimum_capability_boundary_review.{md,json}` |
  CONDITIONAL PASS; 对 L5.2 的 7 项 minimum + 8 项 MISSING 逐项 Capability Deletion Test;
  **核心结论 [D]**: Minimum System Capability Set = **{Aggregation, Evidence Compression}**
  (2 primitive + 6 Compression Fidelity Constraints); L5.2 的 7 项压缩为 2 真正 primitive,
  其余 5 项为派生/合并/复用; 最小性反证: 删 Aggregation → 无 group → Human 手动 group →
  burden transfer; 删 Compression → Human 读全部 N → burden transfer; 两者不可合并/派生彼此;
  Derived from Aggregation: Commonality(=grouping criterion) / Negative Set(=其他 group, 保留非发现)
  / Structural Signature(=frozen features 作 key) / Structural Comparison(=读 frozen pairwise);
  Merged into Compression: Summarization(=输出格式) / Conflict Preservation(=conflict_count 保真约束)
  / UNKNOWN Preservation(=UNKNOWN_count 保真约束) / Coverage(=N/M/K/L 计数) / Semantic Claim
  Candidate(=aggregated 已有 EIC-1 candidates, status=candidate); Deferred: Prototype(L0 不需,
  智能=.bias R2) / Boundary(grouping criteria=boundary, edge=优化); View: Progressive Disclosure(UI);
  EXISTS Reused: Provenance / EIC-1 Governed Mapping / IS-11 INSUFFICIENT_EVIDENCE / EIC-1
  EVIDENCE_CONFLICT; HUMAN Only: Semantic Interpretation / Claim Validation / Negative Semantic
  Role / Boundary Adequacy / Final Authorization / Capability Registration; Authority=0 保证:
  Aggregation signature=structural-only frozen features, Compression 报告已有 EIC-1 candidate 不创建
  新语义, "Compress evidence not meaning"; 无 Semantic Closure (极端 B 检查 PASS); 无 burden transfer
  (极端 A 检查 PASS, 若 minimum 实现); NEW_OBSERVATION_REQUEST=NONE (2 primitive 输入全来自 frozen
  evidence [EV M-B]); 21-case simulation: 4 judgments vs 21, 0 abstraction by Human [D based on O];
  不实施不实验。
- **L5.2→L5.3 压缩** | DESIGN | 7 items → 2 primitives + 6 fidelity constraints; 5 items =
  derived/merged/reused (非独立 primitive); deletion test 判据 = "删除后 Workflow C 是否仍成立"。

## 19. L5.4 Minimum Primitive Contract Boundary Review (DESIGN-ONLY, Contract 正式化)
- **L5.4 primitive contract** | DESIGN REVIEW | `tmp/l5_4_primitive_contract_boundary_review.{md,json}` |
  CONDITIONAL PASS; 为 Aggregation + Evidence Compression 建立 MUST/MAY/MUST NOT Contract;
  CONTRACT_STATUS=READY (但 IMPLEMENTATION NOT AUTHORIZED);
  **Aggregation Contract**: MUST read frozen structural features only / group by structural
  signature equality / output {group_id,signature,member_refs} / preserve provenance / mark
  UNKNOWN+CONFLICT / preserve non-positive groups / declare grouping criteria / enforce
  forbidden-field assertions [O EIC-1 FORBIDDEN set]; MAY cross-doc/page / use frozen
  StructuralRelation+EIC-1; MUST NOT semantic label / infer semantic equivalence / select
  representative / rank/score/recommend/decide / infer boundary/scope / create new relations;
  **Compression Contract**: MUST take aggregation+EIC-1 candidate+provenance+INSUFFICIENT_EVIDENCE
  [O] / output summary (consistent/conflict/UNKNOWN/coverage counts) + Semantic Claim Candidate
  (aggregated EIC-1, status=candidate [O], template) / preserve F1-F7 / declare criteria /
  support Level 4 recovery (F6) / enforce forbidden-field; MAY aggregate existing candidate
  wording / compress instance detail; MUST NOT create new interpretation / generate conclusion /
  close boundary / judge SUPPORTED / silently remove conflict/UNKNOWN/negative / score/rank/
  recommend/fallback/override / runtime action / weight by volume;
  **F1-F7 Compression Fidelity**: F1 positive / F2 negative / F3 boundary / F4 UNKNOWN (IS-11
  [O]) / F5 conflict (EIC-1 [O]) / F6 provenance recoverable (Level 4) / F7 claim traceability
  (Claim→Compressed→Group→Evidence→Observation; any break=Failure);
  **Semantic Claim Candidate 审查**: Aggregation 不产 claim (只 group); Compression 只 aggregate
  已有 EIC-1 candidate (不创建新 Y); System 凭 structural similarity 创造 semantic claim =
  semantic leakage FORBIDDEN; "Template of Existing Candidate Claims" (ALLOWED) ≠ "New Semantic
  Interpretation" (FORBIDDEN); "不能因 candidate 相似就宣称发现 Pattern";
  **关键区分**: "不得丢失" ≠ "必须自动判断" (negative/UNKNOWN/conflict 保留但 System 不判 semantic
  role); Structural Similarity ≠ Semantic Equivalence; Evidence Compression ≠ Semantic
  Compression; Hidden≠Absent, Compressed≠Less-Authoritative;
  **Red-Team 8 场景全 SAFE by contract**: R1 structural≠semantic误读 / R2 conflict隐藏(F5) /
  R3 UNKNOWN隐藏(F4) / R4 negative隐藏(F2) / R5 semantic-equivalence(System正确不做) /
  R6 semantic-role越权(FORBIDDEN labeling) / R7 new-claim越权(F7+compress-not-mean) /
  R8 volume-weighting(count≠weighting); 残余风险=System不诚实计数(R2/R3/R4)→需audit [H];
  **Authority Gradient 不破坏**: 无 forbidden transition (Aggregation→Semantic / Compression→
  Semantic / Compression→Capability / Aggregation→Decision / Compression→Decision 全 FORBIDDEN);
  **不引入新 Capability**: Representative/Boundary/Negative/Conflict/Coverage = derived/constraint/
  view; Pattern Miner/Classifier = FORBIDDEN; Minimum Set 不变 = {Aggregation, Compression};
  NEW_OBSERVATION_REQUEST=NONE; 不实施不实验。

## 20. L5.5 Minimum Primitive Implementation & Contract Verification (ISOLATED EXPERIMENTAL)
- **L5.5 implementation** | ISOLATED EXPERIMENTAL (tmp/ only) | `tmp/l5_5_aggregation.py` (10.2 KB) /
  `tmp/l5_5_evidence_compression.py` (12.9 KB) / `tmp/l5_5_contract_verification.py` (25.2 KB) |
  CONDITIONAL PASS; 在 tmp/ 隔离环境实现 L5.4 Contract 的 2 primitive 并验证;
  **21 cases → 3 groups** (admitted=11/region_not_formed=6/partition_unresolvable=4);
  **3 claims** (1 candidate + 2 UNKNOWN); exposure 3/21; **C1-C10 ALL PASS** (determinism/
  aggregation-purity/compression-purity/UNKNOWN-preservation/conflict-preservation/negative-
  preservation/provenance-1.0/claim-traceability/forbidden-field-0/mutation-0);
  **R1-R8 ALL PASS** (structural≠semantic/conflict-not-hidden/UNKNOWN-not-hidden/negative-not-
  suppressed/semantic-equivalence=Human/no-semantic-role/no-new-claim/no-volume-weighting);
  **F1-F7 ALL PASS**; **THIRD_PRIMITIVE_REQUIRED=NO** (minimality_falsified=False; L5.3 最小性
  证明得到 implementation-level support); **BURDEN_TRANSFER_PROXY=PASS** (Human 3 claims vs 21
  instances, 0 abstraction work); Semantic Claim Candidate = aggregation_of_existing_governed_
  candidates (is_new_semantic_interpretation=False, source=different_cell_candidate from EIC-1);
  authority=0; volume_weighted=False; forbidden_field_violations=0; Level 4 provenance recoverable
  (21/21); 未创建 pattern_engine/miner/classifier/negative_detector/boundary_detector/prototype_
  selector (全 FORBIDDEN); **未长成 Pattern Engine**; 不声称 cognitive load 已实证下降 (engineering
  proxy only, 非 human-subject experiment); FROZEN_BASELINE=INTACT (drift=0, 0 production mods)。
- **implementation baseline** | OBSERVED | `tmp/l5_5_implementation_baseline.json` | 实现前 frozen
  hash 快照: 7 anchors drift=0, GT=7349963d, TLD=022f5c21, harness=b4149402, eic1=d9b6a4b1;
  实现后复验全 MATCH; production modifications=0。
- **contract verification results** | EXPERIMENTALLY VERIFIED | `tmp/l5_5_contract_verification_
  results.json` | C=10/10, R=8/8, F1-F7=7/7, third_primitive=NO, burden_transfer=PASS, all_pass=True。

## 21. L5.6 Evidence Abstraction Research Checkpoint (READ-ONLY AUDIT, 收口)
- **L5.6 research checkpoint** | READ-ONLY AUDIT | `tmp/l5_6_evidence_abstraction_research_checkpoint.{md,json}` |
  CONDITIONAL PASS; 对 L5.0-L5.5 整条研究线独立审计; **逻辑链成立** (每环可验证, 无断裂);
  **Circular Reasoning = LIMITED** (L5.1 定义 Workflow C → L5.3 以其为 deletion test 前提 → L5.5
  验证; 影响=scope 限定, 非结论错误; L5.3 claim 降级为 B: "Workflow C 下最小" 非 "DICE 普适最小");
  **Over-Design Risk = LOW** (L5.0→L5.2 递增 design; L5.3 收敛 7→2; L5.5 退出 design; 当前无 recursion);
  **L5.4 Contract 已足够** (F1-F7+R1-R8 全 PASS; 无 observed failure; 禁止 F8+/R9+/Contract v2);
  **L5.5 已完成** (C1-C10+R1-R8+F1-F7 ALL PASS; 禁止 L5.5.x);
  **Over-Design Audit**: 12 设计对象分类 — 6 不可删除 (observed-driven+verified) / 2 research scaffolding
  (Pattern 概念+Progressive Disclosure 数据结构) / 4 FORBIDDEN (Pattern Engine/Registry/Miner/Classifier);
  **证据分类**: A 类 (experimentally verified: implementation/contract/fidelity/determinism/provenance/
  leakage=0) / B 类 (engineering proxy: 3/21 compression, 0 burden transfer, Workflow C feasible) /
  C 类 (unverified: cognitive load/decision quality/automation bias/Workflow C vs A/B/generalization);
  **NO FURTHER DESIGN REQUIRED** (无 observed failure 强制新设计);
  **NEXT_STEP = HUMAN_VALIDATION_EXPERIMENT** (需单独授权; 目标: Workflow A vs C 对比; 指标:
  cognitive load, decision quality, review time; harness = L5.5 tmp/ 实现);
  **L5_ARCHITECTURE_STATUS = CLOSED** (不再新增 Primitive/Contract/Design);
  NEW_PRIMITIVE=NO / NEW_DESIGN=NO / NEW_CONTRACT=NO; 不实施不实验。

## 22. L5.7 Human Validation Experiment Design (DESIGN-READY, 最小实验设计)
- **L5.7 experiment design** | DESIGN ONLY (no execution, no recruitment) | `tmp/l5_7_human_validation_
  experiment_design.{md,json}` | DESIGN-READY; 最小 Human Experiment 设计回答 RQ-L5.7 (Workflow A/B/C
  对比: cost + quality + burden transfer); **EXPERIMENT_DESIGN_MINIMALITY = PASS** (3 conditions = RQ
  最小集; 3 primary outcomes = 最小; 无新 Primitive/Contract/Architecture; limitations recorded not
  designed-away); within-subject, Latin square counterbalancing, pilot n=3-5, exploratory;
  **Material Audit**: 21 cases → positive=11/negative=6/UNKNOWN=4/boundary=2/conflict=0; GT=19:2
  (SEVERELY_IMBALANCED); **EXPERIMENT_MATERIAL_LIMITATION RECORDED**: (1) GT imbalance 19:2 → quality
  统计不可行 pilot only; (2) conflict=0 → conflict-preservation Human 判断不可测; (3) automation bias
  coverage=LIMITED (0 System≠GT cases, System candidate 全正确); (4) positive 全 KEEP_SEPARATE → C
  false-acceptance 不可测; (5) n=21 → pilot/exploratory 非 confirmatory; **不扩大 Pattern/Primitive/
  系统来弥补**; **Burden Transfer Detection**: B vs C same count(3), compare time+difficulty → 检测
  Naive Pattern 是否转嫁 abstraction burden; **UNKNOWN = 合法 judgment** (不强迫分类); **Negative 必须展示**
  (Group 2+3 = no candidate); **Authority Boundary preserved** (System=0, claim=candidate, Human=authority);
  **Data Supplement Plan PROPOSED** (+5-8 MERGE + 2-3 conflict + 3-5 System≠GT; 需单独授权; 本阶段不执行);
  **RECOMMENDED_PATH = PATH 1 (PILOT NOW, LIMITED SCOPE)**: 用当前 21 cases 做 pilot, 回答 cost + burden
  transfer + descriptive quality, 不回答 automation bias/false-acceptance/conflict, 标记 PILOT/EXPLORATORY/
  LIMITED_SCOPE; **NEXT = HUMAN EXPERIMENT AUTHORIZATION REQUEST (PILOT)**; L5 Architecture=CLOSED;
  不招募不执行不修改 production; FROZEN_BASELINE=INTACT。

## 23. L5.8 Pilot Execution Readiness Check (READINESS CHECK, READY)
- **L5.8 readiness check** | READINESS CHECK (no design, no execution, no recruitment) | `tmp/l5_8_pilot_
  execution_readiness.{md,json}` | **READY**; 确认 L5.7 Pilot 已具备实际执行条件; **EXECUTION_READINESS =
  PASS**; **EXECUTION_DESIGN_MINIMALITY = PASS**; **CORE_MATERIAL = READY** (21 cases: 11 positive/6
  negative/4 UNKNOWN/2 MERGE/0 conflict); **A/B/C = ALL READY** (same task/material/GT/judgment options;
  C claim=CANDIDATE 非 conclusion; 0 answer leak; candidate wording 非 assertion); **UNKNOWN preserved**
  (F4 PASS, all 3 workflows allow UNKNOWN); **Negative visible** (C shows 2 negative + 1 positive groups);
  **CONFLICT_COVERAGE=0** (LIMITATION, 非 blocker, 不人为增加); **F1-F7 ALL PASS** (re-verified this phase);
  **Provenance=1.0** (21/21, Level 4 recoverable); **Recording READY** (case_id+workflow+decision+time;
  optional difficulty+confidence; workload proxy ≠ cognitive_load); **BLOCKER_COUNT=0**; **8 LIMITATIONS**
  (L1 GT imbalance 19:2 / L2 conflict=0 / L3 automation bias 0 System≠GT / L4 positive all KS / L5 n=21
  pilot / L6 learning effect counterbalanced / L7 cross-document NO / L8 harness not yet written) — all
  non-blocking; **5 FUTURE QUESTIONS** (cross-document/large-scale/production/pattern lifecycle/capability
  auto-registration) — not addressed; **ARTIFACT_BOUNDARY**: PRODUCTION=FALSE, 0 production mods,
  FROZEN_BASELINE=INTACT (drift=0), L5.5 tmp/ only (0 outside imports); **ANTI_OVERDESIGN**: NEW_PRIMITIVE=0
  / NEW_CONTRACT=0 / NEW_ARCHITECTURE=0 / NEW_DESIGN=0 (no L5.8.1/8.2, no Pattern Engine/Registry/Miner/
  Classifier, no new layers); **PILOT_SCOPE = LIMITED/EXPLORATORY**; L5 Architecture=CLOSED;
  EXPERIMENT_AUTHORIZATION=NOT AUTHORIZED (需单独授权); NEXT=HUMAN EXPERIMENT AUTHORIZATION → Pilot
  Execution → Real Human Evidence; 不自行执行 Pilot; STOP=TRUE。

## 24. L5.7 Pilot Harness — Execution Preparation (HARNESS-READY, tmp/ only)
- **Pilot harness** | ISOLATED (tmp/ only) | `tmp/l5_7_experiment_harness.py` (19.9 KB) + `tmp/l5_7_pilot_
  materials.json` (50.7 KB) + `tmp/l5_7_pilot_recording_schema.json` (2.3 KB) + `tmp/l5_7_pilot_harness_
  preparation_report.md` | **HARNESS-READY**; 完成 L5.8 L8 (harness not yet written); 从 frozen L5.5 输出
  生成 A/B/C presentation materials (A=21 per-instance / B=3 per-group-all-members / C=3 per-claim-
  compressed); **Material Validation ALL 7 PASS** (same judgment options / C no answer leak / C claim=
  candidate / B shows all members / C Level 4 recoverable / C shows negative); **Recording Schema** 定义
  (required: participant_id+item_id+workflow+decision+time; optional: difficulty+confidence+expansion_count+
  levels_viewed+behavioral_notes); **Behavioral Indicators**: ABSTRACTION_BEHAVIOR / REVISIT_BEHAVIOR /
  EXPANSION_BEHAVIOR; **Progressive Disclosure** (C: Level 0 claim+summary → Level 2 member_refs → Level 3
  boundary/negative/UNKNOWN → Level 4 full provenance; track expansion_count); **Workload Proxy 警告**:
  review_count/evidence_exposure/interaction_count ≠ cognitive_load; true burden = time+difficulty+
  abstraction_burden+task_behavior; **NO HUMAN JUDGMENTS** (不模拟 Human, 不产生合成结果, 不伪造证据);
  Latin square counterbalancing (A→B→C / B→C→A / C→A→B); 允许 C 失败 (不修改 Aggregation/Compression/UI/
  Claim 来"修到 C 成功"); FROZEN_BASELINE=INTACT (drift=0, 0 production mods, L5.5 not modified);
  NEXT: Human Experiment Authorization → recruit participants (n=3-5) → build UI → consent/ethics →
  execute → record → analyze 4 layers → real human evidence (A-class); 不自行执行; STOP=TRUE。

## 25. L5 Human Experiment Authorization Preparation (READY, 全部执行条件就绪)
- **Authorization preparation** | PREPARATION ONLY (no execution, no simulation, no fabricated data) |
  `tmp/l5_human_experiment_authorization_preparation.{md,json}` + `tmp/l5_7_pilot_ui.html` |
  **HUMAN_EXPERIMENT_PREPARATION = READY**; 把真实 Human Pilot 执行条件准备完整;
  **Protocol READY** (RQ-L5.7 + 非方向性 hypothesis H0/H1/H2/H3 全允许 + participants n=3-5 exploratory +
  A/B/C frozen + materials frozen + judgment KEEP_SEPARATE/MERGE/UNKNOWN + Latin square + timing + recording +
  stopping + 8 limitations); **A/B/C Fairness PASS** (same task/material/GT/options; C claim=CANDIDATE;
  0 answer leak; UI no recommend/score/predict); **UI READY** (`tmp/l5_7_pilot_ui.html` 45.8KB standalone
  HTML, no server; display+record decision/time/difficulty/confidence/expansion; GT stripped; NO answer/
  recommend/rank/score/predict); **Recording READY** (schema L5.7_v1; required+optional+behavioral;
  JSON download per participant); **Counterbalancing READY** (Latin square 3 orders auto-assigned);
  **Privacy READY** (anonymous P01/P02; no personal data; offline; no cloud); **Consent TEMPLATE READY**
  (ethics/IRB = institutional requirement identified); **Observation Plan READY** (4-layer: operational/
  cognitive-behavior/quality/reusability; H1-H4 cognitive type; N→claims→work); **Failure Rules READY**
  (C failure allowed; BURDEN_TRANSFER=OBSERVED if count↓ but time/abstraction/exposure↑; 不修改 to "fix";
  quality caution: GT 19:2 → "no material degradation" 非 "C improves accuracy"); **3 BLOCKERS** (全
  authorization-related 非 design/technical: B1 ethics/IRB + B2 recruitment + B3 execution);
  **SIMULATED_HUMAN_DATA=0 / FABRICATED_HUMAN_DATA=0**; L5 Architecture=CLOSED; NEW_PRIMITIVE/CONTRACT/
  ARCHITECTURE/DESIGN=0; FROZEN_BASELINE=INTACT (drift=0, 0 prod mods, L5.5 unchanged);
  EXPERIMENT_AUTHORIZATION=NOT AUTHORIZED; NEXT: Human Experiment Authorization → Ethics/IRB → Recruit →
  Consent → Execute via UI → Collect → Score vs GT → Analyze 4 layers → Real Human Evidence (A-class);
  不执行不模拟不伪造; STOP=TRUE。
