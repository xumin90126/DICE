"""
页面文本提取器：按页提取保留排版的完整文本，并支持按 Y 坐标截取。

pymupdf 的 page.get_text("text") 会按坐标还原换行、缩进、空格，
比逐 span 拼接保留更好的排版。本模块在此基础上支持按 Y 坐标范围截取。
"""
from __future__ import annotations

import fitz
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class PageLine:
    """一行文本（含 Y 坐标）。"""
    text: str
    y: float
    page: int


def extract_page_lines(pdf_path: str) -> dict:
    """
    按页提取文本行（含 Y 坐标），返回 {page_no: [PageLine, ...]}。
    同时提取每页的完整文本（get_text("text") 格式）。
    """
    doc = fitz.open(pdf_path)
    pages_data = {}
    for page_num, page in enumerate(doc, 1):
        # 方法 1：get_text("text") 保留排版
        full_text = page.get_text("text")

        # 方法 2：get_text("dict") 提取每行的 Y 坐标
        lines: List[PageLine] = []
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                # 拼接一行的所有 span
                line_text = ""
                line_y = 0
                for span in line["spans"]:
                    line_text += span["text"]
                    line_y = round(span["bbox"][1], 1)
                line_text = line_text.strip()
                if line_text:
                    lines.append(PageLine(text=line_text, y=line_y, page=page_num))

        pages_data[page_num] = {
            "full_text": full_text,
            "lines": lines,
        }
    doc.close()
    return pages_data


def get_text_by_y_range(pages_data: dict, page: int, y_start: float,
                        y_end: Optional[float] = None) -> str:
    """
    从指定页提取 Y 坐标在 [y_start, y_end) 之间的文本行。
    如果 y_end 为 None，则取到页末。
    """
    if page not in pages_data:
        return ""
    lines = pages_data[page]["lines"]
    result = []
    for line in lines:
        if y_start is not None and line.y < y_start:
            continue
        if y_end is not None and line.y >= y_end:
            continue
        result.append(line.text)
    return "\n".join(result)


def get_full_page_text(pages_data: dict, page: int) -> str:
    """获取指定页的完整文本（保留排版）。"""
    if page not in pages_data:
        return ""
    return pages_data[page]["full_text"]


def extract_chunk_content(pages_data: dict, start_page: int, end_page: int,
                          y_start: Optional[float] = None,
                          y_end: Optional[float] = None,
                          next_page: Optional[int] = None,
                          exclude_title_text: str = "") -> str:
    """
    提取切片内容，保留原始排版。

    策略：
      - 如果 start_page == end_page（同页）：按 Y 坐标截取
      - 如果跨页：start_page 从 y_start 到页末 + 中间页全文 + end_page 从页首到 y_end

    Args:
        pages_data: extract_page_lines 的返回值
        start_page: 起始页
        end_page: 结束页
        y_start: 起始页的 Y 起点（标题之后）
        y_end: 结束页的 Y 终点（下一个标题之前）
        next_page: 下一个标题所在页（用于跨页截断）
        exclude_title_text: 要排除的标题文本
    """
    parts = []

    for pno in range(start_page, end_page + 1):
        if pno not in pages_data:
            continue
        page_text = pages_data[pno]["full_text"]
        lines = pages_data[pno]["lines"]

        if pno == start_page and y_start is not None:
            # 起始页：从 y_start 之后开始（跳过标题行本身）
            page_parts = []
            for line in lines:
                if line.y <= y_start:
                    # 跳过标题行及之前的内容
                    continue
                if y_end is not None and line.y >= y_end:
                    # 到下一个标题了
                    continue
                page_parts.append(line.text)
            parts.append("\n".join(page_parts))
        elif pno == end_page and y_end is not None and pno != start_page:
            # 结束页（跨页情况）：到 y_end 之前
            page_parts = []
            for line in lines:
                if line.y < y_end:
                    page_parts.append(line.text)
            parts.append("\n".join(page_parts))
        else:
            # 中间页：全文
            parts.append(page_text.strip())

    return "\n".join(p for p in parts if p).strip()
