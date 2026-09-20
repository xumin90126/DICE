#!/usr/bin/env python3
"""
HVA-09: Render page images with accurate span positions.
- For PDF cases: search actual text positions, render at 3x, crop around A/B area
- For text cases: render page_context as clean formatted image with highlighted A/B
"""
import json, os, re
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, 'page_images')
os.makedirs(IMG_DIR, exist_ok=True)

# Load data
import sys
sys.path.insert(0, SCRIPT_DIR)
PHASE2 = os.path.dirname(SCRIPT_DIR)
TMP = os.path.dirname(PHASE2)
BASE = os.path.dirname(TMP)

p7m = json.load(open(os.path.join(TMP, 'perception', 'p7', 'independent_machine_resolvability_results.json')))
machine_map = {c['case_id']: c for c in p7m['machine_results']}
p7r = json.load(open(os.path.join(TMP, 'perception', 'p7', 'independent_evaluation_human_review', 'reviewer_a_blind_cases.json')))
reviewer_map = {c['case_id']: c for c in p7r['cases']}

CASE_IDS = [
    'IND-AMB-003', 'IND-AMB-002', 'IND-AMB-052', 'IND-AMB-033', 'IND-AMB-049',
    'IND-AMB-008', 'IND-AMB-005', 'IND-AMB-134',
    'IND-AMB-001', 'IND-AMB-090', 'IND-AMB-084', 'IND-AMB-054', 'IND-AMB-041',
    'IND-AMB-062', 'IND-AMB-067',
]

PDF_PATH = '/tmp/dice2_hetero_docs/arxiv_2402.18619.pdf'
PDF_CASES = ['IND-AMB-001', 'IND-AMB-002', 'IND-AMB-003']

def get_font(size):
    for path in ['/System/Library/Fonts/Menlo.ttc', '/System/Library/Fonts/Courier.dfont',
                 '/System/Library/Fonts/Monaco.dfont', '/Library/Fonts/Menlo.ttc']:
        try:
            return ImageFont.truetype(path, size)
        except:
            pass
    return ImageFont.load_default()

def render_pdf_case(case_id, text_a, text_b):
    """Render PDF page with accurate text positions found by search."""
    import fitz
    
    doc = fitz.open(PDF_PATH)
    
    # Search all pages for text_b (more specific than text_a which may be ".")
    found_page = None
    bbox_b = None
    bbox_a = None
    
    for i in range(len(doc)):
        page = doc[i]
        if text_b and len(text_b) > 1:
            results = page.search_for(text_b)
            if results:
                found_page = i
                bbox_b = results[0]
                break
    
    if found_page is None:
        doc.close()
        return None
    
    page = doc[found_page]
    
    # Find text_a on the same page
    if text_a and len(text_a) > 1:
        results_a = page.search_for(text_a)
        if results_a:
            # Find the one closest to bbox_b
            best = min(results_a, key=lambda r: abs(r.y0 - bbox_b.y0))
            bbox_a = best
    elif text_a == '.':
        # Find period near bbox_b - look at text spans just before bbox_b
        blocks = page.get_text("dict")["blocks"]
        min_dist = float('inf')
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    txt = span["text"]
                    sbbox = span["bbox"]
                    # Look for spans ending with "." near bbox_b's y position
                    if txt.endswith('.') and abs(sbbox[1] - bbox_b.y0) < 5:
                        dist = abs(sbbox[2] - bbox_b.x0)
                        if dist < min_dist:
                            min_dist = dist
                            bbox_a = fitz.Rect(sbbox[2]-2, sbbox[1], sbbox[2], sbbox[3])
    
    # Render full page at 3x
    zoom = 3.0
    mat = fitz.Matrix(zoom, zoom)
    
    # Draw rectangles
    shape = page.new_shape()
    if bbox_a:
        shape.draw_rect(bbox_a)
        shape.finish(color=(1, 0, 0), fill=(1, 0.6, 0.6), fill_opacity=0.4, width=2)
    if bbox_b:
        shape.draw_rect(bbox_b)
        shape.finish(color=(0, 0, 1), fill=(0.6, 0.6, 1), fill_opacity=0.4, width=2)
    shape.commit()
    
    pix = page.get_pixmap(matrix=mat)
    
    # Save full page
    full_path = os.path.join(IMG_DIR, f'{case_id}_full.png')
    pix.save(full_path)
    
    # Also create a cropped version zoomed around A/B area
    if bbox_a and bbox_b:
        min_x = min(bbox_a.x0, bbox_b.x0) - 60
        max_x = max(bbox_a.x1, bbox_b.x1) + 60
        min_y = min(bbox_a.y0, bbox_b.y0) - 80
        max_y = max(bbox_a.y1, bbox_b.y1) + 80
        
        # Ensure valid crop
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(page.rect.width, max_x)
        max_y = min(page.rect.height, max_y)
        
        crop_rect = fitz.Rect(min_x, min_y, max_x, max_y)
        crop_pix = page.get_pixmap(matrix=mat, clip=crop_rect)
        crop_path = os.path.join(IMG_DIR, f'{case_id}_crop.png')
        crop_pix.save(crop_path)
    
    page_w = page.rect.width
    page_h = page.rect.height
    doc.close()
    
    # Convert bbox to pixel coordinates (at zoom factor)
    def to_px(bbox):
        if bbox is None:
            return None
        if hasattr(bbox, 'x0'):
            return [int(bbox.x0 * zoom), int(bbox.y0 * zoom), int(bbox.x1 * zoom), int(bbox.y1 * zoom)]
        return [int(v * zoom) for v in bbox]
    
    return {
        'image_path': f'page_images/{case_id}_full.png',
        'crop_path': f'page_images/{case_id}_crop.png' if bbox_a and bbox_b else None,
        'pdf_page': found_page + 1,
        'page_width': page_w,
        'page_height': page_h,
        'render_width': pix.width,
        'render_height': pix.height,
        'scale': zoom,
        'bbox_a': [bbox_a.x0, bbox_a.y0, bbox_a.x1, bbox_a.y1] if bbox_a and hasattr(bbox_a, 'x0') else (bbox_a if bbox_a else None),
        'bbox_b': [bbox_b.x0, bbox_b.y0, bbox_b.x1, bbox_b.y1] if bbox_b and hasattr(bbox_b, 'x0') else (bbox_b if bbox_b else None),
        'bbox_a_pixel': to_px(bbox_a),
        'bbox_b_pixel': to_px(bbox_b),
        'source': 'actual_pdf',
        'text_a_found': bbox_a is not None,
        'text_b_found': bbox_b is not None,
    }

def render_text_case(case_id, text_a, text_b, page_context):
    """Render page_context as a clean text image with highlighted A/B spans."""
    
    font_size = 16
    font = get_font(font_size)
    line_height = 24
    char_width = 10
    margin_left = 50
    margin_top = 60
    margin_right = 50
    margin_bottom = 40
    
    # Process page_context into lines
    raw_lines = page_context.split('\n')
    clean_lines = []
    for line in raw_lines:
        clean = line
        if clean.startswith('>>>'):
            clean = clean[3:]
        clean = clean.replace('[TEXT A]', '').replace('[TEXT B]', '').rstrip()
        if clean.strip() or clean == '':
            clean_lines.append(clean)
    
    # Remove leading/trailing empty lines
    while clean_lines and not clean_lines[0].strip():
        clean_lines.pop(0)
    while clean_lines and not clean_lines[-1].strip():
        clean_lines.pop()
    
    # Calculate image size
    max_line_len = max((len(line) for line in clean_lines), default=80)
    img_width = max(max_line_len * char_width + margin_left + margin_right, 800)
    img_height = len(clean_lines) * line_height + margin_top + margin_bottom + 40
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), '#fafafa')
    draw = ImageDraw.Draw(img)
    
    # Draw header
    header_font = get_font(13)
    draw.text((margin_left, 15), f"Case: {case_id}  |  文本渲染 / Text-based rendering", fill='#666', font=header_font)
    
    # Legend
    legend_y = 35
    draw.rectangle([margin_left, legend_y, margin_left + 20, legend_y + 16], fill='#ffcccc', outline='#cc0000')
    draw.text((margin_left + 25, legend_y), 'A', fill='#cc0000', font=header_font)
    draw.rectangle([margin_left + 50, legend_y, margin_left + 70, legend_y + 16], fill='#ccccff', outline='#0000cc')
    draw.text((margin_left + 75, legend_y), 'B', fill='#0000cc', font=header_font)
    
    # Draw lines
    for i, line in enumerate(clean_lines):
        y = margin_top + i * line_height
        
        # Check if line contains text_a or text_b
        contains_a = bool(text_a) and len(text_a) > 1 and text_a in line
        contains_b = bool(text_b) and len(text_b) > 1 and text_b in line
        
        # For short text_a like "." or "Le.", check if line ends with it
        if text_a and len(text_a) <= 3:
            stripped = line.rstrip()
            if stripped.endswith(text_a):
                contains_a = True
        
        # Draw highlight background
        if contains_a and contains_b:
            draw.rectangle([margin_left - 8, y - 2, img_width - margin_right, y + line_height - 4], 
                          fill='#e8d8e8', outline='#993399')
        elif contains_a:
            draw.rectangle([margin_left - 8, y - 2, img_width - margin_right, y + line_height - 4], 
                          fill='#ffcccc', outline='#cc0000')
        elif contains_b:
            draw.rectangle([margin_left - 8, y - 2, img_width - margin_right, y + line_height - 4], 
                          fill='#ccccff', outline='#0000cc')
        
        # Draw left margin marker
        if contains_a:
            draw.rectangle([0, y - 2, margin_left - 10, y + line_height - 4], fill='#cc0000')
            draw.text((5, y), 'A', fill='white', font=header_font)
        if contains_b:
            draw.rectangle([0, y - 2, margin_left - 10, y + line_height - 4], fill='#0000cc')
            draw.text((5, y), 'B', fill='white', font=header_font)
        
        # Draw text
        draw.text((margin_left, y), line, fill='#222', font=font)
    
    img_path = os.path.join(IMG_DIR, f'{case_id}_full.png')
    img.save(img_path)
    
    # For text cases, no crop (the whole image is the "page")
    return {
        'image_path': f'page_images/{case_id}_full.png',
        'crop_path': None,
        'pdf_page': None,
        'page_width': img_width,
        'page_height': img_height,
        'render_width': img_width,
        'render_height': img_height,
        'scale': 1.0,
        'bbox_a': None,
        'bbox_b': None,
        'bbox_a_pixel': None,
        'bbox_b_pixel': None,
        'source': 'text_based',
        'text_a_found': True,
        'text_b_found': True,
    }

# Process all cases
results = {}
for cid in CASE_IDS:
    mc = machine_map[cid]
    rc = reviewer_map.get(cid, {})
    text_a = mc.get('text_a', '')
    text_b = mc.get('text_b', '')
    page_context = rc.get('page_context', '')
    
    print(f"Processing {cid}: text_a='{text_a[:20]}', text_b='{text_b[:20]}'")
    
    if cid in PDF_CASES and os.path.exists(PDF_PATH):
        info = render_pdf_case(cid, text_a, text_b)
        if info:
            results[cid] = info
            a_found = '✓' if info['text_a_found'] else '✗'
            b_found = '✓' if info['text_b_found'] else '✗'
            print(f"  → PDF page {info['pdf_page']}, A found={a_found}, B found={b_found}")
            if info.get('crop_path'):
                print(f"  → Full: {info['render_width']}x{info['render_height']}, Crop: {info['crop_path']}")
        else:
            info = render_text_case(cid, text_a, text_b, page_context)
            results[cid] = info
            print(f"  → Text fallback: {info['render_width']}x{info['render_height']}")
    else:
        info = render_text_case(cid, text_a, text_b, page_context)
        results[cid] = info
        print(f"  → Text: {info['render_width']}x{info['render_height']}")

# Save info
info_path = os.path.join(SCRIPT_DIR, 'page_image_info.json')
with open(info_path, 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n=== Summary ===")
pdf_count = sum(1 for v in results.values() if v['source'] == 'actual_pdf')
text_count = sum(1 for v in results.values() if v['source'] == 'text_based')
print(f"  PDF rendered: {pdf_count}")
print(f"  Text rendered: {text_count}")
print(f"  Total: {len(results)}")
