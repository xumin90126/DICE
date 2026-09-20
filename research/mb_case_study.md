# M-B Evidence Integration Case Study

> 层 1: DICE Engineering / Research Evidence。完整因果链: PH-02 → C2 → Corpus Discovery →
> Slicing Failure Ranking → M-B Expressability → Phase 2 → 2.1 → 2.2 → 3 → 3.1 → 3.2。
> 保留失败 → 诊断 → 修改研究对象 → 新假设 → 再实验 → 新发现 → 最终结果。过程本身即研究证据。

标注约定: [OBSERVED] 实测 / [INFERRED] 推断 / [HYPOTHESIS] 假设 / [DESIGN] 设计 /
[EXPERIMENTALLY VERIFIED] 实验验证 / [NOT VERIFIED] 未验证。

---

## A. PH-02 为什么失败

**假设 [HYPOTHESIS, rejected]**: frozen `left_alignment_group` geometry 可直接作为
column-membership signal, 通过 whole-group equidistance predicate 修复目标 FP (IS11-AMB-135)。

**预注册 [DESIGN]**: 15 参数组合 × 45 案例, 全矩阵; PASS 条件 A=1/1 (FP 移除) ∧ B=0 (无
正确案例伤害) ∧ C=0 (无 leakage); 任一不满足 = REJECTED, 无事后调参。

**实验 [EXPERIMENTALLY VERIFIED]**:
- **A = 0/1**: 15/15 参数组合下 FP 未被移除 [OBSERVED];
- **7/13 anchors firing**: is01_a=true 的 13 个 anchor 中 7 个在部分组合下 fire — 全部为
  GT=KEEP_SEPARATE 的真实数值列 (fired-unchanged) [OBSERVED] → specificity risk;
- VALUE_COLUMN / prose contamination 等负例在 whole-group 谓词下与正例不可区分 [OBSERVED]。

**诊断 [INFERRED]**:
1. **whole left_alignment_group 被错误当作 research object** — 它是 page-wide 几何对象
   (正文 margin 组 n=15-24, y_ext 293-393pt) 而非局部结构列;
2. **Geometry Fact ≠ Structural Object** — 对齐组成员资格是几何事实, 把它当列成员语义
   = 无契约的语义跃迁;
3. **whole-group aggregation 不成立** — 目标列与正文 margin 共享同一对齐关系, 整组对象
   无法区分二者;
4. **不是 threshold tuning 问题** — 15 组参数空间已穷举, 无任何阈值使 A=1∧B=0∧C=0;
5. **继续 M6/M7/M8 = patch accumulation** — 每加一个谓词只为特定 case 开窗, 不解决
   research-object 错误, 且扩大 specificity 风险。

**PH-02 REJECTED 正式原因**: A=0 (预注册规则 "REJECTED: A=0" 触发); research object
(whole group) 在结构上无法承担 column-membership 语义; 无补救、无事后调参。

## B. C2 为什么没有直接实现

**设计 [DESIGN]**: candidate-column-segment = 更局部化的列段对象, 试图修正 whole-group 错误。

**Coverage audit [EXPERIMENTALLY VERIFIED]**:
- 545-universe coverage audit;
- 138 numeric x0-clusters (候选正例池);
- 137 negative clusters (VALUE_COLUMN / AXIS_TICK / DIGIT_GRID / CODE_LINE / TOC 等);
- **positive GT-confirmed = 1** (eff p5, 历史锚定);
- independent corpus discovery: 709 簇 / 10 文档, 新边界族 INDEX_LIST;
- corpus acquisition: 4 arXiv 文档 / 80 扫描页 / 131 簇, 新边界 CODE_LINE_NUMBER;
- **positive diversity 仍然不足** (GT_CONFIRMED_POSITIVE 维持 = 1, 新增 = 0)。

**诊断 [INFERRED]**:
- C2 = REQUIRES_REDESIGN (M3 降级 POSSIBLY_REDUNDANT; M5 簇级形式自斥唯一正例 → 成员级重构);
- POSITIVE_COVERAGE = INSUFFICIENT;
- 双重阻塞: redesign × coverage, 即使完成 redesign, coverage 仍独立阻塞。

**决策 [DESIGN]**: **没有因 coverage 不足而继续调 predicates**。选择 corpus expansion +
mechanism redesign, 而非 patch accumulation — 因为 positive diversity 不足是 research-object
层面问题, 加谓词不解决。

## C. 为什么转向 M-B

**Slicing Failure Impact Ranking [OBSERVED + INFERRED]**:
- 45-case independence audit → 失败机制排序;
- **M-B (表格区域证据不可用) = TOP1**: 6 DIRECT + 3 INDIRECT; 唯一真实 FP (AMB-135) +
  多例弃权可变有据决策; 通道正确性 8/8 跨 3 docs 已证;
- med_001 10 例无表格 (不适用 M-B)。

**M-B Expressability Audit [EXPERIMENTALLY VERIFIED]**:
- 冻结 geometry evidence **已经存在** (bbox/lag/band/pairwise/共现);
- 盲页与已解析页 Level-1 事实**同类** (correct-vs-blind 反证);
- **主要问题不是 Observation Gap** (drawings 缺席为 documented, 非 Type C 路线承重);
- **主要问题是 Consumer / Integration Gap** — IS-11 消费者接 TLD (chunker 词法启发式),
  从未查询冻结结构事实。

**M-B 定位 [DESIGN]**: M-B **不是** table detector / row-number recognizer / 新 decision rule。
而是: Frozen Geometry Evidence → LSP → RSC → EIC-1 → Existing IS-11 Contract → Existing Decision。

## D. Phase 2.1 / 2.2 的语义边界发现

**Phase 2.1 [DESIGN REVIEW, code-level]**:
- **原始 LSP → different_cell 映射存在 semantic leakage** [OBSERVED at code level]:
  TLD 的 `different_cell` 以"已检测表格"为前提 (table bbox 包含 → 行列索引);
  LSP 差异无 table 前提 → 直接映射 = producer-side semantic upgrade;
- `different_cell` 不能直接由 LSP 发射;
- **EIC-1 成为语义解释边界** (唯一闸门);
- 三案例共存规则 = NEW DECISION POLICY (非既有契约); CONFLICT_CONTRACT_UNRESOLVED;
- caption canary 风险实测为真 → 升级 MANDATORY SAFETY CANARIES。

**Phase 2.2 [DESIGN, PASS]**:
- **LSP = structural object** (authority 止于零语义);
- **RSC = structural evidence** (ceiling: "局部结构组织", ≠ table region);
- **EIC-1 = interpretation candidate** (Cell Context Evidence = B: Semantic Interpretation,
  非 fact 非 capability; `interpretation_status="candidate"`);
- **Human Validation 才是最终语义权威** (reusable pattern 级, 非 instance annotation);
- **conflict = EVIDENCE_CONFLICT** (observable state + provenance), 非 winner/fallback/trust;
- **No Semantic Closure** 成文 (六类禁止跃迁);
- Authority Gradient L0-L6 固定;
- DECISION_POLICY_CHANGE_REQUIRED = FALSE (EIC 是 interpretation contract, 非 decision policy)。

**caption canaries 成为 hard safety canaries 的原因 [OBSERVED + INFERRED]**: caption 行在
纯 Level-2 分区层面与表格行不可区分 (med p20 band 含 4 伪 cell 片段) → Geometry ≠ Table
Semantics → 必须用 canary 作 semantic-boundary regression gate。

## E. Phase 3.1 Localization Gap (独立 research finding)

**发现 [OBSERVED]**: raw `left_alignment_group` 存在 **page-wide margin / caption
contamination** — caption 页 co-structure = 24 重叠分区, cs p3 = 125; 正文 margin 组
(n=15-24, y_ext 293-393pt) 污染每一页。仅靠共结构计数无法区分表格与 caption →
canary 必 FIRE。

**LOCALIZATION GAP [RESEARCH FINDING]**: 区域推导需 localization 约束 (y_ext ≤ bound),
排除 page-wide 整组 → 这正是 PH-02 whole-group 陷阱的结构性复发点。

**参数定值 [DESIGN, preregistered]** (非为让 AMB-135 PASS 事后调出):
- P_min_members = 2; P_min_bands = 3; **P_localization = 150pt**;
  P_min_costructure_band_local = 3; same_y_band = True (frozen)。

**验证 [EXPERIMENTALLY VERIFIED]**:
- canary pair-band LOCAL density = **0** (跨 100/150/200pt bound 全为 0);
- AMB-135 target pair-band density = **30** (远超阈值 3);
- 150pt = 间隙中点 (表格列 32-88pt vs caption/margin 293-393pt; 裕度 62↓/143↑pt);
- P_localization 在 [100,200]pt 全程鲁棒。

**关键**: 承重参数全在 canary 边界侧, 与"让 FP 通过"无关 — AMB-135 修复不依赖参数精调。

## F. Phase 3.2 最终结果

**实验 [EXPERIMENTALLY VERIFIED]** (frozen 21-row matrix + OFF/ON + determinism double-run):

| 指标 | 值 | 判定 |
|---|---|---|
| S1 AMB-135 corrected | MERGE→KEEP_SEPARATE | PASS |
| S2 canary 0 flips | 414/422 ABSTAIN 不变 | **PASS (HARD GATE)** |
| S3 negative collateral | 0 | PASS |
| S4 correct controls | 8/8 unchanged | PASS |
| S5 semantic leakage | 0 (11 admitted, 全 candidate) | PASS |
| S6 decision policy change | 0 (hash 不变 + 行为 10/10) | PASS |
| S7 provenance | 11/11 (1.0) | PASS |
| S8 determinism | 21/21 byte-identical | PASS |
| S9 OFF byte-identical | 21/21 (8 "mismatch" = tuple/list 伪影) | PASS |
| S10 frozen drift | 0 | PASS |

**F1-F10 = 0**。**Recovery**: AMB-135 FP fixed + 6/8 DIRECT recovered + 2/8 honest ABSTAIN
(313 lag=0, 462 lag=1)。**0 unsafe flip**。**0 collateral**。

**五项 Honest Disclosure**:
1. AMB-262 分类修正 (Phase 2/3 标 "different_band", 实际案例对同带 → GT-consistent recovery);
2. OFF tuple/list serialization pseudo-mismatch (归一化后 0 真实差异);
3. natural conflict coverage = 0 (冲突契约未被自然案例行使);
4. AMB-313/462 honest ABSTAIN (分区不可解, 预期);
5. corpus / descriptive-row coverage limitation (LLaMA/2212/axis 专用 PDF 不在可用语料)。

## 完整因果链 (一句话)

PH-02 whole-group 谓词失败 → C2 局部列段 coverage 不足 → 不堆 predicate, 转 corpus +
mechanism redesign → Impact Ranking 定 M-B 为 TOP1 → Expressability Audit 证 evidence
已存在, gap 在 consumer → Phase 2 设计薄 adapter → Phase 2.1 发现 LSP→different_cell
semantic leakage → Phase 2.2 建 EIC-1 语义闸门 → Phase 3 冻结 replay protocol →
Phase 3.1 发现 localization gap 并定值参数 → Phase 3.2 隔离 replay PASS (FP 修复 +
canary 安全 + 0 语义泄漏 + 决策函数不变)。
