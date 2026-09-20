# DICE Research Asset Inventory

> 分类登记 DICE 重要研究资产, 一眼区分: 系统事实 vs 实验结果 vs 研究假设 vs 论文素材 vs
> 临时实验代码。每资产: ASSET / TYPE / STATUS / SOURCE / EVIDENCE_LEVEL / FROZEN? /
> PRODUCTION? / PAPER_VALUE / DEPENDENCY / NOTES。

---

## CATEGORY 1 — Frozen System Evidence

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| P1 atomic_text.py | drift=0 | layer_registry | Observed | YES | runtime | LOW | base | text atom extraction |
| P2 geometry_engine.py | drift=0 | layer_registry | Observed | YES | runtime | LOW | base | pairwise/single geometry |
| P2 geometry_config.py | drift=0 | layer_registry | Observed | YES | runtime | LOW | base | DEFAULT_CONFIG |
| P2 geometry_observation.py | drift=0 | layer_registry | Observed | YES | runtime | LOW | base | shape observation |
| P4 span_config.py | drift=0 | layer_registry | Observed | YES | runtime | LOW | base | y-band threshold 8pt |
| P6 region_engine.py | drift=0 | layer_registry | Observed | YES | runtime | LOW | base | region detection |
| TLD table_line_detector.py | drift=0 | layer_registry | Observed | YES | runtime | MEDIUM | IS-11 observer | chunker heuristic |
| GT is11_semantic_ground_truth.json | sha 7349963d | frozen | Observed | YES | NO | HIGH | eval baseline | 45-case labels |
| IS-11 harness is11_machine_evaluation.py | sha b4149402 | frozen | Observed | YES | NO | HIGH | experiment | decision fn untouched |
| Atomic Observation Layer | 7 sources | layer_registry | Observed | YES | runtime | MEDIUM | base | adapter.build_case_b_store |

## CATEGORY 2 — Validated Engineering Evidence

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| 45-case independence audit | complete | is11_human_review_report | Observed | NO | NO | HIGH | GT | TCC 26/3docs |
| IS-11 channel 8/8 correctness | verified | machine eval | Experimentally-supported | NO | NO | HIGH | GT+TLD | table-context decision rule |
| M-B Phase 3.2 REPLAY_PASS | complete | phase3.2 report | Experimentally-supported | NO | NO | HIGH | frozen+adapter | S1-S10 PASS F1-F10=0 |
| EIC-1 contract (Phase 2.2) | PASS | phase2.2 review | Mechanism-supported | NO | NO | HIGH | design | sole semantic gate |
| Localization Gap finding | verified | phase3.1 | Experimentally-supported | NO | NO | HIGH | frozen P2 | P_loc=150pt |

## CATEGORY 3 — Experimental Evidence

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| PH-02 15/15 results | complete | ph02_results.json | Experimentally-supported | NO | NO | HIGH | GT+frozen | A=0/1, REJECTED |
| M-B expressability audit | complete | mb_table_region_audit | Experimentally-supported | NO | NO | HIGH | frozen P2 | EXPRESSIBLE |
| M-B Phase 3.2 replay results | complete | phase3.2 results.json | Experimentally-supported | NO | NO | HIGH | adapter+runner | 21-row matrix |
| Correct-vs-blind comparison | verified | mb_case_facts.json | Observed | NO | NO | HIGH | frozen | no L1 diff |
| Canary density measurement | verified | phase3.1 | Experimentally-supported | NO | NO | HIGH | frozen P2 | 0 vs 30 |

## CATEGORY 4 — Rejected Hypotheses

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| PH-02 whole-group predicate | REJECTED | ph02 report | Experimentally-supported (rejected) | NO | NO | HIGH | - | 15/15 A=0; preserved |
| C2 candidate-column-segment | INSUFFICIENT | c2 review | Experimentally-supported | NO | NO | HIGH | - | coverage=1; preserved |
| LSP→different_cell direct mapping | FALSIFIED | phase2.1 | Observed (code-level) | NO | NO | HIGH | - | semantic leakage; preserved |

## CATEGORY 5 — Design-only Hypotheses

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| Design B (Structural Context Adapter) | implemented+verified | phase2 design | Design→Experimentally-supported | NO | NO | HIGH | adapter | recommended design |
| EIC-1 ten-element contract | PASS (design) | phase2.2 | Design | NO | NO | HIGH | - | semantic gate |
| Human Validation pattern-level | design only | phase2.2 | Hypothesis | NO | NO | HIGH | - | L5 not occurred |
| Conflict coexistence contract | design + synthetic-only | phase2.1/2.2 | Design | NO | NO | MEDIUM | - | natural cases=0 |

## CATEGORY 6 — Negative Evidence

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| VALUE_COLUMN (resnet p6 '21.59') | observed | case_facts | Observed | NO | NO | HIGH | frozen | role-blind L2 |
| CODE_LINE_NUMBER (LLaMA) | observed | corpus_acquisition | Observed | NO | NO | HIGH | frozen | sib=0 |
| TOC (2212 p15) | observed | corpus | Observed | NO | NO | HIGH | frozen | hardest confusable |
| caption pseudo-cell (med p20) | observed | phase2.1 microscope | Observed | NO | NO | HIGH | frozen | 4 fragments |
| page-wide margin contamination | observed | phase3.1 | Observed | NO | NO | HIGH | frozen | LOCALIZATION GAP |
| lag=0/1 unresolvable (313/462) | observed | phase3.2 | Experimentally-supported | NO | NO | HIGH | frozen | honest ABSTAIN |

## CATEGORY 7 — Case Studies

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| AMB-135 (FP→fix) | complete | case_study + phase3.2 | Experimentally-supported | NO | NO | HIGH | adapter | MERGE→KEEP |
| AMB-414/422 (canary) | complete | phase3.2 | Experimentally-supported | NO | NO | HIGH | localization | ABSTAIN preserved |
| AMB-313/462 (honest ABSTAIN) | complete | phase3.2 | Experimentally-supported | NO | NO | HIGH | frozen | lag=0/1 |
| AMB-262 (classification correction) | complete | phase3.2 + discrepancy D3 | Experimentally-supported | NO | NO | MEDIUM-HIGH | frozen | GT-consistent |
| AMB-005/024/034/074/346/350/522/530 (controls) | complete | phase3.2 | Experimentally-supported | NO | NO | MEDIUM | frozen | 8/8 unchanged |

## CATEGORY 8 — Paper Materials

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| dice_paper_materials.md/json | complete | this task | Mixed (per-item) | NO | NO | HIGH | - | 9 types A-I |
| mb_case_study.md/json | complete | this task | Mixed | NO | NO | HIGH | - | causal chain |
| dice_research_timeline.md | complete | this task | Mixed | NO | NO | HIGH | - | 12 phases |
| dice_engineering_evidence_index.md | complete | this task | Mixed | NO | NO | MEDIUM | - | 14 sections |

## CATEGORY 9 — Discrepancy / Correction Records

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| dice_evidence_discrepancy_log.md | complete | this task | Observed | NO | NO | HIGH | - | D1-D7, history preserved |
| D1 DIRECT 6→8→9 | logged | discrepancy log | Observed | NO | NO | HIGH | - | reconciliation PASS |
| D3 AMB-262 classification | logged | discrepancy log | Observed | NO | NO | HIGH | - | replay correction |
| D4 OFF pseudo-mismatch | logged | discrepancy log | Observed | NO | NO | MEDIUM | - | tuple/list artifact |

## CATEGORY 10 — Temporary Experimental Code

| ASSET | STATUS | SOURCE | EVIDENCE_LEVEL | FROZEN? | PROD? | PAPER_VALUE | DEPENDENCY | NOTES |
|---|---|---|---|---|---|---|---|---|
| tmp/mb_eic1_adapter.py | experimental | phase3.2 | Implementation | NO | **NO** | MEDIUM | reads frozen store | isolated, flag-gated |
| tmp/mb_phase3_2_replay.py | experimental | phase3.2 | Implementation | NO | **NO** | MEDIUM | imports harness unmodified | isolated |
| tmp/mb_phase3_2_*.json | experimental data | phase3.2 | Observed | NO | **NO** | LOW | - | results/baseline |
| tmp/mb_fp_precise.py / mb_cols.py / mb_case_audit.py | experimental | expressability audit | Observed | NO | **NO** | LOW | reads frozen | microscope scripts |

**EXPERIMENTAL_ARTIFACT_ISOLATION = PASS** — Category 10 全部: 仅 tmp/; 不被 production import;
不 mutation frozen; 不形成 production dependency。
