# DICE 2.0 · P6 前只读架构调研报告

**调研对象**（源码级，非 README）：MinerU、Docling、LayoutParser、PaddleOCR
**调研主题**：原子文本 / 坐标 / Span / Layout / Reading Order / Region / DOM / 调试与验证
**性质**：READ-ONLY 架构评审。本阶段不修改 P1–P5、Frozen 730、Annotation、C1/C2、Evidence/Capability/Runtime，也不进入 P6 编码与 P7。
**产出**：本报告 + `P6_CHANGE_CANDIDATE` 清单（第 10 节，仅记录、不实现）。

---

## 0. 调研方法与取证清单

| 项目 | 取证方式 | 已读源码（commit / 路径） |
|---|---|---|
| MinerU | 浅克隆 `4fe4bde`（tree 完整）+ raw 直读 | `mineru/utils/boxbase.py`、`mineru/utils/enum_class.py`、`mineru/backend/{hybrid,vlm,pipeline,office}` 目录树、`mineru/backend/pipeline/*.py`、`mineru/utils/{span_block_fix,span_pre_proc,para_block_utils}.py`、`mineru/model/pptx/xycut_pp_sorter.py` |
| Docling | raw 直读（main 分支） | `docling/datamodel/base_models.py`、`docling/datamodel/document.py`、`docling-core: docling_core/types/doc/base.py`（BoundingBox）、`labels.py`（DocItemLabel/GroupLabel） |
| LayoutParser | 浅克隆 `04e2816` | `src/layoutparser/elements/{base.py,layout_elements.py,layout.py}` |
| PaddleOCR | GitHub API 目录树 + raw 直读 | `ppstructure/{layout,recovery,table,kie,predict_system.py,utility.py}` 目录结构 |

> 网络不稳定导致 `docling` 与 `PaddleOCR` 未能本地落盘，改为 raw/API 直读，覆盖了本调研所需的全部架构决策点；MinerU 因 partial-clone blob 未拉全，仅 tree 落盘，关键文件已通过 raw 补齐。

---

## 1. 执行摘要（Executive Summary）

四个成熟项目在**「中间表示如何组织」**上高度一致地收敛出五个可复用的设计思想，且与 DICE 的既有分层**方向一致、深度各有差异**：

1. **几何与内容强制分离**：LayoutParser 用 `BaseCoordElement`（Rectangle/Quadrilateral/Interval）承载纯几何，`TextBlock` 只挂一个 `block` 指针；Docling 用一等公民 `BoundingBox`；MinerU 用裸元组 + 纯函数。**DICE P1/P2 的「Observation=事实、几何=纯关系」就是这条路的严格执行版。**
2. **对象身份用 ID 引用而非嵌套对象**：LayoutParser 的 `TextBlock.parent/next`、Docling 的 `self_ref/parent/children` 都是引用式关系。**DICE P4 的 `source_observation_ids`、P5 的 `reading_idx` 已具备雏形。**
3. **置信度是一等字段、且与文档本体分离**：Docling 把 `ConfidenceReport`（parse/layout/table/ocr 四维 + POOR→EXCELLENT 分级）做成**独立于 document 的元数据对象**；LayoutParser 的 `TextBlock.score`、MinerU 的 layout score 都是内嵌字段。**DICE P5 已引入 `confidence`，但「独立置信度报告」这一思想尚未落地。**
4. **语义标签与几何区域在成熟项目里是「融合」的，而这恰恰是 DICE 必须拒绝的**：MinerU `BlockType`（TITLE/TABLE/CAPTION/HEADER/FOOTER…40+ 种）和 Docling `DocItemLabel` 都把语义分类直接写入 layout 块。**DICE 的 P6=几何 Region、P7=语义 Structure 的边界比它们更严格，这条边界不能向它们看齐。**
5. **验证/错误/溯源在 Docling 里是结构化一等公民**（`ErrorItem` 带 component/module/category、`ConversionAssets` 带 version/status/errors/timings/confidence/document）。**这是 DICE 最值得借鉴的一块工程结构。**

**核心结论**：DICE P1–P5 **没有架构级缺口**，事实层/语义层边界、溯源、决策追踪、冻结基线四项比四个参考项目**更严格**，不应为了「像成熟项目」而削弱。本次调研能带来的收益是**有限的 P6 工程增强**（区域源引用、区域几何摘要、区域决策追踪、视觉调试工件），以及把「结构化置信度报告 / 结构化错误」作为 P6/P7 的工程模式引入。**这些改动必须记为 `P6_CHANGE_CANDIDATE`，本阶段不落地。**

---

## 2. MinerU 调研发现

### 2.1 坐标/几何组织 —— 裸元组 + 模块级纯函数
`mineru/utils/boxbase.py` 全部几何操作以 `[x0, y0, x1, y1]` 元组为参数，模块级纯函数实现：
- `is_in`（包含）、`bbox_relative_pos`（left/right/bottom/top 四向关系）
- `bbox_distance` / `bbox_center_distance`（最小距离 / 中心距离）
- `calculate_iou`、`calculate_overlap_area_2_minbox_area_ratio`（重叠占最小框比）
- `calculate_vertical_projection_overlap_ratio`（**x 轴投影重叠比**——与 DICE P5 的列检测思想同源）

**要点**：MinerU 几何层是**函数式、无对象**的。优点：零抽象开销、易测试；缺点：bbox 语义（谁是 left/top）全靠调用约定，**没有坐标系原点的显式表达**（隐含左上角），也没有「几何对象」可被引用/序列化。DICE P2 的 `SingleObservationGeometry` 是 dataclass，比 MinerU 更可序列化、可溯源。

### 2.2 中间表示 —— 三级 JSON 流水线（model.json → middle.json → content_list）
`mineru/backend/pipeline/` 目录树明确暴露三阶段：
- `pipeline_analyze.py` → `model_json_to_middle_json.py` → `middle.json`（layout 块 + 行 + span + OCR 结果）
- `pipeline_middle_json_mkcontent.py` → `content_list.json` / 最终 markdown

`mineru/utils/enum_class.py` 定义输出模式 `MakeMode`：`mm_markdown / nlp_markdown / content_list / content_list_v2`。

**要点**：MinerU 把「检测结果」「中间结构」「最终序列化」拆成三份产物，**中间产物可审计、可重放**。这印证了 DICE 的「分层产物各自落盘」路线。但 MinerU 的层级是**流水线阶段**，不是 DICE 的**事实/语义边界**。

### 2.3 语义类型 —— BlockType 融合（这是 DICE 的「反面教材」）
`mineru/utils/enum_class.py` 的 `BlockType` 直接输出 40+ 种语义标签：`TEXT / TITLE / IMAGE / TABLE / CHART / CAPTION / FOOTNOTE / HEADER / FOOTER / PAGE_NUMBER / ABSTRACT / DOC_TITLE / PARAGRAPH_TITLE / VERTICAL_TEXT / HEADER_IMAGE / FOOTER_IMAGE / FORMULA_NUMBER / EQUATION / LIST / INDEX / CODE / ALGORITHM / REF_TEXT / ASIDE_TEXT …`，另有 `ContentType`/`ContentTypeV2` 承载 span 级内容类型（含 `PAGE_HEADER/PAGE_FOOTER/PAGE_NUMBER`），以及 `NotExtractType`（HEADER/FOOTER/PAGE_NUMBER 等**不提取**的类型）。

**要点**：MinerU 在**layout 检测阶段**就输出语义标签，几何与语义**没有边界**。此外 `mineru/utils/span_block_fix.py` 存在**后置修正**（检测后回改 block/span）——这违反了 DICE 的「上游只读、永不反向修改」原则。DICE 的 P6（几何区域）→ P7（语义结构）切分，是对 MinerU 这种「融合 + 回改」做法的**有意识的纠正**。

### 2.4 阅读顺序
`mineru/model/pptx/xycut_pp_sorter.py`（XY-cut 排序）与 `mineru/backend/utils/para_block_utils.py`（段落块排序）承担阅读顺序。XY-cut 是经典的递归投影切分。

**要点**：XY-cut 是确定性、可复现的几何算法（与 DICE P5 的确定性列检测同族）；但 MinerU 的最终顺序仍掺杂语义（`NotExtractType` 过滤、`title_level_postprocess` 标题层级后处理）。

### 2.5 与 DICE 的历史渊源
DICE 的 Frozen 730 Pool（`phase48_l1_candidate_presentation.json`，730 条）正是 MinerU 产物的派生：其 CandidateSpan 四字段契约 `{document_id, page_reference, span_text, position_metadata{bbox, block_index, block_no}, hints}`。`position_metadata.block_no` 就是 MinerU 的 block 序号；此前发现的 `Position\nStep` 合并文本即 MinerU 块聚类产物。**这印证了：DICE 已把 MinerU 的「块」抽象成自己的「CandidateSpan」，并冻结。**

---

## 3. Docling 调研发现

### 3.1 坐标 —— BoundingBox 是带坐标系原点的一等公民
`docling-core: docling_core/types/doc/base.py` 的 `BoundingBox`：
- 字段：`l / t / r / b` + **`coord_origin: CoordOrigin = TOPLEFT | BOTTOMLEFT`**
- 派生：`width / height / area`
- 谓词：`intersection_area_with / intersection_over_union / intersection_over_self / overlaps / overlaps_horizontally / overlaps_vertically / is_left_of / is_strictly_left_of / is_above / is_strictly_above / is_horizontally_connected / enclosing_bbox`
- 变换：`resize_by_scale / scale_to_size / scaled / normalized / expand_by_scale / to_top_left_origin / to_bottom_left_origin`

**要点**：Docling 把**所有空间谓词**做成 bbox 类型的方法，并**显式建模坐标系原点**（PDF 常为左下原点，图像常为左上原点）。这是 DICE P2 目前**隐含假设左上角原点**所缺失的健壮性细节，属于「可直接借鉴的工程增强」。

### 3.2 布局簇 —— Cluster 带 children/cells/confidence（区域层级 + 源引用）
`docling/datamodel/base_models.py` 的 `Cluster`：
- `id`、`label: DocItemLabel`（语义标签）、`bbox: BoundingBox`、`confidence: float`
- `cells: list[TextCell]`（**源文本单元格引用**——layout 单元指向底层原子文本）
- `children: list[Cluster]`（**递归层级**——区域可嵌套）

`BasePageElement`：`label / id / page_no / cluster / text`。

**要点**：`Cluster` 同时具备「源引用（cells）」「层级（children）」「置信度（confidence）」「几何（bbox）」「标签（label）」。**DICE P6 RegionObservation 应借鉴 cells→source_span_ids 与 children→parent_region_id 这两个结构，但拒绝 label（语义）进 P6。**

### 3.3 页面预测分离 —— layout / table / figure / equation 各归各
`PagePredictions`：`layout: LayoutPrediction`、`tablestructure`、`figures_classification`、`equations_prediction`、`vlm_response`。

**要点**：Docling 把「版面检测」与「表格结构」「图分类」「公式」拆成**独立预测**，彼此不污染。这佐证 DICE 的 P6（Region）与 P7（Structure/Table/Figure）分离是对的；区别在于 Docling 各预测都带语义标签，DICE 的 P6 只保留几何。

### 3.4 产物打包 —— ConversionAssets 把「文档」与「元数据」分离
`docling/datamodel/document.py` 的 `ConversionAssets`：
- `version`（DoclingVersion，**可复现**）、`timestamp`、`status`（ConversionStatus 五态）
- `errors: list[ErrorItem]`（`component_type / module_name / category / page_no / message`——**结构化错误、带组件与类别**）
- `pages: list[Page]`、`timings: dict[str, ProfilingItem]`（**分阶段计时**）
- `confidence: ConfidenceReport`（**独立置信度报告**）
- `document: DoclingDocument`（**文档本体，与元数据完全分离**）

`ConfidenceReport / PageConfidenceScores`：`parse_score / layout_score / table_score / ocr_score` + `POOR / FAIR / GOOD / EXCELLENT` 质量分级。

**要点**：这是本调研**最值得 DICE 整体借鉴的工程结构**：文档本体（DOM）与验证元数据（版本/状态/错误/计时/置信度）**物理分离**，可独立校验、独立重放、独立降级。DICE 当前的 `pX_validation_report.md + pX_test_results.json` 是雏形，但「结构化错误对象 + 分级置信度报告」尚未落地。

### 3.5 语义标签 —— DocItemLabel / GroupLabel
`docling-core: labels.py`：`DocItemLabel`（TITLE/SECTION_HEADER/TEXT/TABLE/PICTURE/CAPTION/PAGE_HEADER/PAGE_FOOTER/FORMULA/LIST_ITEM…）与 `GroupLabel`（LIST/CHAPTER/SECTION/SHEET/SLIDE…，**层级标签，与条目标签分离**）。

**要点**：Docling 用**两套枚举**区分「条目语义」与「容器层级」，且每个 `DocItem` 携带 `prov`（含 page_no/bbox/charspan 的溯源）。**这印证 DICE P7 需要一个「结构层级」概念；但 P6 不引入任何 label。**

---

## 4. LayoutParser 调研发现

### 4.1 几何抽象 —— BaseCoordElement
`src/layoutparser/elements/base.py`：`BaseCoordElement` 抽象基类定义几何接口：
- 属性：`width / height / coordinates / points / area`
- 关系：`condition_on / relative_to`（相对坐标变换）、`is_in(other, soft_margin, center)`
- 运算：`intersect / union / pad / shift / scale`

具体几何：`Interval`（区间）/ `Rectangle`（矩形）/ `Quadrilateral`（四边形），均以 `block_type` 为判别符序列化。

**要点**：LayoutParser 把「几何形状」做成可替换实现（Interval/Rectangle/Quadrilateral），几何运算与形状解耦。DICE P2 目前只有轴对齐矩形 bbox，若未来需要斜文本（Quadrilateral），这是可参考的扩展点——**但当前语料（医疗器械手册 + arxiv 预印本）无斜文本需求，不必现在引入。**

### 4.2 内容与几何分离 + ID 引用式关系 —— TextBlock
`src/layoutparser/elements/layout_elements.py` 的 `TextBlock`：
- `block: BaseCoordElement`（**几何与内容分离**）
- `text`、`id`、`type`（语义类型）、`score`（**置信度**）
- `parent: int`（**父对象 ID 引用**）、`next: int`（**下一块 ID 引用，即阅读顺序的链式表达**）

**要点**：这是四个项目里**最简、最清晰的「几何/内容/关系」三元分离**。`parent`（层级）+ `next`（顺序）用**裸 ID 引用**而非嵌套对象，天然支持「几何对象复用、关系可后补」。DICE P4 的 `source_observation_ids` 与 P5 的 `reading_idx` 是同一思想；P6 应沿用「`parent_region_id` 引用」而非把区域嵌进 span。

### 4.3 页面容器 —— Layout
`src/layoutparser/elements/layout.py`：`Layout(MutableSequence)` 是**块列表 + `page_data`（canvas 宽高）**。提供 `to_dataframe()` 等批量操作，但**没有内建层级**（层级全走 `TextBlock.parent`）。

**要点**：「列表容器 + 页面几何元数据」是页面对象的最小可行抽象。DICE 当前各层产物是**独立列表**，缺一个「页面容器」把它们按页聚合——这是第 10 节的 `P6_CHANGE_CANDIDATE` 之一。

---

## 5. PaddleOCR（PP-Structure）调研发现

### 5.1 模块边界 —— 四个子模块各司其职
`ppstructure/` 目录树：`layout/`（版面检测）、`recovery/`（结构恢复 → docx/markdown）、`table/`（表格结构识别，**独立**）、`kie/`（关键信息抽取，**独立下游**）、`predict_system.py`（编排）、`utility.py`（共享工具/排序）。

**要点**：PaddleOCR 把「版面检测」「结构恢复」「表格」「KIE」做成**四个正交模块**。这与 DICE 的 P6（Region）→ P7（Structure/Table）边界一致；**区别是 PaddleOCR 的 layout 检测直接输出语义 label，恢复阶段再组装阅读顺序**——语义仍在几何层出现。

### 5.2 阅读顺序 —— 朴素二分列（反面教材）
PP-Structure 的 `sorted_layout_boxes`（`predict_system.py`/`utility.py`）以 `center_x < page_width/2` 把块硬切成左右两列，再列内自顶向下排序。

**要点**：这是**硬编码二分列 + 强猜**，正是 DICE P5 明确拒绝的路线——DICE P5 用 bbox 垂直投影探测真实列数（`<min_column_span_count` 的杂散组并入边缘），并在重叠歧义时**降级置信度而非强猜顺序**（「知道不知道比强行猜一个顺序更重要」）。**此项明确「不借鉴」。**

### 5.3 结构恢复 —— recovery 是独立于检测的阶段
`ppstructure/recovery/`：`recovery_to_doc.py / recovery_to_markdown.py / table_process.py`，把 layout 结果按顺序拼回 docx/markdown。

**要点**：PaddleOCR 把「阅读顺序 + 序列化」放在**独立于检测**的恢复阶段——这佐证 DICE 把「顺序解释」放在 P5、把「结构序列化」放在 P7 是对的。

---

## 6. DICE 对照矩阵（13 行 × 7 列）

| DICE Layer | MinerU | Docling | LayoutParser | PaddleOCR | DICE 当前设计 | 值得借鉴 |
|---|---|---|---|---|---|---|
| **1. 原子文本 Observation** | span 含 content/font/size/flags/type，无独立原子层 | `TextCell`（page 级网格）承载底层文本，`charspan` 溯源 | 无原子层，text 直接挂块 | OCR 文本直接挂 region | **P1 AtomicTextObservation（char/word/span/line/block 五层，sha256=74d23ec7…）** | ② Docling `charspan` 的字符级溯源（若 P7 需要字符级） |
| **2. Geometry 坐标** | 裸元组 `[x0,y0,x1,y1]` + 纯函数，无原点表达 | **`BoundingBox` 一等类型，显式 `coord_origin`** | `BaseCoordElement`（Interval/Rect/Quad）可替换形状 | bbox 数组，隐含左上原点 | **P2 SingleObservationGeometry + PairwiseRelation（8 向、对称强制、GeometryConfig 阈值）** | ① **显式 `coord_origin` 字段**；① 空间谓词方法化 |
| **3. Style 样式** | span 存 font/size/flags（无归一化签名） | 不单独建模样式 | 无 | 无 | **P3 StyleObservation + style_signature（bit 位实证）+ StyleComparison** | 无（DICE P3 已更细） |
| **4. Span 构造** | 块聚类（含 `span_block_fix` 后置回改） | `Cluster.cells` 聚合并入 DOM | `TextBlock`（block+text+id+type+score） | region 即块 | **P4 ExperimentalSpan v2（span_id/text/source_observation_ids/bbox/…/merge_decision_trace/provenance）** | ② `TextBlock` 的「几何/内容/关系」三元分离范式（DICE 已实现，属印证而非新增） |
| **5. Reading Order** | XY-cut + 语义过滤 + 标题后处理 | 文档级 `DocItem.children` 排序 | `TextBlock.next` 链式 ID | 朴素 `center_x<w/2` 二分列 | **P5 ReadingOrderObservation + ColumnGroup + 列优先 + overlap→AMBIGUOUS 降置信** | ① **next/prev 显式边**（DICE 有 reading_idx 总量序，缺显式边对象）；③ **拒绝 PaddleOCR 二分强猜** |
| **6. Region/Layout** | layout 块直接带语义 BlockType | `Cluster`（bbox+label+confidence+cells+children） | 无独立 Region（parent 引用） | layout region 直接带语义 | **P6 待设计（当前仅骨架）** | ② **源引用 + 层级引用**（cells→source_span_ids、children→parent_region_id）；③ 拒绝语义标签进 P6 |
| **7. Provenance 溯源** | 无（中间 JSON 隐式保留） | `DocItem.prov`（page_no/bbox/charspan） | 无 | 无 | **P4 source_observation_ids + merge_decision_trace + provenance + version** | 无（DICE P4 已更严：含合并追踪） |
| **8. Confidence 置信度** | layout score（内嵌） | `Cluster.confidence` + **独立 ConfidenceReport** | `TextBlock.score` | 检测 score | **P5 confidence（含 overlap 歧义降级）** | ① **独立分级置信度报告**（parse/layout/table/ocr 四维） |
| **9. Decision Trace 决策追踪** | 无 | 无（只有输入/输出） | 无 | 无 | **P4 merge_decision_trace + P5 ReadingOrderDecisionTrace** | 无（**DICE 独有强项，勿削弱**） |
| **10. DOM** | 无 DOM，只有 JSON 流水线产物 | **DoclingDocument/DocItem（self_ref/parent/children）** | 无（Layout 列表 + parent 引用） | 无（markdown/docx 序列化） | **无统一 DOM（各层独立产物）** | ② **P7 引入最小 DOM**（自实现，非 P6） |
| **11. Debug 输出** | 中间 JSON + 可视化标注脚本 | **页面图像导出 + bbox overlay** | **visualization.py（bbox 叠加渲染）** | 标注图 + 检测可视化 | **仅数值验证报告（pX_validation_report.md）** | ① **bbox 叠加 PNG 视觉调试工件**（P6 新增） |
| **12. Validation 验证** | 无结构化验证 | **ErrorItem（component/module/category）+ ConfidenceReport + ConversionStatus 五态** | 无 | 无 | **pX_validation_report + pX_test_results（确定性/覆盖率/孤儿/重复）** | ① **结构化错误对象 + 分级置信度**（增强现有验证） |
| **13. Semantic Structure 边界** | **无边界**（BlockType 融合语义 + 后置回改） | **无边界**（DocItemLabel 融合语义，但有 prov/confidence 背书） | **弱边界**（type 挂块） | **无边界**（layout 直接出语义） | **P6=几何 Region、P7=语义 Structure，事实层/语义层强隔离，Runtime Authority=ZERO** | ③ **四个项目均不满足 DICE 边界，绝不向其靠拢** |

> 图例：① 可直接借鉴的工程（数据结构组织/bbox 抽象/对象身份/确定性排序/验证/调试工件）；② 借鉴思想但自实现；③ 不引入（LLM/语义进 P6/黑盒分类器/文档特判/关键字规则/一体化解析/复制流水线/二分强猜）。

---

## 7. 值得借鉴的架构模式（Architecture Patterns Worth Borrowing）

### 7.1 ① 可直接借鉴（工程级）
1. **显式坐标系原点 `coord_origin`（Docling BoundingBox）**：DICE P2 隐含左上原点；借鉴「在 bbox 上显式声明原点 + 提供 `to_top_left_origin/to_bottom_left_origin` 转换」以消除 PDF（左下）与图像（左上）的原点歧义。**风险低、收益明确。**
2. **对象身份用裸 ID 引用而非嵌套（LayoutParser parent/next、Docling self_ref/parent/children）**：DICE P6 区域层级用 `parent_region_id` 引用，不把区域嵌进 span；保持「关系可后补、对象可复用」。
3. **独立分级置信度报告（Docling ConfidenceReport）**：把「页级/层级的 parse/layout/table/ocr 分数 + POOR→EXCELLENT 分级」做成**独立于 Observation 本体**的元数据，可单独校验与降级。
4. **结构化错误对象（Docling ErrorItem）**：`component_type/module_name/category/page_no/message` 五元组，替代 DICE 当前自由文本验证条目，使验证报告可机读、可聚合。
5. **bbox 叠加视觉调试工件（LayoutParser visualization.py / Docling 页面图像导出）**：DICE 目前只有数值验证，缺「人可看」的几何调试图。
6. **页面容器最小抽象（LayoutParser Layout = 列表 + page_data）**：把同一页的各层产物聚合成一个「页面工件」，供验证与调试引用。

### 7.2 ② 借鉴思想、DICE 自实现
1. **区域层级（Docling Cluster.children / GroupLabel）**：P6 用**纯几何分组**（覆盖投影、间隙、对齐）构建 `parent_region_id` 树，**不带语义标签**。
2. **源引用（Docling Cluster.cells → DICE source_span_ids）**：Region 显式记录「由哪些 span 组成」，保证 P6 可回溯到 P4/P1。
3. **阅读顺序图（LayoutParser next 链、Docling children 序）**：P6 区域之间建立显式的「下一区域」边，补足 P5 仅有 `reading_idx` 总量序、缺跨列/跨区域显式边的现状。
4. **最小 DOM（Docling DoclingDocument/DocItem）**：**P7** 引入一个自实现的结构 DOM（page → structure item → 源引用 → 溯源），承载语义层级，不照搬 Docling 的 label 体系。

---

## 8. 不应借鉴的模式（Patterns NOT Worth Borrowing）

1. **LLM/VLM 兜底准确率（MinerU `hybrid_magic_model.py`/`vlm` 后端）**：非确定性，违反 DICE 事实层「纯几何、可复现」的确定性承诺。**不引入。**
2. **语义分类进入 Region/P6（MinerU BlockType、Docling DocItemLabel、PaddleOCR layout label）**：DICE 的 P6=Region（几何）、P7=Structure（语义）边界是**有意的更严格设计**，不向成熟项目的「融合式 label」看齐。**不引入。**
3. **黑盒布局分类器（LayoutParser/PaddleOCR 的检测模型）**：不可复现、不可溯源，与 DICE 的 deterministic construction 冲突。**不引入。**
4. **后置修正 / 反向修改（MinerU `span_block_fix.py`）**：违反 DICE「上游只读、永不反向修改」原则。**不引入。**
5. **关键字/标题层级规则（MinerU `title_level_postprocess.py`）**：语义启发式，属 P7 范畴且需另行评审。**P6 不引入。**
6. **一体化解析流水线（四个项目都是 monolithic parser）**：DICE 的分层可审计、可重放是核心资产，**不复制任何项目流水线**。
7. **朴素二分列强猜（PaddleOCR `sorted_layout_boxes`）**：硬编码两列 + 强猜顺序，正是 DICE P5 已用「真实列探测 + 歧义降置信」纠正的做法。**不引入。**

---

## 9. DICE 已有优势（反向审查：DICE 比参考项目更严格的地方）

> 本节为「反向审查」：明确 DICE **已经比**四个成熟项目更严格的设计，**不得为了「看起来像成熟项目」而削弱它们。**

1. **溯源（Provenance）**：DICE P4 的 `source_observation_ids` + `merge_decision_trace` 记录了「每个 span 由哪些观测合并而来、按哪条规则合并」；Docling 只有 `prov`（page_no/bbox/charspan），MinerU/LayoutParser/PaddleOCR 基本无溯源。**DICE 更严。**
2. **决策追踪（Decision Trace）**：`merge_decision_trace`（P4）+ `ReadingOrderDecisionTrace`（P5）是 DICE 独有；四个项目均无逐决策追踪。**DICE 独有强项。**
3. **确定性构造（Deterministic Construction）**：DICE 全程纯几何规则、无 ML；四个项目都依赖 ML 检测器（非确定性）。**DICE 更严。**
4. **冻结基线（Frozen Baseline）**：Frozen 730 Pool（md5_8=a10b368e）作为不可变快照；四个项目均无「冻结中间产物」机制。**DICE 更严。**
5. **上游/下游边界（Upstream/Downstream Boundary）**：DICE 永不反向修改早先层；MinerU `span_block_fix` 存在后置回改。**DICE 更严。**
6. **错误/歧义降级（Ambiguity over forced guess）**：P5 对 overlap 歧义降 `confidence` 并标 `AMBIGUOUS`，绝不强猜；PaddleOCR 二分强猜。**DICE 更严。**
7. **运行时权威（Runtime Authority = ZERO）**：感知输出永不触碰运行时；四个项目无此约束。**DICE 独有。**

**结论**：上述七项是 DICE 的「架构护城河」，本次调研**不产生任何削弱它们的候选**。

---

## 10. P6 变更候选（P6 Change Candidates，仅记录、不实现）

> 本阶段不落地任何变更。以下均记为 `P6_CHANGE_CANDIDATE`，供 P6 编码阶段评审。

- **CAND-P6-1（必要）**：`RegionObservation` 增加 `source_span_ids: list[str]`（区域 → span 源引用），对齐 Docling `Cluster.cells` 思想、LayoutParser 引用式关系。保证 P6 可回溯 P4。
- **CAND-P6-2（必要）**：`RegionObservation` 增加 `region_geometry`（区域 bbox + area + 中心点），即「几何摘要」，对齐 Docling `Cluster.bbox`。
- **CAND-P6-3（必要）**：`RegionObservation` 增加 `decision_trace`（该区域由哪条几何规则/哪个投影阈值分组），延续 P4/P5 的决策追踪，保持 DICE 独有强项。
- **CAND-P6-4（建议）**：`RegionObservation` 增加 `parent_region_id`（区域层级引用），借鉴 Docling `Cluster.children`、LayoutParser `TextBlock.parent`；**纯几何层级，不带语义标签**。
- **CAND-P6-5（建议）**：`RegionObservation` 增加 `confidence`，并对「区域边界模糊」（跨列间隙不清、投影重叠）降级，延续 P5 的歧义处理。
- **CAND-P6-6（建议）**：`SingleObservationGeometry` 增加显式 `coord_origin`（默认 TOPLEFT）+ 坐标转换方法，借鉴 Docling `BoundingBox.coord_origin`。
- **CAND-P6-7（建议）**：P6 交付物增加**视觉调试工件**（bbox 叠加 PNG），借鉴 LayoutParser `visualization.py` / Docling 页面图像导出。
- **CAND-P6-8（建议）**：新增**独立置信度报告**（页级/层级分数 + POOR→EXCELLENT 分级）与**结构化错误对象**（component/module/category/page_no），增强现有验证产物。
- **CAND-P6-9（可选）**：新增「页面容器」最小抽象（列表 + page 几何），聚合各层产物供验证/调试引用。

**明确不进入 P6 的候选（记入 P7 Implications）**：任何语义 label、任何结构层级语义、任何 DOM、任何 ML/VLM。

---

## 11. P7 启示（P7 Implications）

1. **P7 需要「结构层级」概念**：Docling 用 `GroupLabel`（LIST/CHAPTER/SECTION）与 `DocItemLabel` 分离，印证 DICE P7 需要一个独立于「条目语义」的「容器层级」概念（如 section/chapter/table-container）。
2. **P7 需要最小 DOM**：借鉴 Docling `DoclingDocument/DocItem` 的 `self_ref/parent/children` 引用式层级，但**自实现**、只用 DICE 的 Observation/Span/Region 作为叶子。
3. **P7 溯源到字符级**：Docling `prov.charspan` 提供字符级溯源；若 P7 需要「某语义条目精确对应哪些字符」，DICE 可借鉴，但**当前五层（char 层已存在）已足够，不提前引入**。
4. **P7 的语义分类边界**：MinerU BlockType / Docling DocItemLabel 的 40+ 标签是「语义全集」；DICE P7 只需医疗器械手册 + 学术论文语料所需的**最小标签集**，且每标签须带溯源与置信度（借鉴 Docling `DocItem.prov + confidence`）。
5. **P7 拒绝后置修正**：MinerU 的 `span_block_fix` / `title_level_postprocess` 反向改块，DICE P7 必须「语义只读叠加于几何事实之上、不改写事实」。

---

## 12. 最终建议（Final Recommendation）

**总体判断**：DICE P1–P5 的「事实层/语义层边界 + 溯源 + 决策追踪 + 确定性 + 冻结基线」架构**优于**四个参考项目的同层设计，不存在需要「向成熟项目看齐」的架构缺口。本次调研的收益集中在 **P6 的工程增强**：区域源引用、区域几何摘要、区域决策追踪（**必要**），区域层级、置信度、显式坐标原点、视觉调试工件、独立置信度报告、结构化错误（**建议**），页面容器（**可选**）。

**行动**：
1. 本阶段**只交付本报告**，不修改任何代码、不进入 P6 编码与 P7。
2. P6 编码阶段，先评审第 10 节 `CAND-P6-1..9`，**必要项（1/2/3）优先**，建议项按收益/风险排序（视觉调试工件与显式坐标原点性价比最高）。
3. P7 阶段，按第 11 节引入「结构层级 + 最小 DOM + 最小语义标签集」，坚持语义只读叠加、不改写事实。

---

## 附录 A：结构缺口问题 Q1–Q7 解答

**Q1（P4 Span 是否应加属性？）** 不加语义属性。P4 已含 bbox/style/溯源/合并追踪/version，比参考项目的块都更完整。成熟项目给块挂的 `type`（语义）与 `score`（置信度）中，**score 在 P5 已通过 confidence 覆盖，type 属 P7**。结论：P4 保持冻结，无必要新增字段。

**Q2（P5 阅读顺序是否缺稳定的关系表示？）** P5 有 `reading_idx` 总量序 + `ColumnGroup` 列归属，足以表达列优先顺序；缺的是「显式 prev/next 边对象」与「跨区域顺序」。**不回头改 P5（冻结）**；区域间顺序由 P6 的 `parent_region_id` + 区域排序承担（见 CAND-P6-4）。

**Q3（P6 RegionObservation 应加哪些字段？）** 加：`source_span_ids`、`region_geometry`（bbox/area/中心）、`decision_trace`、`parent_region_id`、`confidence`（见 CAND-P6-1..5）。**不加**：语义 label、caption/heading 等（属 P7）。

**Q4（需要统一 DOM 吗？）** P6 不需要；DOM 是 P7 的结构产物。P6 只需「区域列表 + 层级引用」的最小组织。

**Q5（需要统一 Layout Object Model 吗？）** Docling 的 LOM 是「label + 层级」的语义模型，等价于 DICE 的 P7。P6 只需借鉴其「薄容器」（列表 + 页面几何），不引入语义 LOM。

**Q6（需要视觉调试工件吗？）** **需要，这是本次调研发现的最清晰缺口**。借鉴 LayoutParser `visualization.py` / Docling 页面图像导出的 bbox 叠加 PNG，作为 P6 交付物之一（CAND-P6-7）。

**Q7（哪些关注点推迟到 P7？）** 语义分类、结构层级、DOM 序列化、跨页结构装配、标题层级启发式、表格/图语义、字符级溯源（如 P7 需要）。

## 附录 B：最终判定 A–E 解答

**A. DICE P1–P5 是否有明显的架构缺口？** **无架构级缺口。** 仅有工程级微瑕：① 坐标原点隐含假设（未显式）；② 无视觉调试工件；③ 验证条目非结构化（自由文本）；④ 无「页面容器」聚合。四项均为增强项，非缺口。

**B. 当前 P6 RegionObservation 模式是否足够？** **不够。** 缺源引用、区域几何摘要、决策追踪（必要），以及层级、置信度（建议）。

**C. P6 是否需要因本次调研而变更？** **需要，但变更幅度小且偏工程。** 见 CAND-P6-1..9，全部为「增强既有骨架」，不推翻 P6 的几何定位，也不引入语义。

**D. 哪些是必要项、哪些是锦上添花？**
- **必要**：`source_span_ids`、`region_geometry`、`decision_trace`（CAND-P6-1/2/3）。
- **锦上添花（按性价比）**：视觉调试工件、显式 `coord_origin`、`parent_region_id`、`confidence`、独立置信度报告、结构化错误、页面容器。

**E. 哪些能力推迟到 P7？** 语义分类（label）、结构层级（section/chapter）、最小 DOM、跨页装配、标题层级启发式、表格/图语义、（可选）字符级溯源。

---

*报告结束。本阶段为 READ-ONLY：未修改 P1–P5、Frozen 730、Annotation、C1/C2、Evidence/Capability/Runtime，也未进入 P6 编码与 P7。*
