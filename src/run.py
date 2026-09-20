#!/usr/bin/env python3
"""
DICE 2.0 第一步入口：RAG + Guardrails + Human Gate，跑通 4 份 datasheet。

用法：
  python3 run.py                 # 交互模式（逐份 Human YES/NO 裁定）
  python3 run.py --no-interact    # 非交互（跳过 Human 裁定，verdict=PENDING）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline import run_all, save_results, summarize


def main():
    interactive = "--no-interact" not in sys.argv
    print(f"=== DICE 2.0 第一步：RAG + Guardrails + Human Gate ===")
    print(f"交互模式: {'Human YES/NO 裁定' if interactive else '非交互（verdict=PENDING）'}\n")

    results = run_all(interactive=interactive)

    out_path = save_results(results)
    summary = summarize(results)

    print(f"\n{'='*64}")
    print(f"第一步跑通完成，结果已保存: {out_path}")
    print(f"{'='*64}")
    print(f"文档数: {summary['docs']}")
    print(f"Guardrails 拦截总数: {summary['total_violations']}")
    print(f"Guardrails 警告总数: {summary['total_warnings']}")
    print(f"\n逐文档: ")
    for doc, s in summary['per_doc'].items():
        status = "✅ 通过" if s["passed"] else "❌ 有拦截"
        print(f"  {doc}: {status} (拦截 {s['violations']} / 警告 {s['warnings']}) "
              f"[温度 {s['storage_count']} / 组分 {s['component_count']} / 规格 {s['spec_count']}]")


if __name__ == "__main__":
    main()
