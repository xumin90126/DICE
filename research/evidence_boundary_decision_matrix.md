# Evidence Boundary Decision Matrix

> READ-ONLY. `evidence_boundary_decision_design.md` 的数据支撑文档。
> 三态 Relation 的 Feature → State → Action → Authority 映射矩阵。

---

## 1. Feature 组合 → Relation State 映射

### 完整决策表

| # | same_y | gap | same_style | line_obs | w_b | → State | → Action | Authority |
|---|---|---|---|---|---|---|---|---|
| 1 | ✅ (Δy≤3) | ≤8pt | ✅ | any | any | DETERMINISTIC_MERGE | auto-merge | P4 (machine) |
| 2 | ✅ | >50pt | any | any | any | DETERMINISTIC_BLOCK | auto-block | P4 (machine) |
| 3 | ✅ | 8-50pt | ❌ | any | any | DETERMINISTIC_BLOCK | auto-block | P4 (machine) |
| 4 | ✅ | 8-50pt | ✅ | >15 | any | DETERMINISTIC_BLOCK | auto-block | P4 (machine) |
| 5 | ✅ | 8-50pt | ✅ | ≤15 | <15pt | DETERMINISTIC_BLOCK | auto-block | P4 (machine) |
| 6 | ✅ | 8-50pt | ✅ | ≤15 | ≥15pt | **AMBIGUOUS** | **human review** | **Human** |
| 7 | ❌ (Δy>3) | any | any | any | any | DETERMINISTIC_BLOCK (different line) | defer to P4 vertical merge | P4 (machine) |

### 决策优先级

```
Step 1: same_y?
  NO → DETERMINISTIC_BLOCK (different line, P4 vertical logic handles)
  YES → Step 2

Step 2: gap ≤ 8?
  YES → DETERMINISTIC_MERGE (P4 v2 frozen behavior)
  NO → Step 3

Step 3: gap > 50?
  YES → DETERMINISTIC_BLOCK_CROSS (cross-column)
  NO → Step 4

Step 4: same_style?
  NO → DETERMINISTIC_BLOCK_FONT (structural boundary)
  YES → Step 5

Step 5: line_obs > 15?
  YES → DETERMINISTIC_BLOCK_DENSE (formula dense line)
  NO → Step 6

Step 6: w_b < 15?
  YES → DETERMINISTIC_BLOCK_NARROW (formula symbol)
  NO → AMBIGUOUS (human review)
```

---

## 2. State × Document × Volume 矩阵

### 跨文档 pair 分布

| 文档 | DETERMINISTIC_MERGE | DETERMINISTIC_BLOCK | AMBIGUOUS | Total |
|---|---|---|---|---|
| arxiv_toc | ~27 | ~47 | 22 | ~96 |
| arxiv_bio_body | ~950 | ~451 | 4 | ~1405 |
| arxiv_2307 | ~368 | ~215 | 17 | ~600 |
| RA101 | ~80 | ~36 | 0 | ~116 |
| RM501-P4 | ~149 | ~63 | 0 | ~212 |
| E804 | ~53 | ~31 | 0 | ~84 |
| C216 | ~72 | ~36 | 0 | ~108 |
| DC201 | ~145 | ~56 | 0 | ~201 |

### AMBIGUOUS × Document × Class

| 文档 | AMBIGUOUS TRUE | AMBIGUOUS FALSE | AMBIGUOUS Total | Human Workload |
|---|---|---|---|---|
| arxiv_toc | 22 | 0 | 22 | 22 reviews |
| arxiv_2307 | 4 | 13 | 17 | 17 reviews |
| arxiv_bio_body | 4 | 0 | 4 | 4 reviews |
| RA101 | 0 | 0 | 0 | **0** |
| RM501-P4 | 0 | 0 | 0 | **0** |
| E804 | 0 | 0 | 0 | **0** |
| C216 | 0 | 0 | 0 | **0** |
| DC201 | 0 | 0 | 0 | **0** |
| **Total** | **30** | **13** | **43** | **43 reviews** |

### Human Review 效率

| 指标 | 值 |
|---|---|
| 总 same-y pair | 762 |
| 自动处理 (DETERMINISTIC) | 719 (94.4%) |
| 人工处理 (AMBIGUOUS) | 43 (5.6%) |
| Human review 中 TRUE merge | 30 (69.8%) |
| Human review 中 FALSE merge | 13 (30.2%) |
| Human review 效率 (确认率) | 69.8% |
| 设备手册 human workload | 0 |

---

## 3. DETERMINISTIC_BLOCK 子类 × Evidence

| Block 子类 | 几何证据 | 对数 | Precision | 跨文档稳定性 |
|---|---|---|---|---|
| CROSS (gap>50) | cross-column gap | 84 | 100% | ✅ 全部 8 文档 |
| FONT (different style) | style_signature 不一致 | 84 | 100% | ✅ 全部 8 文档 |
| DENSE (line_obs>15) | formula dense line | 71 | 100% | ✅ arxiv 文档 |
| NARROW (w_b<15) | formula symbol width | 129 | 100% | ✅ arxiv 文档 |
| **合计** | | **368** | **100%** | |

---

## 4. AMBIGUOUS pair 的不可区分性证明

### Case A (TRUE merge) vs Case B (FALSE merge) 特征对比

| Feature | Case A ("1"→"Introduction") | Case B ("ψ"→"[recall") | 可区分? |
|---|---|---|---|
| Δy | 0.0pt | 0.0pt | ❌ |
| same_style | ✅ | ✅ | ❌ |
| gap | 10.0pt | 11.7pt | ❌ (重叠) |
| line_obs | 3 | 9 | ❌ (都≤15) |
| w_b | 68.6pt | 25.8pt | ⚠️ (都≥15) |
| same_font | ✅ | ✅ | ❌ |
| **文本内容** | "1" = 数字序号 | "ψ" = 公式符号 | ✅ 可区分，但 **禁止文本分析** |

**结论**：在 geometry/layout only 的约束下，Case A 与 Case B **不可区分**。这是 AMBIGUOUS 存在的实证依据。

### 13 个 Irreducible FALSE merge 的完整清单

| # | 文档 | 页 | gap | w_a | w_b | line_obs | text_a | text_b |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv_2307 | p2 | 26.9 | 6.8 | 19.7 | 14 | (symbol) | (symbol) |
| 2 | arxiv_2307 | p2 | 8.3 | 3.8 | 15.7 | 15 | r | S u |
| 3 | arxiv_2307 | p2 | 12.0 | 7.0 | 18.1 | 15 | (symbol) | (symbol) |
| 4 | arxiv_2307 | p2 | 13.8 | 3.5 | 15.8 | 12 | ( | 2 / |
| 5 | arxiv_2307 | p2 | 18.1 | 7.0 | 18.0 | 12 | (symbol) | (symbol) |
| 6 | arxiv_2307 | p2 | 8.3 | 3.8 | 15.7 | 12 | r | S u |
| 7 | arxiv_2307 | p2 | 12.0 | 7.0 | 18.1 | 15 | (symbol) | (symbol) |
| 8 | arxiv_2307 | p2 | 24.3 | 15.6 | 18.1 | 15 | (symbol) | (symbol) |
| 9 | arxiv_2307 | p2 | 13.4 | 18.1 | 17.8 | 15 | (symbol) | (symbol) |
| 10 | arxiv_2307 | p2 | 11.4 | 7.0 | 17.8 | 15 | (symbol) | (symbol) |
| 11 | arxiv_2307 | p2 | 21.2 | 11.0 | 15.4 | 8 | ( ) | cos( |
| 12 | arxiv_2307 | p3 | 9.0 | 5.9 | 20.6 | 8 | (symbol) | (symbol) |
| 13 | arxiv_2307 | p3 | 9.0 | 5.9 | 20.6 | 13 | (symbol) | (symbol) |

**特征**：全部在 arxiv_2307（公式密集文档），全部是公式碎片与公式碎片/正文的过渡，w_b 在 15-21pt 灰色区间。

---

## 5. Authority × State 矩阵

| State | Machine Authority | Human Authority | Runtime Authority | Evidence Authority |
|---|---|---|---|---|
| DETERMINISTIC_MERGE | ✅ (P4 decides) | ❌ (not needed) | ❌ (cannot override) | ❌ (not from machine) |
| DETERMINISTIC_BLOCK | ✅ (P4 decides) | ❌ (not needed) | ❌ (cannot override) | ❌ (not from machine) |
| AMBIGUOUS → ACCEPT | ❌ (cannot auto-accept) | ✅ (Human decides) | ❌ (cannot override) | ✅ (derived from ACCEPT) |
| AMBIGUOUS → REJECT | ❌ (cannot auto-reject) | ✅ (Human decides) | ❌ (cannot override) | ❌ (no evidence) |
| AMBIGUOUS → NEED_REVIEW | ❌ (cannot decide) | ✅ (Human defers) | ❌ (cannot override) | ❌ (no evidence) |

### Authority 不变量

1. **Machine** 只对 DETERMINISTIC 状态有 authority
2. **Human** 只对 AMBIGUOUS 状态有 authority
3. **Runtime** 对任何状态都没有 authority（ZERO）
4. **Evidence** 只从 Human ACCEPT 派生，不从 Machine 或 Runtime 派生

---

## 6. 状态转换图

```
                    ┌─────────────────────┐
                    │   P1 Observation    │
                    │   (immutable)       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   P4 Span Decision  │
                    │   (frozen v2)       │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼────────┐ ┌────▼─────┐ ┌────────▼────────┐
    │ DETERMINISTIC    │ │ gap>8   │ │ DETERMINISTIC   │
    │ _MERGE (gap≤8)  │ │ same_y  │ │ _BLOCK          │
    └────────┬─────────┘ │         │ │ (gap>50/diff    │
             │           │ style)  │ │  font/dense/    │
             │           │         │ │  narrow)        │
             │           └────┬────┘ └────────┬────────┘
             │                │               │
             │         ┌──────▼──────┐        │
             │         │  AMBIGUOUS  │        │
             │         │ (8<gap≤50)  │        │
             │         └──────┬──────┘        │
             │                │               │
             │         ┌──────┼──────┐        │
             │         │      │      │        │
             │    ┌────▼──┐ ┌▼───┐ ┌▼─────┐   │
             │    │ACCEPT │ │REJ │ │NEED_ │   │
             │    │       │ │    │ │REVIEW│   │
             │    └───┬───┘ └┬───┘ └──────┘   │
             │        │      │      │         │
             │        │      │      │         │
    ┌────────▼────────▼┐ ┌──▼──┐ ┌─▼──────┐   │
    │   Validated      │ │ No  │ │ No     │   │
    │   Evidence       │ │Evid │ │Evid    │   │
    │   (derived)      │ │     │ │(defer) │   │
    └──────────────────┘ └─────┘ └────────┘   │
                                               │
                                    ┌──────────▼──────────┐
                                    │  No Evidence        │
                                    │  (auto-blocked)     │
                                    └─────────────────────┘
```

### 状态不可逆性

| 转换 | 允许? | 理由 |
|---|---|---|
| DETERMINISTIC_MERGE → AMBIGUOUS | ❌ | P4 frozen，merge 不可撤销 |
| DETERMINISTIC_BLOCK → AMBIGUOUS | ❌ | Block 基于 hard evidence |
| AMBIGUOUS → DETERMINISTIC_MERGE | ❌ | 需要 Human ACCEPT → Evidence，不是 P4 修改 |
| AMBIGUOUS → DETERMINISTIC_BLOCK | ❌ | 需要 Human REJECT，不是自动 block |
| Human ACCEPT → REJECT | ❌ | ValidationRecord immutable |
| Human REJECT → ACCEPT | ❌ | ValidationRecord immutable |
| Evidence → 删除 | ❌ | ValidatedEvidence immutable (derived from immutable Record) |

---

## 7. Capability Registration 矩阵

| 文档类型 | AMBIGUOUS 存在? | 已 Human Validated? | Capability Status |
|---|---|---|---|
| arxiv TOC 页 | ✅ (22 pair) | Round 1 部分 (3/10 ACCEPT) | Partial capability |
| arxiv 正文页（含公式） | ✅ (17 pair) | ❌ 未验证 | No capability (needs human) |
| arxiv 正文页（无公式） | ✅ (4 pair) | ❌ 未验证 | No capability (needs human) |
| 设备手册 | ❌ (0 pair) | N/A (no AMBIGUOUS) | **Full capability** (machine-only) |

### Capability Growth 规则

1. 设备手册：全部 DETERMINISTIC → machine-only processing → full capability
2. arxiv 文档：存在 AMBIGUOUS → needs human validation → capability grows per ACCEPT
3. 新文档类型：先运行 P4/P7.1 → 检测 AMBIGUOUS → 如有，需 human validation → 如无，machine-only

**Runtime 不能自动授予 capability。** Capability registration 是 human-controlled——只有 Human ACCEPT 的 Evidence 才扩展 capability。
