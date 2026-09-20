#!/usr/bin/env python3
"""
DICE Pilot Study — Local HTTP Server with Auto-Save
Serves the pilot UI and automatically saves each judgment to a JSON file.
No manual export needed.
"""
import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

PORT = 8090
TMP_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(TMP_DIR, 'pilot_results_live.json')
UI_FILE = os.path.join(TMP_DIR, 'l5_7_pilot_ui.html')

MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
}


class PilotHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Quiet logging — only show saves
        pass

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/' or path == '/l5_7_pilot_ui.html':
            self.serve_file(UI_FILE, 'text/html; charset=utf-8')
        elif path == '/api/results':
            # Return current saved results
            data = self.load_results()
            self.send_json(data)
        elif path == '/api/status':
            self.send_json({'status': 'ok', 'port': PORT, 'results_file': RESULTS_FILE})
        else:
            # Serve other static files from tmp/
            file_path = os.path.join(TMP_DIR, path.lstrip('/'))
            if os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1]
                mime = MIME_TYPES.get(ext, 'application/octet-stream')
                self.serve_file(file_path, mime)
            else:
                self.send_error(404, 'Not found')

    def do_POST(self):
        path = urlparse(self.path).path

        if path == '/api/submit':
            # Save a single judgment
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                judgment = json.loads(body)
                self.save_judgment(judgment)
                self.send_json({'status': 'saved', 'timestamp': time.time()})
            except Exception as e:
                self.send_error(400, f'Bad request: {e}')

        elif path == '/api/complete':
            # Save final complete results
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                count = len(data.get('results', []))
                pid = data.get('participant_id', '?')
                print(f"  [SAVED] Complete: {pid} — {count} judgments → {RESULTS_FILE}")
                self.send_json({'status': 'complete', 'judgments': count})
            except Exception as e:
                self.send_error(400, f'Bad request: {e}')

        elif path == '/api/clear':
            # Clear results (for re-start)
            if os.path.exists(RESULTS_FILE):
                os.remove(RESULTS_FILE)
            self.send_json({'status': 'cleared'})
        else:
            self.send_error(404, 'Not found')

    def serve_file(self, file_path, mime):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, 'File not found')

    def send_json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def load_results(self):
        if os.path.exists(RESULTS_FILE):
            try:
                with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {'results': [], 'participant_id': ''}

    def save_judgment(self, judgment):
        data = self.load_results()
        if not data.get('results'):
            data['results'] = []
        if not data.get('participant_id') and judgment.get('participant_id'):
            data['participant_id'] = judgment['participant_id']
        if not data.get('workflow_order') and judgment.get('workflow_order'):
            data['workflow_order'] = judgment['workflow_order']

        # Update or append
        idx = judgment.get('order_index', len(data['results']))
        if idx < len(data['results']):
            data['results'][idx] = judgment
        else:
            data['results'].append(judgment)

        data['last_updated'] = time.time()

        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        pid = judgment.get('participant_id', '?')
        item = judgment.get('item_id', '?')
        decision = judgment.get('decision', '?')
        count = len(data.get('results', []))
        print(f"  [AUTO-SAVE] {pid} | {item} -> {decision} ({count} total)")


def main():
    server = HTTPServer(('127.0.0.1', PORT), PilotHandler)
    print(f"DICE Pilot Server running on http://127.0.0.1:{PORT}")
    print(f"  UI:       http://127.0.0.1:{PORT}/l5_7_pilot_ui.html")
    print(f"  Auto-save: {RESULTS_FILE}")
    print(f"  Status:    http://127.0.0.1:{PORT}/api/status")
    print(f"  Results:   http://127.0.0.1:{PORT}/api/results")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
