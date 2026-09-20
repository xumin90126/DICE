"""
C1：词/行级重建 + 段落合并（layout_rebuilder）

问题：原 merge_paragraphs 基于 PyMuPDF block 级文本。目标 PDF 每行一个 block，
且 ▲/◇ 与正文同 y 不同 x 被拆到不同 block → block 级合并必碎。

方案：完全绕过 block 分组，用 PyMuPDF "dict" 的 line 层按 y 重新聚类：
  1. 平铺所有 line（含 bbox/字号），按 y0 聚类成"视觉行"，组内按 x0 排序；
     同 y 出现大空隙（双栏/表格列）→ 拆成独立行（防左右栏拼一起）
  2. 视觉行按规则合并段落：行距连续性 + 自适应栏宽 + 缩进续行
  3. 页眉页脚/页码/目录点线清洗（可开关，被删行保留返回供 UI）

输出兼容原 merge_paragraphs：[{"type":"paragraph","text":..,"y":..}]
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple


class VLine:
    """一个视觉行（可能由多个 PDF line 拼成）。"""
    __slots__ = ("x0", "y0", "x1", "y1", "text", "size", "fragments", "page")
    def __init__(self, x0, y0, x1, y1, text, size, fragments, page):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.text, self.size, self.fragments, self.page = text, size, fragments, page
    @property
    def width(self):
        return self.x1 - self.x0
    @property
    def height(self):
        return self.y1 - self.y0
    def __repr__(self):
        return f"<VLine y={self.y0:.0f} x=[{self.x0:.0f},{self.x1:.0f}] sz={self.size:.1f} {self.text[:40]!r}>"


# 页眉页脚/页码等静态噪声
_FOOTER_STATIC = {
    "Version 26.1", "Version 25.1", "Version 24.1", "Version 23.1", "Version 22.1",
    "For Research Use Only. Not for use in diagnostic procedures.",
}
_PAGE_NO_RE = re.compile(r"^[-—–·.]?\s*\d+\s*[-—–·.]?$")
_ROMAN_RE = re.compile(r"^[IVXLC]{1,8}\.?$")
_DOTS_RE = re.compile(r"\.{4,}")


def _line_key(line) -> Tuple[float, float]:
    if "bbox" in line:
        bbox = line["bbox"]
    else:
        bbox = (line["x0"], line["y0"], line["x1"], line["y1"])
    return (round(bbox[1], 1), round(bbox[0], 1))


def _line_metrics(line):
    """提取 line 的 bbox/文本/字号。"""
    bbox = line["bbox"]
    x0, y0, x1, y1 = bbox
    parts = []
    max_size = 0.0
    for span in line["spans"]:
        t = span["text"]
        if t:
            parts.append(t)
            max_size = max(max_size, span["size"])
    if not parts:
        return None
    return {
        "x0": x0, "y0": y0, "x1": x1, "y1": y1,
        "text": "".join(parts),
        "size": max_size,
    }


def extract_flat_lines(page):
    """平铺页面所有文本 line（dict 层），返回指标列表。"""
    out = []
    try:
        data = page.get_text("dict")
    except Exception:
        return out
    for b in data.get("blocks", []):
        if "lines" not in b:
            continue
        for line in b["lines"]:
            m = _line_metrics(line)
            if m:
                out.append(m)
    return out


def cluster_to_visual_lines(lines, y_tol=3.5, col_gap=30.0):
    """
    把平铺 line 聚合成视觉行。
    - 按 y0 贪心聚类（容差 y_tol，标题大字自动放宽：tol 与行高挂钩）
    - 组内按 x0 排序；相邻 gap > col_gap 且右片段不短 → 视为独立行（双栏/列）
    """
    if not lines:
        return []
    lines = sorted(lines, key=_line_key)
    groups = []
    cur = []
    for m in lines:
        if not cur:
            cur = [m]
            continue
        base_y = sorted(x["y0"] for x in cur)[len(cur) // 2]
        # 容差：普通文本 3.5，大字号标题放宽
        tol = y_tol
        if m["size"] >= 14 or any(x["size"] >= 14 for x in cur):
            tol = max(y_tol, 0.5 * m["size"])
        if abs(m["y0"] - base_y) <= tol:
            cur.append(m)
        else:
            groups.append(cur)
            cur = [m]
    if cur:
        groups.append(cur)

    vis = []
    for g in groups:
        g.sort(key=lambda m: m["x0"])
        # 拆列：相邻片段间隙大 → 不同栏（仅当两侧都非极短残行）
        pieces = []
        piece = [g[0]]
        for m in g[1:]:
            prev = piece[-1]
            gap = m["x0"] - prev["x1"]
            avg_sz = (m["size"] + prev["size"]) / 2
            if gap > col_gap and prev["size"] >= 6 and m["size"] >= 6:
                pieces.append(piece)
                piece = [m]
            else:
                piece.append(m)
        pieces.append(piece)

        for p in pieces:
            x0 = min(m["x0"] for m in p)
            y0 = min(m["y0"] for m in p)
            x1 = max(m["x1"] for m in p)
            y1 = max(m["y1"] for m in p)
            text = "".join(m["text"] for m in p).strip()
            if not text:
                continue
            size = max(m["size"] for m in p)
            vis.append(VLine(x0, y0, x1, y1, text, size, p, None))
    return vis


def _is_noise_line(l: VLine) -> bool:
    """静态噪声行判定：页脚固定串、纯页码、罗马数字、纯点线。"""
    t = l.text.strip()
    if not t:
        return True
    if t in _FOOTER_STATIC:
        return True
    if _PAGE_NO_RE.match(t) and len(t) < 10:
        return True
    if _ROMAN_RE.match(t):
        return True
    if _DOTS_RE.search(t) and len(re.sub(r"[.\s]", "", t)) < 4:
        return True
    return False


def rebuild_page_lines(page, exclude_bboxes=None, y_tol=3.5, col_gap=30.0):
    """
    重建一页的视觉行。exclude_bboxes = 表格/图片区域 [(x0,y0,x1,y1),...]，
    落在其内的 line 剔除（它们是表格单元格/图内标签，不是正文段落）。
    """
    lines = extract_flat_lines(page)
    if exclude_bboxes:
        keep = []
        for m in lines:
            cx = (m["x0"] + m["x1"]) / 2
            cy = (m["y0"] + m["y1"]) / 2
            inside = False
            for x0, y0, x1, y1 in exclude_bboxes:
                if x0 - 3 <= cx <= x1 + 3 and y0 - 3 <= cy <= y1 + 3:
                    inside = True
                    break
            if not inside:
                keep.append(m)
        lines = keep
    vis = cluster_to_visual_lines(lines, y_tol=y_tol, col_gap=col_gap)
    for i, v in enumerate(vis):
        v.page = page.number if hasattr(page, "number") else None
    return vis


def split_body_noise(vis_lines: List[VLine], page_height: float,
                     doc_repeats=None) -> Tuple[List[VLine], List[VLine]]:
    """
    正文行 vs 噪声行分离（不删除，返回两组，噪声组可供 UI 展示或丢弃）。
    规则：
      1. 静态串/页码/点线 → 噪声
      2. 页边几何带：页面最顶/最底文本块且落在 6%/12% 边带内、行高小、非大字号 → 噪声
      3. 跨页重复（doc_repeats: {归一化文本: 出现页数}，出现 ≥ max(3, 40%总页) → 噪声）
    """
    if not vis_lines:
        return [], []
    body, noise = [], []
    top_band = page_height * 0.06
    bot_band = page_height * 0.12
    n_pages = (doc_repeats or {}).get("_total", 1)

    for i, l in enumerate(vis_lines):
        t = l.text.strip()
        if _is_noise_line(l):
            noise.append(l)
            continue
        is_top = (l is vis_lines[0] or l.y0 <= min(v.y0 for v in vis_lines) + 1)
        is_bot = (l is vis_lines[-1] or l.y1 >= max(v.y1 for v in vis_lines) - 1)
        small = l.height <= page_height * 0.045 and l.size < 13
        if is_top and l.y1 <= top_band and small and len(t) < 120:
            noise.append(l)
            continue
        if is_bot and l.y0 >= page_height - bot_band and small and len(t) < 120:
            noise.append(l)
            continue
        if doc_repeats and l.size < 13 and len(t) < 90:
            key = re.sub(r"\d+", "@", t)
            freq = doc_repeats.get(key, 0)
            if freq >= max(3, n_pages * 0.4):
                noise.append(l)
                continue
        body.append(l)
    return body, noise


_MATH_SYM = set("αβγδεζηθλμπρστφχψωΓΔΘΛΞΠΣΦΨΩ∂∇∑∏√∫≈≠≤≥±−×∞→ℓ∗ϕκνξο∈⊂⊃∪∩≤≥·∙")
_MATH_CTRL = set("\x00\x01\x02\x03\x04\x0c\x0d\x13\x14\x15\x1f")


def _math_density(t: str) -> float:
    """文本中数学特征字符（含控制字符、希腊字母等）占比。"""
    if not t:
        return 0.0
    n = sum(1 for c in t if c in _MATH_SYM or c in _MATH_CTRL or c.isdigit())
    return n / len(t)


def _is_formula_line(l: VLine, page_width: float, body_left: float) -> bool:
    """疑似 display 公式行：居中(远离正文左缘) + 短窄 + 数学/数字密集。"""
    t = l.text.strip()
    if not t or len(t) > 120:
        return False
    if l.width > page_width * 0.75:
        return False
    centered = (l.x0 - body_left) > page_width * 0.08
    dense = _math_density(t) >= 0.30
    return centered and dense


def _body_left_estimate(lines: List[VLine]) -> float:
    """正文左缘估计：行 x0 的众数附近（30 分位）。"""
    if not lines:
        return 0.0
    xs0 = sorted(v.x0 for v in lines)
    return xs0[int(len(xs0) * 0.30)]


def stitch_formula_lines(lines: List[VLine], page_width: float) -> List[VLine]:
    """
    公式区缝合：连续居中/数学密集短行合并为一个视觉行（作为独立段落源），
    解决 display 公式被逐行拆碎的问题。返回新行列表（非公式行原样保留）。
    判定谨慎：仅当行序列均为公式特征行时才缝合，避免误并文本。
    """
    if not lines:
        return lines
    body_left = _body_left_estimate(lines)
    runs = []
    cur = []
    for l in lines:
        if _is_formula_line(l, page_width, body_left):
            cur.append(l)
        else:
            if cur:
                runs.append(cur)
                cur = []
    if cur:
        runs.append(cur)

    kept = []
    used = set()
    for run in runs:
        if len(run) < 2:
            continue  # 单行不缝（留给常规段落逻辑）
        # 缝合成一个新 VLine（取 y0 均值? 用首行 y0，文本 join）
        merged = VLine(
            x0=run[0].x0, y0=min(v.y0 for v in run),
            x1=max(v.x1 for v in run), y1=max(v.y1 for v in run),
            text=" ".join(v.text for v in run).strip(),
            size=max(v.size for v in run),
            fragments=[f for v in run for f in v.fragments],
            page=run[0].page,
        )
        kept.append(merged)
        for v in run:
            used.add(id(v))
    result = [v for v in lines if id(v) not in used]
    # 结果保持 y 顺序（缝合行与原行混排，按 y0 排序）
    kept.extend(result)
    kept.sort(key=lambda v: v.y0)
    return kept


def merge_paragraphs_from_lines(body_lines: List[VLine], page_width: float,
                                width_ratio: float = 0.80,
                                gap_tol: float = 2.5,
                                col_right: Optional[float] = None) -> List[dict]:
    """
    视觉行 → 段落。
    软换行（续行）条件需同时满足：
      a) 上一行填满：width ≥ 该行可用宽 × width_ratio（可用宽 = 正文右缘 - 该行左缘）
      b) 行距连续：gap 与上次 gap 差 ≤ gap_tol 或 gap ≤ 1.7×行高
      c) 不缩回段落起点左边（允许续行右缩进，不允许回退更左 = 新段）
    col_right: 该栏右缘（双栏页传入栏边界避免跨栏合并）；默认取本组行 x1 的 92 分位。
    """
    if not body_lines:
        return []
    # 正文右缘估计：行 x1 的 90 分位
    if col_right is None:
        xs1 = sorted(l.x1 for l in body_lines)
        col_right = xs1[int(len(xs1) * 0.92)] if xs1 else page_width

    paragraphs = []
    cur_text, cur_y, cur_x0 = [], None, None
    prev = None
    prev_gap = None

    for l in body_lines:
        if prev is None:
            cur_text, cur_y, cur_x0 = [l.text], l.y0, l.x0
            prev = l
            continue
        gap = l.y0 - prev.y0
        line_h = max(prev.height, 1.0)
        usable = max(col_right - prev.x0, 1.0)
        prev_filled = prev.width >= usable * width_ratio

        gap_ok = True
        if prev_gap is not None:
            gap_ok = (abs(gap - prev_gap) <= gap_tol or gap <= line_h * 1.9)
        elif gap > line_h * 2.3:
            gap_ok = False
        indent_ok = (cur_x0 is not None and l.x0 >= cur_x0 - 3.0)

        if prev_filled and gap_ok and indent_ok:
            cur_text.append(l.text)
        else:
            paragraphs.append({"type": "paragraph",
                               "text": " ".join(cur_text).strip(), "y": cur_y})
            cur_text, cur_y, cur_x0 = [l.text], l.y0, l.x0
        prev_gap = gap
        prev = l

    if cur_text:
        paragraphs.append({"type": "paragraph",
                           "text": " ".join(cur_text).strip(), "y": cur_y})
    return [p for p in paragraphs if p["text"]]


def collect_doc_repeats(doc) -> dict:
    """
    收集文档级跨页重复统计：每页最顶/最底文本行（数字归一）→ 出现页数。
    输入 fitz.Document；返回 {归一化文本: 页数, "_total": 总页数}
    """
    stats = {"_total": len(doc)}
    for page in doc:
        lines = extract_flat_lines(page)
        if not lines:
            continue
        ordered = sorted(lines, key=lambda m: m["y0"])
        for cand in (ordered[0], ordered[-1]):
            t = cand["text"].strip()
            if not t or cand["size"] >= 14 or len(t) > 90:
                continue
            key = re.sub(r"\d+", "@", t)
            stats[key] = stats.get(key, 0) + 1
    return stats


def detect_columns(vis_lines: List[VLine], page_width: float,
                   min_col_rows: int = 5) -> List[Tuple[float, float]]:
    """
    探测页面栏结构：单栏 vs 双栏（为表格检测与段落合并分流）。

    原理：统计"行 x0 左边界"的聚类。双栏论文中右栏行 x0 明显靠右（>35% 页宽），
    且右栏行 x1 接近页右缘（正文宽度大，区别于表格窄列）。
    返回栏范围 [(x_lo, x_hi), ...]；单栏返回 [(0, page_width)]。
    """
    if not vis_lines:
        return [(0.0, page_width)]
    # 聚 x0（跳过缩进行用全部行，容差大些）
    xs0 = sorted(v.x0 for v in vis_lines)
    clusters = []  # (lo, hi, count)
    cur_lo = cur_hi = xs0[0]
    cnt = 1
    for x in xs0[1:]:
        if x - cur_hi <= 24:
            cur_hi = x
            cnt += 1
        else:
            clusters.append((cur_lo, cur_hi, cnt))
            cur_lo = cur_hi = x
            cnt = 1
    clusters.append((cur_lo, cur_hi, cnt))
    # 找右栏簇：中心 > 0.35*width 且行数足够 且 该簇行平均宽度 > 0.22*width
    total_rows = len(vis_lines)
    right_clusters = [c for c in clusters
                      if (c[0] + c[1]) / 2 > page_width * 0.35
                      and c[2] >= min_col_rows]
    # 右栏正文行需宽度够大（区别于表格窄列簇）
    right_rows = []
    right_lo = None
    right_hi = None
    for v in vis_lines:
        if v.x0 > page_width * 0.30:
            right_rows.append(v)
    if right_clusters and right_rows:
        avg_w = sum(v.width for v in right_rows) / len(right_rows)
        if avg_w > page_width * 0.22 and len(right_rows) >= min_col_rows:
            right_lo = min(v.x0 for v in right_rows)
            right_hi = max(v.x1 for v in right_rows)
    if right_lo is None:
        return [(0.0, page_width)]
    # 左栏 = 页左到右栏起始
    left_xs = [v for v in vis_lines if v.x0 < right_lo]
    left_hi = max((v.x1 for v in left_xs), default=right_lo - 10)
    return [(0.0, left_hi), (right_lo, right_hi)]


def assign_lines_to_columns(vis_lines: List[VLine],
                            cols: List[Tuple[float, float]]) -> List[List[VLine]]:
    """按栏范围把行分到各栏。"""
    result = [[] for _ in cols]
    for v in vis_lines:
        mx = (v.x0 + v.x1) / 2
        best = 0
        best_d = 1e18
        for i, (lo, hi) in enumerate(cols):
            d = 0.0
            if mx < lo:
                d = lo - mx
            elif mx > hi:
                d = mx - hi
            if d < best_d:
                best_d = d
                best = i
        result[best].append(v)
    return result
