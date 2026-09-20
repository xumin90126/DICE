# DICE Stage 5 — Next Information Source Decision Review

> **READ-ONLY 研究方向决策。不授权任何实现。不修改任何代码。不运行任何实验。**
>
> 阶段: Stage 5 — Next Information Source Decision Review
> 前置: Stage 4 CLOSED, Frozen Baseline INTACT, IS-11 EXPERIMENTALLY EVALUATED

---

## 1. Stage 4 Evidence Summary

### 1.1 实验数据

```
Primary cases = 45

GT:
  MERGE = 2
  KEEP_SEPARATE = 43

Baseline A (Geometry only):
  TP=0, FP=0, FN=0, TN=0, ABSTAIN=45
  Coverage = 0%

Baseline B (Geometry + IS-01 + IS-02):
  TP=0, FP=1, FN=0, TN=18, ABSTAIN=26
  Coverage = 42.2%

Experimental C (Geometry + IS-01 + IS-02 + IS-11):
  TP=0, FP=1, FN=0, TN=26, ABSTAIN=18
  Coverage = 60.0%

Incremental (C vs B):
  ΔFP = 0
  ΔCoverage = +17.8 pp
  ΔRecall = 0.0
  ΔPrecision = 0.0
```

### 1.2 Gates

```
G7 (FP Reduction, PRIMARY) = FAIL  (ΔFP = 0, not < 0)
G8 (Recall/Coverage Safety) = PASS  (ΔRecall=0 ≥ 0, ΔCoverage=+0.1778 ≥ 0)
```

### 1.3 关键事实

```
8/8 C-vs-B differences correct (all INSUFFICIENT_EVIDENCE → KEEP_SEPARATE, GT=KEEP_SEPARATE)

32/45 TABLE_CELL_CONTEXT unavailable:
  25/32 = TABLE_NOT_DETECTED (table_line_detector returned 0 tables)
  7/32  = CANDIDATE_OUTSIDE_TABLE_BBOX (table detected but candidates outside)

Determinism = PASS (0 mismatches in 2 runs)

Cross-document FP reduction = 0/4 documents

Frozen Baseline drift = 0
```

### 1.4 一致性确认

以上数据与 `tmp/is11_machine_evaluation_results.json`、`tmp/is11_machine_evaluation_metrics.json` 完全一致。**无 inconsistency。**

---

## 2. IS-11 真正结论

### 2.1 已证实

1. IS-11 在本次 45-case 实验中**未降低 FP** (G7=FAIL)
2. IS-11 **没有造成 Recall 退化** (G8=PASS)
3. IS-11 **增加了 8 个可判定案例**，全部与 GT 一致
4. IS-11 在可获得 table context 的 13 个 case 中，cell membership **全部正确解析**
5. **Cross-document FP-reduction stability NOT ESTABLISHED** (0/4 docs)
6. **32/45 (71.1%) case 未获得 TABLE_CELL_CONTEXT** — perception coverage 是主要瓶颈
7. 2 个 MERGE GT 均为 figure captions → **IS-11 在设计上无法覆盖**
8. 唯一 FP case (IS11-AMB-135: "4"+"MBConv6, k5x5") 在 unavailable 集合 → IS-11 无法纠正
9. Determinism PASS

### 2.2 尚未证实 (不可声称)

- 不可声称 "IS-11 无价值"
- 不可声称 "TABLE_CELL_CONTEXT 普遍无效"
- 不可声称 "IS-11 能普遍提升 Coverage 17.8pp"
- 不可声称 "table_line_detector 修复后一定可以通过 G7"
- 不可声称 "IS-11 在更强 perception 下必然有效"
- 不可对 Recall/Precision 统计稳定性做过度解释 (GT MERGE=2)

### 2.3 实验设计 §17 的预注册指导

IS-11 实验设计 §17 明确预注册了失败后的路径：

| IS-11 结果 | 预注册下一步 |
|-----------|------------|
| 有效 (G7+G8 PASS) | 测试 IS-12 (ROW_COLUMN_POSITION) 增量 |
| 部分有效 | 分析 F8 (table context insufficient) → 可能需要 IS-14 |
| **无效** | **转为 HUMAN_OWNED 或重新评估 TABLE_CELL boundary class** |
| 无法稳定提取 | DEFER — 等待更好的 table detection 技术 |

当前结果: G7=FAIL → IS-11 "无效" (按预注册标准)。

但需注意：IS-11 的"无效"部分源于 perception coverage 不足 (71.1% unavailable)，而非 cell membership 逻辑错误。这更接近 §17 中的"无法稳定提取"而非纯粹的"无效"。

---

## 3. Research Bottleneck Diagnosis (Q1)

### 核心问题

> DICE 当前最大的科学/系统瓶颈究竟是什么？

### 3.1 四个候选诊断

| 诊断 | 描述 | 证据支持 | 判断 |
|------|------|---------|------|
| A. 缺少足够的结构信息 | 当前 IS-01+IS-02 不足以区分语义连续与结构分离 | IS-11 正确解析 8/8 case；但 32/45 无法获得 IS-11 信息 | **PARTIALLY YES** |
| B. 缺少 Evidence Sufficiency 判断 | 系统无法判断何时证据充分、何时应弃权 | 57.8% (B) / 40.0% (C) abstention；§9.3 协议是二元的 | **YES** |
| C. Perception capability 不足 | table_line_detector coverage 有限 | 71.1% case 无 table context | **PARTIALLY YES (仅限 IS-11)** |
| D. Boundary Decision 信息模型不足 | §9.3 协议过于简单 (IS01∧IS02→MERGE, else ABSTAIN) | FP case "4"+"MBConv6" 因 number+readable→MERGE 而非结构分离 | **YES (根本性)** |

### 3.2 深度诊断: 18 个剩余 INSUFFICIENT_EVIDENCE case 的结构分类

对 Experimental C 中仍为 INSUFFICIENT_EVIDENCE 的 18 个 case 进行逐 case 分析：

| 结构类别 | Case 数 | 代表 case | GT | 需要的信息源 |
|----------|---------|-----------|-----|------------|
| Table column headers | 4 | "Resolution"+"#Channels" | KEEP_SEPARATE | IS-14 (DOCUMENT_STRUCTURE_ROLE: header) |
| Table cell values (diff columns) | 4 | "37.0"+"60.0" | KEEP_SEPARATE | IS-11/IS-12 (if perception worked) |
| Figure captions | 2 | "FIG. 9:"+"Left:" | **MERGE** | IS-14 (DOCUMENT_STRUCTURE_ROLE: caption) |
| Axis tick labels | 3 | "0.70"+"0.75" | KEEP_SEPARATE | IS-14 (DOCUMENT_STRUCTURE_ROLE: axis label) |
| Sentence boundaries | 3 | "[23]."+"Each" | KEEP_SEPARATE | IS-10 (HUMAN_OWNED) 或 sentence boundary detection |
| Diagram items | 1 | "RBF"+"Matérn" | KEEP_SEPARATE | IS-14 (DOCUMENT_STRUCTURE_ROLE: diagram element) |
| Model name vs param | 1 | "41M"+"EfficientNet-B5" | KEEP_SEPARATE | IS-11/IS-12 (if perception worked) |

**关键发现**:

- **10/18 (55.6%)** 的剩余 abstain case 需要 **IS-14 (DOCUMENT_STRUCTURE_ROLE)** — 识别候选对的文档结构角色
- **5/18 (27.8%)** 需要 **IS-11/IS-12 with better perception** — 表格内 cell membership
- **3/18 (16.7%)** 需要 **IS-10 (sentence boundary)** — HUMAN_OWNED

- **2 个 MERGE GT** 全部是 figure captions → 只有 IS-14 能识别 "同属一个 figure caption" → MERGE

### 3.3 FP case 深度分析

```
IS11-AMB-135: text_a="4", text_b="MBConv6, k5x5"
  IS-01_a = True ("4" matches number pattern)
  IS-02_b = True ("MBConv6" has >2 alpha chars)
  §9.3 protocol: IS01=True AND IS02=True → MERGE
  GT = KEEP_SEPARATE (different table cells)
  IS-11 in_table = False (table not detected on efficientnet p5)
```

**FP 根因**: §9.3 协议假设 "number + readable text = continuation of same semantic unit"。但在表格中，"number + readable text" 更可能是 **不同 cell 的相邻值**。

**IS-11 理论上可纠正此 FP** (如果检测到 different_cell → KEEP_SEPARATE)，但 perception 限制导致 table 未检出。

**IS-14 也可纠正此 FP** (如果识别 "4" 和 "MBConv6" 为不同结构角色的 cell values)。

### 3.4 诊断结论

```
PRIMARY BOTTLENECK = D (信息模型不足) + B (Evidence Sufficiency 判断)

当前 §9.3 协议是二元的:
  IS01=True AND IS02=True → MERGE
  IS01=False AND IS02=False → KEEP_SEPARATE
  Otherwise → INSUFFICIENT_EVIDENCE

这导致:
  1. "number + readable text" 在表格中被误判为 MERGE (FP)
  2. 57.8% case 因 IS01/IS02 不匹配而 ABSTAIN
  3. 系统没有 "结构角色" 概念 → 无法区分 table cell vs figure caption vs body text

SECONDARY BOTTLENECK = C (perception capability, 仅限 IS-11)
  table_line_detector coverage = 28.9% → 限制 IS-11 统计功效
```

---

## 4. Q2-Q4 回答

### Q2: 下一轮信息源实验应该优先研究什么？

> **Evidence Sufficiency 的结构基础** — 即：什么结构信息能够帮助系统判断 "证据是否充分" 以及 "应该 MERGE 还是 KEEP_SEPARATE"。

具体而言：不是简单地 "加更多 IS"，而是理解 **当前 abstention 的结构原因**，然后设计能够解决最大类别 abstain 的信息源。

### Q3: 这个研究是否仍然可以保持 Frozen Baseline 不变？

> **YES** — 如果下一轮研究的是新的 Information Source (如 IS-14) 或 Evidence Sufficiency 分析。
>
> 新 IS 作为 experiment-only observer，与 Baseline B 对比。Frozen P1-P6/P4/IS-01/IS-02 全部保持不变。

### Q4: 如果必须修改 Frozen，是否应该作为独立 Capability Improvement 阶段？

> **YES** — 如果将来需要修改 table_line_detector 或 P1-P6，必须作为:
> - 独立的 Capability Improvement 阶段
> - 有明确的 capability gap 证据
> - 有完整 re-freeze 流程
> - 不与 Information Source 实验混淆

当前阶段: **不需要修改 Frozen**。

---

## 5. 四个候选方向比较

### OPTION A — IS-11 Follow-up

**研究问题**: 如果获得更可靠的 TABLE_CELL_CONTEXT，IS-11 是否能产生真正的增量 Boundary Intelligence？

**分析**:

- IS-11 实验设计 §17 预注册: IS-11 无效 → "转为 HUMAN_OWNED 或重新评估"
- 当前 G7=FAIL，但部分源于 perception coverage (71.1% unavailable)
- 在 13 个 available case 中: 8/8 正确，但 **0 FP reduction** (因为 FP case 不在 available 集合)
- 即使 perception 修复，IS-11 只覆盖 table context → 无法解决 figure captions (2 MERGE GT)、axis labels、sentence boundaries
- 成本: HIGH (新 corpus + 可能 re-freeze + 新 GT)
- 风险: 即使投入高成本，IS-11 可能仍无法 PASS G7 (FP case 可能仍不在 table region)

**关键判断**: IS-11 的 hypothesis 本身可能 **过于狭窄** — TABLE_CELL_CONTEXT 只是文档结构角色的一种。即使 perception 完美，IS-11 也无法覆盖 10/18 剩余 abstain case。

### OPTION B — 新 Information Source (IS-12 / IS-14)

**研究问题**: 是否存在比 TABLE_CELL_CONTEXT 更稳定、coverage 更高的结构信息源？

#### IS-12 = ROW_COLUMN_POSITION

- IS-11 的子组件 (§3.3): "在 table 中的行列位置"
- **问题**: IS-12 依赖 table detection → 与 IS-11 有相同的 perception 限制
- 如果 IS-11 因 perception 不足而 FAIL，IS-12 也会因相同原因受限
- **判断**: IS-12 不适合作为下一个独立实验 → 它是 IS-11 的 refinement，应在 IS-11 成功后测试

#### IS-14 = DOCUMENT_STRUCTURE_ROLE

- 比 IS-11 更广泛 (§3.3): "文档结构角色 (table/figure/caption/body/heading/footnote/reference/equation)"
- IS-11 是 IS-14 的一个特例 (table 是 document structure role 之一)
- **潜在覆盖**:
  - Figure captions (2 MERGE GT) → IS-14 可识别 "同属一个 caption" → MERGE
  - Table column headers (4 abstain) → IS-14 可识别 "header" → KEEP_SEPARATE
  - Axis tick labels (3 abstain) → IS-14 可识别 "axis label" → KEEP_SEPARATE
  - Diagram items (1 abstain) → IS-14 可识别 "diagram element" → KEEP_SEPARATE
  - Table cell values (5 abstain + 1 FP) → IS-14 可识别 "cell value in different columns" → KEEP_SEPARATE
- **总潜在覆盖**: 16/18 剩余 abstain + 1 FP = 17/19 (89.5%)
- **不依赖 table_line_detector** → 不受 perception coverage 限制
- 可以复用 Stage 3 的 45-case GT 和 Sampling Frame

**关键判断**: IS-14 是 IS-11 的自然泛化，可覆盖 IS-11 无法覆盖的结构类别。但 IS-14 更广泛 → 定义更模糊 → 需要更谨慎的实验设计。

### OPTION C — Evidence Sufficiency

**研究问题**: 为什么 DICE 在大量案例上无法获得 sufficient evidence？

**分析**:

- Baseline B: 57.8% abstention → 系统过于保守
- 即使 IS-11 后: 40% 仍然 abstain
- §9.3 协议是二元的 → 没有 "部分证据" 或 "证据置信度" 的概念
- 18 个剩余 abstain case 的结构分类 (§3.2) 表明: abstension 不是随机的，而是 **系统性的结构信息缺失**
- Evidence Sufficiency 研究可以:
  - 诊断 abstension 的结构性原因
  - 区分 "genuine info gap" (需要新 IS) vs "protocol too conservative" (需要新协议)
  - 指导下一个 IS 的设计

**关键判断**: Evidence Sufficiency 是最根本的研究方向，但它本身是 **诊断性** 的 → 不直接产生新 IS。它应该作为 Option B (IS-14) 的 **前置研究**。

### OPTION D — Perception Capability Improvement

**研究问题**: 现有 perception layer 是否已经成为 Evidence Intelligence 的瓶颈？

**分析**:

- 71.1% table unavailable 是明确的 perception gap
- 但: 即使 perception 修复，IS-11 只覆盖 table → 10/18 abstain case 仍无法解决
- table_line_detector.py 修改 → 需要 re-freeze P1-P6 → 高风险
- 这是 **工程任务**，不是 **研究问题**
- 应该作为独立 Capability Improvement 阶段 (如果将来需要)

**关键判断**: Perception improvement 是 IS-11 follow-up (Option A) 的前置条件，但 Option A 本身优先级不高。因此 Option D 当前 **不是优先方向**。

---

## 6. Decision Matrix

| Option | Research Value | Evidence Support | Information Gain | Generalizability | Cost | Frozen Impact | Contamination Risk | Priority |
|--------|---------------|-----------------|-----------------|-----------------|------|--------------|-------------------|----------|
| A IS-11 Follow-up | MEDIUM | LOW (G7 FAIL, §17 says re-evaluate) | MEDIUM (may confirm or deny IS-11) | LOW (only tables) | HIGH | HIGH (may need re-freeze) | MEDIUM | LOW-MEDIUM |
| B IS-12/IS-14 | HIGH | MEDIUM (10/18 abstain need IS-14) | HIGH (could cover 89.5% of remaining abstain) | HIGH (all documents have structure roles) | MEDIUM (reuse corpus/GT, new observer) | LOW (experiment-only) | MEDIUM (GT reuse risk) | **HIGH** |
| C Evidence Sufficiency | HIGH | HIGH (57.8% abstain is direct evidence) | HIGH (would reveal systematic patterns) | HIGH (universal concern) | LOW (pure analysis) | NONE | LOW | **HIGH** |
| D Perception Improvement | MEDIUM | MEDIUM (71.1% unavailable) | MEDIUM (only improves table perception) | LOW (only tables) | HIGH (re-freeze) | HIGH | HIGH (invalidates Stage 4) | LOW |

### 评分依据

**Research Value**:
- A=MEDIUM: 会验证 IS-11 在强 perception 下的价值，但 IS-11 hypothesis 本身可能过于狭窄
- B=HIGH: IS-14 可覆盖 IS-11 无法覆盖的结构类别，是 IS-11 的自然泛化
- C=HIGH: 直接回答 "为什么系统无法判断" 这一根本问题
- D=MEDIUM: 解决 perception gap 但不解决信息模型问题

**Evidence Support**:
- A=LOW: G7 FAIL，§17 预注册说 "无效→重新评估"
- B=MEDIUM: 10/18 abstain case 需要 IS-14；但 IS-14 尚无直接实验证据
- C=HIGH: 57.8% abstain 是直接、明确的证据
- D=MEDIUM: 71.1% unavailable 是明确证据，但这是 engineering finding 不是 research finding

**Information Gain**:
- A=MEDIUM: 可能确认或否定 IS-11 价值
- B=HIGH: 可能覆盖 89.5% 剩余 abstain + 纠正 FP
- C=HIGH: 会揭示 abstension 的系统性 pattern
- D=MEDIUM: 只改善 table perception

**Generalizability**:
- A=LOW: 只覆盖 tables
- B=HIGH: 所有文档都有结构角色
- C=HIGH: Evidence sufficiency 是通用问题
- D=LOW: 只改善 table detection

---

## 7. 是否应该继续追求降低 FP？

### 7.1 Stage 4 的 FP 分析

```
FP = 1 (IS11-AMB-135: "4" + "MBConv6, k5x5")
  → §9.3 protocol: number + readable text → MERGE
  → GT: KEEP_SEPARATE (different table cells)
  → IS-11 could not help (table not detected)
  → IS-14 could potentially help (identify as cell values in different roles)
```

### 7.2 FP Reduction vs 其他目标

| 目标 | 含义 | 当前状态 | 是否应作为唯一核心？ |
|------|------|---------|-------------------|
| FP Reduction | 减少错误 MERGE | FP=1, G7=FAIL | 不是唯一核心 — FP=1 样本太小 |
| Coverage Expansion | 增加可判定案例 | 42.2%→60%, 仍有 40% abstain | 重要，但必须与安全配对 |
| Evidence Sufficiency | 理解何时证据充分 | 57.8% abstain (B) | **最根本** — 决定系统何时该判、何时该弃权 |
| Abstention Quality | 弃权是否正确 | 未测量 | 重要 — 需要区分 "genuine gap" vs "protocol limitation" |
| Boundary Confidence | 决策置信度 | §9.3 是二元的 (无置信度) | 长期方向 — 当前未实现 |

### 7.3 判断

> **"降低 FP" 不应继续作为下一轮信息源研究的唯一核心目标。**

理由:
1. FP=1 → 样本太小，无法作为稳定优化目标
2. GT MERGE=2 → Recall 分母=2 → Precision/Recall 统计不稳定
3. 系统的更大问题是 57.8% abstention → 系统不知道何时该判
4. "更安全、更可靠" 不只是 "更少 FP" → 也包括 "知道何时弃权"

### 7.4 建议的下一轮核心目标

```
DUAL PRIMARY GOALS:
  1. Evidence Sufficiency Understanding (诊断性)
     → 为什么 57.8% case 无法达到 sufficient evidence?
     → 哪些是 genuine info gap, 哪些是 protocol limitation?

  2. Structural Information Coverage (实验性)
     → 新 IS (如 IS-14) 是否能覆盖 IS-11 无法覆盖的结构类别?
     → 是否能在不增加 FP 的前提下减少 unjustified abstention?

SAFETY CONSTRAINT (不变):
  → No new FP from former abstain (G8-type gate)
  → Determinism PASS
  → Frozen Baseline intact
```

---

## 8. GT 类别不平衡的考虑

### 8.1 当前状况

```
GT MERGE = 2 (4.4%)
GT KEEP_SEPARATE = 43 (95.6%)
```

### 8.2 影响

- **Recall**: 分母=2 → 1 个 case 变化使 Recall 从 0.0 跳到 0.5 → **统计不稳定**
- **Precision**: 分母=1 (TP+FP=1) → 同样不稳定
- **FP**: 只有 1 个 FP case → 无法判断 FP-reduction 的统计稳定性
- **Coverage/TN**: 相对稳定 (分母大)

### 8.3 对下一轮实验的指导

1. **不可过度解释 8/8 correct**: 8 个 case 全部是 KEEP_SEPARATE → 在极端不平衡 GT 上，"全部判 KEEP_SEPARATE" 本身就有 95.6% 准确率
2. **如果复用 GT**: 必须报告 confidence interval，不只点估计
3. **如果创建新 corpus**: 应考虑分层抽样，获取更多 MERGE case (但不可为了 MERGE 而重新挑选)
4. **本阶段不重新采样**: 遵守约束

### 8.4 统计功效分析

| 指标 | 当前分母 | 可靠性 | 建议 |
|------|---------|--------|------|
| Recall | 2 | ❌ 不可靠 | 不可作为独立判断依据 |
| Precision | 1 | ❌ 不可靠 | 不可作为独立判断依据 |
| FP | 1 | ❌ 不可靠 | 需要更多 FP case 才能评估 FP-reduction |
| Coverage | 45 | ✅ 相对可靠 | 可作为主要指标 |
| TN | 43 | ✅ 相对可靠 | 可作为安全指标 |
| Abstention | 45 | ✅ 相对可靠 | 可作为主要指标 |

---

## 9. Frozen Modification Decision

### 9.1 总体决策

```
当前是否应该解冻 Frozen?

NO
```

理由:
1. 没有明确的实验授权解冻
2. G7 FAIL 不是解冻理由
3. 32/45 table unavailable 是诊断结果，不是解冻条件
4. 下一阶段研究问题尚未最终确定
5. Frozen Baseline 0 drift — 完好

### 9.2 每个 Option 的 Frozen 决策

| Option | Frozen Modification Required? | 说明 |
|--------|------------------------------|------|
| A (IS-11 Follow-up) | **CONDITIONAL** | 如果需要更强 table perception → YES (修改 table_line_detector); 如果使用 parallel experimental detector → NO (但 experiment-only) |
| B (IS-12/IS-14) | **NO** | 新 IS 作为 experiment-only observer，不依赖 frozen detector，不修改 P1-P6 |
| C (Evidence Sufficiency) | **NO** | 纯 READ-ONLY 分析，不修改任何文件 |
| D (Perception Improvement) | **YES** | 修改 table_line_detector.py → re-freeze P1-P6 |

### 9.3 CONDITIONAL 触发条件 (Option A)

如果选择 Option A:
- 触发条件: "需要 table perception coverage > 50%"
- 如果使用 experiment-only parallel detector (不集成 P1-P6) → Frozen 保持 intact
- 如果修改 frozen table_line_detector.py → 必须 re-freeze

---

## 10. PRIMARY NEXT RESEARCH QUESTION

### 推荐

> **PRIMARY NEXT RESEARCH QUESTION:**
>
> **"什么文档结构信息能够帮助 DICE 更安全地判断 Evidence Sufficiency — 即何时应该做出 Boundary Decision，何时应该弃权？"**

### 具体表述

当前 §9.3 协议在 57.8% 的 AMBIGUOUS case 上弃权。分析表明，弃权不是随机的，而是 **系统性的结构信息缺失**:

- 10/18 剩余 abstain case 需要文档结构角色信息 (IS-14)
- 5/18 需要 table cell membership (IS-11/IS-12, perception-limited)
- 3/18 需要 sentence boundary (IS-10, HUMAN_OWNED)

因此，下一轮研究应该:

1. **先做 Evidence Sufficiency 诊断 (Option C)**: 逐 case 分析 45 个 case 的 evidence chain，识别 abstension 的系统性 pattern
2. **基于诊断设计 IS-14 实验 (Option B)**: 将 IS-14 作为 HYPOTHESIS ONLY，设计预注册实验

### 10.1 Why Now

- Stage 4 已完成，IS-11 结果已封存
- 18 个剩余 abstain case 的结构分类已完成 (§3.2)
- 证据明确指向 "文档结构角色" 作为最大信息缺口
- Frozen Baseline 完好 → 可以安全地进行 experiment-only 研究
- 不需要新 corpus/GT → 成本低

### 10.2 Existing Evidence

- IS-11 正确解析 8/8 case (在 available 时) → 结构信息有效
- IS-11 无法覆盖 10/18 剩余 abstain → 需要更广泛的结构信息
- 2 MERGE GT 是 figure captions → 只有 IS-14 能识别
- FP case 需要 "cell value" 角色识别 → IS-14 可覆盖
- Reviewer B 的 MERGE 原则: "same paragraph/caption = MERGE; different cell = KEEP_SEPARATE" → 暗示文档结构角色是关键

### 10.3 Why Alternatives Are Lower Priority

| Option | 为什么低优先 |
|--------|------------|
| A (IS-11 Follow-up) | IS-11 hypothesis 过于狭窄 (只覆盖 tables)；§17 预注册说 "无效→重新评估"；成本高；即使 perception 修复也无法覆盖 10/18 abstain |
| D (Perception Improvement) | 是工程任务不是研究问题；只改善 table perception；需要 re-freeze；高风险 |
| IS-12 (alone) | 是 IS-11 的子组件 → 有相同 perception 限制 → 如果 IS-11 因 perception 失败，IS-12 也会 |

### 10.4 Whether Frozen Stays Intact

```
FROZEN BASELINE = INTACT
```

- Option C (Evidence Sufficiency): 纯 READ-ONLY → 不修改 Frozen
- Option B (IS-14): experiment-only observer → 不修改 Frozen
- P1-P6, P4, P7.1, P7.2, IS-01, IS-02 全部保持 frozen

### 10.5 Required Next Experiment (设计框架，不实现)

如果授权进入下一阶段:

1. **Phase 1: Evidence Sufficiency Diagnostic (Option C)**
   - 逐 case 分析 45 个 case 的 evidence chain
   - 分类: genuine info gap / protocol limitation / IS-covered-but-unavailable
   - 输出: evidence gap taxonomy + IS-14 hypothesis refinement
   - 不需要新 corpus/GT/实验

2. **Phase 2: IS-14 Experiment Design (Option B)**
   - IS-14 = DOCUMENT_STRUCTURE_ROLE (HYPOTHESIS ONLY)
   - 定义 IS-14 的观察组件 (document role detection)
   - 设计 A/B/C 三条件 (B = Geometry+IS-01+IS-02, C = B+IS-14)
   - 预注册 gates
   - 可复用 45-case GT (with acknowledged hindsight bias risk)

3. **Phase 3: IS-14 Machine Evaluation**
   - 实现 experiment-only IS-14 observer
   - 运行 A/B/C
   - 计算 metrics + gates
   - 不集成 P1-P6

### 10.6 Required Independent Corpus

- Phase 1 (Diagnostic): **不需要** — 使用已有 45-case
- Phase 2 (Design): **不需要** — 纯设计
- Phase 3 (Evaluation): **可能不需要** — 可复用 45-case GT
  - 风险: GT reuse → hindsight bias
  - 缓解: IS-14 spec 在 evaluation 前冻结；不从 GT 反推 IS-14 definition
  - 替代: 如果需要独立验证 → 新 corpus (含更多 MERGE case)

### 10.7 Required GT

- Phase 1: 已有 45-case Semantic GT (FROZEN)
- Phase 3: 可复用 (with risk) 或新建 (if independent verification needed)

### 10.8 Required Metrics

```
Primary:
  ΔCoverage (C vs B) — IS-14 是否减少 abstention
  ΔFP (C vs B) — IS-14 是否减少 FP
  Validated Coverage Expansion — 新增可判定案例的正确率

Safety:
  No new FP from former abstain
  Determinism PASS
  Cross-document stability

Diagnostic:
  Evidence gap taxonomy (from Phase 1)
  IS-14 coverage rate (% of cases with IS-14 information available)
```

### 10.9 Required Gates

```
G-E1: IS-14 Spec Freeze (before evaluation)
G-E2: No GT Leakage (provenance audit)
G-E3: Coverage Expansion (ΔCoverage > 0)
G-E4: FP Safety (ΔFP ≤ 0, no new FP from former abstain)
G-E5: Validated Expansion (≥80% of new decisions correct)
G-E6: Determinism (run 1 = run 2)
G-E7: Cross-Document (≥2 docs show coverage expansion)
```

### 10.10 Stop Conditions

```
STOP if:
  - IS-14 cannot be stably observed (non-deterministic)
  - IS-14 creates new FP (G-E4 FAIL)
  - IS-14 coverage < 30% (too limited to be useful)
  - Evidence Sufficiency diagnostic shows no actionable pattern
  - Frozen Baseline drift detected at any point
```

---

## 11. Alternative Options (保留但不优先)

### 11.1 IS-12 = HYPOTHESIS ONLY

```
IS-12 = ROW_COLUMN_POSITION
IS-12 IMPLEMENTATION = NOT AUTHORIZED
```

- 是 IS-11 的子组件 → 有相同 perception 限制
- 适合在 IS-11 或 IS-14 成功后作为 refinement 测试
- 当前不优先

### 11.2 IS-14 = HYPOTHESIS ONLY

```
IS-14 = DOCUMENT_STRUCTURE_ROLE
IS-14 IMPLEMENTATION = NOT AUTHORIZED
```

- 是推荐的下一轮实验方向 (作为 Phase 2/3)
- 但当前阶段仅为 HYPOTHESIS，不实现

### 11.3 IS-11 保留状态

```
IS-11 = EXPERIMENTALLY EVALUATED
IS-11 G7 = FAIL
IS-11 INTEGRATION = NOT AUTHORIZED
IS-11 FOLLOW-UP = LOW PRIORITY (not recommended as primary)
```

### 11.4 Perception Improvement (Option D)

```
PERCEPTION IMPROVEMENT = NOT AUTHORIZED
TABLE_LINE_DETECTOR MODIFICATION = NOT AUTHORIZED
```

- 如果将来 IS-14 实验需要更强的 perception → 再考虑
- 必须作为独立 Capability Improvement 阶段

---

## 12. Required Future Experiment (框架)

### 12.1 Phase 1: Evidence Sufficiency Diagnostic

**目标**: 理解 45 个 case 的 evidence gap 结构

**方法**: READ-ONLY 逐 case 分析

**输出**:
- Evidence gap taxonomy
- 每个 abstain case 的根因分类
- IS-14 hypothesis refinement (基于诊断)
- 不修改任何文件

**Stop condition**: 如果诊断无 actionable pattern → STOP

### 12.2 Phase 2: IS-14 Experiment Design

**目标**: 设计 IS-14 预注册实验

**约束**:
- IS-14 = HYPOTHESIS ONLY
- IS-14 spec 在 GT (如果新建) 之前冻结
- 不从 GT 反推 IS-14 definition
- experiment-only observer

**输出**:
- IS-14 experiment design document
- IS-14 information availability matrix
- Pre-registered gates (G-E1 to G-E7)

### 12.3 Phase 3: IS-14 Machine Evaluation

**目标**: 评估 IS-14 增量价值

**条件**: Phase 1 + Phase 2 完成 + 用户授权

**方法**: A/B/C 三条件 (同 Stage 4 结构)

**输出**: 同 Stage 4 的完整 artifact set

---

## 13. Stop Conditions (总体)

```
STOP if ANY of the following:
  1. Frozen Baseline drift detected (>0)
  2. Evidence Sufficiency diagnostic shows no actionable pattern
  3. IS-14 cannot be stably observed
  4. IS-14 creates new FP
  5. User does not authorize next phase
  6. Any constraint violation detected
```

---

## 14. Final Governance State

```
STAGE 4 = CLOSED
STAGE 5 = COMPLETE (Next Information Source Decision Review)

FROZEN BASELINE = INTACT (0 drift)
FROZEN MODIFICATION = NOT AUTHORIZED

IS-11 = EXPERIMENTALLY EVALUATED
IS-11 G7 = FAIL
IS-11 G8 = PASS
IS-11 INTEGRATION = NOT AUTHORIZED

IS-12 = HYPOTHESIS ONLY
IS-12 IMPLEMENTATION = NOT AUTHORIZED

IS-14 = HYPOTHESIS ONLY
IS-14 IMPLEMENTATION = NOT AUTHORIZED

PRIMARY NEXT RESEARCH QUESTION =
  "什么文档结构信息能够帮助 DICE 更安全地判断 Evidence Sufficiency"

RECOMMENDED PATH:
  Phase 1: Evidence Sufficiency Diagnostic (Option C)
  Phase 2: IS-14 Experiment Design (Option B)
  Phase 3: IS-14 Machine Evaluation (if authorized)

P7.3 = NOT AUTHORIZED
PRODUCTION = FALSE
CAPABILITY REGISTRATION = NOT AUTHORIZED
RUNTIME = NOT AUTHORIZED

IMPLEMENTATION = NOT AUTHORIZED
TABLE_LINE_DETECTOR MODIFICATION = NOT AUTHORIZED

STOP = TRUE
WAIT FOR EXPLICIT AUTHORIZATION
```

---

## 15. 状态机

```
STAGE 4
    ↓
CLOSED
    ↓
FROZEN BASELINE = INTACT
    ↓
STAGE 5: NEXT INFORMATION SOURCE DECISION REVIEW
    ↓
COMPLETE
    ↓
PRIMARY NEXT RESEARCH QUESTION = IDENTIFIED
    ↓
Phase 1: Evidence Sufficiency Diagnostic (PENDING AUTHORIZATION)
Phase 2: IS-14 Experiment Design (PENDING)
Phase 3: IS-14 Machine Evaluation (PENDING)
    ↓
FROZEN MODIFICATION = NOT AUTHORIZED
    ↓
STOP = TRUE
WAIT FOR EXPLICIT AUTHORIZATION
```

```
IS-11
    ↓
EXPERIMENTALLY EVALUATED
    ↓
G7 = FAIL
G8 = PASS
    ↓
NO INTEGRATION
NO P7.3
NO PRODUCTION
```

```
IS-14
    ↓
HYPOTHESIS ONLY
    ↓
IMPLEMENTATION = NOT AUTHORIZED
    ↓
PENDING EXPERIMENT DESIGN (if authorized)
```

```
FROZEN MODIFICATION
    ↓
NOT AUTHORIZED
```

---

## STOP

Stage 5 Next Information Source Decision Review 完成。

推荐下一步: **Evidence Sufficiency Diagnostic → IS-14 Experiment Design**

不实现任何代码。不修改任何 Frozen 文件。不运行任何实验。等待明确授权。

> **Experiment first → Evidence second → Decision third → Implementation last.**
