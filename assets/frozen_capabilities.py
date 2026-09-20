"""
DICE 1.0 冻结能力表 → DICE 2.0 L3 级高精准 Skill 定义。

来源：DICE 1.0 恢复区 capability_loader.py:65 FROZEN_CAPABILITY_TABLE（只读引用，
不修改、不回写）。在 DICE 2.0 中，这 22 条能力作为 L3 级 Skill：
一旦路由命中，直接走硬编码/SOP 提取，无需 LLM 推理（0 幻觉、低 token）。

红线：本文件是 DICE 1.0 冻结资产的**只读快照引用**，绝不在 dice2 里改写能力定义。
"""
from typing import Dict

# capability_id -> capability 名称（与 DICE 1.0 冻结表完全一致，逐字复制）
FROZEN_CAPABILITY_TABLE: Dict[str, str] = {
    "CAP-COMP-TABLE": "ComponentsTableUnderstanding",
    "CAP-STORAGE-DETECT": "StorageConditionsDetection",
    "CAP-SAFETY-DETECT": "SafetyWarningsDetection",
    "CAP-TROUBLESHOOT-DETECT": "TroubleshootingDetection",
    "CAP-PROCEDURE-DETECT": "ProcedureDetection",
    "CAP-PREP-MATERIALS-DETECT": "PrepMaterialsDetection",
    "CAP-TABLE-EXTRACT-BASIC": "BasicTableExtraction",
    "CAP-PARAMETER-LIST": "ParameterListExtraction",
    "CAP-STORAGE-LONG-TERM": "LongTermStorageDetection",
    "CAP-WARNING-EXTRACT": "WarningPhraseExtraction",
    "CAP-STEP-COUNTER": "StepCounter",
    "CAP-TEMP-RANGE": "TemperatureRangeExtraction",
    "CAP-TIME-EXTRACT": "TimeSpecExtraction",
    "CAP-CATALOG-EXTRACT": "CatalogNumberExtraction",
    "CAP-QUANTITY-VALIDATE": "QuantityConsistencyValidation",
    "CAP-UNIT-CONSISTENCY": "UnitConsistencyValidation",
    "CAP-TABLE-TYPE-CLASSIFY": "TableTypeClassification",
    "CAP-TABLE-COLLAPSE-RECONSTRUCT": "CollapsedTableReconstruction",
    "CAP-ANCHOR-EXTRACT": "AnchorDrivenExtraction",
    "CAP-COLUMNAR-EXTRACT": "ColumnarTextExtraction",
    "CAP-NAME-QTY-PAIR": "NameQuantityPairExtraction",
    "CAP-UNSPSC-MATCH": "UnspscProductClassificationMatching",
}

# 第一步直接用到的 L3 Skill 映射（datasheet 关键字段 → 冻结能力 id）
# 说明：这是"路由表"（Human 指定的静态映射，非自动学习），命中后走硬提取逻辑。
L3_SKILL_ROUTES = {
    "storage_temperature": "CAP-TEMP-RANGE",      # 储存温度范围提取
    "component_list": "CAP-NAME-QTY-PAIR",        # 组分名称-装量对提取
    "specification": "CAP-PARAMETER-LIST",        # 规格参数列表提取
}


def frozen_size() -> int:
    """冻结能力数量（应为 22，作为红线自检）。"""
    return len(FROZEN_CAPABILITY_TABLE)


if __name__ == "__main__":
    n = frozen_size()
    print(f"冻结能力表加载：{n} 条" + (" ✅" if n == 22 else " ❌ 应为 22"))
    for k, v in FROZEN_CAPABILITY_TABLE.items():
        print(f"  {k} = {v}")
