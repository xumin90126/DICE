# P7 Evidence Gap Analysis — Read Only

> 基于 P1–P7.1 全部真实语料结果，确定下一阶段最值得建设的 Observation / Validation 能力。
> 本轮零代码修改、零 heuristic、零实现。所有结论由真实 corpus 数据驱动，不由 PDF parser 功能清单驱动。

**数据来源**：`p7_1_acceptance_baseline.md` / `p7_1_acceptance_metrics.json` / `p7_1_freeze_hashes.json`、`tmp/perception/p1–p7/*`、真实文档只读检测（PyMuPDF get_images/get_drawings/get_fonts）。

---

## 0. 真实语料需求检测（原始证据）

对 6 个真实文档做只读检测，统计 **P1 实际跳过的内容**：

| 文档 | 页数 | 图像页数 | 图像总数 | 矢量页数 | 矢量总数 | 受影响页占比 |
|---|---|---|---|---|---|---|
| RM501（设备手册） | 2 | 2 | 3 | 2 | 44 | 2/2 |
| DC201（设备手册） | 8 | 1 | 1 | 7 | 192 | 7/8 |
| arxiv_2310（CS 论文） | 19 | 10 | **83** | 13 | **963** | **18/19** |
| arxiv_bio（39页） | 39 | 0 | 0 | 39 | 794 | 39/39 |
| arxiv_2401 | 18 | 0 | 0 | 0 | 0 | 0/18 |
| qbio_cell（生物） | 7 | 5 | 7 | 4 | 13 | 6/7 |

**核心事实：6 个文档中 5 个含有被 P1 完全跳过的视觉内容（合计 94 图像 + ~2006 矢量对象）。arxiv_2310 的 19 页中 18 页含被跳过的视觉对象。**

其他真实信号：
- **表格信号**：设备手册页面 SPARSE 区域占比 64%（rm501_p2：9/14）与 67%（dc201_p5：8/12）——表格散点是设备手册的主导版面模式。
- **表格与假阳性相关**：rm501 假阳性 heading 的典型形态是宽 11.1pt 的窄条（bbox [66, 441.65, 77.12, 469.7]，bold + width 11 < 284.8×0.8）——即规格表标签/竖排文字被几何信号误判为 heading 候选。
- **公式信号**：arxiv_2310 含 CMMI10/CMSY10（数学斜体/符号），qbio_cell 含 CMMI9/CMSY7；RM501 纯 ArialMT（零公式内容）。P3 真实数据（rm501_p2，168 条）superscript=0、italic=0。
- **TOC 事实**：arxiv_bio p2 是真实目录页（"Contents"，编号条目+页码，含行内数学 KL→γ∗γ∗）；P7.1 产出 33/90 heading 候选（28 LOW + 5 MEDIUM）。

---

## 一、Evidence Gap Matrix（5 个候选方向逐项评估）

### 1. Visual Object Observation

| 维度 | 评估 |
|---|---|
| 真实语料是否出现该类问题 | **是，最大缺口**：5/6 文档含被跳过的图像/矢量；arxiv_2310 18/19 页受影响 |
| 出现频率/覆盖率 | 94 图像 + ~2006 矢量对象被跳过；视觉对象覆盖率 = **0%**（P1 `if block_type != 0: skip`） |
| P1–P7.1 能否表达 | 不能。P6 只能把视觉对象留下的空隙记录为「大间隙」几何事实（deferred to P7），是死胡同 |
| 失败归属 | **A（upstream observation 不足）**为主 |
| 解锁能力 | Figure/Image/Chart 候选、可靠 Caption（需 object reference）、Table 确认（表格线是矢量）、P6 大间隙事实的解释闭环 |
| 是否污染边界 | 中风险：需扩展冻结的 P1（或建 P1 sibling 层），必须保持「记录 bbox/类型事实，不做识别」 |
| 实现复杂度 | 中（PyMuPDF 已提供 get_images/get_drawings；难点是观察层设计而非提取） |
| Evidence Quality 价值 | **高**：arxiv_2310 类文档 94% 的页面含有当前不可见的证据源 |
| 过早建设风险 | 中：其产出仍需 Human Validation 才能成为 Evidence（见 Priority 1 先行理由） |

### 2. Table Cell Geometry

| 维度 | 评估 |
|---|---|
| 真实语料是否出现该类问题 | **是**：设备手册（DICE 主语料）SPARSE 占比 64–67%，表格散点是主导模式 |
| 出现频率/覆盖率 | rm501_p2 9 个 SPARSE 区域、dc201_p5 8 个；且 rm501 的 21 个 heading 候选中 14 个仅靠「短行+样式对比」，其中含表格标签误报 |
| P1–P7.1 能否表达 | 不能。P2 有对齐组但无 cell 级行列 grid；P7.1 的 possible_table_region 被 BLOCKED |
| 失败归属 | A（upstream 不足）为主；B 次之（散点可观察，cell 不可观察） |
| 解锁能力 | Table/Table Cell 候选、设备手册规格表的结构化、heading 假阳性的相当部分归因 |
| 是否污染边界 | 低风险（P2 扩展方向清晰）但**高误报风险**：仅凭散点无法区分表格/表单/列表——需矢量线证据佐证 |
| 实现复杂度 | 高（行列 grid 重建是 PDF 解析公认的难点） |
| Evidence Quality 价值 | **高**（设备手册是主语料），但依赖 Visual Object 先提供表格线 |
| 过早建设风险 | **高**：没有线证据时建设 cell geometry，会产生大量不可验证的表格假设 |

### 3. Graphic / Vector Observation（Flowchart 方向）

| 维度 | 评估 |
|---|---|
| 真实语料是否出现该类问题 | 部分存在：RM501/DC201/arxiv_bio 有大量矢量对象，但**无证据表明它们是 flowchart**（vs 规则线/装饰/表格线） |
| 出现频率/覆盖率 | 未知——矢量内容 0% 被观察，连「是不是流程图」都无法判断 |
| P1–P7.1 能否表达 | 不能 |
| 失败归属 | A（upstream 不足） |
| 解锁能力 | Flowchart 候选（需 shape/arrow/connectivity） |
| 是否污染边界 | 中 |
| 实现复杂度 | 高（connectivity/箭头语义分析） |
| Evidence Quality 价值 | 不明（当前语料无已证实的 flowchart 需求） |
| 过早建设风险 | **高**：需求未被真实语料证实，且是 Visual Object 的子集工作 |

### 4. Formula Atomic Extension

| 维度 | 评估 |
|---|---|
| 真实语料是否出现该类问题 | 部分：arxiv_2310/qbio 含数学字体（CMMI/CMSY）；RM501/DC201 零公式 |
| 出现频率/覆盖率 | 2/6 文档；P3 真实数据 superscript=0（主语料无公式）；P7.1 无任何可归因于公式缺失的失败 |
| P1–P7.1 能否表达 | 弱：P3 有 superscript 位但 subscript/underline=null、无 baseline 关系、无符号类别 |
| 失败归属 | A（upstream 不足），但当前无失败案例 |
| 解锁能力 | 可靠 Formula 候选、数学内容页的识别 |
| 是否污染边界 | 中（需 character-level 观察扩展） |
| 实现复杂度 | 中高 |
| Evidence Quality 价值 | 中（对 arxiv 类文档有价值，对设备手册主语料无价值） |
| 过早建设风险 | **高**：无失败案例驱动，纯理论需求 |

### 5. Human Validation Infrastructure

| 维度 | 评估 |
|---|---|
| 真实语料是否出现该类问题 | **是，且是当前唯一从未通过的关卡**：175 hypotheses / 0 validated |
| 出现频率/覆盖率 | 100%——每一条 hypothesis 都堵在同一关卡；真实语料 ~10 页已产生 175 条，全语料将产生数千条 |
| P1–P7.1 能否表达 | Schema/Contract 已定义（PROPOSED/PARTIALLY_VALIDATED/VALIDATED/REJECTED；最小审阅单位=hypothesis），但**无基础设施执行** |
| 失败归属 | **C（human validation 必需）**——包括 TOC/表格标签这类被契约排除在自动判定之外的不可判定区 |
| 解锁能力 | 整条链的贯通：Hypothesis→Validated Structure→Evidence Candidate→Evidence；P7.1 置信度校准（无人工判定则无法测量 precision）；未来所有 Observation 的产出有了去向 |
| 是否污染边界 | **最低**：不新增 Observation 层、不修改 P1–P6，纯治理侧建设；只要坚持「Hypothesis 不可变 + Validated Structure 独立对象 + Evidence 需另行治理」即不污染 |
| 实现复杂度 | 中低（P7.1 已携带审阅所需全部字段；缺的是验证记录对象与状态机） |
| Evidence Quality 价值 | **决定性**：没有它，DICE 新感知栈产出的 Evidence 数量为零 |
| 过早建设风险 | 低——175 条真实积压就是需求证明 |

---

## 二、TOC Heading 不可判定性分析（禁止 keyword rule）

**事实**：arxiv_toc_p2 33/90 heading 候选（28 LOW + 5 MEDIUM）；rm501_p2 21/44（含表格标签窄条误报）。

### 1. P1–P6 是否已提供足够事实？
**是——区分性事实存在于 P1 文本中**（arxiv_bio p2 目录条目带编号与尾随页码："2.1 ⏎ Leptonic processes ⏎ 4"），P1 已完整观察到这些文本。几何事实上，P2/P3/P5/P6 也已观察到 TOC 条目的全部几何特征（短行、样式对比、左对齐、双栏行对齐）。

### 2. 那为什么 P7.1 仍然无法可靠区分？
因为**判别性信息是文本模式**（尾随页码、编号前缀、点线），而 P7.1 契约**有意**将 Textual/Symbol Evidence 排除在决策路径之外（防 keyword 分类）。P7.1 可用的 4 类几何/样式信号（style_contrast / spatial_separation / reading_position / short_line）在「目录条目」与「真实标题」上**同真**——几何上它们就是同一类东西。rm501 的表格标签窄条同理：bold + 窄条在几何上与短标题无异。

### 3. 是否存在不应通过 heuristic 解决的不可判定区？
**存在，且这是设计使然，不是缺陷。** 「短+粗+左对齐」→ 标题 的推断在几何层不可判定；用文本模式解决就是 keyword rule（被禁止）。正确处置是承认不可判定区，保持 PROPOSED + LOW，交由 Human Validation。P7.1 目前的行为（33 条候选全部 LOW/PROPOSED，不污染下游）正是契约要求的正确表现。

### 4. 哪些信息只有 Human Validation 才能提供？
- 语义裁定本身：「这个短粗行是目录条目还是标题」
- 验证通过率数据（calibration）：没有人工判定，P7.1 验证计划中的 confidence calibration 无法执行
- 假阳性的**系统性归因**：人工审阅 arxiv_toc 33 条后才能确认「TOC 页 heading 候选≈全部假阳性」这一模式，进而为未来 Textual/Symbol Observation 立项提供证据

### 5. 需要新增 Observation，还是保持 PROPOSED？
**当前保持 PROPOSED。** 未来若建「Textual/Symbol Observation」（把页码模式、点线等做成一等观察事实而非临时规则），须满足：(a) 作为独立观察层立项评审，不进 P7.1 决策路径；(b) 非关键词匹配（如「行尾数字模式」是排版事实，"contains 'Contents'" 是关键词，前者可议后者禁止）。现阶段无此必要——HV 即可解决，且语义裁定本就属 Layer D。

---

## 三、Human Validation 是否已成为瓶颈？

**是，它已是整个链路的实际瓶颈。**

证据链：`Document → Observation → Relation → StructureHypothesis → **Human Validation → Validated Structure → Evidence**`

- 当前 175 hypotheses / **0 validated**：新感知栈产出的 Evidence 数量 = **0**。链路在唯一从未通过的关卡上整体阻塞。
- 这不是「将来会堵」，而是「已经堵死」：P7.1 的 175 条、TOC 的不可判定区、以及未来 Visual/Table 的所有产出，都排同一个队。
- 验证计划的 calibration 指标（置信桶 → 人工通过率单调性）在 0 validated 下无法计算——**没有 HV，连 P7.1 的质量都无法测量**。

### 最小人工审阅单位
StructureHypothesis（契约已定），携带审阅所需全部字段。

### 最值得优先审阅的 hypothesis
1. **arxiv_toc_p2 的 33 条 HEADING_CANDIDATE**（28 LOW）——已知假阳性集中区，批量审阅可快速校准
2. **rm501_p2 的 21 条 HEADING_CANDIDATE**——含表格标签误报，审阅可确认「表格内容混入」模式
3. 两条 HEADER / 两条 FOOTER（合成，LOW）——验证跨页重复判定的可用性
4. PARAGRAPH_GROUP 中 9 条 HIGH——快速确认高置信分组的可靠性

### 字段已足够支持人工判断
hypothesis_type、span_ids（经引用链取文本）、region_ids、geometry.bbox、confidence、decision_trace（含每个信号的数值）、supporting_fact_refs、supporting_relation_ids、construction_method/version。

### 字段仍然缺失
- 结构化 `conflicting_evidence`（目前只在 trace 散文中）
- 字段级验证状态载体（PARTIALLY_VALIDATED 需要逐字段记录，schema 未定义验证记录对象）
- heading_level（有意缺席，属 Layer D）
- 验证记录本身（谁/何时/判定/依据）——**这是真正缺的治理对象**

### Human Validation 后应产生什么新治理对象
**ValidationRecord**（验证记录：reviewer、时间、判定、字段级状态、依据）+ **Validated Structure**（Layer D，独立 ID，引用被验证的 hypothesis_id，hypothesis 本身保持 PROPOSED 不可变）。两者都不等于 Evidence——Evidence 需经独立治理流程（归属/权重/版本/引用链）。

### 如何保持三层不等式
Hypothesis 不可变（审计记录）≠ Validated Structure（人工裁定结果）≠ Evidence（另行治理）。HV 基础设施只做「PROPOSED → 裁定状态」的状态机与记录，不写 Evidence Store，不碰 Annotation/Capability/Runtime。

---

## 四、下一阶段优先级（不实施）

### Priority 0 — 必须保持不变的 Frozen / Blocked 边界
P1–P6 代码与输出、Frozen 730（a10b368e）、Annotation、C1/C2、Evidence Store、Capability、Runtime、registry/bootstrap/capability_loader、P7.1 六个冻结文件（哈希已固化）、BLOCKED_TYPES 清单（Table/Figure/Image/Chart/Flowchart/Formula/Caption/Page-Number/Reference/Footnote）、P7.1 决策路径中禁止文本证据的契约。

> **为什么**：这些是全部结论可审计的前提。任何一项被绕过，本轮分析的数据基础即失效。

### Priority 1 — Human Validation Infrastructure
> **为什么现在做，而不是以后做**：
> 1. 它是链路中唯一从未通过的关卡——0/175 validated 意味着 DICE 新感知栈至今产出 **0 条 Evidence**，整条 Document→Evidence 链仍是理论。任何其他建设（包括 Visual Object）的产出都会堆积在同一条队上。
> 2. 真实语料的不可判定区（TOC 33 条、表格标签 heading）**只有** HV 能解决——契约禁止自动解决。
> 3. 没有 HV，连 P7.1 自身的质量都无法测量（calibration 需人工判定率）。
> 4. 需求已被真实数据证实（175 条积压，~10 页语料），且实现复杂度最低、边界污染风险最小（纯治理侧，不碰任何 Observation 层）。
> 5. 先建闸门，后建产能：Visual/Table 落地时立即有治理去向，而不是制造第二批不可审计积压。

### Priority 2 — Visual Object Observation
> **为什么第二、且为什么现在做**：
> 1. 它是**最大的真实证据缺口**：5/6 文档、94 图像 + ~2006 矢量对象被 P1 完全跳过；arxiv_2310 18/19 页含被跳过的视觉内容。这不是理论需求——是当前语料中规模最大的不可见证据源。
> 2. 解锁最多被 BLOCKED 的候选类型（Figure/Image/Chart + 未来的可靠 Caption），并让 P6 已记录的「大间隙」死胡同事实获得解释闭环。
> 3. **为什么不是第一**：它必须扩展冻结的 P1（边界风险高于 HV），且其产出同样要经 HV 才能成为 Evidence——闸门未建先建产能，只会扩大不可审计积压。
> 4. **为什么不是以后**：语料证据已充分（94 图像/2006 矢量），推迟只会让表格确认（Priority 3 依赖矢量线）与 Caption 继续阻塞。

### Priority 3 — 暂缓能力（有真实信号、但有前置依赖或未被失败案例驱动）
- **Table Cell Geometry**：真实信号强（设备手册 SPARSE 64–67%，且 rm501 heading 假阳性即表格标签），**但**表格确认需要矢量线证据（Priority 2 的产出）；仅凭散点建 cell 几何会产生高误报且不可验证。→ 等 Visual Object 之后，用「线 + 散点」联合建设。
- **Formula Atomic Extension**：数学字体在 2/6 文档存在（真实但窄），主语料（RM501/DC201）零公式，P7.1 无任何可归因于公式缺失的失败。→ 无失败案例驱动，暂缓。
- **Graphic/Vector（Flowchart）**：矢量对象大量存在但无证据表明是流程图；connectivity 分析复杂度高；是 Visual Object 的子集工作。→ 先由 Priority 2 建立矢量观察，再评估 flowchart 需求是否真实存在。

---

## 五、决策原则

> **下一阶段的选择由真实 corpus 中的 Evidence Gap 驱动，而不是由 PDF Parser 功能清单驱动。**

本轮矩阵的每一项排序都对应一个可验证的真实数据：
- HV 排第一 ← 175/0 的积压事实与链路阻塞
- Visual 排第二 ← 94 图像 + 2006 矢量被跳过的事实
- Table 暂缓 ← 64–67% SPARSE 是真实信号，但缺矢量线佐证
- Formula/Flowchart 暂缓 ← 需求未被失败案例或内容证据证实

同时，任何新能力必须走完整链条，不得跳层：

```
Document → Observation → Structural Relation → StructureHypothesis
        → Human Validation → Validated Structure → Evidence
```

- Visual Object Observation 的产出是 Observation（Layer A），必须经 Relation/Hypothesis 构造，不得直接变 Evidence。
- Human Validation 的产出是 Validated Structure（Layer D），不得直接写 Evidence Store。
- Textual/Symbol 信息若将来入链，必须作为 Observation 层立项，不得作为 P7.1 的 if/else。

---

## 六、STOP

本轮零代码修改、零 heuristic、零实现。唯一新增文件：本文件。

禁止事项全部未触碰：P7.2 / Visual Object 实现 / Table Cell Geometry / Graphic/Vector 实现 / Formula 实现 / Caption detection / Human Validation UI / Annotation / Evidence / Capability / Runtime / P8 / heuristic patch / document-specific rule。

**Evidence Gap Analysis 完成。STOP。**
