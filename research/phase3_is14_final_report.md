# Phase 3 — IS-14 GRAPHIC_TEXT_CONTEXT Controlled Experiment

> **最终状态: BLOCKED (G-C1 pre-condition FAIL) — 依预注册状态机在 Human Review 之前停止。**
> 无 GT 收集、无 Baseline/C 运行、无评估指标。本报告记录到达 STOP 的全部可审计过程与根因分析。

---

## 1. Executive Summary

Phase 3 在第一个 pre-condition gate (**G-C1 corpus sufficiency**) 处**依预注册规则 BLOCKED**:

- 冻结样本 (n=54, 几何盲分层抽样, seed=20250910) 中 figure-context 案例 = **3** (要求 ≥15) → **G-C1 = FAIL**
- control 案例 = 21 (≥20 ✅)
- 依 Phase 3 §5/§8/§41: pre-condition FAIL → **STOP，不得重抽样、不得改语料定义、不得改阈值、不得改 observer 定义**

过程中发生并处置了一起实现错误事件 (INCIDENT-1: OBS-C run-expansion bug → 首次 G-C1 计数无效 → 修复(阈值零改动) → 独立验证 → 重跑)。修正后的有效计数仍然 FAIL — 失败是**语料/切片结构性属性**, 不是实现假象。

**IS-14 假设未被证伪也未被证实** — 实验从未到达可评估状态。IS-14 = GRAPHIC_TEXT_CONTEXT 保持 **HYPOTHESIS ONLY**。

## 2. Governance State

```text
Phase 1 = COMPLETE (LOOP_SUPPORTED)
Phase 2 = COMPLETE (DESIGN_READY, 3 pre-conditions)
Phase 3 = BLOCKED (G-C1 FAIL) — 无 EXPERIMENT 决策 (§36 各 CASE 均不适用)
IS-14 = GRAPHIC_TEXT_CONTEXT / HYPOTHESIS ONLY
本阶段获得授权: 受控实验实施授权 (experiment-only observer + runner)
未获得: Production / P7.3 / Capability / Runtime / Frozen 修改授权 (始终禁止)
```

## 3. Pre-condition Verification

### G-C1 Corpus Sufficiency — **FAIL**

| 项 | 要求 | 实测 | 判定 |
|----|------|------|------|
| figure-context cases | ≥15 | **3** (caption-block 1 + tick-run 2) | ❌ FAIL |
| control cases | ≥20 | 21 | ✅ |
| corpus 形态 | 4–6 PDFs, ≥3 新域, SHA manifest, seed 冻结 | 5 PDFs, 4 新域 ✅ | ✅ |
| 结构多样性 | 不得全部来自单一文档/figure/pattern | 3 例分布: 2 tick (GraphCast) + 1 caption-block | ⚠️ 勉强但不满足门槛 |

计数定义在运行前预注册并写入 `tmp/phase3_is14_gc1_count.json` metadata; 计数防火墙: 仅用于 gate, 不向评审展示, 不增删案例。

### G-C2 Caption Regex Freeze — **PASS**

- 冻结正则 `^(FIG|Fig\.?|Figure)\s*\d+\s*[:.]?` (IGNORECASE), SHA-256 `b7f8e3d6...` 记录于 corpus manifest
- 在真实语料验证: **115 个 caption-label span 全部命中** (5 PDFs)
- 冻结后未修改; 实验全程未调 regex

### G-C3 Vector Figure Limitation — **PASS**

- 实测: 227 个 image block 仅分布于 27/314 页; LIGO/EHT 图为 raster (80/37 blocks), GraphCast/CAGI 大量为 vector
- 披露已固化于 corpus manifest: **OBS-D = AUXILIARY ONLY, 不得作为 figure 存在性判据**

**Pre-condition 决定 (§8): G-C1 FAIL → PHASE 3 = BLOCKED, STOP = TRUE**

## 4. Independent Corpus

`tmp/phase3_is14_corpus_manifest.json` (FROZEN):

| Doc ID | arXiv | 域 (全部新) | 页 | caption labels | image blocks |
|--------|-------|------------|----|--------------|--------------|
| PH3-ASTRO-001 | 1602.03837 | astrophysics (GW) | 16 | 4 | 80 |
| PH3-EARTH-001 | 1906.11238 | astrophysics (EHT) | 17 | 4 | 37 |
| PH3-EARTH-002 | 2212.12794 | earth science / weather ML | 102 | 53 | 65 |
| PH3-BIO-001 | 2205.05897 | genomics (CAGI) | 124 | 45 | 35 |
| PH3-MED-001 | 2309.04040 | medical physics (MRI) | 55 | 9 | 10 |

独立性: 5 个 arXiv ID 在 repo 全部 artifact grep = 0 匹配; 与既有语料 SHA-256 零重叠。
排除记录: 下载池中 2203.15556 (Chinchilla, LLM — 与 cs_001 域冲突) 与 2212.07702 (10页/2 caption, 不满足 figure-heavy) 被排除, 未进入 manifest。

## 5. Sampling Protocol

- `tmp/phase3_is14_candidate_universe.json`: 1299 AMBIGUOUS cases (冻结 P1–P6 纯几何切片; 39,882 pairs, 14.7s)
- `tmp/phase3_is14_sampling_manifest.json`: n=54, seed=20250910 (corpus 冻结时记录), 几何盲分层 (doc × gap × w_b × line_obs), 分配 8/8/9/12/17, min-per-doc=8
- **无重抽样**; 抽样不含任何 IS/文本内容信息 (与 Stage 1 同纪律)

## 6. Human Review Protocol — **NOT REACHED**

设计已就绪 (Phase 2 §12: label-only, 双盲, 无 reason 字段), 但因 G-C1 FAIL, 评审未开始, 无盲审包生成。

## 7. Frozen GT — **NOT REACHED**

无 GT 收集。`tmp/phase3_is14_gt.json` 不存在 — 依 §31 说明: 该 artifact 仅在到达 GT 阶段后产生; 本阶段在 pre-condition 处合法停止。

## 8. IS-14 Observer Definition

`tmp/phase3_is14_observer.py` — experiment-only, **information-only** (无 decision/score/ranking/recommendation 输出路径):

| OBS | 冻结定义 (Phase 2 §7) | 阈值 (冻结) |
|-----|----------------------|------------|
| OBS-A | caption-label 正则 (G-C2) | — |
| OBS-B | label 块内 / 紧邻连续块 | block gap ≤ 14pt, 同栏, 块内无新 label |
| OBS-C | 纯数值 + 对齐 run (行 y±2pt / 列 x±2pt), ≥3 成员, 字号差 ≤0.5pt, 间距 CV ≤0.15 | 全部冻结 |
| OBS-D | image-block 20pt 邻近 (AUXILIARY ONLY) | — |

域前置: IS-11 as-run (代码逐字复制自冻结 Stage 4 evaluation) → in_table=True 则 IS-14 = NOT_APPLICABLE。

**INCIDENT-1 (§29 分类: IMPLEMENTATION_ERROR / OBSERVER_OUTPUT_ERROR)**: OBS-C 首版贪心扩张在单 gap 窗口停滞 (CV 对 n<2 返回 None 阻断扩张) → med_001 p19 真实 ticks 校验失败 → 修复为穷举极大窗口枚举 (**阈值零改动**) → 真实 ticks 全部检出 (run=5/10, CV≈0) + 负对照通过 → 首次 G-C1 计数判无效, 重跑。详见 `tmp/phase3_is14_incident_log.md`。

## 9–12. OBS-A/B/C/D Results — 仅 G-C1 计数运行

| OBS | 冻结样本 (n=54) | Universe (1299) |
|-----|----------------|-----------------|
| OBS-A (fragment 为 caption-label) | 0 | 3 |
| OBS-B / caption-block membership | 1 | 3 |
| OBS-C (双 fragment 均 in-run) | 2 | 76 |
| OBS-D | 辅助记录, 未参与判定 | — |
| table domain (IS-11 as-run, IS-14 不适用) | **30/54 (55.6%)** | — |

## 13–15. Baseline B / Experimental C / Case-Level Differences — **NOT REACHED**

无评估运行。`baseline_b_results / experimental_c_results` artifacts 不存在 (原因同 §7)。

## 16–18. Safety / Utility / Cross-Document Metrics — **NOT REACHED** (G-S1..S4, G-U1/U2, G-D1 不适用)

G-S5-equivalent 回归验证 **PASS** (见 §21)。

## 19. Determinism

- Observer 确定性冒烟: 同输入双跑 JSON 全等 **PASS**
- 评估级 determinism (G-S3): 不适用 (无评估)

## 20. Provenance

已产生链路: corpus manifest (SHA) → candidate universe (每 case 含 pdf SHA/page/bbox/text) → sampling manifest (seed + 分层) → G-C1 count (case 级 detail + 定义) → regression。全部只读管道, 无 P1–P6 调用签名变化。

## 21. Regression — **PASS**

`tmp/phase3_is14_regression.json` (独立 SHA 验证, 非 runner 自报):

```text
P7.1 drift = 0 | P7.2 drift = 0 | GT SHA unchanged ✅ | Stage 4 sealed unchanged ✅
table_line_detector unchanged ✅ | P4 SpanConfig values present ✅
production files modified = 0 | FROZEN BASELINE = INTACT
```

## 22. Independent Metric Cross-Check

无 runner metrics 需交叉 (§32 不适用)。等价交叉已做: G-C1 计数 (sample) 与 universe 全量扫描独立重算互相印证 (3/54 vs 82/1299 ≈ 6.3%, 几何盲抽样下期望命中 ≈ 54×6.3% ≈ 3.4 — 与实测 3 一致)。

## 23. Failure Analysis (§38 五分法)

| 假设 | 判定 |
|------|------|
| hypothesis failure | **无法判定** — 实验未到达可评估状态; 假设既未证实也未证伪 |
| observer failure |发生过一次 (INCIDENT-1), 已修复并验证; 修复后计数有效 |
| coverage limitation | **主因** — 图形上下文在 AMBIGUOUS 切片中结构性稀疏 (~6.3%): caption 内部 gap ≤8pt 被 P4 确定性合并; LIGO/EHT tick 在 raster 图内无 text span; 变宽数字轴 CV>0.15; 30/54 被 table domain (含冻结 IS-11 对字距标题/双栏版式的过检出) 吸收 |
| corpus limitation | **主因的载体** — "每文档 caption 数" 是 AMBIGUOUS-图形产出的糟糕预测指标 (Phase 2 语料判据缺陷); universe 虽有 82 个 figure-context 案例, 但几何盲抽样按自然比例只能命中 ~3 |
| protocol limitation | 无 — 协议按预注册执行, 事件按 §30 处置 |

## 24. Human Workload Implication

无评审运行 → 无 workload 证据。连 "supports potential future workload reduction" 都不可宣称 (§35 Q9)。Phase 1 的 workload-reduction 论证不受影响 (其证据在 Stage 3/4 语料)。

## 25. Final Gate Evaluation

| Gate | 状态 |
|------|------|
| G-C1 | **FAIL** (3 < 15) |
| G-C2 | PASS |
| G-C3 | PASS |
| G-S1..S4 | 不适用 (无评估) |
| G-S5-equivalent 回归 | PASS |
| G-U1 / G-U2 / G-D1 | 不适用 (无评估) |

## 26. Final Decision

```text
╔══════════════════════════════════════════════════════════════╗
║  PHASE 3 = BLOCKED  (pre-condition G-C1 FAIL → 状态机 STOP)   ║
║  EXPERIMENT 决策枚举: 不适用 (§36 CASE A–D 均未到达)           ║
║  IS-14 = GRAPHIC_TEXT_CONTEXT / HYPOTHESIS ONLY (不变)        ║
║  Phase 2 DESIGN_READY 状态: 保留, 但其 G-C1 pre-condition      ║
║  在本次 corpus 实例化中未达成                                  ║
╚══════════════════════════════════════════════════════════════╝
```

**未来重试的必要条件 (记录, 非授权)**: 需要新的受控设计授权, 且新设计必须解决语料富集与选择偏差的矛盾 — 例如 (a) 寻找图形文本天然落入 8–50pt gap 的文档形态 (med_001 式等宽 tick / 带子标签 caption), 或 (b) 预注册一种不构成 IS-14 信息泄漏的富化方案, 并重新过 G-C1。**任何此类动作都需要新的显式授权; 本阶段不做。**

## 27. Limitations

1. 实验未执行 — 所有结论仅关于 **本次 corpus 实例化 + 本次冻结抽样**, 不构成对 IS-14 假设的任何评估结论。
2. IS-11-as-run 过检出发现 (字距标题/双栏 → 假 table domain) 是冻结行为, 未验证其对评估的影响 (无评估)。
3. G-C1 计数定义中 caption-block membership 与 OBS-B 共享几何阈值 (14pt) — 已预注册, 未做敏感性分析 (禁止调参)。
4. Observer 曾含一个已修复的实现 bug (INCIDENT-1); 当前版本通过 ground-truth 校验 + 负对照, 但未做单元级穷举测试。
5. GraphCast p27 类变宽数字轴 (CV≈0.195) 不满足冻结 tick-run 定义 — 这是**定义的真实行为**, 记录为潜在覆盖率限制, 不构成修改理由。

---

## Final Safety Statement (§43, verbatim)

```text
PHASE 3 = BLOCKED
IS-14 = GRAPHIC_TEXT_CONTEXT
IS-14 EXPERIMENT-ONLY OBSERVER = IMPLEMENTED (gate instrument; validated; NOT evaluated)

PRODUCTION = FALSE
P7.3 = NOT AUTHORIZED
CAPABILITY REGISTRATION = NOT AUTHORIZED
RUNTIME INTEGRATION = NOT AUTHORIZED

FROZEN BASELINE = INTACT
NO GT MODIFICATION
NO POST-HOC TUNING
NO COMPLEX HUMAN ANNOTATION

STOP = TRUE
WAIT FOR EXPLICIT AUTHORIZATION
```

EXPERIMENT 未运行, 故不存在 PASS/FAIL; BLOCKED ≠ IS-14 假设失败。
**执行到最终报告生成后立即 STOP。不得自行进入下一阶段。**
