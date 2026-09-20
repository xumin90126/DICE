# DICE Evidence Discrepancy / Correction Log

> 研究完整性记录。不覆盖历史。每条: OLD → AUDIT → CORRECTED → REASON → TIMING。
> 目的: 未来论文 research integrity — 保留过程的真实演进, 不为统一叙事抹去修正。

标注: [O] original (历史报告原值) · [A] audit (审计发现) · [C] corrected (修正值) ·
[R] reason · [T] timing (修正发生阶段)。

---

## D1. M-B DIRECT case count: 6 → 8 → 9

- **[O] original**: Slicing Failure Impact Ranking 报告 "M-B = 6 DIRECT + 3 INDIRECT"
  (`tmp/slicing_failure_impact_ranking.md`)。基于机器评估报告 §9 的归因
  "5 eff + 3 cs" (eff 弃权 5 例 + cs 弃权 3 例)。
- **[A] audit**: M-B Expressability Audit 逐案显微镜核对, 发现机器评估报告 §9 的归因与
  逐案记录不符: eff 实为 3 例 (AMB-130 p5, AMB-262 p7, AMB-313 p8), cs 实为 7 例 (全 p3)。
  报告 §9 的 "5 eff + 3 cs" 归因错误。Phase 2 design 据此写 "M-B DIRECT = 8" (1 FP + 2 eff +
  5 cs) 但逐案枚举实为 9 (1 FP + 2 eff + 6 cs)。
- **[C] corrected**: **M-B DIRECT = 9** = AMB-135 (FP) + AMB-130, AMB-313 (eff) +
  AMB-457, AMB-462, AMB-467, AMB-483, AMB-505, AMB-514 (cs p3)。Phase 2.1 reconciliation
  PASS (每案独立 inclusion rationale)。OUT of scope: AMB-262 (非同带), AMB-519 (正文)。
- **[R] reason**: 机器评估报告 §9 用了文档级粗归因, 逐案显微镜发现实际 C 弃权在 cs p3
  有 7 例 (非 3); Phase 2 design 的 "8" 是算术笔误 (枚举了 9 但标 8)。
- **[T] timing**: M-B Expressability Audit (首次发现 5eff+3cs 与逐案不符) →
  Phase 2.1 (canonical reconciliation = 9, PASS)。

## D2. eff / cs C-abstain breakdown: "5 eff + 3 cs" → "3 eff + 7 cs"

- **[O] original**: 机器评估报告 §9 "5 eff + 3 cs" (18 例 C 弃权的文档归因)。
- **[A] audit**: 逐案 `case_results` 核对, 实际 = **eff 3 + med 8 + cs 7** (共 18)。
- **[C] corrected**: eff 3 (130/262/313) + med 8 + cs 7 (全 p3)。
- **[R] reason**: 报告 §9 归因口径与逐案 JSON 不一致 (可能早期版本统计口径漂移)。
- **[T] timing**: M-B Expressability Audit (双口径披露)。
- **影响**: 不影响总数 18, 但影响 M-B DIRECT 范围划定 (见 D1)。

## D3. AMB-262 classification: "different_band (OUT of M-B scope)" → "same-band (GT-consistent recovery)"

- **[O] original**: Phase 2 / 2.1 / Expressability Audit 标 AMB-262 为 "same_y_band=False
  (BELOW, v_gap=17.61) → 非同带对 → M-B cell-context 路线不适用 → OUT of scope"。
  依据: 早期 atom 测量 ('41M' × 'EfficientNet-' pairwise same_y_band=False)。
- **[A] audit**: Phase 3.2 isolated replay 实际运行 sampling-frame 的 AMB-262 案例对,
  发现实际案例对为同带 + 不同 x0 分区 (lsp x187.4 vs x213.1, co_density=41) →
  EIC-1 正确发射 → KEEP_SEPARATE (GT=KEEP_SEPARATE, GT-consistent recovery)。
- **[C] corrected**: AMB-262 实际案例对 = 同带 + 不同分区 → EIC-1 发射 → GT-consistent。
  早期 "different_band" 分类针对的是**不同的 atom 对** (非 sampling-frame 的案例对)。
- **[R] reason**: 早期显微镜测量选取的 atom 对 ('41M' × 'EfficientNet-') 与 sampling-frame
  定义的实际候选对不同; replay 用实际案例对纠正了分类。
- **[T] timing**: Phase 3.2 (实验揭示, 非人为修正)。
- **性质**: **非失败** — 实验揭示了分类误差; 结果 GT-consistent, 未引入错误。已记入
  Honest Disclosure。矩阵未因结果修改 (AMB-262 始终在矩阵 C 类)。

## D4. OFF path "mismatches": 8/21 apparent → 0 real (tuple/list serialization artifact)

- **[O] original**: Phase 3.2 replay OFF-vs-archived 报 "13/21 match; 8 mismatches"。
- **[A] audit**: 逐字段核对, 8 mismatch 全部是 TLD-detected table 案例; 决策相关布尔
  (is_in_table/same_cell/different_cell) 全部一致; 差异仅在 `table_info.a_cell/b_cell`
  (harness 返回 `(row_idx, col_idx)` tuple, 存档 JSON 序列化为 list `[row_idx, col_idx]`)。
  tuple→list 归一化后 0 真实差异; 决策 21/21 byte-identical。
- **[C] corrected**: **OFF = byte-identical** (21/21 决策; 8 "mismatch" = 序列化伪影)。
- **[R] reason**: Python tuple vs JSON list 序列化类型差异, 非行为差异。
- **[T] timing**: Phase 3.2 independent audit。
- **性质**: 非失败; S9 PASS。

## D5. AMB-135 '4' atom identity: resolution '4' → row-number '4'

- **[O] original**: 早期显微镜按内容匹配 '4' 取最后匹配, 误取 resolution '4'@521.00
  (h_gap=116.44)。
- **[A] audit**: 全量枚举发现 p5 有两个 '4' 原子; FP pair 实为行号 '4'@320.35
  (lag_n=10, h_gap=30.02)。
- **[C] corrected**: FP pair = 行号 '4'@320.35 × 'MBConv6, k5x5'@354.14 (h_gap=30.02)。
- **[R] reason**: 按内容匹配取最后 = 歧义; 全量枚举修正。
- **[T] timing**: M-B Expressability Audit 前期显微镜 (/tmp/mb_fp_precise.py)。

## D6. 组枚举口径: top left_alignment_group (整页边距组) → 案例 atom 自身 lag + x0 簇

- **[O] original**: 早期组枚举取 top left_alignment_group 作列簇 (n=40, y-ext 600pt)。
- **[A] audit**: top 组是整页边距组 (page-wide margin), 非表格列。
- **[C] corrected**: 改按案例 atom 读自身 lag + p5 表区 x0 单链聚类 (zone 原子直接 x0 聚类)。
- **[R] reason**: 整组对象 ≠ 局部列 (PH-02 whole-group 陷阱的早期体现)。
- **[T] timing**: M-B Expressability Audit 显微镜修正 (/tmp/mb_cols.py)。

## D7. PH-02 "FP=3" (impact ranking) vs "FP=1" (case-level)

- **[O] original**: Impact Ranking 报告 M-B 行 "FP=3 (证据污染)"。
- **[A] audit**: 45-case machine eval 逐案, IS-11 唯一 FP = AMB-135 (C 弃权 18, 非 FP)。
- **[C] corrected**: 真实 FP = 1 (AMB-135)。Impact Ranking 的 "FP=3" 可能指某种聚合计数口径
  (未在报告中精确界定)。
- **[R] reason**: ranking 报告的 "FP=3" 口径未明确, 与逐案 FP=1 不一致。
- **[T] timing**: M-B Expressability Audit (逐案确认唯一 FP)。
- **处置**: 双口径披露, 不强改 ranking 报告历史值。

## 原则
- 历史报告文件**未覆盖修改** (输出纪律: 每轮只新增指定文件);
- 所有修正以新报告 + 本 log 记录, 保留 OLD → CORRECTED 双值;
- 修正原因与时机可追溯; 非为统一叙事抹去过程。
