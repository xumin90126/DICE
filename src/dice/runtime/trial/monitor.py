"""
试运行监控引擎 — Phase 4.

TrialMonitor：收集和报告受控生产试运行的监控指标。

职责：
    1. 计算执行成功率
    2. 统计阻断分布
    3. 分析审批拒绝率
    4. 追踪护栏/权限失败
    5. 检测证据/能力/执行缺失
    6. 生成风险报告

输出：
    dice_output/phase4_trial_monitor/
        trial_metrics.json
        failure_distribution.json
        risk_report.json
        evidence_gap_report.json
        execution_gap_report.json

设计约束：
    - 只读已有数据——不修改任何执行记录
    - 不执行真实动作
    - 不自动生成建议
    - 不属于任何 Runtime 层
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional

from dice.runtime.trial.models import (
    TrialExecutionRecord,
    TrialMetrics,
    TrialStatus,
    TrialBlockReason,
    _now,
)


# ═══════════════════════════════════════════════════════════════════════════
# FailureDistribution — 失败分布
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class FailureDistribution:
    """失败分布统计。"""
    total: int = 0
    by_layer: dict[str, int] = field(default_factory=dict)
    by_reason: dict[str, int] = field(default_factory=dict)
    by_document: dict[str, int] = field(default_factory=dict)
    by_capability: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "by_layer": self.by_layer,
            "by_reason": self.by_reason,
            "by_document": self.by_document,
            "by_capability": self.by_capability,
        }


# ═══════════════════════════════════════════════════════════════════════════
# RiskReport — 风险报告
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class RiskReport:
    """试运行风险报告。"""
    trial_id: str = ""
    overall_risk: str = "low"
    success_rate: float = 0.0
    critical_failures: int = 0
    high_risk_failures: int = 0
    blocking_layers: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    generated_time: str = ""

    def __post_init__(self):
        if not self.generated_time:
            self.generated_time = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "overall_risk": self.overall_risk,
            "success_rate": self.success_rate,
            "critical_failures": self.critical_failures,
            "high_risk_failures": self.high_risk_failures,
            "blocking_layers": self.blocking_layers,
            "recommendations": self.recommendations,
            "generated_time": self.generated_time,
        }


# ═══════════════════════════════════════════════════════════════════════════
# TrialMonitor
# ═══════════════════════════════════════════════════════════════════════════


class TrialMonitor:
    """试运行监控引擎——收集和报告试运行监控指标。

    使用方式：
        monitor = TrialMonitor()
        metrics = monitor.collect_metrics(trial_id, records)
        monitor.generate_reports(trial_id, records)
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Args:
            output_dir: 监控报告输出目录
        """
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "dice_output",
                "phase4_trial_monitor",
            )
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # ── 指标收集 ───────────────────────────────────────────────────

    def collect_metrics(
        self,
        trial_id: str,
        records: list[TrialExecutionRecord],
    ) -> TrialMetrics:
        """从执行记录收集试运行指标。

        Args:
            trial_id: 试运行配置 ID
            records: 执行记录列表

        Returns:
            TrialMetrics——完整指标
        """
        metrics = TrialMetrics(trial_id=trial_id, total_documents=len(records))

        for record in records:
            if record.is_completed:
                metrics.completed_count += 1
            elif record.is_blocked:
                metrics.blocked_count += 1
                # 分层统计
                layer = record.blocked_at_layer
                metrics.blocked_by_layer[layer] = (
                    metrics.blocked_by_layer.get(layer, 0) + 1
                )

            # 护栏失败
            gr = record.guardrail_result
            if gr and gr.get("status") == "BLOCK":
                metrics.guardrail_failures += 1

            # 权限失败
            pr = record.permission_result
            if pr and pr.get("status") == "BLOCK":
                metrics.permission_failures += 1

            # 证据缺失
            ev = record.evidence_result
            if ev and ev.get("evidence_count", 0) == 0:
                metrics.evidence_gaps.append({
                    "document_id": record.document_id,
                    "record_id": record.record_id,
                    "capability_id": record.capability_id,
                })

            # 能力缺失
            cr = record.capability_result
            if cr and cr.get("match_score", 0) <= 0:
                metrics.capability_gaps.append({
                    "document_id": record.document_id,
                    "record_id": record.record_id,
                })

            # 执行缺失
            er = record.execution_result
            if er and not er.get("plan"):
                metrics.execution_gaps.append({
                    "document_id": record.document_id,
                    "record_id": record.record_id,
                    "capability_id": record.capability_id,
                })

        metrics.compute_rates()
        return metrics

    def collect_failure_distribution(
        self,
        records: list[TrialExecutionRecord],
    ) -> FailureDistribution:
        """收集失败分布统计。

        Args:
            records: 执行记录列表

        Returns:
            FailureDistribution——失败分布
        """
        dist = FailureDistribution()

        for record in records:
            if not record.is_blocked:
                continue

            dist.total += 1

            # 按层级
            layer = record.blocked_at_layer
            dist.by_layer[layer] = dist.by_layer.get(layer, 0) + 1

            # 按原因
            reason = record.block_reason
            dist.by_reason[reason] = dist.by_reason.get(reason, 0) + 1

            # 按文档
            doc_id = record.document_id
            dist.by_document[doc_id] = dist.by_document.get(doc_id, 0) + 1

            # 按能力
            cap_id = record.capability_id
            if cap_id:
                dist.by_capability[cap_id] = dist.by_capability.get(cap_id, 0) + 1

        return dist

    def generate_risk_report(
        self,
        trial_id: str,
        metrics: TrialMetrics,
        failure_dist: FailureDistribution,
    ) -> RiskReport:
        """生成风险报告。

        Args:
            trial_id: 试运行配置 ID
            metrics: 试运行指标
            failure_dist: 失败分布

        Returns:
            RiskReport——风险报告
        """
        report = RiskReport(trial_id=trial_id)

        # 整体风险
        if metrics.success_rate >= 0.90:
            report.overall_risk = "low"
        elif metrics.success_rate >= 0.70:
            report.overall_risk = "medium"
        elif metrics.success_rate >= 0.50:
            report.overall_risk = "high"
        else:
            report.overall_risk = "critical"

        report.success_rate = metrics.success_rate
        report.critical_failures = failure_dist.by_layer.get("Permission Check", 0)
        report.high_risk_failures = (
            failure_dist.by_layer.get("Production Guardrail", 0)
            + failure_dist.by_layer.get("Activation Boundary", 0)
        )

        # 阻断层
        report.blocking_layers = sorted(
            failure_dist.by_layer.keys(),
            key=lambda k: failure_dist.by_layer[k],
            reverse=True,
        )

        # 建议
        if metrics.guardrail_failures > 0:
            report.recommendations.append(
                f"护栏失败 {metrics.guardrail_failures} 次——审查安全策略"
            )
        if metrics.permission_failures > 0:
            report.recommendations.append(
                f"权限失败 {metrics.permission_failures} 次——审查 Scope 配置"
            )
        if metrics.evidence_gaps:
            report.recommendations.append(
                f"证据缺失 {len(metrics.evidence_gaps)} 个——审查 Evidence Runtime"
            )
        if metrics.capability_gaps:
            report.recommendations.append(
                f"能力缺失 {len(metrics.capability_gaps)} 个——审查 Capability Registry"
            )
        if metrics.execution_gaps:
            report.recommendations.append(
                f"执行缺失 {len(metrics.execution_gaps)} 个——审查 Execution Runtime"
            )

        return report

    # ── 报告生成 ───────────────────────────────────────────────────

    def generate_reports(
        self,
        trial_id: str,
        records: list[TrialExecutionRecord],
    ) -> dict[str, str]:
        """生成所有监控报告。

        Args:
            trial_id: 试运行配置 ID
            records: 执行记录列表

        Returns:
            报告文件路径字典
        """
        metrics = self.collect_metrics(trial_id, records)
        failure_dist = self.collect_failure_distribution(records)
        risk_report = self.generate_risk_report(trial_id, metrics, failure_dist)

        reports = {}

        # 1. 试运行指标
        metrics_path = os.path.join(self.output_dir, "trial_metrics.json")
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics.to_dict(), f, indent=2, ensure_ascii=False)
        reports["trial_metrics"] = metrics_path

        # 2. 失败分布
        failure_path = os.path.join(self.output_dir, "failure_distribution.json")
        with open(failure_path, "w", encoding="utf-8") as f:
            json.dump(failure_dist.to_dict(), f, indent=2, ensure_ascii=False)
        reports["failure_distribution"] = failure_path

        # 3. 风险报告
        risk_path = os.path.join(self.output_dir, "risk_report.json")
        with open(risk_path, "w", encoding="utf-8") as f:
            json.dump(risk_report.to_dict(), f, indent=2, ensure_ascii=False)
        reports["risk_report"] = risk_path

        # 4. 证据缺失报告
        evidence_gaps = [
            gap for gap in metrics.evidence_gaps
        ]
        evidence_path = os.path.join(self.output_dir, "evidence_gap_report.json")
        with open(evidence_path, "w", encoding="utf-8") as f:
            json.dump(evidence_gaps, f, indent=2, ensure_ascii=False)
        reports["evidence_gap_report"] = evidence_path

        # 5. 执行缺失报告
        execution_gaps = [
            {
                "document_id": gap.get("document_id", ""),
                "record_id": gap.get("record_id", ""),
                "capability_id": gap.get("capability_id", ""),
            }
            for gap in metrics.execution_gaps
        ]
        execution_path = os.path.join(self.output_dir, "execution_gap_report.json")
        with open(execution_path, "w", encoding="utf-8") as f:
            json.dump(execution_gaps, f, indent=2, ensure_ascii=False)
        reports["execution_gap_report"] = execution_path

        return reports

    def get_summary(
        self,
        trial_id: str,
        records: list[TrialExecutionRecord],
    ) -> str:
        """生成人类可读的监控摘要。

        Args:
            trial_id: 试运行配置 ID
            records: 执行记录列表

        Returns:
            监控摘要文本
        """
        metrics = self.collect_metrics(trial_id, records)
        failure_dist = self.collect_failure_distribution(records)
        risk = self.generate_risk_report(trial_id, metrics, failure_dist)

        lines = [
            "=" * 60,
            f"试运行监控报告 — {trial_id}",
            "=" * 60,
            "",
            f"📊 总体指标:",
            f"   文档总数: {metrics.total_documents}",
            f"   ✅ 通过: {metrics.completed_count}",
            f"   ❌ 阻断: {metrics.blocked_count}",
            f"   成功率: {metrics.success_rate:.1%}",
            "",
            f"🔴 风险等级: {risk.overall_risk.upper()}",
            "",
            f"📉 失败分布:",
        ]

        if failure_dist.by_layer:
            for layer, count in sorted(
                failure_dist.by_layer.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                lines.append(f"   {layer}: {count} 次")

        lines.extend([
            "",
            f"⚠️  护栏失败: {metrics.guardrail_failures}",
            f"🔒 权限失败: {metrics.permission_failures}",
            f"🔍 证据缺失: {len(metrics.evidence_gaps)}",
            f"🎯 能力缺失: {len(metrics.capability_gaps)}",
            f"⚡ 执行缺失: {len(metrics.execution_gaps)}",
            "",
        ])

        if risk.recommendations:
            lines.append("💡 建议:")
            for rec in risk.recommendations:
                lines.append(f"   - {rec}")

        return "\n".join(lines)


__all__ = [
    "FailureDistribution",
    "RiskReport",
    "TrialMonitor",
]