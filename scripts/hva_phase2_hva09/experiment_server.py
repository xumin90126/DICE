#!/usr/bin/env python3
"""
HVA-09 Experiment Server
Serves experiment UI, page images, handles case delivery, logs decisions.
No GT exposure in UI. No semantic judgment. Human only does MERGE/KEEP_SEPARATE/UNKNOWN.
"""
import json
import os
import time
import uuid
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASES_PATH = os.path.join(SCRIPT_DIR, 'experiment_cases.json')
RESULTS_PATH = os.path.join(SCRIPT_DIR, 'experiment_results.json')
UI_PATH = os.path.join(SCRIPT_DIR, 'experiment_ui.html')
IMG_DIR = os.path.join(SCRIPT_DIR, 'page_images')
IMG_INFO_PATH = os.path.join(SCRIPT_DIR, 'page_image_info.json')

# Load cases
with open(CASES_PATH) as f:
    CASES_DATA = json.load(f)
CASES = CASES_DATA['cases']

# Load page image info
if os.path.exists(IMG_INFO_PATH):
    with open(IMG_INFO_PATH) as f:
        PAGE_IMAGE_INFO = json.load(f)
else:
    PAGE_IMAGE_INFO = {}

# In-memory session store
SESSIONS = {}

class ExperimentHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def _send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _send_file(self, filepath, content_type):
        if not os.path.exists(filepath):
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', os.path.getsize(filepath))
        self.end_headers()
        with open(filepath, 'rb') as f:
            self.wfile.write(f.read())
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            with open(UI_PATH) as f:
                self._send_html(f.read())
        
        elif parsed.path.startswith('/page_images/'):
            # Serve page images
            filename = parsed.path.replace('/page_images/', '')
            filepath = os.path.join(IMG_DIR, filename)
            ct = mimetypes.guess_type(filepath)[0] or 'image/png'
            self._send_file(filepath, ct)
        
        elif parsed.path == '/api/session':
            session_id = str(uuid.uuid4())[:8]
            session_count = len(SESSIONS)
            order = 'AB' if session_count % 2 == 0 else 'BA'
            
            case_ids = [c['case_id'] for c in CASES]
            half = len(case_ids) // 2
            first_half = case_ids[:half]
            second_half = case_ids[half:]
            
            if order == 'AB':
                case_sequence = [(cid, 'A') for cid in first_half] + [(cid, 'B') for cid in second_half]
            else:
                case_sequence = [(cid, 'B') for cid in first_half] + [(cid, 'A') for cid in second_half]
            
            SESSIONS[session_id] = {
                'session_id': session_id,
                'order': order,
                'case_sequence': case_sequence,
                'current_index': 0,
                'results': [],
                'start_time': time.time(),
            }
            
            self._send_json({
                'session_id': session_id,
                'order': order,
                'total_cases': len(case_sequence),
            })
        
        elif parsed.path == '/api/case':
            params = parse_qs(parsed.query)
            session_id = params.get('session_id', [''])[0]
            
            session = SESSIONS.get(session_id)
            if not session:
                self._send_json({'error': 'Invalid session'}, 400)
                return
            
            idx = session['current_index']
            if idx >= len(session['case_sequence']):
                self._send_json({'done': True, 'results': session['results']})
                return
            
            case_id, condition = session['case_sequence'][idx]
            case = next(c for c in CASES if c['case_id'] == case_id)
            
            if condition == 'A':
                view = case['condition_a']['view']
            else:
                view = case['condition_b']['view']
            
            # Get page image info
            img_info = PAGE_IMAGE_INFO.get(case_id, {})
            
            self._send_json({
                'case_index': idx + 1,
                'total_cases': len(session['case_sequence']),
                'condition': condition,
                'case_id': case_id,
                'view': view,
                'has_raw_context': condition == 'B' and case['condition_b']['raw_context_length'] > 0,
                'raw_context': case['condition_b']['raw_context'] if condition == 'B' else '',
                'page_image': img_info.get('image_path', ''),
                'crop_path': img_info.get('crop_path', ''),
                'page_image_source': img_info.get('source', 'none'),
                'page_image_width': img_info.get('render_width', 0),
                'page_image_height': img_info.get('render_height', 0),
                'bbox_a': img_info.get('bbox_a', []),
                'bbox_b': img_info.get('bbox_b', []),
                'bbox_a_pixel': img_info.get('bbox_a_pixel', []),
                'bbox_b_pixel': img_info.get('bbox_b_pixel', []),
                'timestamp': time.time(),
            })
        
        elif parsed.path == '/api/submit':
            pass
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/submit':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)
            
            session_id = data.get('session_id')
            session = SESSIONS.get(session_id)
            if not session:
                self._send_json({'error': 'Invalid session'}, 400)
                return
            
            case_id = data.get('case_id')
            condition = data.get('condition')
            decision = data.get('decision')
            decision_time_ms = data.get('decision_time_ms', 0)
            raw_context_expanded = data.get('raw_context_expanded', False)
            page_revisited = data.get('page_revisited', False)
            evidence_expansion_count = data.get('evidence_expansion_count', 0)
            interaction_count = data.get('interaction_count', 0)
            levels_viewed = data.get('levels_viewed', 0)
            
            case = next(c for c in CASES if c['case_id'] == case_id)
            
            result = {
                'session_id': session_id,
                'participant_id': session_id,
                'case_id': case_id,
                'condition': condition,
                'decision': decision,
                'decision_time_ms': decision_time_ms,
                'raw_context_expanded': raw_context_expanded,
                'page_revisited': page_revisited,
                'evidence_expansion_count': evidence_expansion_count,
                'interaction_count': interaction_count,
                'levels_viewed': levels_viewed,
                'machine_decision': case['machine_decision'],
                'semantic_gt': case['semantic_gt'],
                'boundary_class': case['boundary_class'],
                'machine_agrees_with_gt': case['machine_agrees_with_gt'],
                'view_length_a': case['condition_a']['view_length'],
                'view_length_b': case['condition_b']['view_length'],
                'has_context_b': case['condition_b']['has_context'],
                'markers_b': case['condition_b'].get('markers', {}),
                'compression_ratio_b': case['condition_b']['compression_ratio'],
                'raw_context_length_b': case['condition_b']['raw_context_length'],
                'timestamp': time.time(),
            }
            
            session['results'].append(result)
            session['current_index'] += 1
            
            all_results = []
            for s in SESSIONS.values():
                all_results.extend(s['results'])
            with open(RESULTS_PATH, 'w') as f:
                json.dump({
                    'results': all_results,
                    'session_count': len(SESSIONS),
                }, f, indent=2, ensure_ascii=False)
            
            self._send_json({'ok': True, 'next_index': session['current_index']})

def main():
    port = 8199
    server = HTTPServer(('127.0.0.1', port), ExperimentHandler)
    print(f"HVA-09 Experiment Server running at http://127.0.0.1:{port}/")
    print(f"  Cases: {len(CASES)}")
    print(f"  Page images: {len(PAGE_IMAGE_INFO)} cases")
    print(f"  Conditions: A (Current Pack) / B (Evidence Pack v2)")
    print(f"  Human task: MERGE / KEEP_SEPARATE / UNKNOWN")
    print(f"  GT: NOT exposed in UI")
    print(f"  Results: {RESULTS_PATH}")
    server.serve_forever()

if __name__ == '__main__':
    main()
