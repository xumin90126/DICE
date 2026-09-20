"""
受控试运行执行器 — Phase 4.

ControlledTrialRunner：编排受控生产试运行的完整流程。

职责：
    1. 消费已批准的 Execution Plan
    2. 按顺序通过七层治理架构
    3. 产生 TrialExecutionRecord——不执行真实生产动作
    4. 记录每层决策结果

设计约束：
    - 禁止执行真实生产动作
    - 禁止绕过任何一层治理
    - 禁止自动批准
    - 禁止自动扩大试运行范围
    - 不属于任何 Runtime 层——是独立的试运行编排层
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.trial.models import (
    TrialConfiguration,
    TrialExecutionRecord,
    TrialBatchResult,
    TrialMetrics,
    TrialStatus,
    TrialBlockReason,
    TrialExecutionPhase,
    _now,
    _uid,
)
from dice.runtime.trial.trial_manager import TrialManager


# ═══════════════════════════════════════════════════════════════════════════
# ControlledTrialRunner
# ═══════════════════════════════════════════════════════════════════════════


class ControlledTrialRunner:
    """受控试运行执行器——编排七层治理架构的完整试运行流程。

    使用方式：
        runner = ControlledTrialRunner(trial_manager)
        record = runner.run(
            trial_id="TRIAL-...",
            document_id="doc_001",
            capability_id="CAP-TROUBLESHOOT-DETECT",
            execution_action="detect_troubleshooting",
            evidence_result={"evidence_count": 5},
            capability_result={"match_score": 0.95},
            execution_result={"plan": "detect_and_record"},
            approval_status="APPROVED",
            activation_result={"status": "ALLOWED"},
            guardrail_result={"status": "ALLOW", "checks": 5},
            permission_result={"status": "ALLOW", "checks": 6},
        )
    """

    def __init__(
        self,
        trial_manager: TrialManager,
        output_dir: Optional[str] = None,
    ):
        """
        Args:
            trial_manager: 试运行管理器
            output_dir: 执行记录输出目录
        """
        self.trial_manager = trial_manager
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "dice_output",
                "phase4_trial_records",
            )
        self.output_dir = output_dir
        self._daily_counters: dict[str, dict[str, int]] = {}
        os.makedirs(self.output_dir, exist_ok=True)

    # ── 主执行方法 ─────────────────────────────────────────────────

    def run(
        self,
        trial_id: str,
        document_id: str,
        capability_id: str = "",
        execution_action: str = "",
        evidence_result: Optional[dict[str, Any]] = None,
        capability_result: Optional[dict[str, Any]] = None,
        execution_result: Optional[dict[str, Any]] = None,
        approval_status: str = "",
        activation_result: Optional[dict[str, Any]] = None,
        guardrail_result: Optional[dict[str, Any]] = None,
        permission_result: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> TrialExecutionRecord:
        """执行受控试运行——通过七层治理架构，产生执行记录。

        不执行真实生产动作。

        Args:
            trial_id: 试运行配置 ID
            document_id: 文档标识
            capability_id: 能力标识
            execution_action: 执行动作
            evidence_result: Evidence Runtime 输出
            capability_result: Capability Runtime 输出
            execution_result: Execution Runtime 输出
            approval_status: 审批状态
            activation_result: 激活决策结果
            guardrail_result: 护栏检查结果
            permission_result: 权限检查结果
            metadata: 扩展元数据

        Returns:
            TrialExecutionRecord——完整执行记录
        """
        record = TrialExecutionRecord(
            trial_id=trial_id,
            document_id=document_id,
            capability_id=capability_id,
            execution_action=execution_action,
            evidence_result=evidence_result or {},
            capability_result=capability_result or {},
            execution_result=execution_result or {},
            approval_status=approval_status,
            activation_result=activation_result or {},
            guardrail_result=guardrail_result or {},
            permission_result=permission_result or {},
            metadata=metadata or {},
        )
        record.trial_status = TrialStatus.RUNNING
        record.started_time = _now()

        # ── 检查 1: 试运行配置是否存在且启用 ──
        trial_config = self.trial_manager.get_trial(trial_id)
        if trial_config is None:
            record.trial_status = TrialStatus.BLOCKED
            record.block_reason = TrialBlockReason.SCOPE_EXCEEDED.value
            record.completed_time = _now()
            self._save_record(record)
            return record

        if not trial_config.enabled:
            record.trial_status = TrialStatus.BLOCKED
            record.block_reason = TrialBlockReason.SCOPE_EXCEEDED.value
            record.completed_time = _now()
            self._save_record(record)
            return record

        # ── 检查 2: 每日文档限制 ──
        if not self._check_daily_limit(trial_config, document_id):
            record.trial_status = TrialStatus.BLOCKED
            record.block_reason = TrialBlockReason.DAILY_LIMIT_EXCEEDED.value
            record.completed_time = _now()
            self._save_record(record)
            return record

        # ── 检查 3: 文档范围 ──
        if not trial_config.is_document_allowed(document_id):
            record.trial_status = TrialStatus.BLOCKED
            record.block_reason = TrialBlockReason.SCOPE_EXCEEDED.value
            record.completed_time = _now()
            self._save_record(record)
            return record

        # ── 检查 4: 能力范围 ──
        if capability_id and not trial_config.is_capability_allowed(capability_id):
            record.trial_status = TrialStatus.BLOCKED
            record.block_reason = TrialBlockReason.SCOPE_EXCEEDED.value
            record.completed_time = _now()
            self._save_record(record)
            return record

        # ── 检查 5: 执行动作范围 ──
        if execution_action and not trial_config.is_action_allowed(execution_action):
            record.trial_status = TrialStatus.BLOCKED
            record.block_reason = TrialBlockReason.SCOPE_EXCEEDED.value
            record.completed_time = _now()
            self._save_record(record)
            return record

        # ── 逐层验证 ──
        block_reason = self._validate_layers(
            record,
            evidence_result,
            capability_result,
            execution_result,
            approval_status,
            activation_result,
            guardrail_result,
            permission_result,
        )

        if block_reason:
            record.trial_status = TrialStatus.BLOCKED
            record.block_reason = block_reason
        else:
            record.trial_status = TrialStatus.COMPLETED

        record.completed_time = _now()
        self._increment_daily_counter(trial_id, document_id)
        self._save_record(record)
        return record

    def run_batch(
        self,
        trial_id: str,
        documents: list[dict[str, Any]],
    ) -> TrialBatchResult:
        """批量执行试运行。

        Args:
            trial_id: 试运行配置 ID
            documents: 文档列表，每个元素是 run() 方法的参数（不含 trial_id）

        Returns:
            TrialBatchResult——批量结果
        """
        trial_config = self.trial_manager.get_trial(trial_id)
        if trial_config is None:
            return TrialBatchResult(
                trial_id=trial_id,
                total_records=0,
                summary={"error": "Trial not found"},
            )

        # 检查批次大小
        if len(documents) > trial_config.max_batch_size:
            return TrialBatchResult(
                trial_id=trial_id,
                total_records=0,
                summary={
                    "error": f"Batch size {len(documents)} exceeds limit {trial_config.max_batch_size}"
                },
            )

        records = []
        for doc in documents:
            record = self.run(trial_id=trial_id, **doc)
            records.append(record)

        # 生成指标
        metrics = self._compute_metrics(trial_id, records)

        return TrialBatchResult(
            trial_id=trial_id,
            total_records=len(records),
            records=records,
            metrics=metrics,
            summary={
                "completed": sum(1 for r in records if r.is_completed),
                "blocked": sum(1 for r in records if r.is_blocked),
            },
        )

    # ── 内部方法 ───────────────────────────────────────────────────

    def _validate_layers(
        self,
        record: TrialExecutionRecord,
        evidence_result: Optional[dict[str, Any]],
        capability_result: Optional[dict[str, Any]],
        execution_result: Optional[dict[str, Any]],
        approval_status: str,
        activation_result: Optional[dict[str, Any]],
        guardrail_result: Optional[dict[str, Any]],
        permission_result: Optional[dict[str, Any]],
    ) -> str:
        """逐层验证七层治理架构，返回阻断原因（空字符串 = 全部通过）。"""

        # L1: Evidence Runtime
        if evidence_result:
            evidence_count = evidence_result.get("evidence_count", 0)
            if evidence_count == 0:
                return TrialBlockReason.EVIDENCE_EXTRACTION_FAILED.value

        # L2: Capability Runtime
        if capability_result:
            match_score = capability_result.get("match_score", 0)
            if match_score <= 0:
                return TrialBlockReason.CAPABILITY_MATCH_FAILED.value

        # L3: Execution Runtime
        if execution_result:
            if not execution_result.get("plan"):
                return TrialBlockReason.EXECUTION_PLAN_FAILED.value

        # L4: Approval Layer
        if approval_status and approval_status != "APPROVED":
            return TrialBlockReason.APPROVAL_REJECTED.value

        # L5: Activation Boundary
        if activation_result:
            activation_status = activation_result.get("status", "")
            if activation_status == "BLOCKED":
                return TrialBlockReason.ACTIVATION_BLOCKED.value

        # L6: Production Guardrail
        if guardrail_result:
            guardrail_status = guardrail_result.get("status", "")
            if guardrail_status == "BLOCK":
                return TrialBlockReason.GUARDRAIL_BLOCKED.value

        # L7: Permission Check
        if permission_result:
            permission_status = permission_result.get("status", "")
            if permission_status == "BLOCK":
                return TrialBlockReason.PERMISSION_BLOCKED.value

        return ""

    def _check_daily_limit(
        self, trial_config: TrialConfiguration, document_id: str
    ) -> bool:
        """检查每日文档限制。"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        trial_id = trial_config.trial_id

        if trial_id not in self._daily_counters:
            self._daily_counters[trial_id] = {}
        if today not in self._daily_counters[trial_id]:
            self._daily_counters[trial_id][today] = 0

        return self._daily_counters[trial_id][today] < trial_config.max_daily_documents

    def _increment_daily_counter(self, trial_id: str, document_id: str):
        """增加每日计数器。"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if trial_id not in self._daily_counters:
            self._daily_counters[trial_id] = {}
        self._daily_counters[trial_id][today] = (
            self._daily_counters[trial_id].get(today, 0) + 1
        )

    def _compute_metrics(
        self, trial_id: str, records: list[TrialExecutionRecord]
    ) -> TrialMetrics:
        """从执行记录计算指标。"""
        metrics = TrialMetrics(trial_id=trial_id)
        metrics.total_documents = len(records)
        metrics.completed_count = sum(1 for r in records if r.is_completed)
        metrics.blocked_count = sum(1 for r in records if r.is_blocked)

        # 各层阻断分布
        for r in records:
            if r.block_reason:
                layer = r.blocked_at_layer
                metrics.blocked_by_layer[layer] = (
                    metrics.blocked_by_layer.get(layer, 0) + 1
                )

        # 护栏和权限失败
        for r in records:
            gr = r.guardrail_result
            if gr and gr.get("status") == "BLOCK":
                metrics.guardrail_failures += 1
            pr = r.permission_result
            if pr and pr.get("status") == "BLOCK":
                metrics.permission_failures += 1

        # 证据/能力/执行缺失
        for r in records:
            ev = r.evidence_result
            if ev and ev.get("evidence_count", 0) == 0:
                metrics.evidence_gaps.append({
                    "document_id": r.document_id,
                    "record_id": r.record_id,
                })
            cr = r.capability_result
            if cr and cr.get("match_score", 0) <= 0:
                metrics.capability_gaps.append({
                    "document_id": r.document_id,
                    "record_id": r.record_id,
                })
            er = r.execution_result
            if er and not er.get("plan"):
                metrics.execution_gaps.append({
                    "document_id": r.document_id,
                    "record_id": r.record_id,
                })

        metrics.compute_rates()
        return metrics

    def _save_record(self, record: TrialExecutionRecord):
        """保存执行记录到磁盘。"""
        filepath = os.path.join(self.output_dir, f"{record.record_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)


__all__ = [
    "ControlledTrialRunner",
]