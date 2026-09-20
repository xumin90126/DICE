# Boundary Intelligence / Information Source Gap Analysis

> READ-ONLY RESEARCH / DESIGN。不修改任何 frozen/production/source 文件。不实施。不进入 P7.3。

---

## Executive Summary

```
Research Question:
  When Human resolves a Boundary, what additional Information Sources does Human use?
  Can DICE reduce Human-owned Boundary by adding new Information Sources?

Key Finding:
  ALL information sources Human used in Round 1 are potentially machine-observable (Category B).
  NONE are Category A (existing-but-uncombined).
  Only AMB-026 has a Category C component (semantic interpretation of raw signals).

  This means: the Information Gap is not "P4 has the data but doesn't combine it."
  The gap is "P4's geometry-only contract excludes textual and visual information
  that are individually machine-observable but collectively require interpretation."

Information Source Expansion Candidates:
  1. Textual Structure Feature (numbering pattern, symbol detection, punctuation) — Category B
  2. Visual/Page Context Feature (formula region, TOC region) — Category B
  3. Sentence Boundary Interpretation — Category C (likely permanent Human-owned)

Human-on-the-Boundary:
  = Boundary Evidence Source (NOT human fallback worker)

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
Frozen = INTACT
```

---

## 一、Current Evidence Boundary

### 1.1 What P4 Currently Has (Layer 1: Geometric)

| Information Source | P4 has? | Used by Human? | Evidence |
|---|---|---|---|
| gap (horizontal distance) | ✅ | ❌ Not directly | Human doesn't look at gap value; uses text content instead |
| Δy (vertical alignment) | ✅ | ❌ Not directly | Human sees visual alignment but doesn't measure Δy |
| w_a / w_b (span width) | ✅ | ❌ Not directly | Human doesn't measure width; reads text content |
| font_family / font_size | ✅ | ❌ Not directly | Human sees typography but doesn't compare font signatures |
| style_signature | ✅ | ❌ Not directly | Human doesn't compute style signatures |
| line_obs_count | ✅ | ❌ Not directly | Human perceives line density but doesn't count observations |
| reading_order | ✅ | ❌ Not directly | Human reads left-to-right naturally |

**关键发现**：P4 的全部几何特征**都不是 Human 直接使用的决策依据**。Human 的决策基于文本内容和页面视觉上下文，几何特征只是 Human 视觉感知的一部分，不是显式判断依据。

### 1.2 What P4's Contract Excludes

P4 的 geometry-only contract 排除了以下信息：

| Excluded Information | Why excluded | Human used? |
|---|---|---|
| Text content (characters, words) | P4 contract: geometry/layout only | ✅ YES (all 20 cases) |
| Text pattern (numbering, symbols) | P4 contract: no text analysis | ✅ YES (19/20 cases) |
| Punctuation | P4 contract: no text analysis | ✅ YES (5 cases) |
| Capitalization | P4 contract: no text analysis | ✅ YES (15 cases) |
| Page-level visual context | P4 is per-pair, not per-page | ✅ YES (all 20 cases) |
| Sentence structure | Not in any DICE layer | ✅ YES (AMB-026) |

### 1.3 The Core Gap

```
P4's information space = {gap, Δy, width, font, style, line_obs, reading_order}

Human's information space = P4's space + {text_content, text_pattern,
    punctuation, capitalization, page_visual_context, sentence_structure}

The gap = {text_content, text_pattern, punctuation, capitalization,
           page_visual_context, sentence_structure}
```

**这个 gap 不是"P4 有数据但没组合"（Category A），而是"P4 的契约排除了整类信息"（Category B/C）。**

---

## 二、Human Information Source Taxonomy

### 2.1 从 Round 1 实际 Human reasoning 归纳的 Information Sources

基于 20 个 case 的逐个信息源归因分析：

| # | Information Source | 类别 | Human 使用次数 | P4 拥有? | Machine-observable? | 说明 |
|---|---|---|---|---|---|---|
| IS-01 | TEXT_NUMBER_PATTERN | Textual | 12 | ❌ | ✅ YES (regex) | "1", "2.1", "B.1" = 编号模式 |
| IS-02 | TEXT_READABLE_TITLE | Textual | 14 | ❌ | ✅ YES (word detection) | "Introduction", "Leptonic processes" = 可读标题词 |
| IS-03 | TEXT_SYMBOL_PATTERN | Textual | 7+6 | ❌ | ✅ YES (character class) | "ψ", "r", "(", "cos(" = 数学符号 |
| IS-04 | TEXT_PUNCTUATION | Textual | 5 | ❌ | ✅ YES (character check) | "." 句号 = 句子边界信号 |
| IS-05 | TEXT_CAPITAL_START | Textual | 15 | ❌ | ✅ YES (case check) | "Its" 大写 = 新句开始信号 |
| IS-06 | TEXT_APPENDIX_LETTER | Textual | 1 | ❌ | ✅ YES (regex) | "B.1" = 附录编号模式 |
| IS-07 | VISUAL_TOC_CONTEXT | Visual | 7 | ❌ | ✅ YES (P6 region) | TOC 页面布局模式 |
| IS-08 | VISUAL_FORMULA_CONTEXT | Visual | 10 | ❌ | ✅ YES (P6 region) | 公式页面布局模式 |
| IS-09 | VISUAL_BODY_CONTEXT | Visual | 3 | ❌ | ✅ YES (P6 region) | 正文页面布局模式 |
| IS-10 | SENTENCE_BOUNDARY_INTERPRETATION | Semantic | 1 | ❌ | ⚠️ Partial | "." + 大写 → 不同句子（需要解释） |

### 2.2 Taxonomy 分类原则

| 类别 | 定义 | Round 1 中的 Information Sources |
|---|---|---|
| **A. EXISTING INFORMATION** | 当前已存在于机器系统，只是尚未组合/建模 | ❌ **NONE** — P4 的几何特征不是 Human 的决策依据 |
| **B. NEW MACHINE-OBSERVABLE** | Human 使用了额外信息，但这种信息原则上可以被机器可靠观察 | IS-01~IS-09（全部 textual + visual sources） |
| **C. INHERENTLY SEMANTIC** | 即使增加机器 observable features，仍然需要语义解释 | IS-10（sentence boundary interpretation） |

### 2.3 关键发现

**Round 1 中没有 Category A 的 Information Source。**

这意味着：Information Gap 不是"P4 有数据但没组合"的问题。P4 v3 Design 已经尝试组合所有几何特征（gap + dy + font + w_b + line_obs），但仍有 irreducible FP。问题在于 P4 的信息空间**结构性缺失**——它排除了文本内容和视觉上下文。

**几乎所有 Human 使用的信息源都是 Category B（machine-observable）。**

这意味着：如果 DICE 增加新的 Information Source（textual structure feature + visual context feature），理论上可以缩小 Information Gap。但"理论上可观察" ≠ "可以可靠组合为 boundary decision"——需要 Generalization Gate 验证。

**只有 1 个 Information Source 是 Category C（inherently semantic）。**

IS-10（sentence boundary interpretation）是 AMB-026 的核心。虽然"."和大写是 machine-observable（B），但解释". + 大写 = 不同句子 = 不同 text unit"需要语义判断（C）。

---

## 三、Boundary × Information Source Matrix

### 3.1 完整矩阵

| Case | Mode | Human Decision | Human Info Sources | P4 Has? | Gap Category | Missing Info | Potential Source |
|---|---|---|---|---|---|---|---|
| AMB-001 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-05 + IS-07 | gap/dy/font only | B | numbering + readable word + TOC context | textual structure + P6 region |
| AMB-005 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-05 + IS-07 | gap/dy/font only | B | same as AMB-001 | same |
| AMB-012 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-05 + IS-07 | gap/dy/font only | B | same | same |
| AMB-014 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-05 + IS-07 | gap/dy/font only | B | same | same |
| AMB-017 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-05 + IS-07 | gap/dy/font only | B | same | same |
| AMB-018 ★ | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-05 + IS-07 | gap/dy/font only | B | same | same |
| AMB-021 | APPENDIX_LETTER | MERGE | IS-06 + IS-02 + IS-05 + IS-07 | gap/dy/font only | B | appendix letter + readable word | same |
| AMB-023 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-05 + IS-09 | gap/dy/font only | B | same (body page context) | same |
| AMB-025 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-05 + IS-09 | gap/dy/font only | B | same | same |
| AMB-026 ★ | BODY_CONT | SEPARATE | IS-02 + IS-04 + IS-05 + IS-09 | gap/dy/font only | **C** | sentence boundary interpretation | text semantics (requires interpretation) |
| AMB-027 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-04 + IS-05 + IS-08 | gap/dy/font only | B | same (formula page context) | same |
| AMB-028 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-04 + IS-05 + IS-08 | gap/dy/font only | B | same | same |
| AMB-029 | FORMULA_WIDE | SEPARATE | IS-03 + IS-08 | gap/dy/font only | B | symbol detection + formula context | char class + P6 region |
| AMB-030 | FORMULA_WIDE | SEPARATE | IS-03 + IS-08 | gap/dy/font only | B | same | same |
| AMB-032 | FORMULA_WIDE | SEPARATE | IS-03 + IS-08 | gap/dy/font only | B | same | same |
| AMB-034 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-04 + IS-05 + IS-08 | gap/dy/font only | B | same | same |
| AMB-037 | FORMULA_WIDE | SEPARATE | IS-03 + IS-08 | gap/dy/font only | B | same | same |
| AMB-040 ★ | FORMULA_WIDE | SEPARATE | IS-03 + IS-08 | gap/dy/font only | B | same | same |
| AMB-041 | FORMULA_WIDE | SEPARATE | IS-03 + IS-08 | gap/dy/font only | B | same | same |
| AMB-043 | TOC_NUM_TITLE | MERGE | IS-01 + IS-02 + IS-04 + IS-05 + IS-08 | gap/dy/font only | B | same | same |

### 3.2 按 Mode 汇总

| Mode | Case 数 | Gap Category | Human Info Sources | Missing Info | Potential Source |
|---|---|---|---|---|---|
| TOC_SECTION_NUMBER_TITLE | 12 | B | IS-01 + IS-02 + IS-05 + IS-07/08/09 | numbering pattern + readable word + page context | textual structure + P6 region |
| APPENDIX_LETTER_TITLE | 1 | B | IS-06 + IS-02 + IS-05 + IS-07 | appendix letter + readable word | same |
| FORMULA_FRAGMENT_WIDE | 6 | B | IS-03 + IS-08 | symbol detection + formula page context | character class + P6 region |
| BODY_TEXT_CONTINUATION | 1 | C | IS-02 + IS-04 + IS-05 + IS-09 | sentence boundary interpretation | text semantics (requires interpretation) |

### 3.3 Adversarial Case 深度分析

#### AMB-018: "6.1" → "SMEFT"

```
Current machine information:
  gap=11.1, dy=0.0, w_a=13.8, w_b=38.2, same_style=True, line_obs=3

Human information used:
  IS-01: "6.1" matches numbering pattern (regex: \d+\.\d+)
  IS-02: "SMEFT" is a readable word (alphabetic, length > 2)
  IS-05: "S" is capitalized
  IS-07: page is TOC page (visual layout context)

Missing information:
  Text pattern recognition: is text_a a number? is text_b a readable word?
  Page context: is this a TOC/heading page?

Potential machine source:
  Textual structure feature layer:
    - number_pattern(text) → boolean (regex)
    - is_readable_word(text) → boolean (word detection)
    - is_capitalized(text) → boolean (case check)
  Visual context feature:
    - page_region_type → TOC / BODY / FORMULA (from P6)
```

#### AMB-040: "( )" → "cos("

```
Current machine information:
  gap=21.2, dy=0.0, w_a=11.0, w_b=15.4, same_style=True, line_obs=8

Human information used:
  IS-03: "( )" and "cos(" are math symbols (non-alphabetic, short)
  IS-08: page is formula-dense page (visual context)

Missing information:
  Symbol detection: is text_a/text_b a math symbol vs a readable word?
  Formula context: is this line in a formula region?

Potential machine source:
  Textual structure feature:
    - is_symbol(text) → boolean (character class analysis)
    - text_length_category(text) → SHORT / MEDIUM / LONG
  Visual context feature:
    - page_region_type → FORMULA (from P6)
    - line_density_category → DENSE / SPARSE
```

#### AMB-026: "transition form factor..." → "Its normalization is"

```
Current machine information:
  gap=9.9, dy=0.0, w_a=237.2, w_b=95.4, same_style=True, line_obs=8

Human information used:
  IS-02: both texts are readable (alphabetic words)
  IS-04: text_a ends with "." (punctuation boundary)
  IS-05: text_b starts with capital "I" (sentence start)
  IS-09: page is body text page (visual context)

Missing information:
  Raw signals (machine-observable, Category B):
    - ends_with_period(text_a) → True
    - starts_capital(text_b) → True
  Interpretation (inherently semantic, Category C):
    - "." + capitalization → "different sentence" → "different text unit"
    - This interpretation requires understanding that:
      (a) "." is a sentence terminator (not decimal, not abbreviation)
      (2) Capital "I" indicates sentence start (not proper noun)
      (3) Different sentences = different text units

Potential machine source:
  Raw signals: textual structure feature (Category B)
  Interpretation: text semantics layer (Category C)
    → Raw signals could REDUCE ambiguity (narrow the AMBIGUOUS zone)
    → But interpretation still requires Human authority
    → Likely PERMANENT HUMAN-OWNED BOUNDARY
```

---

## 四、Existing vs New Machine-observable Information

### 4.1 三种"解决 ambiguity"的方式

#### A. EXISTING INFORMATION (当前已存在，只是未组合)

**Round 1 中的实例：无。**

P4 v3 Design 已经尝试组合所有现有几何特征（gap + dy + font + w_b + line_obs），但仍有 ~13 irreducible FP。这证明：P4 的信息空间**结构性不足**，不是组合问题。

#### B. NEW MACHINE-OBSERVABLE INFORMATION (Human 使用了额外信息，但原则上可被机器观察)

**Round 1 中的实例：IS-01 ~ IS-09（全部 textual + visual sources）。**

| Information Source | Machine-observable method | Deterministic? | 现有 DICE layer 可提供? |
|---|---|---|---|
| IS-01 TEXT_NUMBER_PATTERN | regex: `^\d+(\.\d+)*\.?$` | ✅ deterministic | P1 has text, but P4 doesn't use it |
| IS-02 TEXT_READABLE_TITLE | word detection: `any(w.isalpha() and len(w)>2 for w in text.split())` | ✅ deterministic | P1 has text |
| IS-03 TEXT_SYMBOL_PATTERN | character class: non-alphabetic or length ≤ 3 | ✅ deterministic | P1 has text |
| IS-04 TEXT_PUNCTUATION | character check: `text.endswith('.')` | ✅ deterministic | P1 has text |
| IS-05 TEXT_CAPITAL_START | case check: `text[0].isupper()` | ✅ deterministic | P1 has text |
| IS-06 TEXT_APPENDIX_LETTER | regex: `^[A-F]\.\d+` | ✅ deterministic | P1 has text |
| IS-07 VISUAL_TOC_CONTEXT | P6 region type = TOC | ✅ deterministic | P6 classifies regions |
| IS-08 VISUAL_FORMULA_CONTEXT | P6 region type = FORMULA | ✅ deterministic | P6 classifies regions |
| IS-09 VISUAL_BODY_CONTEXT | P6 region type = BODY | ✅ deterministic | P6 classifies regions |

**关键洞察**：这些信息源**全部是 deterministic 且 machine-observable**。P1 已经有文本内容，P6 已经有 region 分类。问题不是"信息不存在于 DICE 中"，而是"P4 的 contract 禁止使用这些信息"。

这意味着：**Information Source Expansion 的实现路径不是"采集新数据"，而是"允许 P4 或新 layer 使用已有数据"。**

#### C. INHERENTLY SEMANTIC / CONTEXTUAL (即使增加机器 observable features，仍需要语义解释)

**Round 1 中的实例：IS-10（sentence boundary interpretation），仅 AMB-026。**

| Aspect | Machine-observable? | Inherently semantic? |
|---|---|---|
| "." at end of text_a | ✅ YES (IS-04) | ❌ |
| "I" capitalized in text_b | ✅ YES (IS-05) | ❌ |
| ". + capitalization = different sentence" | ❌ NO | ✅ YES (requires interpretation) |
| "different sentence = different text unit" | ❌ NO | ✅ YES (requires semantic judgment) |

**AMB-026 的 B+C 混合性质**：

- Raw signals（"."、大写）是 Category B → 可以缩小 AMBIGUOUS 范围
- Interpretation（"句号+大写=不同句子=不同text unit"）是 Category C → 需要 Human authority

**即使增加 raw signal detection，AMB-026 类型的 case 仍需要 Human 判断**——因为"."可能是小数点、缩写、列表标记；大写可能是专有名词。解释这些信号需要上下文语义理解。

### 4.2 结论

```
Round 1 的 Information Gap:

  Category A (existing, uncombined):    0 sources
  Category B (new, machine-observable): 9 sources (IS-01~IS-09)
  Category C (inherently semantic):     1 source (IS-10)

  → The gap is NOT "P4 has data but doesn't combine it."
  → The gap IS "P4's contract excludes textual and visual information."
  → Most excluded information IS machine-observable.
  → Only sentence boundary interpretation is inherently semantic.
```

---

## 五、Inherently Semantic Boundary

### 5.1 定义

```
INHERENTLY SEMANTIC BOUNDARY
```

**定义**：即使增加所有可能的 machine-observable features，该 boundary 的判断仍需要语义解释，无法通过 deterministic 规则可靠解决。

### 5.2 AMB-026 作为 Inherently Semantic Boundary 的分析

| 判断步骤 | Machine-observable? | 需要 interpretation? |
|---|---|---|
| 1. text_a = "transition form factor of primary interest to us." | ✅ YES (P1 有文本) | ❌ |
| 2. text_b = "Its normalization is" | ✅ YES | ❌ |
| 3. text_a 以 "." 结尾 | ✅ YES (IS-04) | ❌ |
| 4. text_b 以大写字母开头 | ✅ YES (IS-05) | ❌ |
| 5. "." 是句号（不是小数点/缩写） | ❌ NO | ✅ YES (需要上下文) |
| 6. 大写 "I" 是句子开始（不是专有名词） | ❌ NO | ✅ YES (需要上下文) |
| 7. 不同句子 = 不同 text unit | ❌ NO | ✅ YES (需要语义判断) |

步骤 1-4 是 Category B（machine-observable）。步骤 5-7 是 Category C（inherently semantic）。

**即使机器检测到". + 大写"，也无法确定性地得出"不同 text unit"的结论**——因为：
- "." 可能是小数点（"3.14"）、缩写（"e.g."）、列表标记（"1."）
- 大写可能是专有名词（"SMEFT"）、首字母缩写（"DNA"）
- 同一句子内可能有"."（"Dr. Smith said..."）
- 不同句子可能在同一行（论文双栏排版）

### 5.3 Inherently Semantic Boundary 的特征

| 特征 | 说明 |
|---|---|
| Raw signals are machine-observable | 标点、大写等可以被机器检测 |
| Interpretation requires context | 信号的含义取决于上下文 |
| No deterministic rule can replace interpretation | 任何规则都有 false positive/negative |
| Human authority required | 需要 Human 阅读理解文本 |

### 5.4 不强行机器化

**对于 Inherently Semantic Boundary，不尝试 machine resolution。**

这些 boundary 应归类为 **PERMANENT HUMAN-OWNED BOUNDARY**——系统明确知道这里需要 Human Authority。

---

## 六、Information Source Expansion

### 6.1 核心原则

```
DICE 原则：Improve Evidence Quality upstream, rather than patch downstream logic.
```

**不应该**：
```
gap > 8 → exception → heuristic → patch
```

**应该**：
```
问：Human 是不是在看 text structure / visual structure / document hierarchy?
如果是 → 增加 Evidence Source（新的 information layer）
```

### 6.2 Information Source Expansion Candidates

| Candidate | 信息内容 | 实现方式 | 影响的 Mode | Category |
|---|---|---|---|---|
| **Textual Structure Feature** | text_pattern(text) → {NUMBER, READABLE_WORD, SYMBOL, PUNCTUATION, MIXED} | 对 P1 observation 的 text 字段做 pattern analysis | TOC_NUM_TITLE, APPENDIX_LETTER, FORMULA_WIDE | B |
| **Visual Context Feature** | page_region_type → {TOC, BODY, FORMULA, TABLE, MIXED} | 从 P6 region type 派生 | 全部 modes | B |
| **Sentence Boundary Signal** | ends_with_period + starts_capital → boolean signals | 对 P1 text 做 character check | BODY_CONT (reduces AMBIGUOUS zone, but not resolves) | B (raw) + C (interpretation) |

### 6.3 Textual Structure Feature 的概念设计（不实施）

```
Input: P1 observation.text (string)
Output: TextStructureProfile {
    is_number: bool          # regex match \d+(\.\d+)*
    is_appendix_letter: bool # regex match [A-F]\.\d+
    is_readable_word: bool   # contains alphabetic word length > 2
    is_symbol: bool          # non-alphabetic, length <= 5
    ends_with_period: bool   # text.rstrip().endswith('.')
    starts_capital: bool     # text[0].isupper()
    text_length_category: enum  # SHORT(<=5), MEDIUM(6-20), LONG(>20)
}
```

**这个 feature 不修改 P4**。它是 P4 之外的新 information source，可以：
1. 作为 Relation Assessment（概念层）的输入
2. 作为 P7.1 StructureHypothesis 的 signal
3. 作为 Human Review UI 的 context（但不是推荐答案）

### 6.4 不实施的理由

1. 当前阶段是 READ-ONLY research
2. 新 information source 需要独立验证其跨文档稳定性
3. 即使增加 textual structure feature，仍需要 Generalization Gate 验证
4. AMB-026 证明某些 case 即使有 raw signals 仍需 Human interpretation

---

## 七、Boundary Shrinkage 的真正机制

### 7.1 正确路径（非直接 Human→Rule）

```
Human Decision (multiple, independent)
        ↓
Boundary Evidence (ValidationRecord → ValidatedEvidence)
        ↓
Information Source Attribution
    (which IS did Human use? A/B/C?)
        ↓
Repeated Cases (same mode, multiple documents)
        ↓
Cross-document Pattern
    (consistent Human decisions + consistent IS usage?)
        ↓
Generalization Test
    (can machine replicate using identified IS?)
        ↓
Independent Validation
    (second reviewer agreement)
        ↓
Machine Boundary Candidate
        ↓
Promotion Gate (9 gates)
        ↓
┌───────────────────┬───────────────────┐
│                   │                   │
Machine-resolvable │  Human-owned      │
Boundary            │  Boundary         │
(shrinkage)         │ (permanent or     │
                    │  pending more     │
                    │  evidence)        │
└───────────────────┴───────────────────┘
```

### 7.2 Shrinkage 的前提条件

某一类 ambiguity 可以 shrink 的条件：

1. **Information Source Attribution 完成**：明确 Human 使用了哪些 IS
2. **IS 属于 Category B**：machine-observable，非 inherently semantic
3. **Generalization Test 通过**：机器用相同 IS 可以复现 Human judgment
4. **Gate 全部通过**：9 个 Gate 满足

### 7.3 当前各 Mode 的 Shrinkage 可能性

| Mode | IS Attribution | Category | Shrinkage 可能? | 需要什么 |
|---|---|---|---|---|
| TOC_SECTION_NUMBER_TITLE | IS-01 + IS-02 + IS-05 + IS-07/08/09 | B | ⚠️ 可能 | Textual structure feature + 更多 case + inter-reviewer |
| APPENDIX_LETTER_TITLE | IS-06 + IS-02 + IS-05 + IS-07 | B | ⚠️ 可能 | 同上（但仅 1 case） |
| FORMULA_FRAGMENT_WIDE | IS-03 + IS-08 | B | ⚠️ 可能 | Symbol detection + P6 formula region + 更多 case |
| BODY_TEXT_CONTINUATION | IS-02 + IS-04 + IS-05 + IS-09 | **C** | ❌ 不可能 | 需要 sentence boundary interpretation（inherently semantic） |

### 7.4 Shrinkage 的不对称性

- **Category B modes**（TOC_NUM_TITLE, FORMULA_WIDE）：理论上可以 shrink，但需要验证
- **Category C modes**（BODY_CONT）：不可 shrink，永久 Human-owned

**不要求所有 Human case 最终都被机器自动化。** Category C 的存在是系统设计的正确结果，不是失败。

---

## 八、Human-owned Boundary

### 8.1 正式定义

```
HUMAN_OWNED_BOUNDARY
```

**定义**：某类 boundary 判断永久需要 Human authority，因为其信息需求超出机器当前和可预见的信息空间。

### 8.2 归类条件

一个 boundary mode 应被归类为 HUMAN_OWNED_BOUNDARY 的条件（满足任一）：

| 条件 | 说明 |
|---|---|
| 当前信息不足 | P4/P7 当前信息空间无法表达 |
| 新信息源仍不能稳定解决 | 即使增加 Category B 信息源，仍有 irreducible FP |
| Semantic interpretation required | 判断需要 Category C 语义解释 |
| Context-dependent | 信号含义随上下文变化 |
| High false-positive cost | 误判代价高（如破坏公式结构） |
| Adversarial cases cannot be robustly separated | 对抗性 case 无法可靠区分 |
| No stable cross-document feature relationship | 跨文档特征关系不稳定 |

### 8.3 当前候选

| Boundary Mode | Human-owned? | 主要理由 |
|---|---|---|
| BODY_TEXT_CONTINUATION | ✅ 很可能永久 Human-owned | Category C — sentence boundary interpretation is inherently semantic |
| FORMULA_FRAGMENT_WIDE (line_obs≤15) | ⚠️ 可能 Human-owned | 需要 visual context；即使增加 symbol detection，仍需 page-level interpretation |
| TOC_SECTION_NUMBER_TITLE | ❌ 可能 machine-resolvable | Category B — textual structure feature 可能解决，但需 Gate 验证 |

### 8.4 Human-owned ≠ system failure

```
Human-owned Boundary 表示：
  "系统明确知道这里需要 Human Authority。"

不是：
  "系统失败了。"
  "系统有 bug。"
  "需要更多 heuristic。"

而是：
  "系统正确识别了自身信息空间的边界。"
```

---

## 九、Boundary Intelligence Loop

### 9.1 最小闭环

```
Observation (P1, immutable)
    ↓
Machine Assessment (P4 geometry + P7.1 structure)
    ↓
┌─────────────────┬─────────────────┐
│                 │                 │
Deterministic     Ambiguous
(MERGE/BLOCK)     (KEEP_SEPARATE,
│                  needs review)
│                 │
↓                 ↓
Automatic         Human Review
(no human)        (via P7.2)
│                 │
│                 ↓
│            Boundary Evidence
│            (ValidationRecord)
│                 │
│                 ↓
│         Information Source Attribution
│         (which IS did Human use?)
│                 │
│                 ↓
│         Information Gap Identification
│         (A/B/C category)
│                 │
│         ┌───────┴───────┐
│         │               │
│     Category B       Category C
│     (machine-       (inherently
│      observable)     semantic)
│         │               │
│         ↓               ↓
│   Candidate IS     Human-owned
│   Expansion        Boundary
│         │          (permanent)
│         ↓
│   Generalization
│   Evaluation
│         │
│   ┌─────┴─────┐
│   │           │
│   Passed    Not passed
│   │           │
│   ↓           ↓
│ Machine     Keep Human
│ Boundary    Boundary
│ (shrinkage) (pending more
│             evidence)
│
↓
Evidence (derived from ACCEPT)
```

### 9.2 Loop 的目标

**不是**："消灭所有 Human"

**是**："让 Human Review 只存在于真正无法可靠自动决定的 Boundary。"

### 9.3 Loop 的不变量

| 不变量 | 说明 |
|---|---|
| Observation immutable | P1 输出不可变 |
| P4 frozen | P4 v2 不修改 |
| Human Decision immutable | ValidationRecord 不可变 |
| Evidence derived | ValidatedEvidence 从 ACCEPT 派生 |
| Machine Boundary 需要 Gate | 不自动从 Human Decision 推导 |
| Human-owned Boundary 固定化 | 不随文档增长 |

---

## 十、Human Workload Scaling

### 10.1 三个未来情形

#### Scenario A (BAD)

```
Corpus ↑ → Ambiguity ↑ → Human workload ↑ (linear)
```

发生条件：
- 没有 boundary shrinkage
- 没有 document-type capability
- 每个 AMBIGUOUS case 都需要 Human review
- Human workload 与 document volume 成正比

**DICE 应避免此情形。**

#### Scenario B (DESIRED)

```
Corpus ↑ → Boundary shrinkage → Human workload ≈ stable
```

发生条件：
- Category B modes 通过 Gate → shrink 到 machine
- Document-type capability 积累 → 同类型文档自动处理
- AMBIGUOUS 去重 → 相同 pattern 只 review 一次
- Human-owned Boundary 固定化

**DICE 架构设计为此情形。但此情形未被实证验证。**

#### Scenario C (CAPABILITY EXPANSION)

```
New document types → New boundary modes → Human workload ↑ temporarily
→ capability expansion → eventually stabilizes
```

发生条件：
- 新文档类型产生新的 ambiguity pattern
- 新 pattern 需要 Human review 来识别
- 积累足够 evidence 后 shrink 或固定为 Human-owned
- workload 暂时上升，然后稳定

**这是系统成长的正常阶段。**

### 10.2 "更多数据" vs "更多 boundary classes"

| 维度 | 对 Human workload 的影响 | 管理策略 |
|---|---|---|
| 更多同类型数据 | ❌ 不应增加 workload | Document-type capability（同类型自动处理） |
| 更多新文档类型 | ⚠️ 暂时增加 workload | Capability expansion（新类型需要 Human 识别 pattern） |
| 更多新 boundary modes | ⚠️ 暂时增加 workload | Information Source Expansion + Gate 验证 |

**核心区分**：
- "更多数据"（same document type, more instances）→ workload 不应增长
- "更多 boundary classes"（new document type, new ambiguity pattern）→ workload 暂时增长

### 10.3 Architecture 设计原则

```
Human workload 不应仅仅因为 corpus size 增长而线性增长。
```

实现方式：
1. **AMBIGUOUS pattern 去重**：相同 (mode, gap_range, w_b_range, line_obs_range) 的 pair 只 review 一次
2. **Document-type capability**：已验证文档类型的 AMBIGUOUS pattern 自动处理
3. **Boundary Shrinkage**：Category B modes 通过 Gate 后移到 machine
4. **Human-owned Boundary 固定化**：Category C modes 固定为常量 workload

### 10.4 重要声明

```
WHAT WE KNOW:
  - 设备手册 AMBIGUOUS = 0 (5 docs verified)
  - arxiv 文档 AMBIGUOUS = 43 (3 docs)
  - Round 1 workload = 20 cases / 5.1 min

WHAT WE SUSPECT:
  - 同类型文档的 AMBIGUOUS pattern 可能一致（但未验证）
  - Boundary shrinkage 可能减少 workload（但 Gate 未通过）

WHAT WE HAVE NOT VALIDATED:
  - "Human workload tends toward constant" — 这是架构设计目标，未被实证验证
  - Document-type capability 未实现
  - AMBIGUOUS 去重未实现
  - Boundary shrinkage 未发生（Gate 未通过）
```

**正确表述**：

> "Architecture is designed to prevent linear workload growth, but this remains empirically unvalidated."

---

## 十一、Future Experiment Priorities

基于当前 Evidence 的优先级排序（不实施）：

| Priority | Experiment | 目的 | 前置条件 |
|---|---|---|---|
| **R1** | Information Source Attribution Validation | 验证 IS-01~IS-09 的跨文档稳定性 | Timer fix + 更多 case |
| **R2** | Textual Structure Feature Prototype | 验证 text_pattern detection 是否可复现 Human judgment | R1 完成 |
| **R3** | Cross-document Boundary Mode Analysis | 验证同 mode 是否跨文档一致 | 更多文档 + 更多 case |
| **R4** | Second Reviewer Experiment | 测量 inter-reviewer agreement | Timer fix |
| **R5** | Human-owned Boundary Stability | 确认 BODY_CONT 是否永久 Human-owned | 更多 BODY_CONT case |
| **R6** | Boundary Shrinkage Measurement | 测量 shrinkage 是否发生 | R1-R4 完成 + Gate 验证 |
| **R7** | Machine Boundary Promotion Experiment | 验证 Category B mode 是否可 machine-resolve | R1-R6 完成 + Gate 通过 |

**不预设这些一定都要做。** 根据未来 Evidence 调整优先级。

---

## 十二、WHAT WE KNOW / SUSPECT / NOT VALIDATED

### WHAT WE KNOW

1. P4 的 geometry-only contract 排除了文本内容和视觉上下文
2. Round 1 中 Human 使用的全部信息源都是 Category B（machine-observable），除 AMB-026 的 interpretation 是 Category C
3. Information Gap 不是"P4 有数据但没组合"，而是"P4 契约排除了整类信息"
4. P1 已有文本内容，P6 已有 region 分类——信息存在于 DICE 中，但 P4 不使用
5. AMB-026 是 B+C 混合：raw signals 可机器检测，interpretation 需 Human
6. 设备手册 AMBIGUOUS = 0（5 docs verified）
7. Round 1 Human accuracy = 95%（19/20），1 GT disputed
8. Machine Boundary Promotion Gate: 2/9 passed

### WHAT WE SUSPECT

1. TOC_SECTION_NUMBER_TITLE 可能 machine-resolvable（Category B + textual structure feature）
2. FORMULA_FRAGMENT_WIDE 可能部分 machine-resolvable（symbol detection + P6 formula region）
3. BODY_TEXT_CONTINUATION 很可能永久 Human-owned（Category C）
4. 同类型文档的 AMBIGUOUS pattern 可能一致（未验证）
5. Textual structure feature 可能缩小 AMBIGUOUS 范围（未验证）

### WHAT WE HAVE NOT VALIDATED

1. "Human workload tends toward constant" — 架构设计目标，未实证验证
2. Textual structure feature 的跨文档稳定性 — 未测试
3. Inter-reviewer agreement — 未测量（单 reviewer）
4. Boundary shrinkage 是否实际发生 — Gate 未通过
5. Document-type capability — 未实现
6. AMBIGUOUS 去重 — 未实现
7. 剩余 23 AMBIGUOUS case 的表现 — 未测试
8. "Human decisions can be learned by machine" — 未验证，且不自动成立

### 正确表述

```
❌ 不写: "Human workload will remain constant"
✅ 写:   "Architecture is designed to prevent linear workload growth,
          but this remains empirically unvalidated."

❌ 不写: "Human decisions can be learned by machine"
✅ 写:   "Some boundary modes may become machine-resolvable
          if additional information sources demonstrate stable,
          generalizable evidence."

❌ 不写: "Textual structure feature will solve TOC_NUM_TITLE ambiguity"
✅ 写:   "Textual structure feature is a Category B candidate
          that may reduce AMBIGUOUS cases, pending Generalization Gate."
```

---

## 十三、Open Questions

| # | 问题 | 当前状态 | 需要什么 |
|---|---|---|---|
| 1 | Textual structure feature 是否可复现 Human judgment? | 未测试 | R1 + R2 |
| 2 | FORMULA_WIDE 的 visual context 是否可从 P6 获取? | P6 有 region type，但未验证 formula region 的准确性 | 检查 P6 实现 |
| 3 | BODY_CONT 是否真的永久 Human-owned? | 很可能，但仅 1 case | R5 (更多 BODY_CONT case) |
| 4 | 增加 textual structure feature 后，AMBIGUOUS 范围缩小多少? | 未计算 | R2 prototype |
| 5 | 不同 reviewer 是否使用相同 IS? | 未测量 | R4 (second reviewer) |
| 6 | 新文档类型是否产生新 boundary mode? | 未观察 | 更多文档类型测试 |
| 7 | Category B 的 IS 是否跨文档稳定? | 未验证 | R3 (cross-document) |
| 8 | Human workload 是否真的趋向常量? | 未验证 | 需要大规模实验 |

---

## 十四、Authorization Status

```
Research Status: COMPLETE (READ-ONLY)

Human-on-the-Boundary:
  = Boundary Evidence Source
  NOT: Human fallback worker

Information Source Expansion:
  = Design Candidate (Category B identified)
  NOT: Authorized implementation

Machine Boundary Promotion:
  = Gate NOT PASSED (2/9)
  NOT: Authorized

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
P4 v3 = NOT AUTHORIZED (suspended)
Timer Fix = NOT AUTHORIZED (design only)
GT Modification = NOT AUTHORIZED (GT_DISPUTED preserved)
Sample Expansion = NOT AUTHORIZED
Textual Structure Feature = NOT AUTHORIZED (design candidate only)
Frozen Baseline = INTACT
```

---

## STOP

```
DESIGN STATUS = READY (READ-ONLY research, not implementation)

Human-on-the-Boundary:
  PROMISING / EMPIRICALLY SUPPORTED FOR INITIAL FEASIBILITY
  NOT GENERALIZED / NOT FULLY VALIDATED / NOT COST-VALIDATED

Information Source Gap:
  Category A (existing, uncombined):    0 sources
  Category B (new, machine-observable): 9 sources (IS-01~IS-09)
  Category C (inherently semantic):     1 source (IS-10)

Key Insight:
  The gap is not "P4 has data but doesn't combine it."
  The gap is "P4's contract excludes textual and visual information
  that are individually machine-observable but collectively require interpretation."

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
Frozen = INTACT
```

**不进入下一阶段。不修改任何代码。不修改任何实验数据。等待下一步批准。**
