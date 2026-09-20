"""
Phase 4.1.5 Matching Layer Audit Script
=======================================
Scans all relevant files for hidden rule-based regression:
1. Hardcoded routing patterns (doc_class, product_id, filename, capability_id)
2. Pattern-specific if/else branches
3. Legacy handler bypass detection
"""
import re
import os
import json

BASE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "matching": os.path.join(BASE, "dice", "runtime", "matching.py"),
    "ranking": os.path.join(BASE, "dice", "runtime", "ranking.py"),
    "executor": os.path.join(BASE, "dice", "runtime", "executor.py"),
    "nodes": os.path.join(BASE, "dice", "graph", "nodes.py"),
    "selector": os.path.join(BASE, "dice", "runtime", "selector.py"),
}

# ── Forbidden patterns: hardcoded routing ──
ROUTING_PATTERNS = [
    (r'doc_class\s*==', "doc_class equality check"),
    (r'product_id\s*==', "product_id equality check"),
    (r'filename\s*==', "filename equality check"),
    (r'\.doc_class\b', ".doc_class attribute access (routing)"),
    (r'document_class\b.*==', "document_class routing"),
    (r'\bdoc_type\b', "doc_type variable"),
    (r'is_(plasmid|ngs|antibody|extraction|library|purification)\b', "domain-specific boolean"),
]

# ── Forbidden patterns: capability_id hardcoding ──
CAPABILITY_HARDCODE = [
    (r'if\s+capability_id\s*==\s*"', "hardcoded capability_id routing"),
    (r'if\s+capability_id\s*==\s*\'', "hardcoded capability_id routing (single-quote)"),
    (r'capability_id\s*==\s*"CAP-', "CAP- prefixed hardcoding"),
]

# ── Forbidden patterns: pattern-specific if/else ──
PATTERN_HARDCODE = [
    (r'if\s+pattern\.id\s*==\s*"', "hardcoded pattern_id routing"),
    (r'if\s+pattern\.id\s*==\s*\'', "hardcoded pattern_id routing (single-quote)"),
    (r'pattern\.id\s*==\s*"PAT-', "PAT- prefixed hardcoding"),
]

# ── All patterns ──
ALL_PATTERNS = ROUTING_PATTERNS + CAPABILITY_HARDCODE + PATTERN_HARDCODE


def scan_file(filepath: str, label: str) -> dict:
    """Scan a single file for all forbidden patterns."""
    if not os.path.exists(filepath):
        return {"file": label, "status": "NOT_FOUND", "violations": []}

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        content = f.read()
        f.seek(0)
        lines_for_context = lines

    # Phase 1: detect docstring regions to exclude
    in_docstring = False
    docstring_lines = set()
    for i, line in enumerate(lines_for_context):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if in_docstring:
                docstring_lines.add(i)  # closing line
                in_docstring = False
            else:
                docstring_lines.add(i)  # opening line
                # Check if single-line docstring
                count = stripped.count('"""') + stripped.count("'''")
                if count < 2:
                    in_docstring = True
        elif in_docstring:
            docstring_lines.add(i)

    violations = []

    for pattern, description in ALL_PATTERNS:
        for i, line in enumerate(lines_for_context, 1):
            match = re.search(pattern, line)
            if match:
                idx = i - 1
                stripped = line.strip()

                # Exclude docstrings
                if idx in docstring_lines:
                    continue
                # Exclude comments
                if stripped.startswith("#"):
                    continue
                # Exclude mentions of audit/forbidden in context
                if "ZERO doc_class" in stripped or "NO doc_class" in stripped:
                    continue
                if "forbidden" in stripped.lower() or "audit" in stripped.lower():
                    continue

                violations.append({
                    "line": i,
                    "pattern": description,
                    "content": stripped[:120],
                })

    return {
        "file": label,
        "path": filepath,
        "total_lines": len(lines_for_context),
        "violation_count": len(violations),
        "violations": violations,
        "status": "CLEAN" if len(violations) == 0 else "VIOLATIONS_FOUND",
    }


def main():
    results = []
    for label, path in FILES.items():
        result = scan_file(path, label)
        results.append(result)

    # ── Summary ──
    total_violations = sum(r["violation_count"] for r in results)
    clean = [r for r in results if r["status"] == "CLEAN"]
    dirty = [r for r in results if r["status"] == "VIOLATIONS_FOUND"]

    print("=" * 70)
    print("  PHASE 4.1.5 — ZERO HARDCODED ROUTING AUDIT")
    print("=" * 70)

    for r in results:
        icon = "✅" if r["status"] == "CLEAN" else "❌"
        print(f"\n  {icon} {r['file']}.py ({r['total_lines']} lines) — {r['status']}")
        for v in r["violations"]:
            print(f"     L{v['line']:4d} | {v['pattern']}")
            print(f"            | {v['content']}")

    print("\n" + "=" * 70)
    print(f"  SUMMARY: {len(clean)}/{len(results)} clean, {total_violations} violations")
    print("=" * 70)

    if total_violations > 0:
        print("\n  ⚠️  Violations classified:")
        for r in dirty:
            for v in r["violations"]:
                pat = v["pattern"]
                if "capability_id" in pat:
                    cat = "CAPABILITY_ID_HARDCODE (→ Phase 4.2 Runtime will eliminate)"
                elif "pattern.id" in pat or "PAT-" in pat:
                    cat = "PATTERN_ID_HARDCODE (→ Phase 4.1 REMEDIATION)"
                elif "doc_class" in pat or "product_id" in pat or "filename" in pat:
                    cat = "DOC_CLASS_ROUTING (→ CRITICAL: must eliminate immediately)"
                else:
                    cat = "OTHER"
                print(f"     L{v['line']:4d} [{r['file']}.py] → {cat}")

    # Export JSON
    output_path = os.path.join(BASE, "audit_phase4_1_5.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "audit": "Phase 4.1.5 Zero Hardcoded Routing",
            "total_violations": total_violations,
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n  📄 Full report: {output_path}")

    return 0 if total_violations == 0 else 1


if __name__ == "__main__":
    exit(main())
