"""
P7.2 Minimal Review Interface — CLI confirmation interface.

This is a CONFIRMATION interface, not a free annotation tool. Human sees:
1. candidate text + source page + visual evidence/bbox
2. system observation + confidence + reason
and chooses Accept / Reject / Need Review + reason.

Human does NOT re-find text, re-draw bbox, re-annotate spans, or modify the candidate.

Measures REAL interaction duration (start -> submit) for each candidate.
No auto-ACCEPT, no LLM, no batch fabrication.
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .validation_config import (
    DECISION_ACCEPT, DECISION_REJECT, DECISION_NEED_REVIEW,
    DATASET_HUMAN_VALIDATION,
)
from .validation_models import ValidationTask, ValidationRecord
from .validation_engine import create_validation_record


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _print_separator():
    print("\n" + "=" * 70)


def present_candidate(task: ValidationTask, index: int, total: int) -> None:
    """Display one candidate for Human review (read-only presentation)."""
    _print_separator()
    print(f"  CANDIDATE {index}/{total}  |  priority={task.priority}")
    print("-" * 70)
    print(f"  1. SYSTEM OBSERVATION:")
    print(f"     type:      {task.observation_type}")
    print(f"     confidence:{task.confidence}")
    print(f"     document:  {task.document_id}  page: {task.page_number}")
    print()
    print(f"  2. EVIDENCE:")
    cc = task.candidate_content
    print(f"     text:      \"{cc.get('text', '')[:80]}\"")
    print(f"     bbox:      {cc.get('bbox')}")
    print(f"     span_ids:  {cc.get('span_ids', [])[:3]}")
    vr = task.visual_reference
    if vr.get("png_path"):
        print(f"     visual:    {vr.get('png_path')}")
    print()
    print(f"  3. SYSTEM REASON:")
    for step in task.system_reasoning:
        s = step.get("summary", {})
        label = step.get("step", "?")
        if label == "signals":
            sigs = s.get("collected", [])
            print(f"     signals:   {sigs}  (count={s.get('count')}, required={s.get('required')})")
        elif label == "decision":
            print(f"     decision:  {s.get('reason', '')}")
            print(f"     why not final: {s.get('why_not_final', '')}")
        elif label == "confidence":
            print(f"     confidence: structural={s.get('structural')} upstream={s.get('upstream')} final={s.get('final')}")
    print()
    print(f"  4. YOUR DECISION:")
    print(f"     [a] ACCEPT   [r] REJECT   [n] NEED REVIEW   [s] SKIP (save & exit)")


def get_human_decision(task: ValidationTask, index: int, total: int,
                       reviewer_id: str) -> Optional[Tuple[str, str, str, float]]:
    """Interactive: present candidate, capture decision + reason + notes + duration.

    Returns (decision, reason, notes, duration_seconds) or None to skip/exit.
    Measures REAL duration from presentation to submit.
    """
    present_candidate(task, index, total)
    start = time.monotonic()
    print()
    choice = input("     choice [a/r/n/s]: ").strip().lower()
    if choice == "s":
        return None
    decision_map = {"a": DECISION_ACCEPT, "r": DECISION_REJECT, "n": DECISION_NEED_REVIEW}
    if choice not in decision_map:
        print("     invalid; defaulting to NEED_REVIEW")
        choice = "n"
    decision = decision_map[choice]
    reason = input("     reason (required): ").strip()
    if not reason:
        reason = "(no reason given)"
    notes = input("     notes (optional): ").strip()
    duration = time.monotonic() - start
    print(f"     [recorded: {decision}, duration={duration:.1f}s]")
    return (decision, reason, notes, duration)


def run_review_session(tasks: List[ValidationTask],
                       reviewer_id: str,
                       resume_from: int = 0) -> List[Tuple[ValidationTask, ValidationRecord]]:
    """Run an interactive review session over a list of tasks.

    Returns list of (task, record) pairs. Records carry real duration_seconds.
    Pressing 's' saves progress and exits (resume next time).
    """
    results: List[Tuple[ValidationTask, ValidationRecord]] = []
    total = len(tasks)
    print(f"\n{'#' * 70}")
    print(f"#  P7.2 HUMAN VALIDATION SESSION")
    print(f"#  reviewer: {reviewer_id}")
    print(f"#  candidates: {total}  (resuming from {resume_from})")
    print(f"#  This is a CONFIRMATION interface. Do NOT re-annotate.")
    print(f"#  Press 's' at any candidate to save & exit.")
    print(f"{'#' * 70}")

    for i in range(resume_from, total):
        task = tasks[i]
        outcome = get_human_decision(task, i + 1, total, reviewer_id)
        if outcome is None:
            print(f"\n  [session saved at candidate {i + 1}/{total}]")
            break
        decision, reason, notes, duration = outcome
        ts = _now_iso()
        record = create_validation_record(
            task, decision, reason, reviewer_id, ts, duration, notes,
            dataset_tag=DATASET_HUMAN_VALIDATION,
        )
        results.append((task, record))
    else:
        print(f"\n  [session complete: {total}/{total}]")

    return results
