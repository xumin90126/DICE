# Next Information Source Decision: Candidate Research Questions

> **仅提出候选研究问题。不进行 implementation。不授权任何实验。**
> 
> 每个 Option 的目的是为下一阶段决策提供框架，不是执行计划。

---

## Option A — 继续研究 IS-11: TABLE_CELL_CONTEXT 是否在更强 table perception 下具有价值？

### Research Question

> 当 table perception coverage 从当前的 28.9% (13/45) 提升到更高水平时，IS-11 (TABLE_CELL_CONTEXT) 是否能够实现预注册的 FP-reduction 目标 (G7: ΔFP < 0)？

### Current Evidence

- Stage 4 结果: G7 = FAIL (ΔFP = 0)
- 主要限制: 71.1% case 无 table context (25 TABLE_NOT_DETECTED + 7 CANDIDATE_OUTSIDE_TABLE_BBOX)
- 在 13 个可获得 table context 的 case 中: cell membership 全部正确解析, 8/8 INSUFFICIENT_EVIDENCE→KEEP_SEPARATE 全部正确
- 唯一 FP case (IS11-AMB-135) 在 unavailable 集合中 → 无法测试 IS-11 对 FP 的纠正能力

### Expected Information Gain

- 如果 detector coverage 提升, 更多 case 获得 IS-11 信息
- 可能暴露新的 FP case 或纠正已有 FP case
- 可验证 IS-11 在充分信息条件下的 FP-reduction 能力
- 可能发现 cell membership 错误（当前未观察到，但样本太小）

### Required New Corpus

- **必须**: 新的独立 corpus，包含更多表格密集页面
- 理想 corpus: ≥50% 的 AMBIGUOUS case 位于 table region
- 需要确保 candidate universe 中有足够多的 in-table case
- 4+ PDFs, 不同领域, 不同表格风格

### Frozen Modification

- **必须修改**: table_line_detector.py (或引入新的 table perception module)
- **影响**: 修改后 P1-P6 frozen baseline 失效, 需要 re-freeze
- **替代方案**: 不修改 frozen detector, 而是建立 parallel experimental detector（experiment-only, 不集成 P1-P6）
  - 这样 frozen baseline 保持不变
  - 但需要确认 experimental detector 不影响 P1-P6 的 candidate generation

### 是否需要新 GT

- **必须**: 新 corpus → 新 candidate universe → 新 sampling frame → 新 GT
- 不可复用 Stage 3 的 45-case GT（因为 corpus 不同）

### 是否需要新实验

- **必须**: 完整的 A/B/C 三条件实验
- 新的 pre-registered gates (G7/G8 或更新)
- 新的 determinism check

### 风险

1. **Confounding risk**: 如果修改 detector, baseline 变化可能混淆 IS-11 的增量效果
2. **Cost risk**: re-freeze P1-P6 是高成本操作
3. **Negative result risk**: 即使 coverage 提升, IS-11 可能仍然无法 PASS G7
4. **Generalization risk**: 新 corpus 可能不代表真实分布
5. **时间成本**: 完整的 corpus 构建 + GT + 实验可能需要数周

### 推荐优先级

**MEDIUM** — 有价值但成本高。只有在确定 IS-11 是优先研究方向时才推荐。

---

## Option B — 研究新的 Information Source: 是否存在比 TABLE_CELL_CONTEXT 更稳定的结构信息？

### Research Question

> 是否存在一个比 TABLE_CELL_CONTEXT 更稳定、coverage 更高的结构信息源，能够在 AMBIGUOUS case 上实现 FP-reduction？

### 候选 Information Sources (仅列举, 不定义)

- **IS-XX: COLUMN_ALIGNMENT** — 两个 candidate 是否属于同一列（基于 x-position alignment）
- **IS-XX: PARAGRAPH_MEMBERSHIP** — 两个 candidate 是否属于同一段落（基于 indentation + line spacing）
- **IS-XX: FIGURE_CAPTION_CONTEXT** — 两个 candidate 是否属于同一 figure caption（"FIG. X:" 前缀检测）
- **IS-XX: SENTENCE_BOUNDARY** — 两个 candidate 之间是否存在句号/大写边界
- **IS-XX: HEADING_HIERARCHY** — 两个 candidate 是否属于不同 heading 层级

### Current Evidence

- Stage 4 的 32 unavailable case 中:
  - 2 MERGE GT 是 figure captions → FIGURE_CAPTION_CONTEXT 可能有效
  - 7 case 在 cs_001 p3 表格检测到但候选不在表格内 → COLUMN_ALIGNMENT 可能有效
  - 多个 case 是不同列的数值对 → COLUMN_ALIGNMENT 可能有效
- Reviewer B 的 MERGE 原则: "same paragraph/caption = MERGE; different cell = KEEP_SEPARATE"
  → 暗示 PARAGRAPH_MEMBERSHIP 和 FIGURE_CAPTION_CONTEXT 可能是更有效的信号

### Expected Information Gain

- 新 IS 可能覆盖 IS-11 无法覆盖的 case 类型（非表格区域）
- 可能实现更高的 coverage 和 FP-reduction
- 可能不需要修改 frozen detector

### Required New Corpus

- **可能不需要**: 可以复用 Stage 3 的 45-case Sampling Frame 和 GT
- 但需要新 IS 的 experimental observer
- 如果复用 corpus, 可以直接与 Stage 4 Baseline B 对比

### Frozen Modification

- **不需要修改 Frozen** (如果新 IS 不依赖 table_line_detector)
- 新 IS 作为 experiment-only observer, 与 Baseline B 对比
- P1-P6, P4, IS-01/IS-02 全部保持 frozen

### 是否需要新 GT

- **不需要** (如果复用 Stage 3 GT)
- 可以直接使用已有的 45-case Semantic GT

### 是否需要新实验

- **必须**: 新的 pre-registered experiment design
- 新 IS 的 A/B/C 三条件
- 新的 gates

### 风险

1. **Hypothesis risk**: 新 IS 可能同样 FAIL G7
2. **Multiple testing risk**: 如果同时测试多个候选 IS, 需要校正
3. **GT bias risk**: 复用 GT 可能引入 hindsight bias（GT 是在看到 case 后生成的）
4. **Coverage risk**: 新 IS 可能也有 coverage 限制

### 推荐优先级

**HIGH** — 成本低（复用 corpus/GT），潜在信息增益高。推荐优先探索。

---

## Option C — 研究 Evidence Sufficiency: 为什么大量 cases 无法达到 sufficient evidence？

### Research Question

> 为什么 57.8% (Baseline B) / 40.0% (Experimental C) 的 AMBIGUOUS case 无法达到 sufficient evidence？是否存在系统性的 evidence gap？

### Current Evidence

- Baseline B: 26/45 INSUFFICIENT_EVIDENCE (57.8%)
- Experimental C: 18/45 INSUFFICIENT_EVIDENCE (40.0%)
- IS-11 将 8 个 INSUFFICIENT_EVIDENCE 解析为 KEEP_SEPARATE, 但仍有 18 个无法判定
- 18 个未解析 case 的分布:
  - 10 med_001: figure captions, axis labels, diagram items (非表格内容)
  - 5 efficientnet: table_line_detector 未检测到表格
  - 3 cs_001: 候选不在检测到的表格 cell 内

### Expected Information Gain

- 理解 evidence gap 的结构: 是 IS-01/IS-02 定义太窄？还是候选 case 本身需要新的 IS？
- 可能发现 IS-01/IS-02 的改进方向（但不修改 frozen, 只是诊断）
- 可能指导下一个 IS 的设计

### Required New Corpus

- **不需要**: 使用已有 45-case Sampling Frame
- 纯分析性研究, 不需要新数据

### Frozen Modification

- **不需要修改 Frozen**
- 纯 READ-ONLY 分析

### 是否需要新 GT

- **不需要**: 使用已有 GT

### 是否需要新实验

- **不需要新实验**, 但需要新的分析框架
- 可能需要: 逐 case 分析 evidence chain, 识别 evidence gap pattern

### 风险

1. **可能无 actionable conclusion**: 分析可能只确认 "需要新 IS", 但不指出具体方向
2. **Hindsight bias**: 分析已有结果可能引入后见之明
3. **Limited scope**: 45 case 可能不足以发现系统性 pattern

### 推荐优先级

**MEDIUM-HIGH** — 成本最低（纯分析），可以作为 Option B 的前置研究。

---

## 对比总结

| 维度 | Option A (继续 IS-11) | Option B (新 IS) | Option C (Evidence Sufficiency) |
|------|----------------------|-------------------|-------------------------------|
| 成本 | HIGH (新 corpus + 可能 re-freeze) | LOW-MEDIUM (复用 corpus/GT) | LOW (纯分析) |
| Frozen 修改 | 可能需要 | 不需要 | 不需要 |
| 新 GT | 必须 | 不需要 | 不需要 |
| 新 corpus | 必须 | 不需要 | 不需要 |
| 潜在信息增益 | 验证 IS-11 在强 detector 下的价值 | 发现更有效的 IS | 理解 evidence gap |
| 主要风险 | Confounding + negative result | Hypothesis risk | 无 actionable conclusion |
| 推荐优先级 | MEDIUM | **HIGH** | MEDIUM-HIGH |

### 建议路径

```
Option C (诊断 evidence gap)
    ↓
Option B (基于诊断设计新 IS)
    ↓
[如有必要] Option A (在新 IS 基础上重新评估 IS-11)
```

> **注意**: 以上仅为候选研究问题框架。不授权任何实现。下一阶段必须先确定研究问题，再设计实验。
