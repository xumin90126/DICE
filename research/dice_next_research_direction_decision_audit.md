# DICE 下一阶段研究路线决策审计

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION
**Scope**: Route-level decision audit — Route A (收缩) vs Route B (扩 Corpus)

---

## 1. Executive Verdict

> **推荐路线：A→B — 先完成 Route A（收缩研究目标），再基于 Route A 输出决定 Route B（扩 Corpus）是否值得投入。**

Route A 可以**立即**用现有数据产生可验证的研究成果，明确将 Learning 声明为 L3 (Candidate Discovery)。Route B 有**显著不确定性**（TLD 覆盖率未知、CS1 天花板效应、无边界多样性），直接投入 Corpus 扩展风险过高。

---

## 2. Q1 — 当前研究到底缺什么？

| 研究维度 | 状态 | 证据 |
|---|---|---|
| Evidence Quality | ✅ PROVEN | P1-P6 + TLD 冻结，545 候选，确定性 SHA256 验证 |
| Evidence Distillation | ✅ PROVEN | L5.10 Evidence Cue，P722 实验 B2 条件，Cue 可计算 |
| Human Feedback Capture | ✅ PROVEN | 4 free-text + 90 rationales + 93 GT rationales + 55 decisions |
| Signal Discovery | ⚠️ PARTIAL | CS1-CS4 手动识别，无自动化，全部 CANDIDATE |
| Signal Validation | ❌ NOT PROVEN | 验证协议已设计，未执行 |
| Future Case Reuse | ❌ BLOCKED | 独立 Future Cases 不足（CS1: 1, CS2: 3, CS3: 0, CS4: 0） |
| Generalization | ❌ BLOCKED | 无 novel document，Page Leakage = FULL |
| Human Effort Reduction | ❌ NOT PROVEN | 无 Reuse 实验，无 HRR 测量 |
| Iterative Learning | ❌ NOT PROVEN | 闭环未闭合，L3 未达 L4 |

**关键区分**：Evidence Compression (C1) 和 Evidence Cue (C2) 已 PROVEN，但它们**不是 Learning**。Learning (C3) 需要 Reuse + HRR + Quality Preservation，全部 BLOCKED。

---

## 3. Q2 — CS1 是否仍值得继续？

### CS1 七维评估

| 维度 | 评价 | 依据 |
|---|---|---|
| 跨文档潜力 | **MEDIUM** | 3 个文档有 TLD 匹配，但 med_001 完全失败 (0/15 页) |
| 跨页面潜力 | **LOW** | 非过去页面 TLD 检测率仅 13% (2/15) |
| Evidence 可观察性 | **HIGH** | TLD is_in_table + different_cell，确定性可计算 |
| Human Feedback 可表达性 | **HIGH** | 70/90 reviewer rationale 提及 table columns (78%) |
| Signal 可验证性 | **HIGH** | 验证协议已设计，低成本可执行 |
| Future Case 可获得性 | **LOW** | 独立 Future Cases = 1（需 ≥10） |
| Reuse → HRR 潜力 | **UNKNOWN** | 31/31 = KEEP_SEPARATE (天花板效应)，P722 B1 已 100% accuracy/1.7s |

### CS1 真正瓶颈

```
瓶颈 NOT 仅是 Corpus 不足，而是多重因素叠加：

1. TLD 覆盖率有限（41% 页面，0% med_001）
2. TLD 匹配案例集中在相同页面（Page Leakage = FULL）
3. 31/31 Past Cases = KEEP_SEPARATE（无 MERGE 多样性）
4. 0 CONFLICT 案例（different_cell=True + GT=MERGE = 0）
5. 0 UNKNOWN 案例（is_in_table=True + diff_cell=False = 0）
6. CS1 只有一个方向（KEEP_SEPARATE），无法测试安全边界

→ CS1 是 evidence-backed 但 evidence-narrow：
   只能证明"不同表格列 → KEEP_SEPARATE"，
   无法证明 Signal 在 MERGE/CONFLICT/UNKNOWN 情况下的行为。
```

### CS1 作为 Research Object 的判断

```
CS1 仍然是一个有效的 Candidate Signal，
但不适合作为唯一的 Reuse 实验对象。

原因：
- 天花板效应使得 HRR 测量空间极小
- 无边界多样性使得安全测试不可能
- TLD 覆盖率限制使得独立 Future Cases 不足

CS1 更适合作为 Route A 的 Evidence-Grounded Signal Identification 示例，
而非 Route B 的 Reuse 实验主体。
```

---

## 4. 扩 Corpus 可行性反事实分析

### 如果要获得 10 个独立 Future Cases

| 需求 | 估计 | 依据 |
|---|---|---|
| Corpus Diversity | 需 ≥3-5 新文档 | 当前 4 文档已穷尽，CS1 仅在 3 文档有效 |
| Document Diversity | 需 TLD-positive 文档 | TLD 在 tech paper 有效，medical 无效 |
| Page Diversity | 需 ≥10 TLD+ 新页面 | 当前 16 TLD+ 页面已全部使用 |
| Layout Diversity | 需不同表格格式 | 当前 3 文档表格格式相似 |
| TLD Coverage | **UNKNOWN** | TLD 对新文档的覆盖率无法预测 |
| CS1 Frequency | ~37 cases/paper (TLD+) | 基于 resnet/efficientnet/cs_001 平均 |
| Near-duplicate risk | HIGH | 同表同行案例密集，去重后 ~10-15/paper |
| GT/Human adjudication cost | ~30 min/case | 每个新 Future Case 需独立 GT |

### 关键不确定性

```
TLD 覆盖率对新文档：UNKNOWN

依据：
- resnet: TLD+ 73% (8/11 页)
- efficientnet: TLD+ 63% (5/8 页)
- cs_001: TLD+ 60% (3/5 页)
- med_001: TLD+ 0% (0/15 页)

→ TLD 在学术 ML 论文上有效（3/3），在医学论文上无效（0/1）
→ 新文档属于哪种类型：UNKNOWN
→ 如果新文档是 ML 论文：可能有效，预计 ~10-15 独立 cases/paper
→ 如果新文档是医学/其他：可能完全无效
```

---

## 5. 关键问题：扩 20/50/100 个新 PDF 能否产生足够 CS1？

```
概率判断：UNKNOWN — NO BASIS FOR QUANTITATIVE PROJECTION
```

### 依据

1. **TLD 覆盖率无法外推**：TLD 对 med_001 完全失败，说明 TLD 对不同表格格式有不同的检测能力。我们只有 4 个文档（3 个 TLD+、1 个 TLD-），样本不足以估计 TLD 在新文档上的覆盖率。

2. **即使 TLD 有效，CS1 天花板效应仍然存在**：
   - 31/31 Past CS1 = KEEP_SEPARATE
   - 如果新 Corpus 也产生 100% KEEP_SEPARATE → Signal trivially correct
   - HRR 测量的将是"Human 是否信任自动化判断"，不是 Learning

3. **即使 TLD 有效且 CS1 出现，边界多样性仍缺失**：
   - TLD 从不检测 same_cell → 无 UNKNOWN 案例
   - 无 different_cell=True + GT=MERGE → 无 CONFLICT 案例
   - Signal 安全边界无法测试

4. **即使 Corpus 扩展成功，P722 天花板效应限制 HRR 空间**：
   - B1 (no cue) = 100% accuracy, 1.7s avg
   - 如果 Human 已经在 1.7s 内 100% 正确，Reuse 能减少什么？
   - 可能只能减少"是否需要查看 Evidence"的步骤，但这不是真正的 Learning

### 结论

```
扩 Corpus 可能解决 Future Case 数量问题，
但无法解决：
  - CS1 天花板效应（100% KEEP_SEPARATE）
  - 边界多样性缺失（0 CONFLICT, 0 UNKNOWN）
  - HRR 测量空间极小（B1 已 100%/1.7s）
  - TLD 覆盖率不可预测

→ 即使扩 Corpus 成功，CS1 仍可能不是合适的 Reuse Research Object
```

---

## 6. Route A 评估

### Route A 可形成的研究成果

| 研究输出 | 当前状态 | 可验证性 |
|---|---|---|
| Evidence Distillation Quality | PARTIALLY PROVEN | ✅ CAN BE VALIDATED NOW — P722 数据已有 |
| Human Feedback Relevance | IDENTIFIED | ✅ CAN BE VALIDATED NOW — 187 feedback instances 已有 |
| Evidence-Grounded Signal Identification | CANDIDATE | ✅ CAN BE VALIDATED NOW — CS1-CS4 已识别 |
| Semantic Feedback Boundary | DESIGNED | ✅ CAN BE VALIDATED NOW — counter-evidence 已有 |
| Human Validation Minimality | DESIGNED | ⚠️ REQUIRES NEW PARTICIPANTS — 10 past cases 协议已设计 |
| Automation Bias Boundary | DESIGNED | ❌ NOT CURRENTLY TESTABLE — 需要 Reuse ON/OFF 实验 |
| Learning Level Declaration | L3 | ✅ CAN BE ESTABLISHED NOW — L3 = Candidate Discovery |

### Route A 是否能形成独立完整的研究贡献？

```
YES — Route A 可以形成一个独立、完整、可解释的研究贡献：

标题: "Evidence-Grounded Signal Identification from Human Feedback:
       Candidate Discovery without Reuse"

贡献:
1. 证明 System 能将 Raw Evidence 提炼为 Human-decision-relevant Cue (C2, PROVEN)
2. 证明 Human Feedback 中存在 Evidence-grounded 可重复模式 (CS1-CS4, PARTIAL)
3. 证明 这些模式可以表达为 Signal Candidate，但 NOT Validated Signal (L3)
4. 证明 Signal Candidate 的边界可以被定义 (SUPPORTED/UNSUPPORTED/UNKNOWN/CONFLICT)
5. 证明 Reuse 需要独立 Future Cases，当前 Corpus 不足以支持 (INSUFFICIENT)
6. 明确声明: 当前 DICE = C1 + C2, NOT C3 (Learning)

这是一个诚实的、有证据支撑的研究贡献。
它不夸大，不混淆 Distillation 与 Learning。
```

---

## 7. Route B 评估

### Route B: Expected Gain vs Cost vs Risk

| 维度 | 评估 |
|---|---|
| Expected Research Gain | L4-L6 (Human Validation → Reuse → HRR) — IF successful |
| Engineering Cost | HIGH — 新 PDF 采集 + 候选构造 + TLD 计算 + GT 裁决 + 实验设计 + 参与者招募 |
| Data Collection Cost | HIGH — 需 ≥3-5 新文档，每个需人工候选筛选 + GT 裁决 |
| Risk of Repeating Current Failure | MEDIUM-HIGH — TLD 可能对新文档无效 |

### Route B 六大风险

| Risk | 概率 | 影响 | 说明 |
|---|---|---|---|
| **Risk 1**: 新 Corpus 无足够 CS1 | UNKNOWN | FATAL | TLD 对新文档覆盖率不可预测；med_001 0% 覆盖 |
| **Risk 2**: CS1 高度 layout-specific | MEDIUM | SEVERE | 31/31 KEEP_SEPARATE，天花板效应；无 MERGE 多样性 |
| **Risk 3**: Future Cases 仍有 source/layout leakage | MEDIUM | MODERATE | 同领域论文可能有相似表格格式 |
| **Risk 4**: Validation 成功但 Reuse 失败 | MEDIUM | SEVERE | Signal validated 但 HRR=0（B1 已 100%/1.7s） |
| **Risk 5**: Reuse 成功但只是结构重复 | MEDIUM | SEVERE | 不是 generalization，只是 same-pattern recognition |
| **Risk 6**: Review reduction 来自 automation bias | MEDIUM | FATAL | HRR>0 但来自 blind acceptance，不是 learning |

### Route B 成功条件（全部需要满足）

```
1. TLD 在新 Corpus 上有效 (UNKNOWN)
2. CS1 出现足够独立 Future Cases (需 ≥10)
3. CS1 有 GT 多样性 (需 MERGE + CONFLICT + UNKNOWN)
4. Human Validation 成功 (需 ≥8/10)
5. Reuse ON 减少 Human Review (需 HRR > 0)
6. Quality maintained (需 accuracy_ON ≥ accuracy_OFF)
7. Boundary preserved (需 UNKNOWN_preserved)
8. No automation bias (需 override_rate > 0)
```

**8 个条件全部满足的概率：LOW**

---

## 8. Decision Matrix

| Dimension | Route A: 收缩研究 | Route B: 扩展 Corpus |
|---|---|---|
| 当前可执行性 | ✅ HIGH — 现有数据即可 | ❌ LOW — 需新 Corpus + 新 GT + 新实验 |
| 研究价值 | MEDIUM — 证明已实现的 + 明确边界 | HIGH (if successful) — 真正 Reuse Learning |
| Original DICE Goal 一致性 | PARTIAL — 证明 Candidate Discovery，不证明 Reuse | HIGH — 直接追求 Reuse + HRR |
| Evidence 基础 | ✅ STRONG — 187 feedback + 31 CS1 + 545 pool | ⚠️ WEAK — TLD 覆盖率未知 |
| Human Feedback 研究价值 | ✅ HIGH — 识别 evidence-grounded vs image-driven | MEDIUM — Feedback 只在 Reuse 中有价值 |
| Reuse 可验证性 | ❌ NOT ACHIEVABLE | ⚠️ CONDITIONAL — 8 个成功条件，概率 LOW |
| Generalization 风险 | N/A — 不追求 generalization | HIGH — TLD layout-specific, ceiling effect |
| Data Cost | ✅ ZERO — 使用现有数据 | HIGH — 需 3-5 新 PDF + GT 裁决 |
| Engineering Cost | ✅ LOW — 分析 + 设计 | HIGH — 新管道 + 新实验 + 新 UI |
| Research Risk | ✅ LOW — 证明已知的 | HIGH — 6 个风险，2 个 FATAL |
| 当前证据支持程度 | ✅ STRONG | ⚠️ INSUFFICIENT — TLD 覆盖率 + CS1 天花板 |

---

## 9. Recommended Route

```
RECOMMENDED_ROUTE = A→B
```

### 理由

1. **Route A 立即可执行**：现有 187 feedback instances + 31 CS1 past cases + CS1-CS4 candidates + counter-evidence + boundary definitions → 足以形成完整研究贡献。

2. **Route B 有 FATAL 级风险**：Risk 1 (TLD 覆盖率 UNKNOWN) 和 Risk 6 (automation bias) 都是 FATAL — 一旦发生，全部投入浪费。

3. **Route A 输出直接降低 Route B 不确定性**：
   - Human Validation 成功 → CS1 值得扩 Corpus 测试
   - Human Validation 失败 → CS1 不值得扩 Corpus，节省投入
   - Boundary 分析完成 → 知道需要什么类型的 Corpus（有 CONFLICT/UNKNOWN 的）

4. **A→B 是 evidence-based sequencing**，不是回避：
   - Route A 完成后，如果证据支持 Route B → 执行 Route B
   - Route A 完成后，如果证据不支持 Route B → 明确停止或重新定义 Signal

5. **避免 sunk-cost bias**：CS1 已投入大量工作，但 CS1 的天花板效应（100% KEEP_SEPARATE）和边界缺失（0 CONFLICT/UNKNOWN）是结构性限制，不会因扩 Corpus 而消失。

### 不选 INSUFFICIENT_EVIDENCE 的理由

我们有足够证据判断：
- Route A **立即可行**（现有数据充分）
- Route B **风险显著**（TLD 未知 + 天花板 + 无边界）
- A→B **sequencing 合理**（A 的输出降低 B 的不确定性）

这不是"无法判断"，而是"有足够证据选择先 A 后 B"。

---

## 10. Route A 具体研究输出

如果执行 Route A，将产出：

```
1. Evidence Distillation Quality Audit
   → 使用 P722 数据证明 Cue 是否减少 Human Effort (E1: time reduction)
   → 明确声明这是 C2 (Distillation)，不是 C3 (Learning)

2. Human Feedback Evidence-Groundedness Audit
   → 对 187 feedback instances 分类：
     - Evidence-grounded (有 TLD/text evidence 支撑)
     - Image-driven (依赖图像，无 evidence 支撑)
     - Incidental recurrence (偶然重复)
     - Semantic overreach (过度泛化)

3. Signal Candidate Boundary Audit
   → 对 CS1-CS4 定义完整边界 (SUPPORTED/UNSUPPORTED/UNKNOWN/CONFLICT)
   → 使用 counter-evidence 验证边界有效性

4. Learning Level Declaration
   → 明确声明 CURRENT_LEVEL = L3 (Candidate Discovery)
   → 明确声明 NOT Learning (C3 requires Reuse + HRR)
   → 明确声明 Route B 的前提条件

5. Route B Feasibility Assessment (based on Route A output)
   → 如果 Human Validation 可执行且成功 → Route B 有基础
   → 如果 CS1 天花板效应确认 → Route B 需要新 Signal (非 CS1)
   → 如果 TLD 覆盖率分析显示高风险 → Route B 需谨慎
```

---

## 11. Next Minimal Audit (如果选择 A→B)

在 Route A 完成后，执行一个最小 READ-ONLY Audit 来决定 Route B：

```
Audit: TLD Coverage Projection on New Corpus

目标: 估计 TLD 在新文档上的预期覆盖率

方法:
1. 分析 TLD 对 4 个现有文档的覆盖率模式
2. 分析 TLD 检测表格所需的页面布局特征
3. 识别 TLD-positive 和 TLD-negative 页面的结构差异
4. 基于结构特征，估计新文档类型的 TLD 覆盖概率

输出:
- TLD-positive 概率: LOW / MEDIUM / HIGH / UNKNOWN
- 推荐 Corpus 类型: academic ML / medical / mixed / UNKNOWN
- Route B Go/No-Go 建议

注意: 这仍然是 READ-ONLY，不下载新文档，不修改 TLD。
```

---

## 12. Governance Gate

```
DICE_CORE_MODIFICATION      = NO
NEW_MODULE                  = NO
NEW_ENGINE                  = NO
SIGNAL_MODIFICATION         = NO
TLD_MODIFICATION            = NO
EVIDENCE_CUE_MODIFICATION   = NO
RUNTIME_CHANGE              = NO
ML_TRAINING                 = NO
FROZEN_BASELINE             = INTACT
FROZEN_EXPERIMENT           = INTACT
FORMAL_EXPERIMENT           = NOT_STARTED
CS1_REUSE                   = BLOCKED
HUMAN_VALIDATION            = BLOCKED
STOP                        = TRUE
```

---

## 13. 最终回答

> **DICE 下一阶段究竟应该研究什么，以及为什么。**

### 研究什么

```
Route A: 收缩研究目标

1. 证明 Evidence Distillation 的实际效果（C2，使用 P722 数据）
2. 识别 Human Feedback 中的 Evidence-grounded 模式（CS1-CS4）
3. 定义 Signal Candidate 的完整边界（SUPPORTED/UNSUPPORTED/UNKNOWN/CONFLICT）
4. 明确声明 Learning Level = L3（Candidate Discovery），不是 Learning
5. 评估 Route B 可行性（基于 Route A 输出）
```

### 为什么

```
1. Route A 立即可执行 — 现有数据充分，零额外采集成本
2. Route B 有 FATAL 级风险 — TLD 覆盖率 UNKNOWN + CS1 天花板效应
3. Route A 是诚实的 — 不夸大 Distillation 为 Learning，明确边界
4. Route A 降低 Route B 不确定性 — Human Validation 结果决定 Route B Go/No-Go
5. 避免 sunk-cost bias — CS1 的结构性限制（100% KEEP_SEPARATE、0 CONFLICT）不会因扩 Corpus 消失
6. A→B sequencing — 先证明已知的，再追求可能的
```

`STOP = TRUE`。
