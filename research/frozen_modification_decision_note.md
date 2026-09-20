# Frozen Modification Decision Note

> **READ-ONLY 决策文件。不授权任何修改。**
> 
> 生成时间: Stage 4 Closure
> 基于: Stage 4 实验结果 + Frozen Baseline 完整性确认

---

## F1 — 是否已经证明 Frozen 是当前研究瓶颈？

### 结论: INCONCLUSIVE

### 证据

Stage 4 实验结果表明 IS-11 的主要限制是 **table_line_detector coverage 不足** (32/45 = 71.1% 的 case 未获得 table context)。但这不等于 "Frozen 是瓶颈"，原因如下：

1. **table_line_detector.py 是 Frozen 的一部分** (SHA-256 已验证，0 drift)。它的 coverage 限制是当前 frozen detector 的固有特性，不是 drift 或 bug。

2. **"Frozen detector coverage 不足" ≠ "需要修改 Frozen"**。coverage 不足是一个实验发现，可能意味着：
   - (a) IS-11 的假设本身依赖于当前 detector 不具备的能力 → 需要新的 detector（修改 Frozen）
   - (b) IS-11 的假设在当前 detector coverage 范围内已充分测试，结果就是 G7 FAIL → 不需要修改 Frozen
   - (c) 当前 corpus 的表格分布导致 detector coverage 偏低 → 需要新 corpus（不修改 Frozen）

3. **在 13 个可获得 table context 的 case 中**，IS-11 的 cell membership 全部正确解析，8 个 INSUFFICIENT_EVIDENCE → KEEP_SEPARATE 全部正确。这表明 IS-11 在 detector 覆盖范围内可能有效，但覆盖范围不足限制了统计功效。

4. **当前实验无法区分上述三种解释**，因此 INCONCLUSIVE。

### 不能得出 YES 的理由

- 没有证据表明修改 table_line_detector 后 IS-11 会 PASS G7
- 唯一 FP case (IS11-AMB-135) 不在表格区域，即使 detector 修复也可能不在表格内
- 2 个 MERGE GT 都是 figure captions，不是表格内容

### 不能得出 NO 的理由

- 71.1% case 无 table context 确实限制了实验的 statistical power
- 如果 detector coverage 更高，可能有更多 case 获得 IS-11 信息
- 无法排除 "修复 detector 后 IS-11 有效" 的可能性

---

## F2 — 如果下一阶段继续研究 IS-11，是否必须修改 Frozen？

### Case A — 只做新的 Information Source experiment

**是否必要修改 Frozen: NO**

如果下一个实验研究的是 IS-10 / IS-12 / IS-14 或其他新的 Information Source：
- 可以使用当前 frozen P1-P6、P4 SpanConfig、IS-01/IS-02 作为 baseline
- 新 IS 作为 experimental variable，与 Baseline B 对比
- 不需要修改任何 frozen 组件
- 不需要建立新 baseline

**是否污染已有实验: NO**
- 已有实验结果 (Stage 4) 保持 frozen
- 新实验使用新的 sampling frame / GT / corpus
- 两个实验独立，互不影响

**是否需要新 baseline: NO**
- Baseline B (Geometry + IS-01 + IS-02) 仍然是标准 baseline
- 新 IS 在 Baseline B 之上叠加

---

### Case B — 需要增强 table perception capability

**是否必要修改 Frozen: YES (如果目标是让 IS-11 获得更强的 table perception)**

如果研究问题是 "IS-11 在更强 table perception 下是否具有价值"：
- 当前 table_line_detector.py 是 frozen 的，coverage 受限
- 需要新的 table perception capability（新的 detector 或增强版）
- 这意味着修改 chunker/table_line_detector.py 或引入新的 table perception module

**是否污染已有实验: YES**
- 修改 table_line_detector.py 会改变 P1-P6 的 frozen baseline
- 已有 Stage 4 结果无法与新结果直接对比
- 需要 re-run P1-P6 重新 freeze baseline

**是否需要新 baseline: YES**
- 修改 detector 后需要重新生成 candidate universe
- 需要重新抽样、重新生成 GT
- 需要重新运行 Baseline A/B/C

**风险:**
- 可能引入 confounding（detector 变化影响所有下游）
- 可能破坏 frozen baseline 的 reproducibility
- 需要完整的 re-freeze 流程

---

### Case C — 需要修改 P1-P6

**是否必要修改 Frozen: NO (除非有明确证据表明 P1-P6 有 bug)**

当前没有证据表明 P1-P6 有 bug 或需要修改：
- P7.1 drift = 0
- P7.2 drift = 0
- P1-P6 runner SHA 全部 match
- IS-01/IS-02 定义 frozen 且一致

如果修改 P1-P6：
- 会破坏整个 frozen baseline
- 所有已有实验结果失效
- 需要完整 re-freeze

**是否污染已有实验: YES (全部)**
**是否需要新 baseline: YES (全部)**

---

### Case D — 需要修改 P4 geometry

**是否必要修改 Frozen: NO**

P4 SpanConfig (max_horizontal_gap=8.0, max_vertical_gap=14.0, same_line_tolerance=3.0, cross_column_gap_threshold=30.0, overlap_tolerance=0.5) 是 frozen 的，且 0 drift。

当前没有证据表明 P4 geometry 是瓶颈：
- 45 个 case 都是 AMBIGUOUS 状态（P4 无法判定）
- 这是实验设计的选择，不是 P4 的 bug
- 修改 P4 会改变 AMBIGUOUS 的定义，影响整个 candidate universe

**是否污染已有实验: YES**
**是否需要新 baseline: YES**

---

## F3 — 当前是否有资格解冻 Frozen？

### 结论: NOT AUTHORIZED

### 理由

1. **没有明确的实验授权** — 当前只有 Stage 4 Machine Evaluation 的授权，已完成并封存。
2. **G7 FAIL 不是解冻理由** — 实验失败不自动触发 frozen 修改。
3. **32/45 table unavailable 是诊断结果，不是解冻条件** — 诊断发现不等于修改授权。
4. **下一阶段研究问题尚未确定** — 在确定 "研究什么问题" 之前，不可讨论 "修改什么 frozen"。
5. **Frozen Baseline 0 drift** — 当前 frozen 状态完好，没有技术理由需要解冻。

### 默认状态

```
FROZEN MODIFICATION = NOT AUTHORIZED
```

除非：
- 用户明确授权新的实验阶段
- 新实验设计明确需要 frozen 修改
- 新 corpus / GT / metrics / gates 全部预注册
- 才讨论是否解冻具体组件

---

## 总结

| 问题 | 结论 |
|------|------|
| F1: Frozen 是当前研究瓶颈？ | INCONCLUSIVE |
| F2-A: 新 IS 实验 → 修改 Frozen？ | NO |
| F2-B: 增强 table perception → 修改 Frozen？ | YES (但污染已有实验) |
| F2-C: 修改 P1-P6 → 修改 Frozen？ | NO (无证据) |
| F2-D: 修改 P4 geometry → 修改 Frozen？ | NO (无证据) |
| F3: 当前有资格解冻 Frozen？ | **NOT AUTHORIZED** |
