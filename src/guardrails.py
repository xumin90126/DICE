"""
DICE 2.0 — Guardrails 程序断言层。

挂载在 LLM 输出之后、Human Gate 之前。用确定性程序校验（Pydantic + 正则 +
原文匹配）自动拦截"低级错误"，不把找错压力交给人类。

四条硬规则（Human 指定的"最不能容忍的低级错误"清单）：
  G1 数值与单位缺失  —— 数值必须带明确单位，严禁孤立数字
  G2 原文归因断言     —— 每个结构化字段必须有 source_quote，且能在原文中定位
  G3 关键规格空值     —— 关键字段（温度/组分/规格）为空或 N/A 触发断言警告
  G4 格式合规性       —— 范围值必须解析为 [min, max]，不允许"约/左右"等模糊描述

设计原则：Guardrails 只做「确定性事实校验」，不做语义判断。命中规则就拦/警告，
不命中就放行。它不替代 Human 裁定（Human Gate 仍是最终 YES/NO）。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .schemas import Component, ExtractionResult, Specification, StorageCondition

# ── 允许的单位词表（G1 用）──
KNOWN_UNITS = [
    "°c", "℃", "c", "ph", "mg/ml", "μg/ml", "ng/μl", "μg/μl", "mg", "μg", "g",
    "ml", "μl", "µl", "ul", "%", "mm", "cm", "m", "nm", "μm", "µm", "um",
    "kda", "da", "nt", "bp", "kb", "mm", "rpm", "ma", "v", "h", "min", "sec",
    "t", "rxns", "×", "x", "mw",
]

# ── 模糊描述词（G4 用，禁止出现在温度范围/数值里）──
# 注意：不含 "~"，因为 "~" 在 datasheet 里是合法范围符号（15 ~ 25°C = 15 到 25）
VAGUE_WORDS = ["约", "左右", "大约", "大概", "约为", "about", "approximately", "approx"]

# ── N/A 变体（G3 用）──
NA_VARIANTS = ["", "n/a", "na", "null", "none", "无", "空"]

# ── 计数量词（G1 用：无量纲计数，单位隐含在字段名里，不需物理单位）──
# 例：Post-PCR Cycles 9（循环次数）、Binding Plate 1（板数）、1 tube（支数）
COUNT_WORDS = [
    "cycle", "cycles", "plate", "tube", "well", "pcs", "piece", "bottle",
    "vial", "strip", "column", "孔", "支", "瓶", "块", "板", "片", "盒", "袋",
    "次", "轮", "孔板", "份",
]


def _normalize(text: str) -> str:
    """归一化：去所有空白 + 小写（保留字母数字和标点，用于子串定位）。"""
    if not text:
        return ""
    return re.sub(r"\s+", "", text).lower()


@dataclass
class GuardrailViolation:
    """一条断言违规记录（纯事实，非行动）。"""

    rule_id: str          # G1/G2/G3/G4
    field: str            # 违规字段定位
    severity: str         # "block"（拦截）/ "warn"（警告）
    message: str          # 事实说明

    def to_dict(self) -> dict:
        return {"rule_id": self.rule_id, "field": self.field,
                "severity": self.severity, "message": self.message}


@dataclass
class GuardrailsResult:
    """Guardrails 校验结果。"""

    passed: bool = True                  # 无 block 级违规
    violations: List[GuardrailViolation] = field(default_factory=list)   # block 级
    warnings: List[GuardrailViolation] = field(default_factory=list)     # warn 级

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": [w.to_dict() for w in self.warnings],
        }


# ─────────────────────────────────────────────────────────────────────────
# G2 原文归因：source_quote 必须在原文中能定位
# ─────────────────────────────────────────────────────────────────────────
def _source_grounded(source_quote: str, source_text: str,
                     min_tokens: int = 2, match_ratio: float = 0.8) -> bool:
    """
    判断 source_quote 是否能在原文中定位。

    两级匹配：
      1. 精确连续匹配：归一化后 source_quote 是原文的连续子串（最严格）
      2. token 级匹配：把 source_quote 拆成 token，≥match_ratio 比例的 token
         能在原文中定位（容忍表格跨行/跨列导致的拼凑归因）

    设计意图：G2 拦截「幻觉引用」（编造的、原文没有的内容），但不误拦
    「表格内容拼凑」（LLM 正确理解了表格结构，把分列的名称+装量拼成一段）。
    """
    q_norm = _normalize(source_quote)
    t_norm = _normalize(source_text)
    if not q_norm:
        return False

    # 1. 精确连续匹配
    if q_norm in t_norm:
        return True

    # 2. token 级匹配（容忍跨行/跨列拼凑）
    tokens = [t for t in re.findall(r"\S+", source_quote.strip())
              if len(_normalize(t)) >= 2]
    if len(tokens) < min_tokens:
        return False
    matched = sum(1 for tok in tokens if _normalize(tok) in t_norm)
    return matched >= max(min_tokens, int(len(tokens) * match_ratio))


# ─────────────────────────────────────────────────────────────────────────
# G1 数值单位：数值必须带单位（物理量），无量纲计数豁免
# ─────────────────────────────────────────────────────────────────────────
def _has_unit(value: str, unit: str, context: str = "") -> bool:
    """
    判断数值是否带单位。三种情况视为「有单位」：
      1. unit 字段非空
      2. value 本身含已知单位词
      3. context（字段名）含计数量词（循环/板/支/瓶等，无量纲计数，单位隐含在名称里）
    """
    if unit and unit.strip().lower() not in NA_VARIANTS:
        return True
    v = value.strip().lower()
    for u in KNOWN_UNITS:
        if u in v:
            return True
    ctx = context.lower()
    if any(w in ctx for w in COUNT_WORDS):
        return True
    # 纯数字（无任何单位）→ 无单位
    return not bool(re.fullmatch(r"[\d.]+", value.strip()))


# ─────────────────────────────────────────────────────────────────────────
# G4 格式合规：范围值 [min, max]，不允许模糊描述
# ─────────────────────────────────────────────────────────────────────────
def _vague_range(text: str) -> bool:
    """检查文本是否含模糊描述词（约/左右/about 等）。"""
    t = text.lower()
    return any(w in t for w in VAGUE_WORDS)


# ─────────────────────────────────────────────────────────────────────────
# 主校验入口
# ─────────────────────────────────────────────────────────────────────────
def validate(result: ExtractionResult, source_text: str) -> GuardrailsResult:
    """
    对一份提取结果执行 4 条 Guardrails 断言。

    Args:
        result:      LLM 结构化输出（Pydantic 模型）
        source_text: 原始文档全文（用于 G2 原文归因定位）

    Returns:
        GuardrailsResult（passed + violations + warnings）
    """
    gr = GuardrailsResult()

    # ── G3 关键空值：温度/组分整体为空 → warn ──
    if not result.storage_conditions:
        gr.warnings.append(GuardrailViolation(
            "G3", "storage_conditions", "warn",
            "未提取到任何储存温度条件（关键字段为空）"))
    if not result.components:
        gr.warnings.append(GuardrailViolation(
            "G3", "components", "warn",
            "未提取到任何组分（关键字段为空）"))

    # ── 逐字段校验 ──
    _check_storage(result.storage_conditions, source_text, gr)
    _check_components(result.components, source_text, gr)
    _check_specifications(result.specifications, source_text, gr)

    gr.passed = len(gr.violations) == 0
    return gr


def _check_storage(conds: List[StorageCondition], src: str, gr: GuardrailsResult) -> None:
    for i, c in enumerate(conds):
        loc = f"storage_conditions[{i}]"
        # G2 原文归因（block）
        if not _source_grounded(c.source_quote, src):
            gr.violations.append(GuardrailViolation(
                "G2", loc, "block",
                f"source_quote 无法在原文定位: {c.source_quote[:40]!r}"))
        # G4 模糊描述（block）
        if _vague_range(c.condition_text):
            gr.violations.append(GuardrailViolation(
                "G4", loc, "block",
                f"温度范围含模糊描述: {c.condition_text!r}"))
        # G4 范围未解析为数值（block：min/max 都空）
        if c.min_temp is None and c.max_temp is None:
            gr.violations.append(GuardrailViolation(
                "G4", loc, "block",
                f"温度范围未解析为 [min, max]: {c.condition_text!r}"))
        # G1 单位（block）
        if (c.min_temp is not None or c.max_temp is not None) and not c.unit:
            gr.violations.append(GuardrailViolation(
                "G1", loc, "block",
                "温度数值缺少单位（unit 为空）"))


def _check_components(comps: List[Component], src: str, gr: GuardrailsResult) -> None:
    for i, c in enumerate(comps):
        loc = f"components[{i}]"
        # G3 组分名称空（warn）
        if not c.name or c.name.strip().lower() in NA_VARIANTS:
            gr.warnings.append(GuardrailViolation(
                "G3", loc, "warn", "组分名称为空或 N/A"))
        # G2 原文归因（block）
        if not _source_grounded(c.source_quote, src):
            gr.violations.append(GuardrailViolation(
                "G2", loc, "block",
                f"source_quote 无法在原文定位: {c.source_quote[:40]!r}"))
        # G1 数值单位（block：有数量但无单位，且非计数量词）
        if c.quantity and not _has_unit(c.quantity, c.unit, c.name):
            gr.violations.append(GuardrailViolation(
                "G1", loc, "block",
                f"组分数量缺少单位: {c.quantity!r} unit={c.unit!r}"))


def _check_specifications(specs: List[Specification], src: str, gr: GuardrailsResult) -> None:
    for i, s in enumerate(specs):
        loc = f"specifications[{i}]"
        # G2 原文归因（block）
        if not _source_grounded(s.source_quote, src):
            gr.violations.append(GuardrailViolation(
                "G2", loc, "block",
                f"source_quote 无法在原文定位: {s.source_quote[:40]!r}"))
        # G1 数值单位（block：有值但无单位，且非计数量词）
        if s.value and not _has_unit(s.value, s.unit, s.parameter):
            gr.violations.append(GuardrailViolation(
                "G1", loc, "block",
                f"规格数值缺少单位: {s.value!r} unit={s.unit!r}"))
