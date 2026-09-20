# Human-on-the-Boundary Empirical Validation — Round 1

> READ-ONLY 实验设计。不修改任何 frozen/production 文件。
> 本文件是实验准备报告 + 等待真实 Human Review 的 STOP 点。

---

## 0. 实验定位

### 前提

- P4 v2 frozen，不修改
- P4 v3 不实施
- calibration_filter 不进入正式 pipeline
- Evidence Boundary Decision Design = READY
- 三态模型成立：DETERMINISTIC_MERGE / DETERMINISTIC_BLOCK / AMBIGUOUS

### 目标

验证 Human-on-the-Boundary 是否具有真实可行性：

> 机器处理确定性情况，Human 只处理 AMBIGUOUS boundary。

本阶段是 **measurement，不是 optimization**。不追求某个预设 accuracy 数字。

---

## 1. 实验对象

### 1.1 AMBIGUOUS pair 全集

跨 8 文档审计，共 43 个 AMBIGUOUS pair：

| 文档 | AMBIGUOUS 对数 | SHOULD_MERGE | SHOULD_NOT_MERGE |
|---|---|---|---|
| arxiv_toc | 22 | 22 | 0 |
| arxiv_2307 | 17 | 4 | 13 |
| arxiv_bio_body | 4 | 4 | 0 |
| RA101 | 0 | 0 | 0 |
| RM501-P4 | 0 | 0 | 0 |
| E804 | 0 | 0 | 0 |
| C216 | 0 | 0 | 0 |
| DC201 | 0 | 0 | 0 |
| **Total** | **43** | **30** | **13** |

设备手册 AMBIGUOUS = 0 → 不需要 human review。

### 1.2 AMBIGUOUS 分类

| Ambiguity Mode | 对数 | 文档 | 说明 |
|---|---|---|---|
| TOC_SECTION_NUMBER_TITLE | 27 | arxiv_toc, arxiv_2307, arxiv_bio_body | 序号+标题（"1"→"Introduction"） |
| APPENDIX_LETTER_TITLE | 2 | arxiv_toc | 附录字母+标题（"B.1"→"Two-point function"） |
| BODY_TEXT_CONTINUATION | 1 | arxiv_bio_body | 正文同行续接 |
| FORMULA_FRAGMENT_WIDE | 13 | arxiv_2307 | 公式碎片（w_b 15-21pt 灰色区间） |

### 1.3 每个 case 保留的 metadata

| 字段 | 说明 | 是否展示给 Reviewer? |
|---|---|---|
| case_id | AMB-001 ~ AMB-043 | ✅ |
| doc_id | 文档标识 | ✅ |
| page | 页码 | ✅ |
| text_a | 片段 A 文本 | ✅ |
| text_b | 片段 B 文本 | ✅ |
| image_url | 页面图片（红框=A，蓝框=B） | ✅ |
| bbox_a / bbox_b | 观测坐标 | ❌ 不展示 |
| w_a / w_b / h_gap / dy | 几何特征 | ❌ 不展示 |
| same_style / line_obs_count | 上下文特征 | ❌ 不展示 |
| ambiguity_mode | 分类标签 | ❌ 不展示 |
| ground_truth_label | 预期答案 | ❌ 不展示（反 confirmation bias） |

---

## 2. Round 1 选样

### 2.1 选样策略

从 43 个 case 中选取 **20 个**，覆盖：
- 3 个文档（arxiv_toc / arxiv_2307 / arxiv_bio_body）
- 4 种 ambiguity mode
- 已知 adversarial pattern（公式碎片 vs 短标题）
- 不同 gap / line_obs / w_b 区间

### 2.2 选样覆盖

| 维度 | 分布 |
|---|---|
| 文档 | arxiv_toc=7, arxiv_2307=10, arxiv_bio_body=3 |
| Mode | TOC_SECTION_NUMBER_TITLE=12, FORMULA_FRAGMENT_WIDE=6, APPENDIX_LETTER_TITLE=1, BODY_TEXT_CONTINUATION=1 |
| Ground truth | SHOULD_MERGE=14, SHOULD_NOT_MERGE=6 |
| Gap 范围 | 8.3-26.9pt |
| w_b 范围 | 15.4-295.0pt |
| line_obs 范围 | 2-15 |

### 2.3 Adversarial case 设计

| Adversarial pair | 为什么是 adversarial |
|---|---|
| AMB-018 ("6.1"→"SMEFT") vs AMB-040 ("( )"→"cos(") | 两者 w_b 接近（38 vs 15），gap 接近（11 vs 21），但 ground truth 相反 |
| AMB-027 ("1."→"Introduction") vs AMB-029 (formula→formula) | 两者 gap 都 >20pt，但 ground truth 相反 |
| AMB-026 (body text continuation) | 独特模式：两个长文本片段同行，不涉及序号 |

### 2.4 完整 20 case 列表

| # | Case ID | 文档 | 页 | gap | w_b | line | Mode | GT |
|---|---|---|---|---|---|---|---|---|
| 1 | AMB-001 | arxiv_toc | p2 | 10.0 | 68.6 | 3 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 2 | AMB-005 | arxiv_toc | p2 | 12.4 | 62.2 | 3 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 3 | AMB-012 | arxiv_toc | p2 | 11.1 | 82.4 | 9 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 4 | AMB-014 | arxiv_toc | p2 | 10.0 | 76.0 | 8 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 5 | AMB-017 | arxiv_toc | p2 | 10.0 | 295.0 | 3 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 6 | AMB-018 | arxiv_toc | p2 | 11.1 | 38.2 | 3 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 7 | AMB-021 | arxiv_toc | p2 | 8.8 | 90.7 | 3 | APPENDIX_LETTER_TITLE | MERGE |
| 8 | AMB-023 | arxiv_bio_body | p3 | 13.5 | 74.0 | 2 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 9 | AMB-025 | arxiv_bio_body | p5 | 12.5 | 101.6 | 2 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 10 | AMB-026 | arxiv_bio_body | p5 | 9.9 | 95.4 | 8 | BODY_TEXT_CONTINUATION | MERGE |
| 11 | AMB-027 | arxiv_2307 | p1 | 22.0 | 49.5 | 3 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 12 | AMB-028 | arxiv_2307 | p2 | 22.1 | 172.8 | 3 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 13 | AMB-029 | arxiv_2307 | p2 | 26.9 | 19.7 | 14 | FORMULA_FRAGMENT_WIDE | NO_MERGE |
| 14 | AMB-030 | arxiv_2307 | p2 | 8.3 | 15.7 | 15 | FORMULA_FRAGMENT_WIDE | NO_MERGE |
| 15 | AMB-032 | arxiv_2307 | p2 | 13.8 | 15.8 | 12 | FORMULA_FRAGMENT_WIDE | NO_MERGE |
| 16 | AMB-034 | arxiv_2307 | p2 | 22.1 | 221.2 | 3 | TOC_SECTION_NUMBER_TITLE | MERGE |
| 17 | AMB-037 | arxiv_2307 | p2 | 24.3 | 18.1 | 15 | FORMULA_FRAGMENT_WIDE | NO_MERGE |
| 18 | AMB-040 | arxiv_2307 | p2 | 21.2 | 15.4 | 8 | FORMULA_FRAGMENT_WIDE | NO_MERGE |
| 19 | AMB-041 | arxiv_2307 | p3 | 9.0 | 20.6 | 8 | FORMULA_FRAGMENT_WIDE | NO_MERGE |
| 20 | AMB-043 | arxiv_2307 | p3 | 22.0 | 219.2 | 3 | TOC_SECTION_NUMBER_TITLE | MERGE |

---

## 3. Human Review Interface

### 3.1 设计原则

| 原则 | 实现 |
|---|---|
| **不显示系统推荐答案** | UI 中无"系统建议"区域 |
| **不显示几何特征** | 不显示 gap / w_b / line_obs / same_style |
| **不显示 ambiguity mode** | 不显示分类标签 |
| **不显示 ground truth** | 不显示预期答案 |
| **反 confirmation bias** | 只显示客观信息：页面图片 + 两个文本片段 + 中性系统状态 |
| **三选一** | MERGE / KEEP_SEPARATE / CANNOT_DETERMINE |
| **允许 CANNOT_DETERMINE** | 不强迫选择 MERGE 或 KEEP_SEPARATE |

### 3.2 Reviewer 看到的内容

1. **原始 PDF 页面图片**（2x 渲染，红框=片段A，蓝框=片段B）
2. **片段 A 文本**（红框对应）
3. **片段 B 文本**（蓝框对应）
4. **文档标识 + 页码**
5. **中性系统状态**：

   > "系统无法仅根据当前证据确定这两个文本片段是否属于同一个文本单元。"

6. **三个决定按钮**：
   - ✓ 属于同一文本单元 (MERGE)
   - ✕ 不属于同一文本单元 (KEEP_SEPARATE)
   - ? 无法确定 (CANNOT_DETERMINE)
7. **可选备注**（textarea，不强制）

### 3.3 Reviewer 看不到的内容

- ❌ gap 值
- ❌ w_a / w_b 值
- ❌ Δy 值
- ❌ line_obs_count
- ❌ same_style
- ❌ ambiguity_mode
- ❌ ground_truth_label
- ❌ 系统推荐答案
- ❌ AI-assisted calibration 结果
- ❌ 任何模型 confidence score

### 3.4 技术实现

| 组件 | 路径 | 说明 |
|---|---|---|
| 实验服务器 | `tmp/perception/p7/boundary_review/boundary_review_server.py` | 独立于 frozen P7.2 review_server.py，端口 5073 |
| Review UI | `tmp/perception/p7/boundary_review/boundary_review.html` | 独立于 frozen P7.2 index.html |
| Case 数据 | `tmp/perception/p7/boundary_review/round1_cases.json` | 20 个 case，含完整 metadata（但 UI 只展示 public 字段） |
| 页面图片 | `tmp/perception/p7/boundary_review/page_images/` | 20 张 PNG，红框=A，蓝框=B |
| 结果存储 | `tmp/perception/p7/boundary_review/round1_results.json` | 记录每次 decision |

---

## 4. Metrics 记录 Schema

### 4.1 每条 Review Record

```json
{
  "record_id": "uuid",
  "reviewer_id": "reviewer_1",
  "case_id": "AMB-001",
  "decision": "MERGE",           // MERGE / KEEP_SEPARATE / CANNOT_DETERMINE
  "comment": "",                  // optional
  "start_time_ms": 1234567890,   // case 加载时间
  "decision_time_ms": 1234567950, // decision 提交时间
  "duration_ms": 60,              // decision_time - start_time
  "timestamp": "2026-09-08T22:52:04"
}
```

### 4.2 核心 Metrics（实验完成后计算）

| # | Metric | 计算方法 |
|---|---|---|
| 1 | Human Review Rate | 完成 case 数 / 总 case 数 |
| 2 | Median Decision Time | median(duration_ms) |
| 3 | P75 Decision Time | percentile(duration_ms, 75) |
| 4 | P95 Decision Time | percentile(duration_ms, 95) |
| 5 | Decision Distribution | count(MERGE) / count(KEEP_SEPARATE) / count(CANNOT_DETERMINE) |
| 6 | Reviewer Disagreement | (如有第二 reviewer) 不同 decision 的 case 比例 |
| 7 | Decision Reversal | (如有第二 reviewer) 第二 reviewer 推翻第一 reviewer 的 case 数 |
| 8 | Evidence Formation Success | ACCEPT(MERGE) → ValidatedEvidence 成功生成数 |
| 9 | Provenance Completeness | 每条 record 的 provenance chain 完整性 |
| 10 | Frozen Baseline Integrity | 实验后所有 frozen 文件 hash 未变 |

---

## 5. Ground Truth 规则

### 5.1 Ground Truth 来源

**Ground Truth = Human final decision。**

- AI-assisted calibration 结果（`ground_truth_label`）只用于实验分析，**不作为 Ground Truth**
- `ground_truth_label` 不展示给 reviewer
- 实验结束后，将 human decision 与 `ground_truth_label` 对比，计算 agreement

### 5.2 第二 Reviewer（如有）

- 独立完成全部 20 case
- 不得看到第一 reviewer 的结果
- 计算 agreement / disagreement / reversal
- 如果没有第二 reviewer，明确记录：

  > "Single-reviewer empirical validation; inter-reviewer agreement not measured."

### 5.3 CANNOT_DETERMINE 处理

- 如果 reviewer 选择 CANNOT_DETERMINE，**保留该决定**
- 不强迫选择 MERGE 或 KEEP_SEPARATE
- CANNOT_DETERMINE 不产生 Evidence
- 如果出现 CANNOT_DETERMINE，说明该 case 即使对人类也有歧义

---

## 6. Evidence Boundary Principle

### 6.1 三种 certainty 的区分

| Certainty 类型 | 来源 | 用途 |
|---|---|---|
| Machine certainty | P4 geometry/layout | DETERMINISTIC_MERGE / DETERMINISTIC_BLOCK |
| Human certainty | Human decision | AMBIGUOUS → MERGE / KEEP_SEPARATE / CANNOT_DETERMINE |
| Evidence admissibility | ValidatedEvidence (from ACCEPT only) | 下游使用 |

### 6.2 Human MERGE ≠ 自动 Capability

```
Human decision: MERGE
    ↓
ValidationRecord (immutable)
    ↓
ValidatedEvidence (derived, ACCEPT only)
    ↓
Capability Registration (Human Controlled, NOT automatic)
```

- Human MERGE 只产生 ValidationRecord → ValidatedEvidence
- Capability Registration 仍然需要 Human Controlled 批准
- Runtime Authority = ZERO

---

## 7. Acceptance Criteria

### Gate 判定（实验完成后）

| Gate | 条件 |
|---|---|
| **A. EMPIRICALLY_SUPPORTED** | Human 可以操作 + ambiguity 可被有效处理 + decision provenance 完整 + review cost 可测量 + frozen baseline 完整 |
| **B. EMPIRICALLY_INCONCLUSIVE** | Human 可以操作但样本不足 / reviewer disagreement 高 / ambiguity 类型仍不清楚 / review cost 无法稳定估计 |
| **C. HUMAN-BOUNDARY-NOT-VIABLE** | Human 也无法稳定处理 / 或 review cost 没有实际优势 / 或 provenance 无法保证 |

**不为了推进项目而选择 A。**

---

## 8. 实验准备状态

### 8.1 准备完成清单

| # | 项目 | 状态 |
|---|---|---|
| 1 | 43 个 AMBIGUOUS pair 提取 | ✅ 完成（`ambiguous_cases_all.json`） |
| 2 | 20 个 case 选样（覆盖 3 文档 + 4 mode + adversarial） | ✅ 完成（`round1_cases.json`） |
| 3 | 20 张页面图片生成（红框=A，蓝框=B） | ✅ 完成（`page_images/`） |
| 4 | 实验性 Review Server | ✅ 完成（端口 5073，独立于 frozen P7.2） |
| 5 | 实验性 Review UI（无系统推荐，三选一，反 confirmation bias） | ✅ 完成（`boundary_review.html`） |
| 6 | Metrics 记录 schema | ✅ 完成（reviewer_id / time / duration / decision / comment） |
| 7 | 结果存储 | ✅ 完成（`round1_results.json`，自动保存） |
| 8 | 服务器运行中 | ✅ 运行中（http://127.0.0.1:5073） |
| 9 | Frozen baseline 完整性 | ✅ 未修改任何 frozen 文件 |

### 8.2 如何开始真实 Human Review

1. **打开浏览器**访问 `http://127.0.0.1:5073`
2. 输入 Reviewer ID（默认 `reviewer_1`，可修改）
3. 依次查看 20 个 case：
   - 左侧显示 PDF 页面图片（红框=片段A，蓝框=片段B）
   - 右侧显示片段文本 + 中性系统状态 + 三个决定按钮
4. 对每个 case 做出判断：
   - ✓ 属于同一文本单元 (MERGE)
   - ✕ 不属于同一文本单元 (KEEP_SEPARATE)
   - ? 无法确定 (CANNOT_DETERMINE)
5. 可选填写备注
6. 可以前后翻页修改之前的判断（更改 decision 会确认）
7. 完成全部 20 个 case 后显示完成画面
8. 结果自动保存到 `round1_results.json`

### 8.3 如果需要第二 Reviewer

- 用不同的 Reviewer ID（如 `reviewer_2`）访问同一 URL
- 系统会为每个 reviewer 独立记录 start_time / decision_time
- 第二 reviewer 独立完成，看不到第一 reviewer 的结果
- 完成后对比两个 reviewer 的 decision，计算 agreement

### 8.4 实验完成后

- 读取 `round1_results.json`
- 计算 10 个核心 Metrics
- 将 human decision 与 `ground_truth_label` 对比
- 计算 agreement rate
- 填写 Gate 判定（A / B / C）
- 生成最终实验报告

---

## 9. 禁止项确认

| # | 禁止 | 状态 |
|---|---|---|
| 1 | 不修改 P1-P6 | ✅ UNCHANGED |
| 2 | 不修改 P4 v2 | ✅ UNCHANGED |
| 3 | 不实施 P4 v3 | ✅ NOT AUTHORIZED |
| 4 | 不修改 P7.1 | ✅ UNCHANGED |
| 5 | 不修改 Frozen 730 | ✅ UNCHANGED |
| 6 | 不修改 CandidateSpan / Manifest | ✅ UNCHANGED |
| 7 | 不修改 calibration_filter | ✅ UNCHANGED |
| 8 | 不修改 Evidence schema | ✅ UNCHANGED |
| 9 | 不修改 P7.2 validation semantics | ✅ UNCHANGED |
| 10 | 不进入 P7.3 | ✅ NOT AUTHORIZED |
| 11 | 不用 AI 替代 Human | ✅ 等待真实 Human |
| 12 | 不自动生成 Human decision | ✅ 等待真实 Human |
| 13 | 不显示系统推荐 | ✅ UI 无推荐 |
| 14 | 不显示几何特征 | ✅ UI 无 gap/w_b/line_obs |
| 15 | 不显示 ground truth | ✅ UI 无答案 |

---

## 10. 文件清单

### 新增文件（全部在 `tmp/perception/p7/boundary_review/`）

| 文件 | 说明 | 大小 |
|---|---|---|
| `extract_ambiguous.py` | 提取 43 个 AMBIGUOUS pair 的脚本 | — |
| `select_round1.py` | 选样 20 case + 生成图片的脚本 | — |
| `ambiguous_cases_all.json` | 全部 43 个 case 的完整数据 | — |
| `round1_cases.json` | 20 个选中 case 的数据 | — |
| `boundary_review_server.py` | 实验服务器（端口 5073） | — |
| `boundary_review.html` | 实验 Review UI | — |
| `page_images/` | 20 张页面图片（PNG） | — |
| `round1_results.json` | 实验结果（待 Human Review 后填充） | 待生成 |

### 未修改的文件

- P1-P6: UNCHANGED
- P4 v2 (span_rules.py, span_observation.py): UNCHANGED
- P7.1 (6 frozen files): UNCHANGED
- P7.2 (8 frozen files): UNCHANGED
- Frozen 730: UNCHANGED (a10b368e)
- calibration_filter.py: UNCHANGED

---

## STOP

实验准备完成。等待真实 Human Review。

**不自行模拟 Human。不用 AI 替代 Human。不自动生成 Human decision。**

Review URL: **http://127.0.0.1:5073**

Reviewer 需要在浏览器中访问该 URL，依次完成 20 个 case 的判断。结果自动保存到 `round1_results.json`。

完成后，将基于真实 Human decision 计算 Metrics 并填写 Gate 判定。

**STOP。等待 Human Review。**
