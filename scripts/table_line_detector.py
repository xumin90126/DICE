"""
行级表格检测（C1）：基于视觉行重建结果的表格识别。

背景：旧 detect_tables 基于 block 层"同一 y 多个不同 x 的 block"，只能处理
"每格一个 block"的表格（C216）；对"每列一个多行 block"的表格（RA101）完全漏检。
行级重建（layout_rebuilder）已把两类版式统一成"视觉行 = 同 y 的多 x 片段"，
因此表格检测也应迁移到行级。

保守判定（C1 版，防双栏正文误判）：
  - 逻辑表格行：同一视觉行的 x 片段数 ≥ 3（双栏正文只有 2 列，天然排除）
  - 或片段数 = 2 但其中一列是"值列"（数字/单位占主导，如 50 μl / 1.25 ml）
  - 连续 ≥ 2 个逻辑行 → 表格带
  - 列 x 位置跨行聚类成"列中心"
"""
from __future__ import annotations
import re
from typing import List, Tuple, Optional
from .layout_rebuilder import VLine

_VALUE_RE = re.compile(
    r"^(?:[\d.,\-−~≤≥<>×x()\[\]/μµml%°℃\s]+)$|"
    r"^(?:[\d.]+)\s*(?:μl|µl|ml|µg|mg|g|ng|U|kU|IU|rxns|units|×|bp|kb|kb|°C|℃|min|h|s|hr)\b",
    re.IGNORECASE,
)


def _cluster_xs(xs: List[float], tol: float = 8.0) -> List[float]:
    """一维 x0 聚类 → 列中心。"""
    if not xs:
        return []
    xs = sorted(xs)
    centers = []
    cur = [xs[0]]
    for x in xs[1:]:
        if x - cur[-1] <= tol:
            cur.append(x)
        else:
            centers.append(sum(cur) / len(cur))
            cur = [x]
    if cur:
        centers.append(sum(cur) / len(cur))
    return centers


def _is_value_text(t: str) -> bool:
    t = t.strip()
    if not t or len(t) > 40:
        return False
    return bool(_VALUE_RE.match(t))


def group_lines_into_rows(lines: List[VLine], y_tol: float = 3.0) -> List[List[VLine]]:
    """
    把视觉行聚成"逻辑表格行"：同 y 的多 x 片段 = 一行多列。
    y_tol 内同组（容忍跨片段 1-2pt 的 y 抖动）。
    """
    if not lines:
        return []
    ordered = sorted(lines, key=lambda v: (v.y0, v.x0))
    rows: List[List[VLine]] = []
    cur: List[VLine] = []
    cur_y = None
    for v in ordered:
        if cur_y is None:
            cur_y = v.y0
            cur = [v]
            continue
        if abs(v.y0 - cur_y) <= y_tol:
            cur.append(v)
        else:
            rows.append(cur)
            cur = [v]
            cur_y = v.y0
    if cur:
        rows.append(cur)
    # 行内按 x0 排序
    for r in rows:
        r.sort(key=lambda v: v.x0)
    return rows


_MATH_CHARS = set("αβγδεζηθλμπρστφχψωΓΔΘΛΞΠΣΦΨΩ∂∇∑∏√∫≈≠≤≥±−×∞→ℓ∗ϕκνξο")


def _is_math_fragment(t: str) -> bool:
    """判断一个文本片段是否是数学公式碎片（区别于表格单元格文本）。"""
    t = t.strip()
    if not t:
        return False
    # 含 PDF 数学字形控制字符
    if any(ord(c) < 32 for c in t):
        return True
    # 纯单字符符号
    if len(t) <= 2 and (t[0] in _MATH_CHARS or t in {"=", ",", "−", "+", "1", "2", "z", "K", "s", "ℓ"}):
        return True
    # 短串且数学符号占主导
    if len(t) <= 4:
        m = sum(1 for c in t if c in _MATH_CHARS or c.isdigit())
        if m >= max(1, len(t) // 2):
            return True
    return False


def _is_text_cell(t: str) -> bool:
    """正常表格单元格文本（词/数值+单位），非公式碎片。"""
    t = t.strip()
    if not t or len(t) < 3:
        return False
    return not _is_math_fragment(t)


def detect_tables_from_lines(lines: List[VLine], page_width: float,
                             min_rows: int = 3, col_gap: float = 12.0) -> Tuple[List[dict], List[VLine]]:
    """
    行级表格检测。

    判定原则（防公式/目录误判）：
      1. 候选"逻辑表格行"：同 y 行内 x 片段间隙 ≥ col_gap（多列外观）
      2. 连续候选行 ≥ min_rows 且行距连续 → 潜在表格带
      3. **列稳定校验**：对潜在带做跨行列中心聚类，要求多数行(≥70%)的片段
         能对齐到稳定列中心 —— 公式行片段零散、列不稳定，会被此步拒绝
      4. **文本性校验**：带内需有足够"文本型单元格"，纯数学符号区拒绝

    Returns:
        (table_elements, non_table_lines)
    """
    if not lines:
        return [], []
    rows = group_lines_into_rows(lines)

    # 候选多列行：行内片段间有明显 x 间隙
    def is_multicol(r):
        if len(r) < 2:
            return False
        gaps = [r[i + 1].x0 - r[i].x1 for i in range(len(r) - 1)]
        return sum(1 for g in gaps if g >= col_gap) >= 1

    # 扫描潜在表格带：核心 = ≥3 连续"真多列行"；带内允许夹短窄单列行(BOX 标签等)
    # 断带条件：遇到 宽正文行(单列且宽度>0.35页宽 且行距突跳)
    def is_short_single(r):
        """单片段短窄行（BOX/分组标签等）。"""
        if len(r) != 1:
            return False
        v = r[0]
        return v.width <= page_width * 0.40 and len(v.text.strip()) <= 40

    def is_wide_text(r):
        """宽正文行：单片段且宽大文本 → 必不是表格行。"""
        if len(r) != 1:
            return False
        v = r[0]
        return v.width > page_width * 0.40 and len(v.text.strip()) > 40

    bands = []
    cur = []          # (row_index, is_anchor)
    anchor_count = 0
    for i, r in enumerate(rows):
        if is_multicol(r):
            cur.append((i, True))
            anchor_count += 1
        elif is_wide_text(r):
            if anchor_count >= 3 and len(cur) >= 3:
                bands.append([idx for idx, _ in cur])
            cur = []
            anchor_count = 0
        else:
            # 短窄行：仅当带内已有多列锚点时并入
            if cur:
                cur.append((i, False))
            # 带未开始则不启动
    if cur and anchor_count >= 3 and len(cur) >= 3:
        bands.append([idx for idx, _ in cur])

    # 列稳定校验 + 建表
    table_lines_used = set()
    tables = []
    for idxs in bands:
        band = [rows[i] for i in idxs]
        # 列中心：仅从"真多列锚点行"的片段取 x0 聚类
        anchor_rows = [rows[i] for i in idxs if len(rows[i]) >= 2]
        all_xs = [v.x0 for r in anchor_rows for v in r]
        col_centers = _cluster_xs(all_xs, tol=10.0)
        if len(col_centers) < 2:
            continue
        # 列稳定校验：锚点行片段 x0 距最近列中心 ≤16pt 的比例
        # （用 x0 而非中点——宽单元格中点会远离列中心）
        def row_align(r):
            if not r:
                return 0.0
            hit = 0
            for v in r:
                if min(abs(c - v.x0) for c in col_centers) <= 16.0:
                    hit += 1
            return hit / len(r)
        aligns = [row_align(r) for r in anchor_rows]
        if not aligns or sum(aligns) / len(aligns) < 0.75:
            continue  # 列不稳定（公式等）→ 拒绝为表格

        # 文本性校验：带内所有单元格文本中，"文本型"须占多数，纯公式区拒绝
        all_cells = [v.text for r in band for v in r]
        if all_cells:
            text_ratio = sum(1 for t in all_cells if _is_text_cell(t)) / len(all_cells)
            if text_ratio < 0.45:
                continue  # 纯数学符号区（公式）→ 拒绝为表格


        # 表头吸收：带上方紧邻行，若 x0 落列范围或文本短且 y 连续 → 并入表格
        # （RA101 型：表头 'Components'/'RA101-01' 是独立短行，y 在数据行上方）
        head_rows = []
        if idxs[0] > 0:
            k = idxs[0] - 1
            taken = 0
            top_y = min(rows[i][0].y0 for i in idxs)
            while k >= 0 and taken < 3:
                r = rows[k]
                y0 = r[0].y0
                h = max(r[0].height, 5)
                if top_y - y0 > h * 2.6:
                    break
                txt_all = " ".join(v.text for v in r).strip()
                # 需与带相关的候选表头：短文本 或 x0 落在列范围内；
                # 排除句子型文本（含逗号/长句 = 正文，如 'Second, D'Ambrosio'）
                rx0 = min(v.x0 for v in r)
                rx1 = max(v.x1 for v in r)
                col_lo = min(col_centers) - 20
                col_hi = max(col_centers) + 20
                relates = (rx1 >= col_lo and rx0 <= col_hi)
                sentencish = "," in txt_all or (len(txt_all) > 24 and " " in txt_all)
                if relates and not sentencish and len(txt_all) < 90 and len(r) <= 2:
                    head_rows.append(r)
                    taken += 1
                    k -= 1
                else:
                    break
            if head_rows:
                head_rows.reverse()
        all_rows = head_rows + band

        def row_cells(r):
            col_parts = {c: [] for c in col_centers}
            for v in r:
                best = min(col_centers, key=lambda c: abs(c - v.x0))
                col_parts[best].append(v.text.strip())
            return [" ".join(col_parts[cx]).strip() if col_parts[cx] else ""
                    for cx in col_centers]

        grid = [row_cells(r) for r in all_rows]
        if not grid:
            continue
        header = grid[0]
        data_rows = grid[1:]
        b_x0 = min(v.x0 for r in all_rows for v in r)
        b_x1 = max(v.x1 for r in all_rows for v in r)
        b_y0 = min(r[0].y0 for r in all_rows)
        b_y1 = max(r[-1].y1 for r in all_rows)

        tables.append({
            "type": "table",
            "headers": header,
            "rows": data_rows,
            "y": b_y0,
            "page": rows[idxs[0]][0].page,
            "bbox": [round(b_x0, 1), round(b_y0, 1), round(b_x1, 1), round(b_y1, 1)],
        })
        for i in idxs:
            for v in rows[i]:
                table_lines_used.add(id(v))

    non_table = [v for v in lines if id(v) not in table_lines_used]
    return tables, non_table
