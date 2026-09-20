# Human Boundary Review — Round 1 Case-Level Appendix

> 20 个 case 的逐个分析。READ-ONLY。

---

## 全部 20 Case 明细

### AMB-001
| 字段 | 值 |
|---|---|
| 文档 | arxiv_toc p2 |
| text_a | "1" |
| text_b | "Introduction" |
| gap | 10.0pt |
| w_b | 68.6pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap (inter-decision) | N/A (first case) |
| Comment | (空) |
| 分析 | 经典 TOC 序号+标题，Human 从页面布局立即识别 |

### AMB-005
| 字段 | 值 |
|---|---|
| 文档 | arxiv_toc p2 |
| text_a | "2.3.1" |
| text_b | "Factorization" |
| gap | 12.4pt |
| w_b | 62.2pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 5.2s |
| Comment | (空) |
| 分析 | 多级编号+标题，Human 正确识别 |

### AMB-012
| 字段 | 值 |
|---|---|
| 文档 | arxiv_toc p2 |
| text_a | "4.1" |
| text_b | "Decomposition of" |
| gap | 11.1pt |
| w_b | 82.4pt |
| line_obs | 9 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 5.5s |
| Comment | (空) |
| 分析 | 较高密度 TOC 行（line_obs=9），但 Human 仍正确识别 |

### AMB-014
| 字段 | 值 |
|---|---|
| 文档 | arxiv_toc p2 |
| text_a | "5" |
| text_b | "Prediction for" |
| gap | 10.0pt |
| w_b | 76.0pt |
| line_obs | 8 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 37.4s (较长) |
| Comment | (空) |
| 分析 | 较长 gap 可能因 Human 仔细查看 TOC 布局 |

### AMB-017
| 字段 | 值 |
|---|---|
| 文档 | arxiv_toc p2 |
| text_a | "6" |
| text_b | "Consequences for physics" |
| gap | 10.0pt |
| w_b | 295.0pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 51.0s (最长之一) |
| Comment | (空) |
| 分析 | w_b=295pt 是最宽标题，Human 可能花时间查看完整标题 |

### AMB-018 ★ ADVERSARIAL
| 字段 | 值 |
|---|---|
| 文档 | arxiv_toc p2 |
| text_a | "6.1" |
| text_b | "SMEFT" |
| gap | 11.1pt |
| w_b | 38.2pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 2.5s |
| Comment | (空) |
| 分析 | **Adversarial case 1**。w_b=38.2pt（与公式碎片 w_b=15-28pt 接近），但 Human 从 TOC 页面上下文正确识别 "6.1" 是节号、"SMEFT" 是标题。Human 利用了页面布局信息（geometry-only pipeline 不可用）。 |

### AMB-021
| 字段 | 值 |
|---|---|
| 文档 | arxiv_toc p2 |
| text_a | "B.1" |
| text_b | "Two-point function" |
| gap | 8.8pt |
| w_b | 90.7pt |
| line_obs | 3 |
| Mode | APPENDIX_LETTER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 2.5s |
| Comment | (空) |
| 分析 | 附录字母+标题，Human 正确识别 |

### AMB-023
| 字段 | 值 |
|---|---|
| 文档 | arxiv_bio_body p3 |
| text_a | "1" |
| text_b | "Introduction" |
| gap | 13.5pt |
| w_b | 74.0pt |
| line_obs | 2 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 2.7s |
| Comment | (空) |
| 分析 | 正文中的 section heading（非 TOC 页），Human 从正文上下文正确识别 |

### AMB-025
| 字段 | 值 |
|---|---|
| 文档 | arxiv_bio_body p5 |
| text_a | "2.1" |
| text_b | "Leptonic processes" |
| gap | 12.5pt |
| w_b | 101.6pt |
| line_obs | 2 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 2.8s |
| Comment | (空) |
| 分析 | 正文 subsection heading，Human 正确识别 |

### AMB-026 ★ ERROR
| 字段 | 值 |
|---|---|
| 文档 | arxiv_bio_body p5 |
| text_a | "transition form factor of prim" |
| text_b | "Its normalization is" |
| gap | 9.9pt |
| w_b | 95.4pt |
| line_obs | 8 |
| Mode | BODY_TEXT_CONTINUATION |
| GT | SHOULD_MERGE |
| **Human** | **KEEP_SEPARATE ❌** |
| Gap | 5.2s |
| Comment | (空) |
| 分析 | **唯一 error**。GT 标记为 SHOULD_MERGE（基于 w_a≥25 AND w_b≥25），但 Human 判断两个短语语义独立。这可能是 GT 标签问题而非 Human 错误——"transition form factor of prim" 和 "Its normalization is" 是两个独立短语，不应合并为同一文本单元。**Human 提供了语义判断，纠正了 geometry-only 分类的过度宽泛。** |

### AMB-027
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p1 |
| text_a | "1." |
| text_b | "Introduction" |
| gap | 22.0pt |
| w_b | 49.5pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 35.1s (较长) |
| Comment | (空) |
| 分析 | 文档切换（arxiv_toc → arxiv_2307），较长 gap 可能因新 PDF 加载 |

### AMB-028
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p2 |
| text_a | "2." |
| text_b | "The model: spinor Gross-P" |
| gap | 22.1pt |
| w_b | 172.8pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 3.4s |
| Comment | (空) |
| 分析 | Section heading，gap=22pt（较大），Human 正确识别 |

### AMB-029
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p2 |
| text_a | "" (公式符号) |
| text_b | "" (公式符号) |
| gap | 26.9pt |
| w_b | 19.7pt |
| line_obs | 14 |
| Mode | FORMULA_FRAGMENT_WIDE |
| GT | SHOULD_NOT_MERGE |
| **Human** | **KEEP_SEPARATE ✅** |
| Gap | 6.6s |
| Comment | (空) |
| 分析 | 公式碎片，Human 从公式行上下文正确识别 |

### AMB-030
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p2 |
| text_a | "r" |
| text_b | "S u" |
| gap | 8.3pt |
| w_b | 15.7pt |
| line_obs | 15 |
| Mode | FORMULA_FRAGMENT_WIDE |
| GT | SHOULD_NOT_MERGE |
| **Human** | **KEEP_SEPARATE ✅** |
| Gap | 17.4s |
| Comment | (空) |
| 分析 | 公式碎片（最高密度行 line_obs=15），Human 正确识别 |

### AMB-032
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p2 |
| text_a | "(" |
| text_b | "2 /" |
| gap | 13.8pt |
| w_b | 15.8pt |
| line_obs | 12 |
| Mode | FORMULA_FRAGMENT_WIDE |
| GT | SHOULD_NOT_MERGE |
| **Human** | **KEEP_SEPARATE ✅** |
| Gap | 28.6s |
| Comment | (空) |
| 分析 | 公式碎片，Human 正确识别 |

### AMB-034
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p2 |
| text_a | "3." |
| text_b | "Bound (localized) states" |
| gap | 22.1pt |
| w_b | 221.2pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 30.6s |
| Comment | (空) |
| 分析 | Section heading，Human 正确识别 |

### AMB-037
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p2 |
| text_a | "" (公式符号) |
| text_b | "" (公式符号) |
| gap | 24.3pt |
| w_b | 18.1pt |
| line_obs | 15 |
| Mode | FORMULA_FRAGMENT_WIDE |
| GT | SHOULD_NOT_MERGE |
| **Human** | **KEEP_SEPARATE ✅** |
| Gap | 57.4s (最长) |
| Comment | **"都是数字，符号，但没什么语义关联"** |
| 分析 | **唯一有 comment 的 case**。Reviewer 明确写出语义判断理由："没什么语义关联"。最长 gap（57.4s）可能因 Reviewer 仔细查看公式上下文后做出判断。 |

### AMB-040 ★ ADVERSARIAL
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p2 |
| text_a | "( )" |
| text_b | "cos(" |
| gap | 21.2pt |
| w_b | 15.4pt |
| line_obs | 8 |
| Mode | FORMULA_FRAGMENT_WIDE |
| GT | SHOULD_NOT_MERGE |
| **Human** | **KEEP_SEPARATE ✅** |
| Gap | 2.3s |
| Comment | (空) |
| 分析 | **Adversarial case 2**。与 AMB-018 几何特征部分重叠（gap 11-21pt, w_b 15-38pt），但 GT 相反。Human 从 arxiv_2307 公式页面上下文正确识别 "( )" 和 "cos(" 是公式碎片，不应合并。**Human 利用了页面上下文信息（公式页 vs TOC 页），这是 geometry-only pipeline 无法获取的。** |

### AMB-041
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p3 |
| text_a | "" (公式符号) |
| text_b | "" (公式符号) |
| gap | 9.0pt |
| w_b | 20.6pt |
| line_obs | 8 |
| Mode | FORMULA_FRAGMENT_WIDE |
| GT | SHOULD_NOT_MERGE |
| **Human** | **KEEP_SEPARATE ✅** |
| Gap | 4.2s |
| Comment | (空) |
| 分析 | 公式碎片，Human 正确识别 |

### AMB-043
| 字段 | 值 |
|---|---|
| 文档 | arxiv_2307 p3 |
| text_a | "4." |
| text_b | "Families of fundamental a" |
| gap | 22.0pt |
| w_b | 219.2pt |
| line_obs | 3 |
| Mode | TOC_SECTION_NUMBER_TITLE |
| GT | SHOULD_MERGE |
| **Human** | **MERGE ✅** |
| Gap | 6.8s |
| Comment | (空) |
| 分析 | Section heading，Human 正确识别 |

---

## 汇总表

| Case | Doc | Mode | GT | Human | Correct? | Gap(s) | Comment |
|---|---|---|---|---|---|---|---|
| AMB-001 | arxiv_toc | TOC_NUM_TITLE | MERGE | MERGE | ✅ | N/A | |
| AMB-005 | arxiv_toc | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 5.2 | |
| AMB-012 | arxiv_toc | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 5.5 | |
| AMB-014 | arxiv_toc | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 37.4 | |
| AMB-017 | arxiv_toc | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 51.0 | |
| AMB-018 ★ | arxiv_toc | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 2.5 | |
| AMB-021 | arxiv_toc | APPENDIX_LETTER | MERGE | MERGE | ✅ | 2.5 | |
| AMB-023 | arxiv_bio | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 2.7 | |
| AMB-025 | arxiv_bio | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 2.8 | |
| AMB-026 ★ | arxiv_bio | BODY_CONT | MERGE | SEPARATE | ❌ | 5.2 | |
| AMB-027 | arxiv_2307 | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 35.1 | |
| AMB-028 | arxiv_2307 | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 3.4 | |
| AMB-029 | arxiv_2307 | FORMULA_WIDE | NO_MERGE | SEPARATE | ✅ | 6.6 | |
| AMB-030 | arxiv_2307 | FORMULA_WIDE | NO_MERGE | SEPARATE | ✅ | 17.4 | |
| AMB-032 | arxiv_2307 | FORMULA_WIDE | NO_MERGE | SEPARATE | ✅ | 28.6 | |
| AMB-034 | arxiv_2307 | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 30.6 | |
| AMB-037 | arxiv_2307 | FORMULA_WIDE | NO_MERGE | SEPARATE | ✅ | 57.4 | "都是数字，符号，但没什么语义关联" |
| AMB-040 ★ | arxiv_2307 | FORMULA_WIDE | NO_MERGE | SEPARATE | ✅ | 2.3 | |
| AMB-041 | arxiv_2307 | FORMULA_WIDE | NO_MERGE | SEPARATE | ✅ | 4.2 | |
| AMB-043 | arxiv_2307 | TOC_NUM_TITLE | MERGE | MERGE | ✅ | 6.8 | |

**Totals**: 19 ✅ + 1 ❌ = 95.0% accuracy
