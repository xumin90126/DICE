# Human Boundary Review Round 1 — Independent Audit & Measurement Integrity Review

> READ-ONLY audit。不修改任何 source/production/frozen 文件。不修复 bug。不修改 GT。

---

## Executive Summary

```
DATA INTEGRITY
- Case records = PASS
- Decision records = PASS
- Duration measurement = INVALID
- Ground Truth integrity = DISPUTED (AMB-026)

HUMAN FEASIBILITY
- Completion = 20/20
- MERGE = 13
- KEEP_SEPARATE = 7
- CANNOT_DETERMINE = 0
- Raw GT accuracy = 19/20 = 95.0%
- Disputed-case adjusted view = 19/19 = 100.0% (仅辅助)
- Adversarial resolution = PASS

INFORMATION GAIN
= SUPPORTED (limited to tested cases)

HUMAN COST
= INVALID (original duration_ms broken; inter-decision gap APPROXIMATE ONLY)

OVERALL:
EMPIRICALLY_SUPPORTED

Implementation:
NOT AUTHORIZED

P7.3:
NOT AUTHORIZED
```

---

## 一、Duration Measurement Integrity

### Q1. 是否存在任何字段能够直接代表真实 case-level Human review duration？

**否。**

每条 record 包含以下时间字段：

| 字段 | 来源 | 含义 | 可用? |
|---|---|---|---|
| `start_time_ms` | `/api/case` handler (server L113) | 服务器收到 case 请求时的时间戳 | ❌ 被污染 |
| `decision_time_ms` | `/api/submit` handler (server L155) | 服务器收到 submit 时的时间戳 | ✅ 可信 |
| `duration_ms` | `decision_time_ms - start_time_ms` (server L163) | 两个服务器时间戳之差 | ❌ 不可信 |
| `timestamp` | `time.strftime` (server L191) | `decision_time_ms` 的人类可读格式 | ✅ 可信 |

**Bug 根因**：

`boundary_review.html` 的 `submitDecision()` 函数（L230-276）在提交 decision 之前调用了 `/api/case`（L235）来获取当前 `case_id`：

```javascript
async function submitDecision(decision) {
  // ...
  // Get current case_id from the loaded case
  const res = await fetch(`/api/case?reviewer_id=${...}&index=${currentIndex}`);  // ← L235: THIS RESETS start_time_ms
  const data = await res.json();
  // ...
  const submitRes = await fetch('/api/submit', { ... });  // ← L254: submit uses the reset start_time
}
```

服务器端 `/api/case` handler（L109-113）在每次请求时都会重置 `start_time_ms`：

```python
_state["session_start"][reviewer_id][case["case_id"]] = int(time.time() * 1000)  # ← L113: OVERWRITES
```

因此 `duration_ms = decision_time_ms - start_time_ms` = `/api/case` 响应到 `/api/submit` 收到的间隔 = **网络往返时间（1-6ms）**，不是人类思考时间。

**实际 duration_ms 值**：全部 20 条记录的 `duration_ms` 为 1-6ms。

### Q2. 当前 reconstructed inter-decision gap 的定义是什么？

**定义**：`gap[i] = decision_time_ms[i] - decision_time_ms[i-1]`

即：相邻两个 case 的 submit 时间戳之差。

这假设 reviewer 按顺序完成 case（实际确实如此——从 timestamp 序列可验证 case 顺序与 manifest 顺序一致）。

### Q3. 它是否可能混入其他因素？

**是。** inter-decision gap 混入了以下成分：

| 成分 | 说明 | 可分离? |
|---|---|---|
| CASE_NAV | 点击"下一题"的 UI 交互时间 | ❌ |
| IMAGE_LOAD | 新页面图片 HTTP 加载时间 | ❌ |
| HUMAN_THINK | Human 阅读和判断时间 | ❌ |
| HUMAN_DECIDE | Human 点击 decision 按钮 | ❌ |
| API_SUBMIT | `/api/submit` 网络往返 | ❌ |
| DOC_SWITCH | 文档切换时的新 PDF 页加载（AMB-021→023, AMB-026→027 等） | ❌ |
| IDLE_TIME | Human 可能暂停/分心 | ❌ |

**没有任何成分可以被分离。** inter-decision gap 是这些成分的总和，无法提取纯 HUMAN_THINK 时间。

### Q4. 能否作为正式 Human Cost metric？

**否。**

```
HUMAN COST = INVALID
```

标记为 `UNRELIABLE_FOR_FORMAL_COST_METRIC`。

理由：
1. 原始 `duration_ms` 完全无效（1-6ms = 网络往返）
2. inter-decision gap 混入 6+ 种非思考成分
3. 无法分离纯人类判断时间
4. 样本量 19（排除第一个 case），percentile 估计不稳定
5. 较长的 gap（37s, 51s, 57s）无法区分是"思考时间长"还是"文档切换/idle"

inter-decision gap 仅可用于**粗略量级估计**（总 session 5.1 min / 20 cases = ~15.4s/case），不可用于：
- 正式 Human Cost metric
- percentile 报告（P75/P95）
- 与其他 review 方式的成本比较

### Q5. 最小 instrumentation fix 设计（只描述，不实施）

#### Timer Lifecycle 设计

```
State Machine:
  CASE_OPEN → CASE_DISPLAYED → HUMAN_DECISION → CASE_SUBMITTED

Timestamps to record:
  1. case_open_ts:   loadCase() 被调用时（客户端，在 fetch /api/case 之前）
  2. case_displayed_ts: 页面图片 onload 完成时（客户端，图片渲染完毕）
  3. decision_click_ts: Human 点击 decision 按钮时（客户端）
  4. case_submitted_ts: /api/submit 服务器收到时（服务端）

Derived durations:
  - load_time = case_displayed_ts - case_open_ts     (图片加载时间)
  - think_time = decision_click_ts - case_displayed_ts (纯人类思考时间)
  - submit_rtt = case_submitted_ts - decision_click_ts  (网络往返)
  - total_case_time = case_submitted_ts - case_open_ts  (总 case 时间)
```

#### 修复要点

1. **客户端记录 `case_open_ts`**：在 `loadCase()` 函数开头记录 `Date.now()`
2. **客户端记录 `case_displayed_ts`**：在图片 `onload` 事件中记录
3. **客户端记录 `decision_click_ts`**：在 `submitDecision()` 函数开头记录（在 fetch /api/case 之前）
4. **客户端发送所有 timestamp**：在 `/api/submit` body 中包含 `case_open_ts`、`case_displayed_ts`、`decision_click_ts`
5. **服务端不再在 `/api/case` 中设置 `start_time_ms`**：移除 L109-113 的 session_start 记录
6. **服务端计算 `think_time`**：`think_time = decision_click_ts - case_displayed_ts`

#### Persistence

- `think_time` 存入 record 的独立字段
- `total_case_time` 存入 record 的独立字段
- `load_time` 存入 record 的独立字段（用于分析图片加载是否影响 review 体验）

**此修复不实施。标记为 FUTURE IMPROVEMENT CANDIDATE。**

---

## 二、AMB-026 GT Dispute Audit

### AMB-026 完整 metadata

| 字段 | 值 |
|---|---|
| case_id | AMB-026 |
| doc_id | arxiv_bio_body |
| page | 5 |
| text_a | "transition form factor of primary interest to us." |
| text_b | "Its normalization is" |
| w_a | 237.2pt |
| w_b | 95.4pt |
| h_gap | 9.9pt |
| dy | 0.0pt |
| same_style | True |
| line_obs_count | 8 |
| ambiguity_mode | BODY_TEXT_CONTINUATION |
| ground_truth_label | SHOULD_MERGE |
| Human decision | KEEP_SEPARATE |
| Human comment | (空) |

### Q1. 原 GT SHOULD_MERGE 是依据什么产生的？

GT 由 `extract_ambiguous.py` 中的以下逻辑产生：

```python
is_body_continuation = (
    wa >= 25 and wb >= 25
    and len(ta) >= 10 and len(tb) >= 10
)
is_true_merge = is_toc_num_title or is_appendix or is_body_continuation
gt_label = "SHOULD_MERGE" if is_true_merge else "SHOULD_NOT_MERGE"
```

AMB-026 匹配了 `is_body_continuation`（w_a=237≥25, w_b=95≥25, len(ta)=49≥10, len(tb)=20≥10），因此 GT = SHOULD_MERGE。

### Q2. 该 GT 是什么类型？

**Geometry-based label。**

| GT 类型 | 是否? | 证据 |
|---|---|---|
| Geometry-based label | ✅ 是 | 基于 w_a, w_b, len(text_a), len(text_b) 四个几何/长度特征 |
| Semantic label | ❌ 否 | 没有分析文本内容的语义关系 |
| Manual expert label | ❌ 否 | 没有人工标注 |
| Derived label | ✅ 是 | 从 P1/P4 几何特征自动派生 |

GT 是**纯几何分类规则的产物**，不是语义判断。

### Q3. Human KEEP_SEPARATE 的理由是什么？

Human 没有写 comment（comment 为空）。

但从 Human 可见的信息推断：
- text_a = "transition form factor of primary interest to us." → 这是一个完整的名词短语，以句号结尾
- text_b = "Its normalization is" → 这是一个新句子的开头（主语 "Its" + 谓语 "is"）

Human 通过阅读文本内容，识别出：
- text_a 以句号 "." 结尾 → 前一句的结束
- text_b 以 "Its" 开头 → 新句子的开始
- 两者在同一行但属于**不同句子**

### Q4. Human 的判断是否与"semantic text unit boundary"定义一致？

**是。**

Semantic text unit 的定义是"属于同一文本单元的 observation 集合"。对于正文文本，一个 text unit 通常对应一个句子或一个短语。

"transition form factor of primary interest to us." 和 "Its normalization is" 是：
- 两个不同的句子片段（前者以句号结尾，后者是新句子的主语+谓语）
- 在同一行（same_y, dy=0）但在语义上不连续
- 不属于同一 text unit

**Human 的 KEEP_SEPARATE 符合 semantic text unit boundary 定义。**

### Q5. 是否存在 GT ontology 与目标语义定义的 mismatch？

**是。**

| 维度 | GT ontology | 目标语义定义 |
|---|---|---|
| 判断依据 | 几何特征（width, text length） | 语义关系（是否同一文本单元） |
| AMB-026 判断 | SHOULD_MERGE（w_a≥25 AND w_b≥25 AND len≥10） | SHOULD_NOT_MERGE（不同句子） |
| 适用场景 | 纯几何 pipeline 的粗分类 | 语义层面的 text unit boundary |

GT ontology 使用几何特征来**近似**语义关系。对于 TOC_SECTION_NUMBER_TITLE（序号+标题）和 FORMULA_FRAGMENT_WIDE（公式碎片），几何近似与语义判断一致。但对于 BODY_TEXT_CONTINUATION，几何近似失效——两个宽文本片段在同一行不意味着它们是同一文本单元。

**这是一个 GT ontology mismatch：geometry-based GT 在 body text continuation 场景下与 semantic text unit 定义不一致。**

### Q6. 是否需要定义 GT_DISPUTED？

**是，作为 audit finding 记录。**

```
GT_DISPUTED: AMB-026
  GT label: SHOULD_MERGE (geometry-based)
  Human decision: KEEP_SEPARATE (semantic-based)
  Dispute reason: GT ontology uses width+length heuristics for body text continuation;
                  these heuristics do not capture sentence boundaries.
  Audit finding: Human decision is semantically correct.
                 GT label is a geometry approximation that is over-general for body text.
  Action: NONE (do not modify GT; record as audit finding only)
```

**不修改当前 GT。** GT_DISPUTED 仅作为 audit finding 记录，不作为正式状态变更。

---

## 三、Accuracy 多口径报告

| 口径 | 计算 | 结果 | 说明 |
|---|---|---|---|
| A. Raw GT Accuracy | correct / 20 | 19/20 = 95.0% | 官方结果 |
| B. Resolved Accuracy | correct / (20 - CANNOT_DETERMINE) | 19/20 = 95.0% | CANNOT_DETERMINE=0，与 A 相同 |
| C. Excluding disputed AMB-026 | correct / 19 | 19/19 = 100.0% | 仅辅助，不作为官方结果 |
| D. Alternative semantic (AMB-026 Human=correct) | correct / 20 | 20/20 = 100.0% | ⚠️ HYPOTHETICAL / NOT OFFICIAL |

**官方结果**：A. Raw GT Accuracy = 95.0%

C 和 D 仅作为辅助分析视角，不修改官方结果。AMB-026 的 GT dispute 未解决——在没有独立专家标注或第二 reviewer 确认之前，不能将 D 作为正式结果。

---

## 四、Human Information Gain 重新审查

### AMB-018: "6.1" → "SMEFT"

| 信息源 | Human 是否利用? | 证据 |
|---|---|---|
| Page context | ✅ 是 | Human 看到 TOC 页面布局，识别 "6.1" 是节号 |
| Text context | ✅ 是 | Human 读到 "SMEFT" 是缩写标题，不是公式符号 |
| Visual structure | ✅ 是 | TOC 页的行布局（稀疏、序号在左、标题在中、页码在右） |
| Semantic relation | ✅ 是 | "6.1" + "SMEFT" 构成编号+标题的语义关系 |

### AMB-040: "( )" → "cos("

| 信息源 | Human 是否利用? | 证据 |
|---|---|---|
| Page context | ✅ 是 | Human 看到 arxiv_2307 公式页面，识别这是公式行 |
| Text context | ✅ 是 | Human 读到 "cos(" 是数学函数，不是标题 |
| Visual structure | ✅ 是 | 公式行的密集符号布局 vs TOC 行的稀疏布局 |
| Semantic relation | ✅ 是 | "( )" 和 "cos(" 是公式中的独立符号，不是编号+标题 |

### 结论

```
INFORMATION GAIN = SUPPORTED
```

Human 成功利用了 page context + text context + visual structure + semantic relation 区分了两个几何同构但 GT 相反的 adversarial case。

**但 claim 不扩大为 "Human always resolves ambiguity"。**

准确表述：

> "Human successfully resolved the tested adversarial cases (AMB-018 and AMB-040) by utilizing page context, text semantics, and visual structure — information sources unavailable to the geometry-only P4 pipeline."

这个结论基于 2 个 adversarial case，不能推广到所有 AMBIGUOUS case。43 个 AMBIGUOUS 中只有 20 个被测试，剩余 23 个未验证。

---

## 五、Coverage Limitations

| 维度 | 当前状态 | 限制 |
|---|---|---|
| Sample | 20 / 43 AMBIGUOUS | 仅 46.5% 覆盖 |
| Documents | 3 (arxiv_toc, arxiv_2307, arxiv_bio_body) | 设备手册 AMBIGUOUS=0（合理），但未覆盖其他学术论文类型 |
| Modes | 4 (TOC_NUM_TITLE, FORMULA_WIDE, APPENDIX_LETTER, BODY_CONT) | BODY_TEXT_CONTINUATION 仅 1 case |
| Reviewer | 1 (reviewer_1) | Inter-reviewer agreement 未测量 |
| Duration | Instrumentation invalid | Human cost 无法正式测量 |
| Ground Truth | 1 disputed (AMB-026) | GT ontology 在 body text 场景可能过宽 |
| Statistical power | N=20 | 无法做显著性检验，只能做 descriptive analysis |

### 当前定位

```
Human-on-the-Boundary =
  PROMISING / EMPIRICALLY SUPPORTED FOR INITIAL FEASIBILITY

NOT:
  GENERALIZED / FULLY VALIDATED
```

---

## 六、不进行的操作

| # | 不进行 | 理由 |
|---|---|---|
| 1 | 不修复 timer | 只描述 fix design，不实施 |
| 2 | 不修改 Review UI | 记录为 FUTURE IMPROVEMENT CANDIDATE |
| 3 | 不修改 AMB-026 GT | GT_DISPUTED 仅作为 audit finding |
| 4 | 不修改 case metadata | 保持原始结果完整 |
| 5 | 不修改 P4/P7.1/P7.2 | 全部 frozen |
| 6 | 不修改 Frozen 730 | UNCHANGED |
| 7 | 不修改 calibration_filter | UNCHANGED |
| 8 | 不进入 P7.3 | NOT AUTHORIZED |
| 9 | 不自动补 Human decision | 等待真实 Human |
| 10 | 不 AI 重判 Human | 禁止 |
| 11 | 不根据 GT 修正 Human | 禁止 |
| 12 | 不将 CANNOT_DETERMINE 强行转换 | 无 CANNOT_DETERMINE |

---

## 七、FUTURE IMPROVEMENT CANDIDATES

| # | 候选 | 说明 | 优先级 |
|---|---|---|---|
| 1 | Timer instrumentation fix | 客户端记录 case_open_ts / case_displayed_ts / decision_click_ts；服务端不再在 /api/case 中重置 start_time | HIGH |
| 2 | 第二 reviewer | 测量 inter-reviewer agreement | HIGH |
| 3 | 扩大到全部 43 AMBIGUOUS cases | 当前仅 20/43 | MEDIUM |
| 4 | BODY_TEXT_CONTINUATION 扩样 | 当前仅 1 case，无法判断该 mode 是否是 Human 困难区 | MEDIUM |
| 5 | GT ontology 重新评估 | body text continuation 的 SHOULD_MERGE 标签需要语义审查（非几何分类） | MEDIUM |
| 6 | 独立专家标注 | 为 disputed case（AMB-026）提供独立专家判断 | LOW |

**以上全部不实施。**

---

## 八、禁止项确认

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
| 10 | 不修改 timer/UI | ✅ 只描述，不实施 |
| 11 | 不修改 AMB-026 GT | ✅ 只记录 GT_DISPUTED |
| 12 | 不 AI 重判 Human | ✅ 未执行 |

---

## 九、Frozen Baseline 验证

| 文件集 | 状态 |
|---|---|
| P7.1 frozen (6 files) | UNCHANGED ✅ |
| P7.2 frozen (8 files) | UNCHANGED ✅ |
| P1-P6 regression baseline | UNCHANGED ✅ |
| Frozen 730 | a10b368e ✅ |
| P4 span (3 files) | UNCHANGED ✅ |
| calibration_filter.py | UNCHANGED ✅ |

**Frozen baseline: INTACT**

---

## STOP

```
OVERALL:        EMPIRICALLY_SUPPORTED
Implementation: NOT AUTHORIZED
P7.3:           NOT AUTHORIZED
Frozen:         INTACT
```

**不进入下一阶段。等待下一步批准。**
