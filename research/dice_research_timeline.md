# DICE Research Timeline

> 按 Phase 顺序记录近期重要演进: Failure → Diagnosis → Hypothesis → Experiment →
> Rejection/Pass → Revision → New Evidence → Current State。每步保留 QUESTION / HYPOTHESIS /
> EVIDENCE / DECISION / WHY / NEXT STATE。

标注: [O] observed · [I] inferred · [H] hypothesis · [D] design · [EV] experimentally verified

---

## Phase 0 — 失败分析基础
- **QUESTION**: IS-11 machine eval 的 45 案例真实失败分布是什么? 哪些是独立 failure mechanism?
- **HYPOTHESIS**: 逐案冻结事实可揭示机制边界。
- **EVIDENCE** [O]: 45-case independence audit; TCC 26 例 = 3 docs/10 页; med 抽样加权 1.86×;
  AMB-135 = 唯一 FP; C 弃权 18 (eff3+med8+cs7); 通道 8/8 已证。
- **DECISION**: 建立失败机制排序基础。
- **WHY**: 没有逐案冻结事实, 任何修复都是盲调。
- **NEXT STATE**: 进入 PH-02 假设实验。

## Phase PH-02 — Column-Membership Predicate (REJECTED)
- **QUESTION**: frozen left_alignment_group 能否直接作 column-membership signal 修复 AMB-135?
- **HYPOTHESIS** [H]: whole-group equidistance predicate 可区分 in-column vs not。
- **EVIDENCE** [EV]: 15/15 × 45; A=0/1 (FP 未移除任一组合); 7/13 anchors firing (全 GT=KEEP
  真实数值列 fired-unchanged = specificity risk)。
- **DECISION**: **REJECTED** (预注册规则 A=0, 无补救, 无事后调参)。
- **WHY**: research object (whole group) 在结构上无法承担 column-membership 语义 —
  page-wide margin 组与目标列共享对齐关系; 不是 threshold 问题 (15 组穷举)。
- **NEXT STATE**: research object revision → C2 局部列段。

## Phase C2 — Candidate Column Segment (REQUIRES_REDESIGN)
- **QUESTION**: 更局部化的列段对象能否修正 whole-group 错误?
- **HYPOTHESIS** [H]: candidate-column-segment (成员级) 可提高正例覆盖。
- **EVIDENCE** [EV]: 545-universe; 138 numeric clusters; 137 negative; positive GT-confirmed=1;
  M3 POSSIBLY_REDUNDANT; M5 簇级自斥唯一正例 → 成员级重构。
- **DECISION**: **REQUIRES_REDESIGN** + POSITIVE_COVERAGE=INSUFFICIENT; **不堆 predicate**。
- **WHY**: positive diversity 不足是 research-object 层面问题; 加谓词不解决; 选择
  corpus expansion + mechanism redesign。
- **NEXT STATE**: corpus discovery / acquisition。

## Phase Corpus — Discovery / Acquisition
- **QUESTION**: 独立语料能否提供更多正例多样性?
- **HYPOTHESIS** [H]: 独立 arXiv 语料可发现新 column-segment 结构。
- **EVIDENCE** [O]: discovery 709 簇/10 文档 (新 INDEX_LIST 边界); acquisition 4 文档/80 页/
  131 簇 (新 CODE_LINE_NUMBER 边界 NM-06, M4 第二佐证); **positive 新增 = 0**, GT-confirmed 维持=1。
- **DECISION**: CORPUS_LIMITATION=CONFIRMED; positive diversity 仍不足。
- **WHY**: 正例稀缺是真实结构事实, 非 coverage 调参可解; 继续调 predicate = patch accumulation。
- **NEXT STATE**: slicing failure ranking 重新定位最高价值机制。

## Phase Impact Ranking — M-B = TOP1
- **QUESTION**: 哪个 failure mechanism 价值最高 (可回溯性 × 通道已证 × 修复价值)?
- **HYPOTHESIS** [H]: M-B (表格区域证据不可用) 是 TOP1。
- **EVIDENCE** [I+O]: 6 DIRECT + 3 INDIRECT; 唯一 FP=AMB-135; 通道 8/8 跨 3 docs 已证;
  med 10 例无表 (排除); RESEARCH_HYPOTHESIS=NOT_READY。
- **DECISION**: 转向 M-B; 不继续 C2 predicate。
- **WHY**: M-B 的证据已存在 (通道 8/8 证决策规则正确), 缺的是区域可用性 — 比 PH-02 更接近根因。
- **NEXT STATE**: M-B expressability audit。

## Phase M-B Expressability — EXPRESSIBLE
- **QUESTION**: 冻结 geometry evidence 是否足以表达 vector-table 局部结构?
- **HYPOTHESIS** [H]: 证据已存在, gap 在 consumer。
- **EVIDENCE** [EV]: correct-vs-blind 无 Level-1 差异 (eff p9 lag4 band8 vs cs p3 lag6 band9 同类);
  FP 对 lag10×lag6 same_band h_gap=30.02 完整; p5 表区 12 列簇; drawings 缺席 documented 非承重。
- **DECISION**: **EXPRESSIBLE**; primary gap=Consumer/Integration; NEW_OBSERVATION_REQUEST=NONE。
- **WHY**: 证据在盲页齐全且与已解析页同类; 差异全在 TLD 内部 (chunker 词法启发式)。
- **NEXT STATE**: Phase 2 consumer integration design。

## Phase 2 — Minimal Consumer Integration Design
- **QUESTION**: 最小 consumer integration 是什么?
- **HYPOTHESIS** [H]: 薄 adapter 作第二生产者, 决策函数零改动。
- **EVIDENCE** [D]: 3 设计比较 (A 注入/B adapter/C 并行框架); 选 B; TLD 共存三案例;
  AMB-135 walkthrough; caption canary M3。
- **DECISION**: Design B 推荐; DESIGN-ONLY。
- **WHY**: 决策契约可插拔 (is11_obs dict); TLD 只是一个生产者。
- **NEXT STATE**: Phase 2.1 contract review。

## Phase 2.1 — Integration Contract Review (CONDITIONAL_PASS)
- **QUESTION**: LSP 能否直接产生 different_cell? 共存契约是既有还是新增?
- **HYPOTHESIS** [H, falsified]: adapter 发 is11_obs 形状即复用既有契约。
- **EVIDENCE** [O at code level]: TLD different_cell 以 detected table 为前提 (L140-258);
  LSP 差异无 table 前提 → SEMANTIC_MAPPING_GAP=TRUE; 1 处语义泄漏;
  canonical DIRECT=9 (修正 8); CONFLICT_CONTRACT_UNRESOLVED; canary 事实确认。
- **DECISION**: **CONDITIONAL_PASS**; 3 项最小修正 (C1 移除 is11_obs 形状发射/C2 conflict 契约/C3 显式层级)。
- **WHY**: 主体设计成立, 但语义升级必须封死。
- **NEXT STATE**: Phase 2.2 evidence interpretation contract。

## Phase 2.2 — Evidence Interpretation Contract (PASS)
- **QUESTION**: 能否定义最小、可审计、无语义越权的 EIC?
- **HYPOTHESIS** [H]: EIC 作 interpretation contract (非 decision policy), 决策函数不变。
- **EVIDENCE** [D+O]: EIC-1 十要素; Authority Gradient L0-L6; No Semantic Closure;
  Cell Context=B (interpretation, candidate); 代码证决策函数只读 different_cell/same_cell,
  all-False=既有 "unknown" 约定; DECISION_POLICY_CHANGE_REQUIRED=FALSE; Gate A-O 全满足。
- **DECISION**: **PASS / DESIGN-READY**。
- **WHY**: 语义解释 authority 明确在 EIC-1 (经治理) + L5 人审; 低层不自动升级。
- **NEXT STATE**: Phase 3 replay protocol 冻结。

## Phase 3 — Isolated Replay Design (DESIGN-READY)
- **QUESTION**: 如何在最小隔离测试集上验证 7 项性质?
- **HYPOTHESIS** [H]: 冻结 25 行矩阵 + S1-S10/F1-F10 可证伪。
- **EVIDENCE** [D]: 21 决策行 + 4 描述行; S1-S10 (S2 hard gate); F1-F10;
  patch-accumulation precommitment (禁 M6/M7/M8); scientific claim boundary。
- **DECISION**: **DESIGN-READY**; IMPLEMENTATION/REPLAY = NOT AUTHORIZED。
- **WHY**: 矩阵预固定, 结果无关, 不得事后增删。
- **NEXT STATE**: 参数定值 (用户选择)。

## Phase 3.1 — Preregistration Parameter Fixation (COMPLETE)
- **QUESTION**: EIC-1 区域共组织参数如何定值?
- **HYPOTHESIS** [H]: 承重参数在 canary 边界侧, 非目标侧。
- **EVIDENCE** [EV]: **LOCALIZATION GAP 发现** — raw alignment group page-contaminated
  (caption 页 24 重叠分区); localization 约束 (y_ext≤150pt) 排除 margin 组;
  canary density=0 (跨 100/150/200pt) vs target=30; 150pt=间隙中点鲁棒。
- **DECISION**: **COMPLETE**; MISSING_PARAMETER=0; P_min_mem=2/P_min_bands=3/P_loc=150pt/P_costr=3。
- **WHY**: 参数从冻结测量事实定值, 非从"让 AMB-135 通过"反推; AMB-135 不依赖精调 (density=30≫3)。
- **NEXT STATE**: 实施授权决策 (用户授权)。

## Phase 3.2 — Implementation + Isolated Replay (REPLAY_PASS)
- **QUESTION**: 实施后冻结矩阵能否通过 S1-S10 且 F1-F10=0?
- **HYPOTHESIS** [H]: EIC-1 契约链可修复 FP 且 canary 安全。
- **EVIDENCE** [EV]: S1-S10 ALL PASS; F1-F10=0; AMB-135 MERGE→KEEP (eic1_single_source);
  6/8 DIRECT recovered + 2/8 honest ABSTAIN; 0 unsafe flip; 0 collateral; 8/8 controls;
  0 semantic leakage (11 admitted 全 candidate); provenance 1.0; determinism 21/21;
  OFF byte-identical (21/21, 8 "mismatch"=tuple/list 伪影); 决策函数 hash 不变; frozen drift 0。
- **DECISION**: **REPLAY_PASS**。独立审计与 runner 自报一致。
- **WHY**: 契约链成立; localization 保护 canary; 语义闸门有效; 决策政策不变。
- **NEXT STATE**: STOP = TRUE (不自行进入下一阶段)。

## Current State
- M-B Phase 3.2 = REPLAY_PASS; frozen baseline INTACT; production FALSE; STOP TRUE。
- 科学结论边界: "在当前冻结测试框架中, 验证了该 minimal Consumer Integration 能够处理
  已识别的结构切片失败模式" (GT-confirmed positive=1; mechanism validation ≠ generalization proof)。
