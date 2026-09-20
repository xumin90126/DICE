# Atomic Observation Layer — Architecture Challenge

> **本轮不是继续设计功能。** 目标 = 攻击 Candidate B, 判定它是真正的通用 Observation Layer,
> 还是换了名字的 IS-11/IS-14 detector/feature layer。经不起攻击则否决或缩减。
>
> READ-ONLY (除本文档)。不创建代码、不修改现有代码、不运行实验、不修改 MAP。
> 证据标签: **OBSERVED** (代码/artifact 可查) / **INFERRED** / **NOT ESTABLISHED**。
> 攻击对象: `tmp/phase4_research_object_design.md` 之 Candidate B (DESIGN_SUPPORTED_WITH_LIMITATIONS)。

---

## 0. 攻击前的新事实核查 (本轮 READ-ONLY 检索发现)

| # | 事实 | 影响 |
|---|------|------|
| F1 | `atomic_text.py:256`: **P1 显式跳过非文本块** (`if block_type != 0: # skip non-text blocks (images/drawings)`) | IMAGE atom 不是"补遗漏", 是**改冻结设计决定** — 需正面论证 |
| F2 | `region_config.py:39-42`: P6 曾设 VISUAL_REGION 后**删除**, 记录在案: *"P1 explicitly SKIPS non-text blocks … and '这是 Image' is forbidden. → deleted. Large gaps are recorded instead"* | **"IMAGE" 一词本身在冻结纪律中是语义雷区** — 命名必须避开 |
| F3 | P2 artifact (`rm501_p2_geometry_observations.json`) = 单验证文档 (RM501) + `max_pairwise=2000` 截断 + 报告导向 | **既有 P2 artifact 不是完整事实库** — "直接暴露既有 artifact" 不成立为唯一来源 |
| F4 | P2 `compute_page_bundle` 有 pairwise cap (168 spans→28k pairs 的可计算性截断) | 全对物化在冻结代码中即被承认不可行 → 层必须 query-scoped |
| F5 | P1/P2/P3/P4/P5/P6 artifact 均存在于 `tmp/perception/p1..p6/` (验证交付物形态) | 暴露层有真实锚点， 但覆盖范围 = 验证文档集 |

---

## 1. 第一攻击 — Relation 是否实际上是 Feature? (逐个审问 4 个 set-level relations)

### R-1 `UNIFORM_RUN_MEMBERSHIP`

| 问 | 答 |
|----|----|
| 事实还是解释? | "run 成员资格" = **带阈值的谓词** — 它把 "这 5 个原子构成均匀 run" 当作层的输出 → 阈值进入 observation 身份 [INFERRED: 越界] |
| 跨 hypothesis 复用? | 高 (任何 "序列状结构" 都想要) |
| 依赖 semantic role? | 否 |
| 包含 threshold? | 是 (min_run, cv_max, align_tol) |
| threshold 属于 relation 还是 query parameter? | **这是要害**: 分组/均匀性判据如果由层固定， 层就在替 hypothesis 做 "什么算 run" 的决定 |
| 需要 caption/table/axis/heading/sentence? | 否 |
| 不知道语义标签仍成立? | 成立 |
| IS-11/IS-14 删除后仍值得保留? | 见攻击十 |

**判定 [INFERRED]**: 以"成员资格谓词"形式 = **SEMANTIC_FEATURE 倾向** (阈值即语义决定)； 以"原始测量"形式 = observation。→ **缩减** (见 R1 refinement): 替换为 `GAP_SEQUENCE` 纯测量。

### R-2 `EQUIPACED_SEQUENCE` (数值等差)

| 问 | 答 |
|----|----|
| 事实还是解释? | "解析文本为数值并判等差" = **内容解读** — 数值性/等差性是对内容的语义化度量 |
| 依赖 semantic role? | 隐性依赖 "token 是数字" 的内容分类 |
| 不知道语义标签仍成立? | 成立， 但已经站在内容解释的斜坡上 |

**判定 [INFERRED]: SEMANTIC_FEATURE** — 数值解析与等差判断属 hypothesis 侧词法/统计。
Phase 3 已有先例: `value_delta_cv` 在冻结 OBS-C 中被明确降为 diagnostic (不参与判定)。
→ **删除**。

### R-3 `IDENTICAL_VALUE` (重复值)

| 问 | 答 |
|----|----|
| 事实还是解释? | 事实 (字符串相等) — 但 |
| 是否被 atom 已覆盖? | **是** — content 字段已暴露, 相等性是 hypothesis 一行代码 |

**判定 [INFERRED]**: 冗余 primitive → **删除** (层最小主义: atom 已暴露 content)。

### R-4 `IN_REGION`

| 问 | 答 |
|----|----|
| 事实还是解释? | 纯几何包含谓词 (点/bbox ∈ bbox) — 事实 |
| threshold? | 无 (包含是精确几何; boundary tolerance 属 RegionFact 自身 bbox) |
| 依赖 detector? | 依赖 RegionFact 的存在， 但不依赖其语义 |
| 不知道语义标签仍成立? | 成立 ("原子位于某确定性过程输出的区域 bbox 内") |

**判定: observation — 保留** (真正的 set/region 级事实接口)。

### 附: 既有 P2 关系 (SAME_LINE, PAIRWISE_GAP_X/Y, 对齐组, 同行带)

[OBSERVED] 纯几何、无语义、已在冻结代码中 — **保留** (它们正是层的既有基座)。

---

## 2. 第二攻击 — set-level 到底是什么意思?

| Option | 判定 |
|--------|------|
| 1 Atom-pair relation | 纯 observation (P2 已有) |
| 2 Local neighborhood observation | observation (窗口/近邻是几何定义; 只要窗口参数显式) |
| 3 Set-level derived pattern | **分界线在此**: "在给定几何分组的原子集合上计算闭式统计量 (gap 序列/CV/计数)" = observation; "识别出 axis tick run / 判定成员类别" = **pattern recognition → SEMANTIC_FEATURE** |

**任务原例的精确落点** [INFERRED]:
- "这是一个 axis tick run" → semantic leakage ✗
- "在给定窗口内存在 N 个数值 token, 满足某种几何关系" → 若"N 个**数值** token"由层判定 → 层在做内容分类 ✗； 若层只输出 "该几何分组的 gap 序列 = [...]", **数值性与 N 由 hypothesis 判定** → ✓ observation

**结论**: set-level 本身不是问题; 问题在于**谁做分词/分类/阈值决定**。层只做: 几何分组 (P2 既有) + 闭式统计 (新增 1 个) + 包含判定 (既有)。分词、内容分类、阈值后果 = hypothesis。

---

## 3. 第三攻击 — 参数纪律: 是不是可调 feature engine?

**边界定义 (本轮确立)** [INFERRED]:

> **Query parameter 可以筛选 observation, 不能改变 observation 本体。**
> 可操作化: 层函数输出 **measurement + params_hash**; 层**永不**输出类别谓词
> (`is_uniform=true` / `is_run_member`); 阈值后果由 hypothesis 计算并负责。

| Allowed parameters (查询条件) | Forbidden parameters (改变 observation 语义) |
|------------------------------|---------------------------------------------|
| 原子筛选: kind / page / region 过滤 | 每 hypothesis 私调 align_tol / cv_max 后把结果当 "层事实" |
| 读取哪个 relation 类型 / 哪个分组带 | 层内部按 hypothesis 临时改 gap 定义 (center vs edge) 而不改测量身份 |
| 窗口/范围界定 (query-scoped 计算) | detector 参数变化后仍复用旧 RegionFact 而不更新 provenance |

**残余难点 (诚实披露)**: 几何分组 (same_y_band) 本身需要容差 (浮点坐标)。处理: 分组容差 =
**测量身份的一部分** (registered profile, 固定+版本化, 对所有 hypothesis 一致), 不接受 per-hypothesis
调参; hypothesis 需要不同容差 → 注册新 profile (治理), 不得静默调参。
[INFERRED: 此纪律使层成为 "固定身份的测量目录", 而非 "可调 feature engine"]

---

## 4. 第四攻击 — IMAGE Atom

| 问 | 答 |
|----|----|
| 保存什么? | **仅**: page + bbox + PDF 自身声明的 block 类型 + 来源 provenance。无 OCR、无分类、无去重裁决 |
| 是 generic observable 吗? | **是** — "文档存在非文本块于位置 B" 是 PDF 结构事实, 与任何 IS 无关; 任何关于页面构成的 hypothesis 都需要 |
| 是 IS-14 hack 吗? | 否 — 但 [OBSERVED F1/F2] **存在两个真问题**: (a) P1 跳过非文本块是**在案设计决定**; (b) P6 已裁决 "'这是 Image' is forbidden" |
| 命名修正 | 原提案 `kind=IMAGE` 踩雷 → **改为 `NON_TEXT_BLOCK_ATOM` + `pdf_block_type` (PDF 自己的结构声明)** — 层不使用 "image/figure" 词汇, 与 P6 删除裁决的语义关切正交 (该裁决针对 *语义区域分类*; 本 atom 是 *PDF 结构事实*, content=null) |
| 与 P6 "large gaps instead" 路线冲突? | 不冲突 — P6 用大间隙近似不可见区域; NON_TEXT_BLOCK 提供直接事实, 两者并存, hypothesis 自选 |

**判定: 保留, 缩窄命名与字段** (presence/bbox/page/block_type — 4 项, 无一语义)。

---

## 5. 第五攻击 — RegionFact

| 问 | 答 |
|----|----|
| `TABLE_REGION` 是 semantic label 吗? | **是** — 原提案中任何 "table/graphic region" 类型名都是语义断言 → **从 schema 删除** |
| Geometry fact 形态 | RegionFact = "`source_detector@version/sha` 在 `params_hash` 下输出 bbox=B 的区域" — 是**关于 detector 主张的事实**, 不是 "这就是 table" |
| 为何仍属 observation? | detector 输出是确定性、可复现、可追溯的几何事实; 语义解读由 hypothesis 完成 (与 P7.1 "hypothesis ≠ fact" 纪律同构) |
| 如何防 provenance 被误当 ground truth? | (a) 字段名强制 `source_detector` (无 `region_type` 语义字段); (b) `params_hash` 必填; (c) 治理规则: RegionFact 永远是 "claim by D", hypothesis 引用时必须连 provenance 一起引用 |
| 多个 competing detectors? | **允许共存, 层不仲裁**: 同页可有 `region_source=A` 与 `region_source=B` 两个 RegionFact; `IN_REGION` 关系引用**具体** region_id → hypothesis 看到各自 provenance, 自行决定采信策略。层若仲裁 = 越权成为 decision layer |
| detector label 字段? | 删除 — label 可由 source_detector 身份重建, schema 不携带 |

**判定: 保留, 语义字段删除, 共存不仲裁**。

---

## 6. 第六攻击 — P1/P2 需要 replay 吗? (expose vs duplicate)

**新事实改变了 Phase 4 的论证** [OBSERVED F3/F5]: 既有 P1/P2 artifact 是**验证交付物**
(单测试文档、pair 截断、报告导向), **不是任意文档的完整事实库**。

| Option | 判定 |
|--------|------|
| A 全量 replay (重新解析) | 对已有 artifact 的文档 = **duplicating** (违反 expose-first 原则); 对无 artifact 文档 = 必要 |
| B 只读既有 artifact | 对覆盖内文档最优; **覆盖外不可用** (IS 实验文档大多无 P1/P2 持久 artifact) |
| **C 稳定 adapter (选定)** | **expose-first**: artifact 存在 → 直接暴露 (携带 artifact sha); 不存在 → **用冻结函数确定性重放并持久化为层内 artifact** (下次即暴露) |

**重放的正确形态** (关键细化): 重放**只允许调用冻结 P1/P2 函数** (read-only reuse — Stage 3/4
已验证的实践), **禁止层内重写几何数学**; 非相邻对关系按需计算 (query-scoped, 尊重 F4 可计算性
边界), 用**冻结的** `compute_pairwise`; IMAGE/NON_TEXT_BLOCK 枚举 = 唯一没有冻结函数覆盖的
新事实源 (最小新代码, 实验侧)。

| 判据 | C 之下的结果 |
|------|-------------|
| determinism | 同 PDF → 同 artifact → 同层输出; 重放调用冻结函数 |
| duplication | 最小化 (expose-first; 重放仅覆盖缺口) |
| provenance | 每事实携带 `geometry_source = artifact sha \| frozen function sha` |
| versioning | 层 artifact 独立版本化; 生成器身份必填 |
| computational cost | expose = O(1) 读; 重放 = 单文档一次性, 之后 O(1) |
| consistency risk | 由 "单一几何真源" 纪律消除 (攻击八) |

---

## 7. 第七攻击 — 与 CandidateSpan 的 "same document, different truth" 风险

**风险真实存在** [INFERRED]: candidate 轨道几何 = P1/P2/P4 冻结定义 (same_line_tolerance=3.0 等);
若层自带一套 gap/对齐计算, 同一文档会出现两套 "same_line"。

**既定纪律 (DESIGN, 不改 Frozen)**:

1. **Single source of geometric truth** = 冻结的 P1/P2/P4 定义, 以 **sha 引用**;
   层的 `same_line` / gap / 对齐 **必须**声明引用哪个冻结定义, 禁止层内平行几何数学。
2. **Coordinate contract**: 统一 PyMuPDF 页面坐标系, coord_origin 显式 (P6 已有此纪律, 层沿用)。
3. CandidateSpan frozen path 零修改 — 层是**同一真源的第二读者**, 不是第二真源。

---

## 8. 第八攻击 — 未知 IS-27 模拟

场景: 完全不知领域的 IS-27, 只知 "human feedback 反复发现某类 boundary error"。

```text
Human feedback (1-click 判断 × N, 无 reason)
  → 只读分歧/失败模式分析 (Phase 1 方法, 不需层配合)
  → hypothesis: "该类 error 与 <某种几何/集合模式> 相关"
  → declares: required_atoms = [TEXT_ATOM(, NON_TEXT_BLOCK_ATOM)]
              required_relations = [SAME_LINE, PAIRWISE_GAP_X, GAP_SEQUENCE, IN_REGION, …闭集内]
  → 层查询 (零 schema 变更) → 词法/统计解释 = hypothesis 自带
  → 预注册 protocol → GT → 评估
```

[INFERRED] **PASS**: 任何**几何/集合**模式可仅凭闭集声明; 任何**内容**模式由 hypothesis 词法
自含; 唯一需要触层的情形 = 出现真正新的几何测量类型 → 层版本升级 (治理, GT 前完成) —
这是**设计内**的扩展路径, 不是 schema 缺陷。

---

## 9. 第九攻击 — 删除 IS-11 / IS-14 的 thought experiment

若两者永久删除, Candidate B 是否仍是合理的 DICE 基础设施?

**YES** [INFERRED], 依据:
1. 它的实体 = P1-P6 冻结事实的**暴露层** — 这些事实与任何 IS 无关地存在;
2. Human Feedback → Machine Improvement 闭环 (Phase 1, LOOP_SUPPORTED) 的下一步**天然**需要
   "hypothesis 声明 observable" 的查询面 — 与具体 IS 无关;
3. 它消除的是结构性浪费 (每个 observer 重复解析 PDF — IS-11/IS-14 两个 observer 已各自实现
   一遍 [OBSERVED]);
4. Roadmap 阶段 1-2 的存在证明这是平台级意图, 非实验私器。

---

## 10. 第十攻击 — Anti-if/else test

未来 IS-15…18 连续到来:

| 反模式 | 是否复现? |
|--------|----------|
| `if table: … elif figure: …` (决策代码) | **否** — 层无决策面; hypothesis 侧的分类逻辑不进层 |
| `TableObservation / FigureObservation / AxisObservation / …` (schema 膨胀) | **否** — 原子/关系闭集固定; 新 hypothesis = 新**查询**, 不是新类 |
| 新 detector → 新 RegionFact 增多 | **会** — 但这是**数据增长**, 不是 schema 增长; 治理面 = detector 注册 (provenance), 层 schema 不动 |

[INFERRED] **PASS**, 附一条诚实边界: 层抵抗的是 **schema 层** if/else; detector 家族的扩张是
独立治理面, 层不负责阻止 (也不应负责 — RegionFact 共存机制已把裁决权留在 hypothesis)。

---

## 11. Candidate B 最终评分

| # | 维度 | 评分 (1-5) | 说明 |
|---|------|-----------|------|
| 1 | Genericity | 4→**4.5** | R1/R2 缩减后无内容解读原语 |
| 2 | Reusability | **5** | 八案例全覆盖 + 未知 hypothesis 声明制 |
| 3 | Semantic leakage risk | 3→**4.5** | 删 EQUIPACED/成员谓词/语义 region 名后仅剩纯几何+结构事实 |
| 4 | Frozen compatibility | **5** | 并行层 + 冻结函数只读复用; 零修改 |
| 5 | Determinism | **5** | expose-first + 冻结函数重放 + sha 全程 |
| 6 | Provenance | **5** | geometry_source / source_detector / params_hash 强制 |
| 7 | Versionability | **4.5** | 测量身份注册制; 层版本升级有治理路径 |
| 8 | Implementation complexity | **4** | adapter-first 成本低于 Phase 4 估计 (F3/F5 表明大部分可暴露) |
| 9 | Hypothesis independence | **5** | 声明制; 层不认识任何 hypothesis |
| 10 | Resistance to feature accumulation | 3→**4.5** | 闭集 + "删/缩优先"; detector 增长为独立治理面 (诚实边界) |

---

## 12. REQUIRED REFINEMENT (全部为删/缩, 零新增对象)

| # | Refinement | 类型 |
|---|-----------|------|
| **R1** | 关系集 4→2: 删 `EQUIPACED_SEQUENCE` (内容解读→hypothesis 侧); 删 `IDENTICAL_VALUE` (atom 已暴露); `UNIFORM_RUN_MEMBERSHIP` **降为 `GAP_SEQUENCE` 纯测量** (几何分组的有序 gap 序列, 无成员谓词); 保留 `IN_REGION` (纯包含) | **缩小** |
| **R2** | 参数纪律成文: 层输出 measurement+params_hash, **永不输出类别谓词**; 分组容差 = 注册测量身份 (全 hypothesis 一致), 禁 per-hypothesis 调参; 阈值后果归 hypothesis | 边界成文 |
| **R3** | `IMAGE_ATOM` → **`NON_TEXT_BLOCK_ATOM`** (+`pdf_block_type`, presence/bbox/page; 无 "image" 词汇 — 尊重 F2 冻结裁决; content=null 永久) | 缩窄 |
| **R4** | RegionFact 删语义类型名: 仅 `source_detector@sha + bbox + params_hash`; 多 detector 共存不仲裁; label 字段删除 | 缩小 |
| **R5** | **Expose-first adapter**: artifact 存在→暴露 (带 sha); 不存在→**冻结函数**确定性重放并持久化; 禁止层内重写几何数学; 唯一新代码 = NON_TEXT_BLOCK 枚举 | 修正来源策略 |
| **R6** | **Single source of geometric truth**: 层的 same_line/gap/对齐必须声明引用冻结定义 (sha); 统一坐标系 (P6 coord_origin 纪律沿用); 禁平行几何 | 一致性纪律 |

**未通过而需删除的对象**: 无 (经 R1-R4 缩减后全部原语通过攻击一/二)。
**新增对象**: 无 (R1 净减 2 个 relation; R3 仅改名缩窄)。

---

## 13. FINAL DESIGN STATUS

```text
╔══════════════════════════════════════════════════════════════╗
║  ARCHITECTURE VERDICT = B_SUPPORTED_WITH_REFINEMENT          ║
║  (R1–R6 为接受条件; 全部为删/缩, 零新增)                       ║
║                                                              ║
║  Candidate B (refined) = 冻结 P1-P6 事实的暴露层 +            ║
║  NON_TEXT_BLOCK 原子 + IN_REGION + GAP_SEQUENCE 纯测量        ║
║  + provenance/参数纪律 — 不是 detector/feature layer          ║
╚══════════════════════════════════════════════════════════════╝
```

**原 Phase 4 设计中被告倒并删除的部分**: `EQUIPACED_SEQUENCE` (内容解读),
`IDENTICAL_VALUE` (冗余), `UNIFORM_RUN_MEMBERSHIP` 谓词形式 (阈值语义化),
RegionFact 语义类型名, "IMAGE" 命名。
**设计因此变小** — 符合本轮原则: 宁可更小, 不为 IS-11/IS-14 做成 feature layer。

最终设计状态 (继承 Phase 4 框架, 经本轮缩窄):
**DESIGN_SUPPORTED_WITH_LIMITATIONS** (limitation 不变: raster 内容不可达 / 闭集版本治理 /
P1 block 层不稳定 → word-span 锚定 / detector 家族扩张为独立治理面)。

---

## 14. 最终治理

```text
ARCHITECTURE CHALLENGE = COMPLETE
IMPLEMENTATION = NOT AUTHORIZED
EVALUATION = NOT AUTHORIZED
GT = NOT AUTHORIZED
FROZEN MODIFICATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
PRODUCTION = FALSE
CAPABILITY REGISTRATION = NOT AUTHORIZED
RUNTIME INTEGRATION = NOT AUTHORIZED

NO CODE FILE CREATED
NO EXISTING CODE MODIFIED
NO NEW EXPERIMENT
NO MAP MODIFICATION
FROZEN BASELINE = INTACT

STOP = TRUE
WAIT FOR EXPLICIT AUTHORIZATION
```
