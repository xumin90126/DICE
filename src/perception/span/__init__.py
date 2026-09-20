# Experimental Span v2 (P4)
from .span_config import (
    SpanConfig, DEFAULT_CONFIG, to_dict,
    REASON_MERGE, REASON_KEEP_SEPARATE,
    MERGE_REASON_SAME_LINE_CONTIGUOUS, MERGE_REASON_NEXT_LINE_CONTIGUOUS,
    SEPARATE_REASON_LARGE_HORIZONTAL_GAP, SEPARATE_REASON_CROSS_COLUMN_GAP,
    SEPARATE_REASON_LARGE_VERTICAL_GAP, SEPARATE_REASON_PAGE_BOUNDARY,
    SEPARATE_REASON_STYLE_BREAK, SEPARATE_REASON_NOT_ADJACENT, SEPARATE_REASON_NO_OVERLAP,
)
from .span_observation import ExperimentalSpan, MergeDecision
from .span_rules import decide_merge
from .span_engine import (
    construct_spans, construct_spans_with_trace,
    verify_observation_coverage, reconstruct_span_text,
)
