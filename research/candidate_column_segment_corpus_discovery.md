# Candidate Column Segment — Independent Corpus Discovery

> 阶段: CORPUS DISCOVERY ONLY (READ / ENUMERATE / CLASSIFY / ADJUDICATE / AUDIT / REPORT)。
> 零实现、零实验、零调参、零 GT/冻结修改; 新增文件仅本文档、配套 JSON 与只读脚本
> `tmp/corpus_discovery/scan_corpus.py`。
> 固定发现协议在扫描前声明 (`scan_corpus.py` 头部), 扫描后未调整。

---

## 1. Corpus Scope (§五)

| 项 | 值 |
|----|-----|
| total_documents_available | **14** PDF (9 in `/tmp/is11_independent_corpus` + 5 in `/tmp/phase3_is14_corpus`); `docs/*.txt` 为非 PDF 规格, 不在本问题枚举范围 |
| documents_in_545_universe | **4** (resnet / efficientnet / med_001 / cs_001; 39 (doc,page) 已在前阶段扫描) |
| documents_outside_545_universe | **10** (eng_001, mat_001, medimg_001, nlp_001, transformer_001, 1602.03837, 1906.11238, 2309.04040, 2205.05897, 2212.12794) |
| pages_available (universe 外) | **426** |
| pages_scanned (本轮) | **294** (≤40pp 文档全扫; >40pp 文档按声明预算 first-20 + 隔页 — 2309: 38, 2205: 72, 2212: 61) |
| pages_scanned (前阶段, universe 内) | 39 |
| 不可枚举文档 | **0** (全部 PDF 可解析; MuPDF color-space 警告为非致命) |
| universe 定义 | 未修改 |

## 2. Independent Structural Setting Definition (§四)

`unique_structural_setting` = (document_id, page, cluster identity (x0 + y-span + 成员集)),
且要求结构模式 (family + 版式角色) 可独立描述。三条纪律:
1. 同页同结构的多个数字 ≠ 多个 setting;
2. 同文档不同 page 是否独立按 layout/结构上下文判断, 不自动计独立;
3. 同一重复模板的跨页实例标记 **SAME_TEMPLATE_REPETITION** (本轮实证: 2309 的
   参考文献编号列在 p10–p51 重复出现 = 同一结构模式, 记 1 个 setting 而非 9 个)。
FAMILY/template 定义不可靠 (无 publisher metadata) → **FAMILY = UNKNOWN**。

## 3. Candidate Enumeration Method (§六)

与设计阶段完全相同的 instrument (未重调): 数值词法 (INT/DEC) + x0 单链聚类
(冻结 2.0pt) + ≥3 数值成员 → 候选段。**候选生成阶段无任何语义启发式**;
语义裁决 (§七) 在枚举之后逐簇人工进行。709 簇 / ~333 累计扫描页。

## 4. Positive Candidates (§八 严格定义)

满足全部 10 条 (局部结构 / 可描述 coherence / 可区分 / 非孤立 tick / 非 VALUE /
非 GRID / 非 MIXED / 非仅"看着像" / setting 可独立 / GT 或 MANUAL 标记) 的结果:

```text
GT_CONFIRMED_POSITIVE = 1 (eff p5 行号列 — 唯一, 继承)
MANUAL_CANDIDATE (row-index-like) = 0
```

新语料中**没有发现任何新的表格行号列结构**。所有"升序连续整数 + 左对齐"的新发现
均属编号列表族 (见 §5 / §7)。

## 5. Near-Miss Structures (§十三 — 边界证据, 不得改判 positive)

| id | 结构 | 为何是 near miss | 对象边界启示 |
|----|------|------------------|--------------|
| NM-01 | **2309.04040 参考文献编号列 ×9** (p1/p10/p17/p39/p41/p45/p47/p51; SAME_TEMPLATE_REPETITION, 1 setting) | 升序连续整数 + 左对齐 + 边距 — "index-like" 的最强形态; 但右邻 = 文献条目文本, dy ratio 2.45-8.59 (M2 排除), 多数 sib=0 (M4 排除); 语义 = 文献编号, 非表格行号 | **C2 的 M2/M4 恰好把编号列表排除在外** — 对象边界必须显式声明 "numbered-list margin numbers 不在 segment 内" (或未来显式纳入) |
| NM-02 | **2212.12794 p15 TOC 章节号列** ('1 2 3 4 5', 右邻 = 章节标题) | 同上; 另发现同页**右对齐页码列** ('18 18 20 23…'@x526.9) — M1-left 参照选择直接决定其可见性 | 对齐参照 (x0/center/x1) 是对象定义的实质决策 |
| NM-03 | med p8 [0,1,2,3,4] 孤立刻度 (继承) | sib=0 | M4 排除面 |
| NM-04 | eff p5 [2,3] 同页非独立 (继承) | n<k + 同页 | 独立性纪律 |
| NM-05 | resnet p6 '21.59' 等距值列 (继承) | GT=KEEP | "等距+对齐+数字 ≠ 行号" |

## 6. Negative Structures (§六/§七)

709 簇裁决分布 (MANUAL_RULE_ASSISTED, 逐族 basis 记录于 JSON):

| family | n | 说明 |
|--------|--:|------|
| OTHER_INT_STRUCT | 206 | 图内标注/杂项整数结构 |
| MIXED_ARTIFACT | 199 | 跨结构混合 (dy 断裂/年代) |
| DIGIT_GRID | 135 | 图示数字网格 (w≤6) |
| VALUE_COLUMN | 131 | 数值/百分比数据列 |
| AXIS_TICK | 29 | 单调刻度列 |
| **INDEX_LIST** | **9** | **本轮新裁决族**: 文献/目录编号列 (NM-01/02) |

文档级簇数: 1602.03837=153, 2212.12794=197, 1906.11238=94, nlp_001=70, mat_001=62,
2205.05897=40, 2309.04040=34, transformer_001=29, eng_001=26, medimg_001=4。

## 7. GT vs Manual Adjudication (§七/§九)

- 所有 label 均为 **MANUAL_ADJUDICATION_LABEL**, 附 adjudication_basis (JSON 逐簇);
- **GT_CONFIRMED = 1** (仅 eff p5, 由 IS11-AMB-135 人类裁决锚定);
- 无任何 manual candidate 被当作 GT; 无 negative 改判 positive;
- 无"为样本量反向调整裁决标准" (协议扫描前冻结)。

## 8. Positive Diversity Matrix (§十/§十四)

| Dimension | Count |
|-----------|------:|
| Documents (扫描) | 14 (10 本轮新扫) |
| Pages (扫描) | ~333 (294 新 + 39 前阶段) |
| Unique structural settings (全部族) | ~数百 (709 簇 → 去 SAME_TEMPLATE_REPETITION 后仍 >100 独立设置) |
| Layout families / patterns | **FAMILY = UNKNOWN** (无可靠 template metadata); 结构族 = 6+ (value/tick/grid/mixed/index-list/row-index) |
| **GT-confirmed positives** | **1** |
| **Manual row-index-like candidates** | **0** |

五维正面多样性:
- D1 跨 document? **否** (GT 正例仅 1 文档; INDEX_LIST 跨 2 文档但非行号);
- D2 跨 page/layout? **否** (正例 1 页 1 设置);
- D3 不同 structural configurations? **否** (行号形态仅 1 种);
- D4 不同 neighbor configurations? **否**;
- D5 不同 spacing/width patterns? **否** (正例单一)。

```text
POSITIVE_DIVERSITY = INSUFFICIENT
```

依据: 结构多样性在**负例/边界族**上丰富 (6 族, 跨 14 文档), 但在**正例**上为零增长;
GT_CONFIRMED 恒为 1, 且新语料结构表明该稀疏性是语料构成的属性 (图表/文献密集型
arxiv 文档), 不是枚举不足。

## 9. Independence Audit (§九)

- eff p5 GT 正例: 独立设置 = 1 (无重复计)。
- INDEX_LIST 9 簇 → SAME_TEMPLATE_REPETITION → 1 个模式设置 (未计为 positive)。
- 无任何"同页重复结构当独立设置"情形。

## 10. Frozen Evidence Sufficiency (§十)

枚举/裁决全程仅用冻结输出 (x0/bbox/center_y/词法文本/兄弟簇)。**未发现任何需要
新观测才能描述的真实结构** — 包括新发现的 INDEX_LIST 族 (其 M2/M4 排除完全可由
既有事实表达)。

```text
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE (维持)
```

## 11. C2 / C2' Implications (§十一/§十七)

1. C2 = REQUIRES_REDESIGN 状态不变; 本轮发现**不放松**该判定 — 反而强化:
   NM-01/02 证明"升序连续整数 + 左对齐"在语料中大量属于编号列表 → 任何 C3 式
   词法捷径 (升序连续整数 ⇒ 行号) 被族级反例封死。
2. C2' 边界新增一条必须显式声明的排除: numbered-list margin numbers
   (由 M2/M4 现行定义自动排除 — 边界目前稳定, 无 Stop D)。
3. 未发现 C2' 无法描述的真实 positive (无 Stop C)。

## 12. Coverage Verdict (§十二/§十六/§十八)

```text
Stop A 触发: GT_CONFIRMED_POSITIVE = 1 且无新 independent setting

POSITIVE_COVERAGE = INSUFFICIENT
CORPUS_LIMITATION = CONFIRMED
PREREGISTRATION = NOT READY
NEW_HYPOTHESIS = DESIGN BLOCKED
```

**CORPUS_LIMITATION 判断**: 当前可用语料 (arxiv ML/物理/化学论文 + 综述 + 技术报告,
~333 扫描页) 对"candidate column segment → 行号角色"研究问题**本质上过薄**:
~333 页仅产出 1 个真实表格行号列设置, 而图形/文献/矩阵结构占绝对主导。该结论
不是枚举失败, 是语料构成属性。**验证该研究问题需要表格密集型新语料
(benchmark/对比表为主的文档) + 人工裁决建立 GT — 这是语料采集任务, 不是
predicate 任务。**

## 13. Recommended Next Research Decision (§十三)

1. **语料采集授权申请** (非本轮范围): 以"表格密集"为采集标准获取新文档, 并对
   row-index-like 结构做人工裁决建立 GT — 这是解开 POSITIVE_COVERAGE 阻塞的
   唯一路径;
2. 在语料扩充前: C2' 重设计 (c2 review 已给出方向) 可作为纸面工作存在, 但保持
   DESIGN BLOCKED;
3. 不建议: 继续在现有语料上做任何 predicate/阈值工作 (已被 CORPUS_LIMITATION
   判定无验证力)。

## 14. Governance Gate (§二十一)

```text
╔══════════════════════════════════════════════════════════════════╗
║  PH02 = REJECTED          PH02B = NOT AUTHORIZED                 ║
║  C2 = REQUIRES_REDESIGN                                          ║
║                                                                  ║
║  IMPLEMENTATION = NOT AUTHORIZED                                 ║
║  EXPERIMENT = NOT AUTHORIZED                                     ║
║  GT_MODIFICATION = NONE                                          ║
║  ATOMIC_OBSERVATION_MODIFICATION = NONE                          ║
║  PERCEPTION_PRODUCTION_MODIFICATION = NONE                       ║
║  FROZEN_BASELINE = INTACT                                        ║
║  PRODUCTION = FALSE                                              ║
║                                                                  ║
║  GT_CONFIRMED_POSITIVE = 1 (无新独立设置 → Stop A)                ║
║  POSITIVE_COVERAGE = INSUFFICIENT                                ║
║  CORPUS_LIMITATION = CONFIRMED                                   ║
║  PREREGISTRATION = NOT READY                                     ║
║  NEW_HYPOTHESIS = DESIGN BLOCKED                                 ║
║  NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE                      ║
║  STOP = TRUE                                                     ║
╚══════════════════════════════════════════════════════════════════╝
```
