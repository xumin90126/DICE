# Candidate Column Segment — Independent Structural Corpus Acquisition & GT Expansion

> 阶段: Independent Structural Corpus Acquisition (READ / ENUMERATE / CLASSIFY /
> ADJUDICATE / AUDIT / REPORT)。零实现、零实验、零调参、零历史 GT/冻结修改。
> 新增文件仅本文档、配套 JSON 与只读脚本 `tmp/corpus_acquisition/scan_new_corpus.py`
> (+ 已下载 4 份公开 arXiv PDF 于 `tmp/corpus_acquisition/corpus/`)。
> 基线状态原样继承, 不变。

---

## 0. 基线继承 (不变)

PH02=REJECTED · PH02B=NOT_AUTHORIZED · C2=REQUIRES_REDESIGN ·
DESIGN_STATUS=INSUFFICIENT_COVERAGE · IMPLEMENTATION/EXPERIMENT=NOT_AUTHORIZED ·
GT/层/production 修改=NONE · FROZEN_BASELINE=INTACT · GT_CONFIRMED_POSITIVE=1 ·
POSITIVE_COVERAGE=INSUFFICIENT · CORPUS_LIMITATION=CONFIRMED ·
PREREGISTRATION=NOT_READY · NEW_HYPOTHESIS=DESIGN_BLOCKED · STOP=TRUE。

## 1. Corpus Acquisition (§三/§四)

采集标准 (声明于扫描前): 表格密集 + 模板/venue/年代多样 + 与现有 4-doc corpus 独立。
来源: 公开 arXiv PDF (curl 下载, 记录 URL+sha256)。

| document_id | 来源 | pages | 扫描页 | clusters | document_family |
|-------------|------|------:|-------:|---------:|-----------------|
| T5 (1910.10683) | arxiv.org/pdf/1910.10683 | 67 | **10** ⚠ | 3 | UNKNOWN (JMLR-style) |
| LLaMA (2302.13971) | arxiv.org/pdf/2302.13971 | 27 | 27 | 74 | UNKNOWN (Meta single-col) |
| BERT (1810.04805) | arxiv.org/pdf/1810.04805 | 16 | 16 | 37 | UNKNOWN (NAACL) |
| MMLU (2009.03300) | arxiv.org/pdf/2009.03300 | 27 | 27 | 17 | UNKNOWN (arXiv) |

⚠ **T5 扫描限制**: 仅前 10/67 页 — 附录大表页 (P2 全配对在密集页上内存爆炸 2.5GB+
CPU thrashing) 无法在本环境用冻结层完成扫描。这是**工具/环境限制**, 非发现; 附录
表区可能含未观测的 table-index 结构, 记为未覆盖。document_family 全部 UNKNOWN
(无 publisher metadata, 不猜)。

采集未成功: 2005.14165 (GPT-3)、2106.09685 (LoRA) 下载超时/中断 (arXiv 限流),
不计入。本轮实际新增 **4 文档 / 80 扫描页 / 131 簇**。

## 2. Candidate Discovery 协议 (§五)

instrument 与前序阶段**完全相同** (未重调, 候选生成零语义启发式):
数值词法 (INT/DEC) + x0 单链聚类 (冻结 2.0pt) + ≥3 成员。语义裁决在枚举后人工进行。
**禁止并已遵守**: "1,2,3,4,5 ⇒ positive" 词法捷径。

## 3. 裁决分类 (§六, 13 类体系)

131 簇裁决分布 (MANUAL_ADJUDICATION + basis, 逐簇存 JSON):

| family | n | 说明 |
|--------|--:|------|
| VALUE_COLUMN | 78 | 数值/百分比数据列 (benchmark 结果表主导) |
| MIXED_ARTIFACT | 30 | 跨结构混合 |
| DIGIT_GRID | 7 | 图示数字网格 |
| AXIS_TICK | 7 | 单调刻度 (BERT p16, LLaMA p8, MMLU p2/7/14) |
| OTHER_INT_STRUCT | 7 | 图内标注/重复维值 (BERT p9 '768×4') |
| **NUMBERED_LIST** | **2** | **本轮新发现边界族**: CODE_LINE_NUMBER (见 §4) |
| REFERENCE_NUMBER / TOC_NUMBER / PAGE_NUMBER | 0 | 本轮未触发 (这些 ML 论文的文献/目录编号未形成 ≥3 成员 x0 对齐簇) |
| ROW_INDEX_LIKE | **0** | **无新表格行号列** |

## 4. 关键发现: CODE_LINE_NUMBER (新边界族, §八 near-miss)

- **LLaMA p19 x0=87.2**: '1 2 3 4 5 6 7 8 9', n=9, ratio=**1.0** (均匀 dy), w=4.48, **sib=0**;
  右邻 = Python 代码 token ('def solve(a:float,b:float,c:float):', '"""finds real roots…"""',
  '#discriminant', 'd = b**2-4*a*c', 'if', 'return', 'elif d==0:', 'else')。
- **LLaMA p22 x0=82.7**: '10 11 12', n=3, ratio=1.0, sib=0; 右邻 = JS 代码 ('};', 'request.send()')。
- 同文档同模式 (代码块行号续编) → **SAME_TEMPLATE_REPETITION = 1 unique structural setting**。

**裁决**: NUMBERED_LIST (sublabel CODE_LINE_NUMBER), 非表格行号列。
**对象边界意义**: 该族与行号列**结构高度相似** (左对齐 + 升序连续 + 均匀 dy + 窄宽),
唯一结构区分 = **sib=0 (无兄弟数据列)** → **M4 (grid embedding) 恰好排除之**。
这是对 M4 必要性的**独立佐证** (前序仅孤立刻度一例; 现增代码行号一例, 机制相同:
"孤立对齐数字堆 ≠ 表格列")。归入 near-miss 集 (NM-06), 不得改判 positive。

## 5. Positive 严格判定 (§七)

GT_CONFIRMED_POSITIVE (10 条全满足) 新增 = **0**。
- 唯一升序连续簇 (LLaMA p19/p22) 经人工裁决 = CODE_LINE_NUMBER (右邻代码 token,
  sib=0, 非表格) → 不满足条件 4 (numbered list) 与条件 7 (与 eff p5 结构独立但属不同类)。
- MANUAL_CANDIDATE (row-index-like) 新增 = **0**。
- **GT_CONFIRMED_POSITIVE 维持 = 1** (eff p5, 历史锚定, 未动)。

## 6. Near-Miss / Boundary 集 (§八, 累积)

| id | 结构 | 边界作用 |
|----|------|----------|
| NM-01 | 2309.04040 参考文献编号列 ×9 (前阶段) | M2/M4 排除; 词法捷径封死 |
| NM-02 | 2212.12794 p15 TOC+页码 (前阶段) | 对齐参照决策; M2/M4 排除 |
| NM-03 | med p8 [0,1,2,3,4] 孤立刻度 | M4 排除 |
| NM-04 | eff p5 [2,3] 同页非独立 | 独立性纪律 |
| NM-05 | resnet p6 '21.59' 等距值列 | "等距+对齐+数字 ≠ 行号" |
| **NM-06** | **LLaMA p19/p22 CODE_LINE_NUMBER** (本轮新) | **升序+均匀dy+左对齐仍非行号; M4 (sib=0) 独立排除 — M4 必要性第二佐证** |

边界族现已覆盖 6 类 (reference / TOC / page / tick / value / code-line), 全部由
M2/M4/M5 现行定义排除 — 对象边界**稳定** (无 Stop D)。

## 7. 独立性 (§九)

- LLaMA p19+p22 = 1 unique setting (SAME_TEMPLATE_REPETITION, 不计 2)。
- 全部新增簇 INSTANCE_COUNT=131, UNIQUE_STRUCTURAL_SETTINGS (去重后) ~110+,
  UNIQUE_DOCUMENTS=4 — 但 **positive 独立设置增量 = 0**。
- 累计 (18 文档 / ~413 扫描页): GT_CONFIRMED_POSITIVE_INSTANCE/DOCUMENT/PAGE/
  STRUCTURAL_SETTING_COUNT 全部 = **1**。

## 8. Positive Diversity Matrix (§十, 五维)

| Dimension | 本轮新增 | vs eff p5 |
|-----------|---------|-----------|
| D1 document | +4 (LLaMA/BERT/MMLU/T5) | 正例仍 1 文档 |
| D2 page/layout | +80 页, 含代码块/benchmark表/图 | 正例仍 1 设置 |
| D3 structural config | +1 边界族 (CODE_LINE_NUMBER), +0 正例 | — |
| D4 neighborhood | **新**: 代码 token 右邻 (monospace) | 正例右邻仍 cell-like |
| D5 spacing/alignment | 无新 (CODE_LINE_NUMBER ratio=1.0 同正例) | — |

**STRUCTURALLY_DISTINCT positive vs eff p5: 无** (无新正例)。
POSITIVE_DIVERSITY = **INSUFFICIENT** (维持)。

## 9. Frozen Evidence Sufficiency (§五)

全部新结构 (含 CODE_LINE_NUMBER) 由既有冻结事实 (x0/y/w/词法/兄弟簇/右邻) 完整描述。
**NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE** (维持; 无 Stop C)。

## 10. Q1–Q13 (§十六)

- **Q1** +4 文档 / +80 扫描页 / +131 簇 / +1 新边界族 (CODE_LINE_NUMBER) / +0 正例设置。
- **Q2** 否 — GT_CONFIRMED_POSITIVE 维持 1。
- **Q3** N/A (未增加)。
- **Q4** N/A。
- **Q5** 新对齐模式? 否 (CODE_LINE_NUMBER 同为左对齐升序)。
- **Q6** 新间距模式? 否 (ratio=1.0 同理想行号)。
- **Q7** **新邻接模式? 是** — 代码 token 右邻 (vs eff p5 的 cell-like 表格邻接)。
- **Q8** 新表/版式? 否 (代码块版式新, 但非表)。
- **Q9** 负/边界仍远多于正? **是** (本轮 131:0; 累计 ~840:1)。
- **Q10** 语料限制仍在? **是 — CONFIRMED** (扩至 18 文档 / ~413 页, 正例仍 1)。
- **Q11** 足以进入 Research Object Reassessment? **否** — 正例覆盖仍 INSUFFICIENT。
- **Q12** 缺哪种结构性多样? **表格行号列结构本身**: 左/右/居中对齐变体、多位、稀疏、
  多页、有/无表头、异宽/异距/异邻接 — 在可访问语料中除 eff p5 外**全缺**。
- **Q13** 继续采集还是重设对象? 两条可选: (a) 继续采集**非 ML 表格密集文档**
  (统计/财务/审计/技术手册/零件表 — 这些更可能含 "No./#" 行号列); (b) 若仍无增长,
  重新审视 "candidate column segment → row-number 角色" 是否为正确对象 (正例基础
  本质过薄)。本轮发现 (CODE_LINE_NUMBER 强化 M4) 增加了边界理解, 但**不解除正例阻塞**。

## 11. C2/C2' 含义 (§十一/§十四)

- C2 = REQUIRES_REDESIGN 不变; 本轮**强化 M4 必要性** (第二独立佐证: 代码行号)。
- 未发现 C2' 无法描述的正例 (无 Stop C); 边界稳定 (无 Stop D)。
- 不进入 C2' redesign / preregistration / experiment (§十八 禁止)。

## 12. Coverage Verdict (§十三/§十四)

```text
Stop A 触发: GT_CONFIRMED_POSITIVE 仍 = 1, 无新独立正例设置
Stop D 触发: 新语料产生大量 boundary (CODE_LINE_NUMBER 等), positive 无独立增长

POSITIVE_COVERAGE = INSUFFICIENT (维持)
CORPUS_LIMITATION = CONFIRMED (维持, 范围扩至 18 文档)
PREREGISTRATION = NOT READY
C2 = REQUIRES_REDESIGN
NEW_HYPOTHESIS = DESIGN BLOCKED
```

**研究结论**: 可访问语料 (arXiv ML 论文 + 综述 + 技术报告, 18 文档 ~413 页) 对
"candidate column segment → 行号角色"对象的**正例基础本质过薄** (n=1); 语料被
图形/文献/代码/值列结构主导。边界理解丰富 (6 族, M2/M4/M5 排除面稳), 但正例
独立增长为零。**验证该对象需非 ML 表格密集语料 + 人工 GT** (本轮未获, 因公开
arXiv 限流与非 ML 报告 URL 不可靠)。

## 13. Recommended Next Research Decision

1. **优先**: 申请采集**非 ML 表格密集文档** (政府统计摘要 / 财务审计报告 / 技术手册
   零件表 / 医学检验报告 — 这些含 "No./Item/序号" 行号列的概率高), 并人工裁决建 GT。
2. 若新一轮仍无正例独立增长 → 重审 Research Object 定义 (行号角色可能过窄;
   "structurally coherent candidate column segment" 作为更宽对象或许更可证伪)。
3. **不建议**: 在现有语料继续 predicate/阈值工作 (CORPUS_LIMITATION 已判无验证力)。
4. C2' 纸面重设计可并行 (M4 已双佐证), 但保持 DESIGN BLOCKED。

## 14. Governance Gate (§十八)

```text
╔══════════════════════════════════════════════════════════════════╗
║  PH02 = REJECTED          PH02B = NOT AUTHORIZED                 ║
║  C2 = REQUIRES_REDESIGN                                          ║
║                                                                  ║
║  IMPLEMENTATION = NOT AUTHORIZED                                 ║
║  EXPERIMENT = NOT AUTHORIZED                                     ║
║  GT_HISTORICAL_MODIFICATION = NONE                               ║
║  ATOMIC_OBSERVATION_MODIFICATION = NONE                          ║
║  PERCEPTION_PRODUCTION_MODIFICATION = NONE                       ║
║  FROZEN_BASELINE = INTACT                                        ║
║  PRODUCTION = FALSE                                              ║
║                                                                  ║
║  GT_CONFIRMED_POSITIVE = 1 (Stop A+D)                            ║
║  POSITIVE_COVERAGE = INSUFFICIENT                                ║
║  CORPUS_LIMITATION = CONFIRMED (扩至 18 文档 / ~413 页)           ║
║  PREREGISTRATION = NOT READY                                     ║
║  NEW_HYPOTHESIS = DESIGN BLOCKED                                 ║
║  NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE                      ║
║  NEW_BOUNDARY_FAMILY = CODE_LINE_NUMBER (M4 第二独立佐证)         ║
║  RESEARCH_OBJECT_REASSESSMENT = NOT AUTHORIZED (正例阻塞未解)     ║
║  STOP = TRUE                                                     ║
╚══════════════════════════════════════════════════════════════════╝
```
