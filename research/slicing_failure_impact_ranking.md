# DICE — Slicing Failure Impact Ranking

> 阶段: ANALYSIS ONLY / NO IMPLEMENTATION。零代码、零阈值、零 predicate、零实验、零 GT 修改。
> 唯一问题: **如果只有一次修复机会, 哪个真实 failure mechanism 最有可能让 DICE 的
> slicing / Evidence Quality 真正变好?**
> 数据源 (全部既有, 未修改): 45-case human GT (2 MERGE / 43 KEEP) ·
> failure_case_independence_audit · document_perception_failure_analysis (CC-01..06,
> 显微镜实测) · IS-11 machine evaluation (A/B/C 三条件, G7 FAIL/G8 PASS) ·
> PH-02 replay (REJECTED) · PH-02 failure mechanism review · PH3 incident log。
> 证据标签: OBSERVED (artifact 实测) / INFERRED / NOT YET QUANTIFIED。

---

## 1. 基线继承 (不变)

PH02=REJECTED · C2=REQUIRES_REDESIGN · CORPUS_LIMITATION=CONFIRMED ·
POSITIVE_COVERAGE=INSUFFICIENT · IMPLEMENTATION/EXPERIMENT=NOT_AUTHORIZED ·
GT/层/production 修改=NONE · FROZEN_BASELINE=INTACT · PRODUCTION=FALSE · STOP=TRUE。

## 2. 关键事实基座 (全部 OBSERVED)

1. **当前自动决策的真实错误面 = 3 例**: Baseline B 自动决策 19/45 (18 TN + 1 FP);
   FP = IS11-AMB-135 (eff p5, "4"+"MBConv6, k5x5" 误 MERGE → cell 证据污染);
   2 例 GT=MERGE (med_001 图注) 落入 ABSTAIN → 图注 label↔continuation 停留碎片。
2. **弃权质量**: 26 例 ABSTAIN 中 24 例 GT=KEEP (弃权/保守默认正确), 2 例 GT=MERGE
   (真实碎片错误)。⇒ 弃权对 KEEP 类是安全的, 对 MERGE 类是唯一缺口。
3. **IS-11 通道证明**: 当 table_line_detector 检测到表格时, cell-context 证据
   **8/8 全部正确解析** (ΔCoverage +17.8%); 但检测覆盖率仅 13/45 (28.9%) —
   **5 例 efficientnet p5-p8 矢量表格完全未被检测** (含 FP 所在的 p5!), 3 例 cs_001
   bbox 落在检测 cell 外, 10 例 med_001 本无表格。
4. **失败重复性 (独立性审计修正口径)**: TCC 26 例 = 3 docs / 10 页设置 / top1 doc 57% /
   HHI 0.421 (DOCUMENT-CONCENTRATED, 非 corpus-wide); HEADER 7 = 3 docs / 6 页;
   CAPTION 2 = 1 doc × 2 页 (Phase 3 独立证据同样单文档集中 96.2% GraphCast);
   TICK 3 = 1 doc × 1 页; PROSE 4 = 3 docs / 4 页; med_001 抽样加权 1.86×。
5. **PH-02 教训**: 判据侧 (column-membership whole-group) 15 组预注册参数全部失败,
   WHOLE_GROUP_AS_RESEARCH_OBJECT = INVALID; C2 = REQUIRES_REDESIGN 且被正例覆盖阻塞。
   ⇒ **裁决规则路线已穷尽; 证据可用性路线未动过。**

## 3. Failure Mechanism 抽象 (§六 — 每个机制可回溯到具体 case)

| ID | Mechanism (感知环节) | 可回溯 case | case_count | doc_count | page_count | unique_settings | cross_doc_support |
|----|---------------------|------------|-----------:|----------:|-----------:|----------------:|-------------------|
| M-B | **表格区域证据不可用** (table-region evidence unavailability — 矢量表格在区域检测面失效, cell-context 通道无输入) | 5 eff abstains (p5-p8) + IS11-AMB-135 (FP) DIRECT; 3 cs_001 (bbox 外) INDIRECT | 6 DIRECT + 3 INDIRECT | 2-3 | ≥6 | ≥6 (页级) | in-frame 2-3 docs; 通道正确性 8/8 跨 3 docs |
| M-A | **空间关联断裂** (caption label↔continuation 关联证据缺失; P4 冻结 8pt < 真实间距 10.5-18.1pt) | CC-01a/b (med p20/p24) | 2 DIRECT (+Phase 3 prevalence 6.08%, 79/1299, 跨框架) | 1 | 2 | 2 | 单文档集中 (两个独立观测一致) |
| M-C | **列成员裁决失败** (numeric 列成员 vs 同行 cell 不可分) | IS11-AMB-135 | 1 | 1 | 1 | 1 | 1 doc (TCC 26 例同构但 GT=KEEP 默认安全) |
| M-D | **页眉污染** (页顶重复短行进入表格/正文结构证据) | 45-pool 0 例; PH3 incident-2 (30/54 in_table FP) + 显微镜 p6 | 0 in-frame / 30 cross-frame | 0 / 1(PH3) | — | — | 唯一跨语料机制, in-frame 频率 NOT YET QUANTIFIED |
| M-I | **表头角色无证据** (header vs data 不可分) | TABLE_HEADER 7 例 | 7 | 3 | 6 | 6 | 3 docs (HHI 0.429) |
| M-F | **散文句界无覆盖** | PROSE 4 例 | 4 | 3 | 4 | 4 | 3 docs (n 小) |
| M-H | **刻度/网格角色混淆** | FIGURE_AXIS_TICK 3 | 3 | 1 | 1 | 1 | 1 doc (med 加权 1.86×) |
| M-E | **列盲 band 推理** (band×列未联合) | CC-04 (eff p5, CC-02 同根因) | 0 独立 (1 机制实例) | 1 | 1 | — | 1 doc, 频率 NOT YET QUANTIFIED |
| M-G | **跨页连续性** | 无案例 (CC-06 空白) | 0 | 0 | — | — | 无 |

## 4. 六维评分 (§七 — 不求和定 winner, 逐维解释)

| ID | A Frequency | B Independence | C Slicing Impact | D Evidence Avail. | E Experimentability | F Regression Risk |
|----|------------|----------------|------------------|-------------------|---------------------|-------------------|
| **M-B** | 9/45 可回溯 (6 DIRECT) | **2-3 docs / ≥6 页设置** | **FP=3 (证据污染) + 弃权→有据决策=2** | 2 (通道 8/8 已证; 盲页可表达性待显微镜验证 → 附条件) | **2** (GT 重放 + 逐案预测表, 基建现成) | 1 (KEEP 单向抑制; 风险=伪区域) |
| M-A | 2/45 (+跨框架 6.08%) | 1 doc × 2 页 (两观测同判单文档集中) | **3** (重要内容被拆: 图注语境丢失) | **2** (双案例显微镜实测完整) | 2 (需预注册负例集) | 1 (过关联) |
| M-C | 1/45 | 1 doc | 3 | 2 (显微镜完整) | 2 — **但预注册路线已跑且 REJECTED** | 2 |
| M-D | 0 in-frame (30 cross-frame) | 跨语料 (分母不同, 已披露) | 2-3 (PH3 frame) | 2 | 2 (incident 重放 + 负例) | 1 |
| M-I | 7/45 | 3 docs / 6 页 | 1 (GT=KEEP, 默认已对) | 2 | 2 | 0-1 |
| M-F | 4/45 | 3 docs / 4 页 | 1 | 1 (IS-10 冻结 HUMAN_OWNED) | 1 | 0 |
| M-H | 3/45 | 1 doc × 1 页 | 0-1 | 2 | 2 | 0 |
| M-E | 0 独立 | 1 doc | UNCERTAIN (风险乘数) | 2 | 1 | 1 |
| M-G | 0 | 无 | 未知 | 1 | 0 | — |

## 5. EXPECTED_CASE_IMPACT (§八 — DIRECT/INDIRECT/UNCERTAIN 严格区分)

| ID | DIRECT | INDIRECT | UNCERTAIN | 修复后是否改变 slicing output? (§十) |
|----|-------:|---------:|----------:|--------------------------------------|
| **M-B** | **6** (IS11-AMB-135 FP→TN + 5 eff abstains→有据 KEEP) | 3 (cs_001 bbox 外, 亚机制不同) | med_001 10 例 (无表格, 不适用) | **YES** — 消唯一真实 FP + 5 例弃权变有据正确决策 |
| M-A | **2** (2 例 GT=MERGE 弃权→正确 MERGE, 碎片消除) | Phase 3 框架 ~79 (跨框架, 不计入) | 0 | **YES** — 唯一 MERGE 类缺口修复 |
| M-C | 1 (同一 FP) | 0 | 0 | YES 但**路线已穷尽** (15 组预注册全败; C2' 被 coverage 阻塞) |
| M-D | 0 (in-frame) | 0 | 30 (PH3 frame, 分母不同) | 当前量化 frame 内 **NO**; PH3 frame 内 YES |
| M-I | 0 | 7 (证据质量精化) | 0 | **NO** (GT=KEEP, 弃权默认已正确) |
| M-F | 0 | 4 (弃权→有据) | 0 | 弱 YES (n=4, IS-10 冻结约束) |
| M-H | 0 | 3 | 0 | NO (KEEP 默认已对) |
| M-E | 0 | 0 | 全部 | UNCERTAIN |
| M-G | 0 | 0 | 全部 | 未知 |

## 6. Patch Accumulation 检查 (§十二)

| ID | PATCH_ACCUMULATION_RISK | 依据 |
|----|-------------------------|------|
| M-C | **HIGH** | C2 审查实证: 3/5 判据弱根基 (M3 冗余/M4 negative-driven/M5 case-motivated); 继续加判据 = 规则补丁堆积 |
| M-B | **LOW-MEDIUM** | 决策规则已被 IS-11 冻结证明 (different_cell→KEEP 单向); 缺的只是区域可用性; 若区域划定依赖 frozen 列/对齐结构则原理性, 若滑向启发式则升 MEDIUM |
| M-A | LOW-MEDIUM | 需 graphic-zone 区分; 若靠词法 "FIG N:" 列表化则升 HIGH (词法必须留 hypothesis 侧) |
| M-D | MEDIUM | 页顶位置阈值 + 形态词法易特例化 |
| 其余 | LOW | 影响面小 |

## 7. 排名表 (§十四)

| Rank | Failure Mechanism | Cases | Docs | Pages | Unique Settings | Slicing Impact | Evidence | Experimentability | Regression Risk | Expected Direct Impact | Verdict |
|------|-------------------|------:|-----:|------:|----------------:|----------------|----------|--------------------|-----------------|------------------------|---------|
| 1 | **M-B 表格区域证据不可用 (矢量表格盲区)** | 6D+3I | 2-3 | ≥6 | ≥6 | 3 | 2 (附条件) | 2 | 1 | **6 DIRECT** | **HIGH_PRIORITY** |
| 2 | M-A Caption 空间关联断裂 | 2D | 1 | 2 | 2 | 3 | 2 | 2 | 1 | 2 DIRECT | MEDIUM_PRIORITY |
| 3 | M-D 页眉污染 | 0 in-frame | 0 (1 PH3) | — | — | 2-3 (PH3) | 2 | 2 | 1 | 0 in-frame | MEDIUM_PRIORITY |
| 4 | M-F 散文句界 | 4 | 3 | 4 | 4 | 1 | 1 | 1 | 0 | 0 | LOW_PRIORITY |
| 5 | M-I 表头角色 | 7 | 3 | 6 | 6 | 1 | 2 | 2 | 0-1 | 0 | LOW_PRIORITY |
| 6 | M-H 刻度/网格角色 | 3 | 1 | 1 | 1 | 0-1 | 2 | 2 | 0 | 0 | LOW_PRIORITY |
| 7 | M-E 列盲 band | 0 独立 | 1 | 1 | — | UNCERTAIN | 2 | 1 | 1 | 0 | INSUFFICIENT_EVIDENCE |
| 8 | M-C 列成员裁决 | 1 | 1 | 1 | 1 | 3 | 2 | 2 (路线已穷尽) | 2 (patch HIGH) | 1 (经 M-B 可达) | LOW_PRIORITY |
| 9 | M-G 跨页连续 | 0 | 0 | — | — | 未知 | 1 | 0 | — | 0 | INSUFFICIENT_EVIDENCE |

## 8. TOP 3 (§十五)

### TOP 1 — M-B: 表格区域证据不可用 (矢量表格盲区)

**WHY_THIS_ONE**: 它是唯一同时满足以下全部条件的机制:
(a) **消除当前唯一真实 FP** (IS11-AMB-135) — 注意: 该 FP 的可修路径不是已被 REJECTED 的
PH-02 判据路线, 而是证据可用性路线 (p5 表格被检测 → IS-11 different_cell → KEEP);
(b) **把已证明 8/8 正确的 cell-context 通道扩展到盲页** — 通道正确性已由 IS-11 实验
在 3 文档上背书, 缺的只是输入; (c) **DIRECT 影响 6 例** = 全部机制中最大;
(d) 跨 2-3 文档 ≥6 页设置, 机制重复性有实测背书; (e) 全部用冻结证据, GT 重放基建
现成, 逐案可证伪; (f) KEEP 单向抑制 → regression 面小; (g) 不需要被 REJECTED 的
whole-group research object, 不与 C2' 阻塞纠缠。相比之下: C2/PH-02 攻裁决规则
(已败+阻塞), M-A 只有 2 例且单文档集中, M-D 在当前 frame 内改变 0 个输出。

**WHAT_WOULD_HAVE_TO_BE_TRUE** (下一阶段验证前必须成立的事实):
1. efficientnet p5-p8 与 cs_001 相关页的矢量表格结构**确实可由冻结 P2/P5 事实**
   (对齐组 / 列组 / GAP_SEQUENCE / band) 划出区域 — 尚未显微镜验证 (当前唯一缺口);
2. 基于冻结事实的区域证据在已检测表格的 8 例上**复现 IS-11 的 8/8 正确** (无回归);
3. 在新覆盖页上, 5 例 eff abstain 的判定与 GT (全 KEEP) 一致;
4. IS11-AMB-135 在新区域证据下 in_table=True ∧ different_cell (GT=KEEP), 且不翻转
   任何已正确 case;
5. 2 例 caption MERGE case 不被误纳入表格区域 (无 over-region 回归)。

### TOP 2 — M-A: Caption 空间关联断裂
2 例真实碎片错误 (45 案例中仅有的 GT=MERGE), 双案例显微镜证据完整, 修复即改变
slicing output; 但单文档集中 (两次独立观测同判), 作为 corpus 级优先级受限
(独立性审计已降 MEDIUM)。是 MERGE 类证据的**唯一**修复路径, 与 TOP 1 无竞争
(med_001 无表格, 两机制作用面不相交)。

### TOP 3 — M-D: 页眉污染
唯一拥有跨语料证据的机制 (PH3: 30/54 in_table FP), 模板级泛化论证最强; 但在当前
45-case 量化 frame 内 **0 例 → 修复不改变任何现有 slicing output** (§十 纪律),
且频率 NOT YET QUANTIFIED。进入前列的条件: 先把 PH3 frame 的 chunk 级影响量化。

## 9. Q1–Q12 (§十八)

- **Q1** 真正影响 slicing 的机制: M-B (1 FP 污染 + 5 弃权无据), M-A (2 碎片)。
  即当前自动错误面 3 例的全部来源。
- **Q2** 仅 perception 异常、对 slicing 影响有限: M-I (header, GT=KEEP 默认已对),
  M-H (ticks), M-F (IS-10 冻结, n=4), M-E (风险乘数, 无独立案例)。
- **Q3** 最大 DIRECT IMPACT: **M-B (6 DIRECT)**。
- **Q4** 最好 cross-document support: **M-B** (in-frame 2-3 docs / ≥6 页设置, 且通道
  正确性跨 3 docs 8/8); M-D 的跨语料证据泛化性最强但 in-frame 为 0 (分母差异已披露)。
- **Q5** frozen evidence 最充分: M-A 与 M-C (双案例/单案例显微镜实测完整); M-B 的
  通道已证但盲页可表达性**待验证** (唯一前置缺口)。
- **Q6** 最容易做 falsifiable experiment: **M-B** (45-case GT 重放基建现成 + 逐案
  预测表 + 已证通道对照); M-A 次之 (需先预注册负例集)。
- **Q7** regression risk 最低: 全表内 M-F/M-H (0), 但影响也最小; TOP 3 内 **M-B ≈
  M-A (各 1) < M-D**, M-B 略优 (KEEP 单向 vs M-A 引入 MERGE 关联风险)。
- **Q8** 最大 patch accumulation risk: **M-C** (C2 实证 3/5 弱根基, 15 组全败)。
- **Q9** TOP 1 = **M-B 表格区域证据不可用**。
- **Q10** 为什么比 PH-02/C2 更值得: PH-02/C2 攻"裁决规则"且已失败 (15 组预注册全败,
  whole-group 对象判 INVALID) 并被正例覆盖阻塞; M-B 攻"证据可用性" — (a) 同一个 FP
  可经已证 8/8 的通道到达, 不需要失败的 research object; (b) DIRECT 6 例 vs 1 例;
  (c) 不与 DESIGN BLOCKED 状态纠缠; (d) 改善的是 Evidence Quality 的可自动裁决面
  (coverage 42.2%→60% 的 IS-11 增量证明该方向有真实回报)。
- **Q11** 修复 TOP 1 可改善的已有 cases: IS11-AMB-135 (FP→正确 KEEP); 5 例
  efficientnet p5-p8 abstains (→有据 KEEP); 3 例 cs_001 (INDIRECT, 亚机制不同);
  Evidence Quality 面全部 TCC/HEADER 类案例在盲页获得 cell-context 通道。
- **Q12** **RESEARCH_HYPOTHESIS = NOT_READY** — 机制选择证据已足 (本文档), 但 TOP 1
  的可表达性前提 (WHAT_WOULD_HAVE_TO_BE_TRUE #1: 冻结 P2/P5 事实能否在 eff p6-p8 与
  cs_001 盲页划出表格区域) 尚未显微镜验证。该验证是只读操作, 属下一阶段前置;
  在其完成前不自行设计 hypothesis。

## 10. 最终 Gate (§十九)

```text
╔══════════════════════════════════════════════════════════════════╗
║  ANALYSIS = COMPLETE                                             ║
║  HIGH_LEVERAGE_CANDIDATE = M-B (表格区域证据不可用)               ║
║  TOP_3 = M-B > M-A > M-D                                         ║
║  RESEARCH_HYPOTHESIS = NOT_READY (待盲页可表达性只读验证)          ║
║                                                                  ║
║  IMPLEMENTATION = NOT AUTHORIZED                                 ║
║  EXPERIMENT = NOT AUTHORIZED                                     ║
║  GT_MODIFICATION = NONE                                          ║
║  ATOMIC_OBSERVATION_MODIFICATION = NONE                          ║
║  PERCEPTION_PRODUCTION_MODIFICATION = NONE                       ║
║  FROZEN_BASELINE = INTACT                                        ║
║  PRODUCTION = FALSE                                              ║
║  NO_NEW_PREDICATE / NO_THRESHOLD / NO_CODE                       ║
║  STOP = TRUE                                                     ║
╚══════════════════════════════════════════════════════════════════╝
```
