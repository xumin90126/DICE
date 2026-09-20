# Phase 3 — Incident Log

## INCIDENT-1: OBS-C implementation error invalidates first G-C1 count

| 字段 | 值 |
|------|-----|
| 阶段 | Phase 3 — G-C1 corpus sufficiency count |
| 分类 (§29) | **IMPLEMENTATION_ERROR / OBSERVER_OUTPUT_ERROR** (非 corpus 限制, 非 IS-14 假设失败) |
| 发现方式 | §30 事件处理: G-C1 首次计数 = 1 figure-context → 触发 "checker bug vs corpus reality" 区分流程 |
| 处理 | STOP → 独立验证 → 定位 bug → 修复 → 验证 → 重新计数 |

### 时间线

1. **首跑**: `phase3_is14_gc1_count.py` 用 observer 对冻结样本 (n=54) 计数 → figure_context=1, tick_run=0。
2. **触疑**: universe 有 99 个 both-numeric pair 而 tick-run=0 → 与 Phase 2 探测证据 (med_001 p19 存在 ≥5 成员等差 tick-run) 矛盾 → 怀疑实现错误而非 corpus 属性。
3. **独立验证**: 用 med_001 p19 (Phase 2 已人工验证的真实 tick 数据: 0.70/0.75/0.80/0.85/0.90 等差) 作为 ground-truth 校验集 → OBS-C 对 '0.70' 返回 **False** → 确认实现错误。
4. **根因**: `_find_run` 的贪心双侧扩张在窗口仅含 1 个 gap 时停滞 (spacing CV 对 n<2 值返回 None → while 条件 `is not None` 失败 → 不扩张) → run 永远无法从 1 member 长到 ≥3。
5. **修复**: 贪心扩张改为**穷举极大窗口枚举** (所有包含 fragment 的连续窗口中取满足 CV ≤ 0.15 的最长者)。**阈值/定义零改动** (OBS_C_MIN_RUN=3, CV ≤ 0.15, 对齐 ±2pt, 字号 ≤0.5pt — 全部与 Phase 2 §7 冻结定义一致)。
6. **修复验证**:
   - med_001 p19 真实 ticks: '0.70'/'0.75'/'17.9'/'18.5'/'1.35'/'0.85' 全部 → run=5 或 10, tick_run=True ✅
   - 负对照 (med_001 p2 正文数字): 多数 tick_run=False ✅
7. **无效化与重跑**: 首次 G-C1 计数**判定无效** (IMPLEMENTATION_ERROR), 文件被修正后重跑覆盖; 重跑结果 figure_context=3, tick_run=2。

### 治理说明

- 修复发生在 **GT 收集之前** (GT 尚未生成), 不存在 "看了结果调参" — 修复对象是代码 bug, 冻结定义未动。
- 修复使 observer 与 Phase 2 冻结定义**一致** (修复前是不一致)。
- 首跑计数从未用于任何 gate 之外的决策; 无案例因首跑被增删。

---

## FINDING-2: IS-11-as-run 在新版式上的行为 (非事件, 记录性发现)

冻结 IS-11 detector 在 Phase 3 新语料上把 54 个样本中的 **30 个**判为 table domain, 其中包含**非表格**案例:

- `IS14-AMB-018/019` (PH3-ASTRO-001 p6): 期刊页眉字距拉开的 "P H Y S I C A L / R E V I E W" 被检测为 table 行 (cells (0,0)/(0,1))
- `IS14-AMB-089` (PH3-EARTH-001 p10): 作者单位文字被判定 in_table

含义: line-based detector 对 letter-spaced 标题/双栏版式存在**过检出** (Stage 4 语料全部单栏, 未暴露此行为)。此为**冻结 IS-11 的既有行为**, 本阶段不可修改; 记录为 frozen-baseline 行为发现, 供未来 Perception 轨道参考。

---

## FINDING-3: 图形上下文在 AMBIGUOUS 切片中的结构性稀疏 (G-C1 FAIL 根因)

| 证据 | 数值 |
|------|------|
| Universe (1299 AMBIGUOUS) 中 figure-context 案例 (fixed observer) | **82** (caption-block 3 + OBS-A 3 + tick-run 76, 有重叠) ≈ 6.3% |
| 冻结样本 (n=54, 几何盲抽样) 中 figure-context | **3** (caption 1 + tick 2) < 15 要求 |
| 样本页中含 caption-label 的页 | 4/33 |
| 样本中 table domain (IS-11 as-run) | 30/54 (55.6%) |

结构原因:
1. **caption 内部 fragment 间距 ≤ 8pt** → P4 DETERMINISTIC_MERGE → 根本不进 AMBIGUOUS 切片;
2. **LIGO/EHT 图为 raster** (80/37 个 image block) → tick 文字在图像内, 无 text span;
3. **变宽数字轴标签** (如 GraphCast '100/200/300') 的中心距 CV > 0.15 → 不满足冻结 tick-run 定义;
4. **table domain 优先权** 吸收了大量图形页 pair (含过检出)。

结论: "每文档 caption 数" 是**糟糕的** AMBIGUOUS-切片图形产出预测指标 (Phase 2 语料选择判据缺陷)。未来若重试, 需要能产出 graphic-context AMBIGUOUS 案例的语料 (如 med_001 式等宽 tick、带子图标签的 caption), 或预注册的、非选择偏差的富集方案 — 属于**新的设计授权**, 非本阶段可做。
