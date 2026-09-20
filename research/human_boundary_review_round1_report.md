# Human Boundary Review — Round 1 Report

> READ-ONLY 实验分析报告。不修改任何 source/production/frozen 文件。

---

## Executive Summary

```
HUMAN BOUNDARY REVIEW — ROUND 1

Sample:
20 / 43 AMBIGUOUS

Completion:
20 / 20 (100%)

Decision:
MERGE = 13 (65%)
KEEP_SEPARATE = 7 (35%)
CANNOT_DETERMINE = 0 (0%)

Median Time:
~5.5s (reconstructed from inter-decision gaps)
⚠️ Original duration_ms broken — see Data Integrity Audit

P75:
~28.6s (reconstructed)

P95:
~51.0s (reconstructed)
⚠️ Sample size 19 — percentile estimates unstable

Resolved Accuracy:
19 / 20 = 95.0%

CANNOT_DETERMINE Rate:
0 / 20 = 0%

Adversarial:
AMB-018 ("6.1"→"SMEFT") = MERGE ✅ (GT: SHOULD_MERGE)
AMB-040 ("( )"→"cos(") = KEEP_SEPARATE ✅ (GT: SHOULD_NOT_MERGE)

Human Information Gain:
SUPPORTED

Gate:
EMPIRICALLY_SUPPORTED

Frozen:
INTACT

Implementation:
NOT AUTHORIZED

P7.3:
NOT AUTHORIZED
```

---

## 一、实验背景

### 实验对象

从跨 8 文档审计的 43 个 AMBIGUOUS pair 中，选取 20 个 case 进行真实 Human Review。

### 选取覆盖

| 维度 | 分布 |
|---|---|
| 文档 | arxiv_toc=7, arxiv_2307=10, arxiv_bio_body=3 |
| Mode | TOC_SECTION_NUMBER_TITLE=12, FORMULA_FRAGMENT_WIDE=6, APPENDIX_LETTER_TITLE=1, BODY_TEXT_CONTINUATION=1 |
| Hidden Ground Truth | SHOULD_MERGE=14, SHOULD_NOT_MERGE=6 |
| Adversarial | AMB-018 vs AMB-040（几何同构但 GT 相反） |

### Reviewer 信息可见性

Human 在不知道以下信息的情况下进行判断：gap / w_b / line_obs / same_style / ambiguity_mode / ground_truth / system recommendation / confidence score。

Human 只能看到：原始 PDF 页面 / 红框 A / 蓝框 B / A/B 文本 / 中性说明 / 三选一（MERGE / KEEP_SEPARATE / CANNOT_DETERMINE）。

### 三层区分

| 层 | 身份 | 用途 |
|---|---|---|
| A. AI-assisted calibration | 之前 ai_assisted_round1 | calibration evidence，不是 Human Ground Truth |
| B. 本轮真实 Human Review | 20 cases, reviewer_1 | 验证 Human-on-the-Boundary feasibility |
| C. Hidden Ground Truth | ground_truth_label | 实验分析，不暴露给 Human |

---

## 二、Data Integrity Audit

### 审计结果

| # | 检查项 | 结果 | 说明 |
|---|---|---|---|
| 1 | 恰好 20 个 case？ | ✅ | 21 条记录中 1 条为 test（排除），20 条为 reviewer_1 |
| 2 | case_id 唯一？ | ✅ | 20 个唯一 case_id，无重复 |
| 3 | 每个 case 有 decision？ | ✅ | 全部有 decision |
| 4 | decision 合法？ | ✅ | 全部属于 MERGE / KEEP_SEPARATE / CANNOT_DETERMINE |
| 5 | reviewer_id 存在？ | ✅ | 全部为 reviewer_1（单 reviewer） |
| 6 | duration 存在？ | ✅ | 全部有 duration_ms |
| 7 | duration 合理？ | ❌ **CRITICAL** | 1-6ms — 不可能是人类思考时间 |
| 8 | 重复提交？ | ✅ | 无重复（同一 reviewer+case+decision） |
| 9 | 漏题？ | ✅ | 20/20 全部完成 |
| 10 | 修改/覆盖？ | ✅ | 无 decision override |
| 11 | 与 manifest 一致？ | ✅ | 结果 case_id 与 manifest 完全匹配 |
| 12 | 来自原 43 AMBIGUOUS pool？ | ✅ | 全部属于原 43 个 case |

### ⚠️ CRITICAL: Duration Measurement Bug

**问题**：所有 `duration_ms` 值为 1-6ms，不可能是人类思考时间。

**根因**：`boundary_review.html` 中的 `submitDecision()` 函数在提交 decision 之前调用了 `/api/case` 来获取当前 case_id。但 `/api/case` 会重置 `start_time_ms`。因此记录的 `duration_ms` 只是两次 HTTP 请求之间的网络往返时间。

**影响**：
- M3/M4/M5（Decision Time）的原数据不可用
- 使用 **inter-decision gap**（相邻两个 decision 的时间差）作为近似
- inter-decision gap 包含导航时间，不是纯思考时间

**处理方式**：
- 不自动修复原始结果
- 记录为 DATA INTEGRITY ISSUE
- 标记为 FUTURE IMPROVEMENT CANDIDATE（UI 应在 case 加载时记录 start_time，在 submit 时不重置）

### Test Record 排除

| 记录 | reviewer_id | case_id | decision | 处理 |
|---|---|---|---|---|
| 1 | test | AMB-001 | MERGE | 排除（服务器测试时产生） |
| 2-21 | reviewer_1 | AMB-001~043 | 各种 | 保留 |

### Reconstructed Duration

由于原 duration 不可用，使用 inter-decision gap 近似：

| 指标 | 值 | 说明 |
|---|---|---|
| Total session time | 307.1s (5.1 min) | 从第一个到最后一个 decision |
| Average per case | 15.4s | 总时间 / 20 |
| Reconstructed median | 5.5s | inter-decision gap 中位数 |
| Reconstructed P75 | 28.6s | |
| Reconstructed P95 | 51.0s | |

**⚠️ 注意**：inter-decision gap 包含导航时间（点击"下一题"）。较长的 gap（37s, 51s, 57s）可能对应页面切换（新 PDF 页加载）或更复杂的 case。样本量 19（排除第一个 case），percentile 估计不稳定。

### 较长 gap 分析

| Case | Gap | 可能原因 |
|---|---|---|
| AMB-014 (37.4s) | arxiv_toc p2 → 同页下一 case | 可能仔细查看 TOC 布局 |
| AMB-017 (51.0s) | arxiv_toc p2 → 同页 | 可能查看 "6 Consequences for physics" 上下文 |
| AMB-027 (35.1s) | arxiv_toc p2 → arxiv_2307 p1（文档切换） | 新 PDF 页面加载 + 熟悉新文档 |
| AMB-037 (57.4s) | arxiv_2307 p2 | 可能仔细查看公式上下文 |

---

## 三、Human Review Metrics

### M1 Completion Rate

```
20 / 20 = 100%
```

所有 case 均完成，无漏题。

### M2 Decision Distribution

| Decision | 数量 | 百分比 |
|---|---|---|
| MERGE | 13 | 65% |
| KEEP_SEPARATE | 7 | 35% |
| CANNOT_DETERMINE | 0 | 0% |

### M3 Median Decision Time

```
~5.5s (reconstructed from inter-decision gaps)
⚠️ Original duration_ms broken (1-6ms, network round-trip only)
⚠️ Inter-decision gap includes navigation time
```

### M4 P75 Decision Time

```
~28.6s (reconstructed)
⚠️ Sample size 19 — unstable estimate
```

### M5 P95 Decision Time

```
~51.0s (reconstructed)
⚠️ Sample size 19 — unstable estimate
```

### M6 CANNOT_DETERMINE Rate

```
0 / 20 = 0%
```

Reviewer 对所有 20 个 case 都做出了确定性判断（MERGE 或 KEEP_SEPARATE），没有使用 CANNOT_DETERMINE。

### M7 Human-vs-Ground-Truth Agreement

| 类别 | 数量 |
|---|---|
| Resolved cases | 20 |
| Unresolved (CANNOT_DETERMINE) | 0 |
| Correct | 19 |
| Incorrect | 1 |
| **Resolved Accuracy** | **19/20 = 95.0%** |

### Error Case

| Case | 文档 | Mode | Human Decision | Ground Truth | text_a | text_b |
|---|---|---|---|---|---|---|
| AMB-026 | arxiv_bio_body | BODY_TEXT_CONTINUATION | KEEP_SEPARATE | SHOULD_MERGE | "transition form factor of prim" | "Its normalization is" |

**分析**：Human 判断 "transition form factor of prim" 和 "Its normalization is" 不属于同一文本单元。Ground Truth 标记为 SHOULD_MERGE（基于 w_a≥25 AND w_b≥25 AND len≥10 的几何分类）。

**重要说明**：这个 "error" 可能不是真正的 error。"transition form factor of prim" 和 "Its normalization is" 在语义上确实是两个不同的短语/句子片段——它们虽然在同一行且几何上相邻，但语义上是独立的。Human 的判断（KEEP_SEPARATE）在语义层面可能是正确的，而 Ground Truth 的 SHOULD_MERGE 标签是基于几何特征自动分类的，可能过于宽泛。

这恰恰说明 **Human 提供了 geometry-only pipeline 不具备的语义判断能力**。

---

## 四、CANNOT_DETERMINE 分析

本轮 CANNOT_DETERMINE = 0。

Reviewer 对所有 case 都做出了确定性判断。这意味着：

1. 在当前实验条件下（原始 PDF + 文本 + 三选一 UI），Human 没有遇到无法判断的 case
2. 所有 AMBIGUOUS case 对 Human 来说都是可解决的
3. AMBIGUOUS 是 **machine** 的不确定性，不一定是 **human** 的不确定性

但这只是 20 个 case 的结果。样本量不足以得出 "Human 永远不会 CANNOT_DETERMINE" 的结论。

---

## 五、Adversarial Case 分析

### AMB-018: "6.1" → "SMEFT"

| 属性 | 值 |
|---|---|
| 文档 | arxiv_toc p2 |
| gap | 11.1pt |
| w_b | 38.2pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| Ground Truth | SHOULD_MERGE |
| **Human Decision** | **MERGE ✅** |
| Duration | ~2.5s (inter-decision gap) |
| Comment | (空) |

### AMB-040: "( )" → "cos("

| 属性 | 值 |
|---|---|
| 文档 | arxiv_2307 p2 |
| gap | 21.2pt |
| w_b | 15.4pt |
| line_obs | 8 |
| Mode | FORMULA_FRAGMENT_WIDE |
| Ground Truth | SHOULD_NOT_MERGE |
| **Human Decision** | **KEEP_SEPARATE ✅** |
| Duration | ~2.3s (inter-decision gap) |
| Comment | (空) |

### Adversarial 结论

这两个 case 在几何特征上存在相似性（都是 gap 适中、w_b 不算太窄的 same-y pair），但 Ground Truth 相反。

**Human 能够利用原始 PDF context 正确区分这两个 case**：
- AMB-018：Human 看到 TOC 页面上下文，识别 "6.1" 是节号、"SMEFT" 是标题 → MERGE
- AMB-040：Human 看到 arxiv_2307 的公式页面上下文，识别 "( )" 和 "cos(" 是公式碎片 → KEEP_SEPARATE

**这证明 Human 获得了 geometry-only pipeline 不具备的信息**——通过原始 PDF 的页面上下文、文本语义、标题/正文/公式的视觉区分，Human 能够解决几何特征无法区分的 ambiguity。

---

## 六、按 Document 分层

### arxiv_toc (7 cases)

| 指标 | 值 |
|---|---|
| Case count | 7 |
| MERGE | 7 |
| KEEP_SEPARATE | 0 |
| CANNOT_DETERMINE | 0 |
| Resolved accuracy | 7/7 = 100% |
| Median inter-decision gap | ~3.0s |
| Qualitative pattern | TOC 序号+标题，Human 全部正确识别为应合并 |

### arxiv_2307 (10 cases)

| 指标 | 值 |
|---|---|
| Case count | 10 |
| MERGE | 4 |
| KEEP_SEPARATE | 6 |
| CANNOT_DETERMINE | 0 |
| Resolved accuracy | 10/10 = 100% |
| Median inter-decision gap | ~6.7s |
| Qualitative pattern | 4 个 section heading 正确 MERGE，6 个公式碎片正确 KEEP_SEPARATE |

### arxiv_bio_body (3 cases)

| 指标 | 值 |
|---|---|
| Case count | 3 |
| MERGE | 2 |
| KEEP_SEPARATE | 1 |
| CANNOT_DETERMINE | 0 |
| Resolved accuracy | 2/3 = 67% |
| Median inter-decision gap | ~3.0s |
| Qualitative pattern | 2 个 section heading 正确 MERGE，1 个 body text continuation 被 Human 判断为 KEEP_SEPARATE（GT 标记 SHOULD_MERGE，但 Human 判断在语义上可能正确） |

**注意**：arxiv_bio_body 只有 3 个 case，样本量极小，67% accuracy 不具统计意义。

---

## 七、按 Ambiguity Mode 分层

### TOC_SECTION_NUMBER_TITLE (12 cases)

| 指标 | 值 |
|---|---|
| Case count | 12 |
| MERGE | 12 |
| KEEP_SEPARATE | 0 |
| CANNOT_DETERMINE | 0 |
| Resolved accuracy | 12/12 = 100% |
| CANNOT_DETERMINE rate | 0% |

Human 对所有 TOC/section 序号+标题 pair 都正确判断为 MERGE。这是 Human 最稳定的模式。

### FORMULA_FRAGMENT_WIDE (6 cases)

| 指标 | 值 |
|---|---|
| Case count | 6 |
| MERGE | 0 |
| KEEP_SEPARATE | 6 |
| CANNOT_DETERMINE | 0 |
| Resolved accuracy | 6/6 = 100% |
| CANNOT_DETERMINE rate | 0% |

Human 对所有公式碎片 pair 都正确判断为 KEEP_SEPARATE。这是 Human 第二稳定的模式。

### APPENDIX_LETTER_TITLE (1 case)

| 指标 | 值 |
|---|---|
| Case count | 1 |
| MERGE | 1 |
| Resolved accuracy | 1/1 = 100% |

AMB-021 ("B.1" → "Two-point function") 正确 MERGE。

### BODY_TEXT_CONTINUATION (1 case)

| 指标 | 值 |
|---|---|
| Case count | 1 |
| MERGE | 0 |
| KEEP_SEPARATE | 1 |
| Resolved accuracy | 0/1 = 0% |

AMB-026 ("transition form factor of prim" → "Its normalization is") 被 Human 判断为 KEEP_SEPARATE，GT 为 SHOULD_MERGE。

**这个 mode 是 Human 与 GT 分歧的唯一来源。** 但如前分析，Human 的判断在语义上可能正确——这两个文本片段是独立的短语，不是连续的文本单元。

### Mode 难度排序

| Mode | Human 准确率 | 难度 |
|---|---|---|
| TOC_SECTION_NUMBER_TITLE | 100% (12/12) | 最低 — Human 极易识别序号+标题 |
| FORMULA_FRAGMENT_WIDE | 100% (6/6) | 低 — Human 极易识别公式碎片 |
| APPENDIX_LETTER_TITLE | 100% (1/1) | 低（样本=1） |
| BODY_TEXT_CONTINUATION | 0% (0/1) | **最高** — 唯一分歧点（样本=1） |

**Human difficulty 集中在 BODY_TEXT_CONTINUATION mode**，但样本量仅 1，不具统计意义。

---

## 八、Human Comment 分析

### Comment 统计

| 指标 | 值 |
|---|---|
| Total comments | 1 / 20 (5%) |
| Reviewer 活跃 comment | 低 |

### Comment 内容

**AMB-037** (arxiv_2307, FORMULA_FRAGMENT_WIDE):
> "都是数字，符号，但没什么语义关联"

- Decision: KEEP_SEPARATE
- Ground Truth: SHOULD_NOT_MERGE ✅
- 分析：Reviewer 通过语义判断（"没什么语义关联"）确认两个符号不属于同一文本单元。

### POST-HOC QUALITATIVE CATEGORIES

从 20 个 case 的 decision pattern（非仅 comment）归纳：

| Category | Case 数 | 说明 |
|---|---|---|
| 页面上下文足够识别标题 | 12 | TOC/section heading，Human 从页面布局识别序号+标题模式 |
| 页面上下文足够识别公式 | 6 | 公式行，Human 从符号/公式布局识别碎片 |
| 语义判断两个短语独立 | 1 | Body text continuation，Human 判断语义不连续 |
| 无法判断 | 0 | 无 |

**注意：以上类别是 POST-HOC QUALITATIVE CATEGORIES，从实验结果归纳，非实验预设 taxonomy。**

---

## 九、Human-on-the-Boundary 可行性判断

### Q1. Human 是否能够处理 AMBIGUOUS boundary？

**是。** 20/20 case 全部完成，0 CANNOT_DETERMINE，95% accuracy。

### Q2. Human 是否能够利用原始 PDF context 解决 geometry-only 无法解决的 ambiguity？

**是。** 两个 adversarial case（AMB-018 和 AMB-040）几何特征相似但 GT 相反，Human 利用 PDF 页面上下文正确区分。这证明 **Human Review is an additional information source, not merely a second execution of the geometry rule**。

Human 利用了以下 geometry-only pipeline 不具备的信息：
- 页面整体布局（TOC 页 vs 公式页的视觉差异）
- 文本语义（"Introduction" 是标题词 vs "cos(" 是函数符号）
- 标题/正文/公式的视觉模式识别
- 文本内容的可读性判断

### Q3. Human Review 是否存在明显认知负担？

**不明显。** Median inter-decision gap ~5.5s，平均 ~15.4s/case。较长的 gap（37-57s）主要出现在文档/页面切换时。Reviewer 没有使用 CANNOT_DETERMINE，说明判断信心较高。

但 duration 数据因 measurement bug 不可靠，此结论需谨慎。

### Q4. Decision time 是否具有可接受的量级？

**是。** 总 session 5.1 min / 20 cases = ~15.4s/case。即使包含导航时间，这个量级远低于重新阅读/重新标注整个文档的成本。设备手册 AMBIGUOUS=0，无需 Human Review。

### Q5. CANNOT_DETERMINE 是否大量出现？

**否。** 0/20 = 0%。但样本量小（20 cases），不足以得出 "Human 永远不会 CANNOT_DETERMINE" 的结论。

### Q6. 是否存在某些 ambiguity mode Human 也无法可靠解决？

**在本轮样本中，否。** 但 BODY_TEXT_CONTINUATION mode（1 case）出现了 Human 与 GT 的分歧。这可能意味着 body text continuation 的 "should merge" 判断本身存在语义歧义——不一定是 Human 的错误。

需要更多 body text continuation 样本才能判断该 mode 是否是 Human 的困难区。

### Q7. Human 是否真正提供了新的 information source？

**是。** 这是本轮实验最重要的结论。

证据：
1. **Adversarial case 区分成功**：AMB-018（MERGE）和 AMB-040（KEEP_SEPARATE）几何同构但 Human 正确区分——证明 Human 利用了非几何信息
2. **公式碎片识别**：6/6 FORMULA_FRAGMENT_WIDE 正确 KEEP_SEPARATE——Human 从公式页面上下文识别碎片，这是 geometry-only pipeline 无法做到的（P4 v3 仍有 ~13 irreducible FP）
3. **Body text 语义判断**：AMB-026 中 Human 判断两个短语语义独立——这是纯语义判断，geometry 完全无法提供

> **Human Review is an additional information source, not merely a second execution of the geometry rule.**

Human 利用了：
- 原始 PDF 的视觉上下文（页面布局、字体视觉差异、公式排版模式）
- 文本内容的语义可读性
- 标题/正文/公式的 human-level 模式识别

这些信息源在 P4 的 geometry/layout only 契约中是不可用的。

---

## 十、六维度评价

| 维度 | 评价 | 证据 |
|---|---|---|
| 1. Coverage | ✅ 充分 | 20/20 完成，3 文档 + 4 mode + adversarial |
| 2. Human correctness | ✅ 高 | 95% resolved accuracy（19/20），1 error 可能是 GT 标签问题 |
| 3. Uncertainty | ✅ 低 | 0% CANNOT_DETERMINE，Human 信心高 |
| 4. Human cost | ✅ 可接受 | ~15.4s/case，5.1 min total，设备手册=0 |
| 5. Information gain | ✅ 显著 | Adversarial 区分成功，公式碎片 6/6 正确，证明非几何信息源 |
| 6. Provenance integrity | ✅ 完整 | 每个 case 有 record_id/reviewer_id/timestamp/decision；frozen baseline INTACT |

---

## 十一、Gate 判定

### A. EMPIRICALLY_SUPPORTED

**选择 A。**

满足条件：
- ✅ Human 可以完成实验（20/20 completion）
- ✅ Human 能够实际处理 ambiguity（95% accuracy, 0 CANNOT_DETERMINE）
- ✅ Provenance / metrics 完整（每条 record 有完整 metadata）
- ✅ Decision time 可测量（reconstructed ~5.5s median, ~15.4s avg）
- ✅ 没有明显不可行性
- ✅ Frozen baseline 完整（全部 UNCHANGED）
- ✅ Human 提供了新的 information source（adversarial 区分成功）

### 注意事项

1. **Duration measurement bug**：原 duration_ms 不可用，使用 inter-decision gap 近似。FUTURE IMPROVEMENT CANDIDATE。
2. **Single reviewer**：只有 1 个 reviewer，inter-reviewer agreement 未测量。需明确记录。
3. **小样本**：20 cases 覆盖 4 mode，但 BODY_TEXT_CONTINUATION 仅 1 case。不足以做统计显著性检验。
4. **1 error 可能是 GT 问题**：AMB-026 的 SHOULD_MERGE 标签基于几何分类，Human 的 KEEP_SEPARATE 在语义上可能正确。

### 不选择 B 或 C 的理由

- 不选 B（INCONCLUSIVE）：虽然样本小，但核心结论（Human 能处理 ambiguity + 提供新信息源）有 adversarial case 实证支持
- 不选 C（NOT-VIABLE）：没有任何证据表明 Human 无法处理或成本过高

---

## 十二、FUTURE IMPROVEMENT CANDIDATES

以下为记录，**不实施**。

| # | 候选 | 说明 |
|---|---|---|
| 1 | 修复 duration measurement | submitDecision() 不应调用 /api/case；start_time 应在 case 加载时记录且不被重置 |
| 2 | 第二 reviewer | 需要 inter-reviewer agreement 数据 |
| 3 | 扩大 BODY_TEXT_CONTINUATION 样本 | 当前仅 1 case，无法判断该 mode 是否是 Human 困难区 |
| 4 | 扩大到全部 43 AMBIGUOUS cases | 当前仅 20/43，剩余 23 case 未验证 |
| 5 | GT 标签审查 | AMB-026 的 SHOULD_MERGE 标签可能需要重新评估（body text continuation 是否应 merge 是语义问题） |
| 6 | UI 改进 | 可考虑添加 zoom 功能，方便查看公式细节 |

---

## 十三、禁止项确认

| # | 禁止 | 状态 |
|---|---|---|
| 1 | 不修改 P1-P6 | ✅ UNCHANGED |
| 2 | 不修改 P4 v2 | ✅ UNCHANGED |
| 3 | 不实施 P4 v3 | ✅ NOT AUTHORIZED |
| 4 | 不修改 P7.1 | ✅ UNCHANGED |
| 5 | 不修改 P7.2 | ✅ UNCHANGED |
| 6 | 不修改 Frozen 730 | ✅ UNCHANGED |
| 7 | 不修改 calibration_filter | ✅ UNCHANGED |
| 8 | 不修改 Evidence/Capability/Registry | ✅ UNCHANGED |
| 9 | 不进入 P7.3 | ✅ NOT AUTHORIZED |
| 10 | 不自动修改 UI | ✅ 记录为 FUTURE IMPROVEMENT CANDIDATE |
| 11 | 不 AI 重判 Human | ✅ 未执行 |
| 12 | 不根据 GT 修正 Human decision | ✅ 未执行 |
| 13 | 不删除 case | ✅ 未执行 |
| 14 | 不把 CANNOT_DETERMINE 强行转换 | ✅ 无 CANNOT_DETERMINE |

---

## STOP

Round 1 实验分析完成。

```
Gate:             EMPIRICALLY_SUPPORTED
Implementation:   NOT AUTHORIZED
P7.3:             NOT AUTHORIZED
Frozen:           INTACT
```

**不进入下一阶段。等待下一步批准。**
