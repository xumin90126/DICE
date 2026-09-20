"""
DICE 2.0 — 轻量 Human Gate（后置对齐）。

Human 只看最终产出（Guardrails 已经拦掉硬错误），做二选一审判：
  YES —— 接受本次提取（作为成功 Trace，供后续轨迹蒸馏）
  NO  —— 拒绝（丢弃/调整，供后续定位问题）

设计原则：
  - Human 是最终裁定者（System 零权威，LLM 仅提案）
  - 只暴露 YES/NO + 可选修改框，不做前置边界定义
  - 每次裁定记录 user_feedback + trace_id，与审计 trace 关联
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .schemas import ExtractionResult
from .guardrails import GuardrailsResult


@dataclass
class HumanVerdict:
    """一次 Human 裁定记录。"""

    trace_id: str = ""
    verdict: str = "PENDING"     # YES / NO / PENDING
    feedback: str = ""           # 可选修改意见（NO 时建议填）
    judged_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "verdict": self.verdict,
            "feedback": self.feedback,
            "judged_at": self.judged_at,
        }


def _render(result: ExtractionResult, gr: GuardrailsResult) -> str:
    """把提取结果 + Guardrails 结果渲染成可读文本，供 Human 快速判断。"""
    lines = [f"\n{'='*60}", f"文档：{result.document_id}", f"{'='*60}"]

    lines.append(f"\n【Guardrails 断言】{'✅ 通过' if gr.passed else '❌ 有拦截'}")
    for v in gr.violations:
        lines.append(f"  ❌ [{v.rule_id}] {v.field}: {v.message}")
    for w in gr.warnings:
        lines.append(f"  ⚠️ [{w.rule_id}] {w.field}: {w.message}")

    lines.append(f"\n【储存温度】({len(result.storage_conditions)} 条)")
    for c in result.storage_conditions:
        lines.append(f"  · {c.condition_text!r} [{c.min_temp}, {c.max_temp}] {c.unit}")

    lines.append(f"\n【组分】({len(result.components)} 条)")
    for c in result.components:
        lines.append(f"  · {c.name!r} {c.quantity} {c.unit}")

    lines.append(f"\n【规格参数】({len(result.specifications)} 条)")
    for s in result.specifications:
        lines.append(f"  · {s.parameter!r} = {s.value} {s.unit}")

    lines.append(f"\n请输入裁定：YES（接受）/ NO（拒绝）/ 直接回车跳过")
    return "\n".join(lines)


def ask_human(result: ExtractionResult, gr: GuardrailsResult,
              trace_id: str, interactive: bool = True) -> HumanVerdict:
    """
    询问 Human 裁定。

    Args:
        interactive: True 时读 stdin 交互；False 时返回 PENDING（自动化测试用）。
    """
    verdict = HumanVerdict(trace_id=trace_id)

    print(_render(result, gr))
    if not interactive:
        print("  [非交互模式] 跳过 Human 裁定，verdict=PENDING")
        return verdict

    try:
        answer = input("> ").strip().upper()
    except EOFError:
        answer = ""

    if answer == "YES":
        verdict.verdict = "YES"
    elif answer == "NO":
        verdict.verdict = "NO"
        feedback = input("  修改意见（可选）> ").strip()
        verdict.feedback = feedback
    else:
        verdict.verdict = "PENDING"
    return verdict


def append_verdict(verdict: HumanVerdict, path: Path) -> None:
    """把裁定记录追加到 human_gate 日志（append-only）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(verdict.to_dict(), ensure_ascii=False) + "\n")
