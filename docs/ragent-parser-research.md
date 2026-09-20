# ragent 文档解析 / PDF 提取 / 版面定位源码调研报告

调研对象：https://github.com/nageoffer/ragent（Java，企业级 Agentic RAG）
调研方式：整仓 tarball 下载后本地精读（`/tmp/ragent`），非抓页面拼凑；所有结论均来自源码。

关键模块路径（repo 相对路径，均为 Java）：

- 解析器接口/注册表：`rag/src/main/java/com/nageoffer/ai/ragent/core/parser/`
- Block 中间模型：`.../core/parser/model/`
- MinerU（PDF 版面解析，唯一 PDF 通道）：`.../core/parser/mineru/`
- 分块层：`.../core/chunk/{ChunkingService, blockaware/, text/, model/}`
- 入库编排：`.../ingestion/node/{ParserNode, EnhancerNode, ChunkerNode}.java`
- PDF 摄取示例：`docs/examples/pdf-ingestion-example.md`、`docs/examples/pdf-pipeline-request.json`
- 依赖：根 `pom.xml` 声明 Tika 3.2.3 BOM；`rag/pom.xml` 引入 `tika-parsers-standard-package`。

---

## 1. ragent 的文档解析流程

### 支持格式与解析器分工（ParserType + ParserRegistry 启动期建表）

6 类解析器按 (MIME × 档位) 认领，同一键被两个解析器认领即启动失败：

| 格式 | 解析器 | 关键点 |
|---|---|---|
| **PDF / Word / PPT** | `MinerUDocumentParser`（SaaS） | 两个档位都只有 MinerU 一条路；**生产代码里 PDF 从不走本地库** |
| Excel(xls/xlsx) | FAST 档 `ExcelDocumentParser`(POI)；FIDELITY 档才走 MinerU | 见 `MinerUDocumentParser.SPREADSHEET_MIME_TYPES` |
| CSV | `CsvDocumentParser`（AutoDetectReader 探测字符集 + RFC4180，产单张 key-val 表格） | |
| Markdown | `MarkdownDocumentParser`（commonmark + GFM Tables） | `text/plain` 也由它认领 |
| 长尾 text/html、json、xml、rtf、`text/*` | `TikaDocumentParser` | Tika 输出是平文本，按 `\n{2,}` 空行切成 ParagraphBlock |
| PNG/JPG/SVG | `ImageDocumentParser` | VLM 图生文（描述 + OCR 文字） |

注册表设计值得注意：
- `ParserRegistry`：路由键 (MIME × 档位)，查找顺序为 精确+请求档 → 通配+请求档 → 精确+FAST → 通配+FAST，**全不命中显式抛错，绝不静默兜底**给通用解析器产出垃圾文本。
- 启动自检（`selfCheck`）：对外声明支持的扩展名清单里的每个扩展名，必须被某个解析器**精确**认领，否则启动失败。
- MIME 探测以字节为准（Tika `detect(bytes, fileName)`），文件名只作为辅助；"认不出就报错"贯穿全局。
- 档位（`ParseProfile`）只有 fast / fidelity 两档：Excel 在 FAST 走 POI key-val、FIDELITY 才付 MinerU 成本。PDF 因为只有 MinerU 一条路，两档命中同一解析器，档位对 PDF 是空操作。

### PDF 用什么库解析 —— 直接答案

**PDF 没有任何本地解析主路径。** PDF 一律通过 `MinerUDocumentParser` 上传给 MinerU SaaS（https://mineru.net/api/v4）做版面解析：

1. 拿 Redisson 分布式信号量许可（压住 MinerU 并发，`concurrency-limit=5`，lease 900s）；
2. `requestUpload` 提交 `enable_table / enable_formula / language(ch) / is_ocr / files[{name(必须带扩展名), data_id}]`，拿到上传 URL + batchId；
3. 字节直接 PUT 到 MinerU OSS（适配内网，不依赖公网源 URL）；
4. 轮询 batch 状态（`MinerUPollingExecutor` + `MinerUStatus{state, zipUrl, errorMessage}`）到 DONE；
5. 下载结果 zip → `MinerUResultUnpacker` 解包。

结果 zip 契约 = **1 份 markdown + 若干图片（表格/公式/插图裁切图）**。也就是说 ragent 把"版面还原"整体外包给了 MinerU（其底层是 PDF-Extract-Kit 那类：版面检测、表格结构识别、公式识别、OCR），自己只做产物归一化。

仓库里 `TikaDocumentParser` 有一个 `PDFParserConfig` 静态块（关了内嵌图提取），但该 config **从未被挂到任何 PDFParser 上**，且 PDF 的 MIME 已被 MinerU 精确认领、根本路由不到 Tika——是死配置/历史残留。Tika 实际只用它解析 html/json/xml/rtf/text，以及 MIME 探测。

### 提取后如何切 chunk（Block 语义切分，v1.1 主路径）

流程：`ParserNode`（字节 → MIME → 按 (MIME×档位) 找解析器 → `parseStructured` 产出**有序 Block 列表** + 渲染纯文本兜底）→ `ChunkerNode` → `ChunkingService` → `BlockAwareChunkerDispatcher` → `ChunkAssembler` → embedding → 落库。

核心：**先归一化成一份统一的有序 Block 中间表示，再按 Block 类型分派切分**。Block 是 `sealed interface`，编译期穷举 7 类：

- `HeadingBlock(level, text)`、`ParagraphBlock(text)`、`TableBlock(headers, rows)`、
  `HtmlTableBlock(html)`（MinerU/HTML 里整段 `<table>` 原文）、
  `ImageBlock(asset, caption, altText, description)`、`ListBlock(ordered, items)`、`CodeBlock(language, code)`；
- 每块带 `Provenance(sourceFile, sheetName)`——注意：**注释里提到"页码/bbox/单元格范围"，但实际只有 sourceFile+sheetName 两个字段**（见下文局限）。

切分（`blockaware/`）的核心规则：

1. **标题驱动的大纲**：`HeadingHandler` 按标题 level 弹栈维护"章节路径"（带 level 列表，避免"不以 H1 开头就把同级层层嵌套"），每个 chunker 拿到自己所属的 outlinePath。
2. **每种 Block 类型一个 chunker，查表分发**（`BlockAwareChunkerDispatcher`），冲突启动即失败；新增类型只补一个 chunker。
3. **能整块就不切，切点只在结构边界**：判据统一是预算 `ChunkBudget.toleranceChars() = maxChars × 3（封顶 8192）`。整块 ≤ tolerance 就作为原子块保留；超出才按 maxChars 降级切分，且切点落在"行 / 表格行 / 列表项 / 句末"上，绝不在下标处硬截。
4. **打包（ChunkPacker）**：以"相邻两个标题之间"为一节；整节 ≤ tolerance 是原子的（整节并块或整节成块）；按 maxChars 贪心合并相邻节；**合并块不重叠**（节边界没有被切断的句子）；只有"整节超 tolerance 的节内切分"才由 TextSplitter 负责重叠。
   - 反碎片细节：不足 `maxChars/4` 的"碎屑"块在 flush 时**并回上一块**（即使跨节）；表格/代码块前的那段前导语（如"保证金单位为元"）会**捎进大块**而不是甩成孤块。
5. **装配（ChunkAssembler）**：`content` 存原文（Markdown 渲染，标题按原文位置在正文里，不篡改原文）；`embeddingText` 单独拼"正文缺失的章节前缀 + 检索正文"——**展示文本与向量文本分离**，续块才补章节词面（首块自带标题就不再重复拼）。序号 `index` 从 0 单调递增落库，可据此还原文档顺序。

各类型 chunker 要点：
- `ParagraphChunker`：先按 tolerance 量一次，切不动说明整段可保留；切出多片才退回 maxChars 重切，委托 `TextSplitter` 做边界回溯与归一化。
- `TableChunker`（规整表）：展示用 Markdown 表格渲染（单元格 `|` 转义、换行转 `<br>`），**向量文本单独渲染成 `列名: 值; 列名: 值` 的 key-value 行**（逐行），按 rowsPerChunk(默认 50) 与字符预算切组，切片标记为 piece 不再参与并块。
- `HtmlTableChunker`（MinerU 的 HTML 表）：去 colspan/rowspan=1 噪声，按 `<tr>` 拆行，首行当表头，**每片都拼成完整合法的 `<table><thead>…</table>`**，绝不把标签切断。
- `ImageChunker`：内容 = `VLM 描述 + ![caption](asset_url)`；**向量文本只用描述（去 URL 噪声）**；asset 进元数据。`assetUrl` 指向对象存储里上传的原图——图本身保留、描述进向量。
- `ListChunker` 按条目切、保持编号；`CodeChunker` 按行切、保持 fence。

### 备选路径：整文档单块 & 纯文本老路径

- `ChunkBudget.wholeDocument()`（前端 `-1` 哨兵）：全文渲染成一个 chunk，不分块。
- 文档示例里的老式管线 `fetcher → parser → enhancer → chunker → indexer` 仍以纯文本为主（`EnhancerNode.CONTEXT_ENHANCE` 对 `rawText` 做 LLM 整理），与新 Block 路径并存；新路径（ParserNode→ChunkerNode）直接消费 blocks。

---

## 2. 对表格 / 图片 / 版面的处理方式

### 表格
- **MinerU 的表格以原始 HTML `<table>` 嵌在 markdown 里**，被 commonmark 归为 HtmlBlock——代码注释明确写："表格单拎出来：落成段落会被按字符硬切、断面停在标签中间"→ 产出 `HtmlTableBlock`，由 `HtmlTableChunker` 保证每片是完整合法 HTML 表格。这是他们防"表格识别后被打散"的关键动作。
- 规整表格（表头+行的语义结构）存成 `TableBlock(headers, rows)`；**行式切分 + 逐行 `列名:值` 渲染成向量正文**（比 Markdown 表格文本更适合检索）；超宽表按 rowsPerChunk 分片，每片重复表头。
- Excel：POI 侧 `ExcelTableNormalizer` 处理**合并单元格展开（expandMergedRegions）、多行表头（按配置 headerRows 拍平、`|` 连接）、空列剔除、公式求值（FormulaEvaluator）、删除线 ~text~**；FIDELITY 档整表交给 MinerU 版面解析。

### 图片
- 独立图片文件（PNG/JPG/SVG）：`ImageDocumentParser` 用 VLM"中文描述 + 图中文字逐字 OCR"（描述提示词内置），空描述=解析失败（避免只入库一条 URL 永远召不回）；SVG 先用 Batik 铺白底栅格化成 PNG 再送 VLM。
- PDF/文档内嵌图：MinerU 抽出的图片在解包时**逐张上传对象存储换公开 URL**（assets/{documentId}/uuid.ext），图片引用地址（含 `./images/` 前缀差异）按 zip 内路径精确/文件名模糊匹配改写；**并串行调 VLM 给每张图生成描述**（单张失败只记日志不中断整篇）。段首独立图片提升为 `ImageBlock`（可被单独 chunk+检索），行内插图留在段落文本里保留 `![alt](url)`。

### 版面
- 版面（阅读顺序、标题层级、页眉页脚、双栏）的恢复**全部交给 MinerU 输出 markdown 的天然顺序**：解包器按 markdown AST 顺序产出有序 blocks；后续切分严格保持顺序，并靠标题大纲把正文"归属"到章节路径。ragent 自己没有 bbox/坐标/分栏检测逻辑，**也没有把 MinerU 可能带的页面信息（分页标记/裁切框）往下传**——见第 4 节局限。
- 上层可选的 LLM 兜底：PDF 示例管线在 parser 后插 enhancer，systemPrompt 是"文本排版与结构修复器"：合并被硬换行打断的句子、恢复标题层级与列表缩进、打散的表格只允许用文本方式（`\t`/`|`）恢复且**不得推断缺失单元格**、去页眉页脚页码水印仅当 100% 确认、逐字符保留原文禁止任何改写。

---

## 3. 对"文本碎片 / 乱序"的处理策略

代码里没有"版面坐标级重排"逻辑，但有**三层防碎片/防乱序**机制：

1. **源头结构化**（治本）：PDF 走 MinerU 拿到"已按版面排好序"的 markdown → 有序 Block。切分全程以"有序 Block 流 + 标题大纲"为准，chunk 序号单调递增，顺序信息天然保留。
2. **归一化 + 边界感知切分**（`TextSplitter`，细节很值得抄）：
   - `normalize()`：去 `\r`；**CJK 字被软换行拆开时合回**（"商\n保通 → 商保通"，只对 CJK 字且非标点）；**URL 跨行断裂修复**（遇 `http(s)://` 进入 URL 态，空白跨行时按前后字符决定合并，绝不合并空行——空行是段落分隔，也绝不合并下一行像 `2.`/`10)` 的列表项）。
   - 边界回溯顺序：换行 → 中文句末（。！？）→ 英文句末（. ! ?，**英文点必须后跟空白或结尾才算边界，否则会把 URL 域名点切开**）；回溯距离 = overlap。
3. **反碎片打包**（`ChunkPacker`）：碎屑并回前块、表格前导语捎进大块、节内切分残留回收到下一节——见第 1 节第 4 点。
4. **可选 LLM 整理节点**（EnhancerNode + PDF 示例里的强约束修复提示词）：合并错误换行、还原标题/列表/被打散表格、保守去页眉页脚页码。约束核心是"只修版式不改内容、不确定宁保留不猜"。

---

## 4. 哪些可直接借鉴，哪些不适用

### 可直接借鉴（对"语义切片 + 版面还原引擎"很有价值）

1. **统一有序 Block 中间表示作为解析→切分的契约**。sealed 类型 + 按类型分派 chunker + 冲突即启动失败，结构非常干净。你引擎的"版面还原结果"建议先归一成你自家的一等公民类型（paragraph/table/image/figure 等），切分阶段不许再回到纯字符串。
2. **展示文本与向量/检索文本分离**（ChunkAssembler + ChunkDraft.effectiveBody）：正文原样入库（要用于版面还原输出），检索文本可自由合成（补章节前缀、表格转 key-value、图片去 URL 噪声）。**这一条对"版面还原 + 检索"双目标是最实用的架构决策。**
3. **标题大纲（章节路径）在切分前先建好、注入每个 chunk 的元数据**，拼前缀时"只补正文缺失的那截路径"避免章节名重复占向量位。
4. **tolerance（maxChars×3）而非硬上限的决策模型**：优先保语义完整，其次才压缩；反碎片打包规则（碎屑回并、前导语捎带、残留回收、不足下限不单独成块）。
5. **表格两种形态分别处理**：HTML 表格整块按 `<tr>` 拆片并保持每片是完整合法 HTML；语义表格逐行 `列名: 值` 渲染成检索正文。
6. **CJK 软换行合并、URL 断行修复、句末标点回溯、中文英文边界优先级**——这正是你"文本切碎"问题的一大部分直接解药，可直接搬。
7. **图片"原图入库 + VLM 描述进检索文本"的双轨**（原图供版面还原/预览，描述供召回）。
8. **"认不出就报错不兜底" + 启动期自检注册表**：宁缺毋滥，避免某个坏解析器把版面还原结果污染成垃圾。
9. **MinerU 模式（作为参照）**：用成熟版面解析服务/模型产出 markdown + 图片裁切，工程侧做"结果归一化"而不是自己硬啃 PDF 内部对象模型。如果你引擎不缺自己实现版面检测，这条是"要不要自研 vs 调 MinerU/PDF-Extract-Kit/PP-Structure 类服务"的决策参照——他们最终选择了外包版面、自己做下游（表格防切、图片资产化、语义切分）。

### 不适用 / 需注意（诚实说明，不夸大）

1. **ragent 没有真正实现版面/坐标层**。`Provenance` 注释里写了"页码/bbox"，但实际字段只有 sourceFile+sheetName；MinerU 结果里页面级信息（如分页标记、裁切框、坐标）在解包时被丢弃。如果你的目标是把 PDF 还原成**带版面坐标**的段落/表格/图片，需要自己建模 bbox/page——ragent 没有现成方案，只能借鉴"结构归一化"部分。若你的输入已不是"还原 PDF 原貌"而是"做语义切片"，那 bbox 缺失不碍事。
2. **MinerU SaaS 是黑盒**：其版面/表格/公式识别的具体算法在外部服务里（mineru.net），仓库只含 HTTP 客户端与 zip→blocks 归一化，无任何可迁移的版面识别算法代码。你要的"表格/图片识别准"算法层，得从 MinerU/PDF-Extract-Kit 或自研模型获取。
3. **"文本乱序"没有坐标级重排**：乱序问题的解决完全押在 MinerU 的阅读顺序上。你引擎如果输入是"已经切碎乱序的文本"（而不是原始 PDF），ragent 的 block 流水线不直接适用，可借鉴的是第 3 节第 4 点的 LLM 修复提示词思路与 TextSplitter 归一化。
4. **Tika 的 PDF 部分在仓库里是死代码**（PDFParserConfig 未挂载、PDF 路由不到 Tika），不要照抄它当本地 PDF 解析方案。
5. **EnhancerNode 默认提示词很弱**（"修复格式错误/保持完整"三行），有效的修复提示词藏在 `docs/examples/pdf-pipeline-request.json`（管线示例），不是默认内置——参考时要看示例 JSON 而非 `EnhancerPromptManager`。
6. 反碎片打包与"合并块不做重叠"的取舍建立在"节边界 = 语义边界"假设上，对标题缺失的长文/分栏报刊类 PDF 不成立，借鉴时要保留字符级重叠兜底开关。

---

## 5. 3–5 条具体可操作建议（面向你的 PDF 版面还原引擎）

1. **先定中间表示，再写切分器**：把解析/版面还原输出归一成一份"有序 Block 流"（sealed 类型：Heading/Paragraph/Table(HtmlTable)/Image/List/Code），Block 上从一开始就带 `page + bbox + 阅读序 index` 三个溯源字段（ragent 漏了 bbox/page，你补上是关键差异点）；下游一律只消费这份结构，禁止切分阶段操作原始切碎文本。
2. **采用"展示文本 / 检索文本双轨"与 tolerance 决策模型**：正文原样渲染用于版面还原展示；检索文本另行合成（表格渲染成 `列名: 值` 逐行、图片用描述文本、续块自动补"正文缺失的章节前缀"）。整块在 maxChars×3 tolerance 内一律不切，超出才按"行 / 表格行 / 列表项 / 句末"降级切；碎片（<maxChars/4）并回前块，表格/代码前导语随块捎带。
3. **把 TextSplitter 的归一化直接搬走**：CJK 软换行合并（仅 CJK 字、非标点、跨空行不合并）、URL 断行修复（不进 URL 态不合并、不吞列表项行首）、边界回溯优先级 换行→。！？→. ! ?（英文点后必须空白/结尾），overlap 同时充当回溯最大距离。
4. **表格/图片识别不准 → 双保险**：结构上，HTML 表格整块处理、按 `<tr>` 行切片并让每片都是完整合法 `<table>`，绝不在标签中间断（直接解决"断面停在标签中间"）；识别层若自研不足，先接 MinerU（或开源 MinerU/PP-Structure）这类版面服务，工程侧做归一化、资产化（图片逐张上传换 URL + VLM 描述入向量），把"识别精度"问题外包，把"防打散/可检索/可还原"问题留给自己。
5. **乱序文本走"强约束 LLM 修复 + 确定性规则"双通道**：规则层（TextSplitter 归一化 + 表格/列表结构恢复）先行；规则覆盖不了的（页眉页脚页码、断行错乱、被打散表格）再走 LLM 修复节点，提示词照抄 PDF 示例的硬约束——只修版式、逐字符保留原文、表格缺失单元格**不得推断**、不确定宁保留不猜；并把 LLM 修复产物与规则产物做 diff 留痕，便于回滚。

---

## 附：未能核实/抓取到的内容（如实说明）

- MinerU SaaS 端版面/表格/公式识别的内部算法不可见（外部服务）；仓库仅含客户端与结果归一化。
- MinerU zip 内 markdown 的"分页标记/页眉格式"细节未在代码中处理，无法从仓库确认其确切格式（代码直接忽略）。
- 该仓库 PDF 本地解析（PDFBox/Tika）没有可用的生产实现，仅 POI(Excel)、commonmark(Markdown)、Tika(文本类) 在本地跑。
- 未逐一验证 MinerU 在线 API 的具体返回 JSON 字段（BatchSubmitRequest/Status 之外的字段名以 `MinerUClient` 内嵌 ObjectNode 构造为准，已读源码确认：`enable_formula/enable_table/language/files[{name,is_ocr,data_id}]`）。
