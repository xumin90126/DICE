# IS-11 Stage 4 Closure: READ-ONLY Conclusion Note

> **本文件为 READ-ONLY 诊断结论。不包含任何修改建议。不授权任何实现。**

---

## 一、已证实 (Proven)

以下结论严格基于 Stage 4 的 45-case 实验结果，可直接引用：

1. **IS-11 在本次 45-case experiment 中未降低 FP。**
   - Baseline B: FP=1
   - Experimental C: FP=1
   - ΔFP = 0
   - G7 (FP Reduction, PRIMARY gate) = **FAIL**

2. **IS-11 没有造成 Recall 退化。**
   - Baseline B: Recall=0.0
   - Experimental C: Recall=0.0
   - ΔRecall = 0.0
   - G8 (Recall/Coverage Safety) = **PASS**

3. **Coverage 从 42.2% 增至 60.0%。**
   - ΔCoverage = +17.8 percentage points
   - IS-11 将 8 个 INSUFFICIENT_EVIDENCE case 解析为 KEEP_SEPARATE
   - 这 8 个 case 的 GT 全部为 KEEP_SEPARATE → 全部正确

4. **8 个新增可判定案例均与 GT 一致。**
   - 所有 8 个 C vs B 差异均为 INSUFFICIENT_EVIDENCE → KEEP_SEPARATE
   - 所有 8 个的 GT 均为 KEEP_SEPARATE
   - 无新增 FP，无新增 FN

5. **Determinism PASS。**
   - 两次运行 Experimental C，0 mismatches
   - case-level prediction, IS-11 observation, decision, abstention, trace 全部一致

6. **当前实验没有建立 cross-document FP-reduction stability。**
   - 0/4 文档减少了 FP
   - cross-document stability = **NOT_ESTABLISHED**

7. **32/45 (71.1%) 的 case 未获得 TABLE_CELL_CONTEXT 信息。**
   - 25 case: TABLE_NOT_DETECTED (table_line_detector 未检测到表格)
   - 7 case: CANDIDATE_OUTSIDE_TABLE_BBOX (检测到表格但候选不在表格区域内)
   - PRIMARY bottleneck = table_line_detector coverage

8. **2 个 MERGE GT case 均在 unavailable 集合中。**
   - IS11-AMB-414 (med_001 p20, figure caption) 和 IS11-AMB-422 (med_001 p24, figure caption)
   - 两者都不是表格内容 → IS-11 在设计上无法提供增量信息

9. **唯一 FP case (IS11-AMB-135) 在 unavailable 集合中。**
   - efficientnet p5, text_a="4", text_b="MBConv6, k5x5"
   - table_line_detector 未检测到该页表格
   - IS-11 无法提供 cell context → 无法纠正此 FP

---

## 二、尚未证实 (Not Yet Proven)

以下结论**不可声称**，因为当前实验证据不足：

1. **不可声称 "IS-11 无价值"。**
   - IS-11 正确解析了 8 个 ambiguous case，覆盖率提升 17.8%
   - 但 G7 FAIL，未实现预注册的 FP-reduction 目标
   - "无 FP-reduction 价值" ≠ "无任何价值"

2. **不可声称 "TABLE_CELL_CONTEXT 无效"。**
   - 71.1% 的 case 因 table_line_detector coverage 不足而无法获得 IS-11 信息
   - 在可获得 IS-11 信息的 13 个 case 中，cell membership 全部正确解析
   - 信息源本身的有效性未被充分测试

3. **不可声称 "IS-11 能普遍提升 Coverage 17.8%"。**
   - 17.8% 是 45-case sample 上的点估计
   - MERGE=2, KEEP_SEPARATE=43 的极端不平衡分布使统计稳定性不足
   - 不可外推到全部 545 case 或其他 corpus

4. **不可声称 "table_line_detector 修复后一定有效"。**
   - 修复 detector coverage 可能增加 IS-11 可用 case 数
   - 但新增 case 中 IS-11 是否能正确提供 cell context 未知
   - 不存在 "修复 detector → IS-11 自动 PASS G7" 的保证

5. **不可声称 "IS-11 一定能够降低 FP"。**
   - 当前唯一 FP case 不在表格区域
   - 即使 detector coverage 提升，FP case 可能仍不在检测到的表格内
   - FP-reduction 能力未被实验证实

6. **不可对 Recall / Precision 的统计稳定性做过度解释。**
   - GT MERGE = 2 → Recall 的分母仅为 2
   - 1 个 case 的变化就会使 Recall 从 0.0 跳到 0.5
   - Precision 同理 (TP+FP=1 → 分母为 1)
   - 这些指标的置信区间极宽，不可作为独立判断依据

---

## 三、实验边界

| 维度 | 值 | 影响 |
|------|-----|------|
| Sample size | 45 | 统计功效有限 |
| GT MERGE | 2 | Recall 分母=2，统计不稳定 |
| GT KEEP_SEPARATE | 43 | TN 分母大，相对稳定 |
| Corpus | 4 PDFs | 不可外推到其他文档类型 |
| IS-11 observer | table_line_detector (frozen) | coverage 受限于当前 detector |
| Information source | IS-11 only | 不可同时评估 IS-10/IS-12/IS-14 |
| Experimental | experiment-only | 不可集成进 P1-P6 |

---

## 四、结论

> IS-11 (TABLE_CELL_CONTEXT) 在当前 45-case 实验条件下：
> - **G7 = FAIL** → 未通过预注册的 PRIMARY gate (FP reduction)
> - **G8 = PASS** → 覆盖率和 recall 安全
> - **覆盖率提升** → 8 个 ambiguous case 正确解析
> - **cross-document stability NOT ESTABLISHED**
> - **信息可用性 bottleneck** → 71.1% case 无 table context

> 根据 §23 研究结论规则：
> 
> G7 = FAIL → **IS-11 does not demonstrate the preregistered FP-reduction value.**
> 
> 但这不等于 "IS-11 无价值"——覆盖率提升和 8/8 正确解析表明 IS-11 在可获得信息时可能有效，但当前实验设计无法充分验证其 FP-reduction 能力。
