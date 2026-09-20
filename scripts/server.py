#!/usr/bin/env python3
"""HTTP server for M-A A/B Evidence Sufficiency Pilot.
Serves static files + receives results via POST.
"""
import http.server
import json
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ABPilotHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/save_results':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                results = json.loads(body)
                results_path = os.path.join(DIRECTORY, 'data', 'ab_pilot_results.json')
                with open(results_path, 'w') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"\n[SERVER] Results saved to {results_path}", flush=True)
                print(f"[SERVER] Total cases: {results.get('total_cases')}", flush=True)
                print(f"[SERVER] Completed: {results.get('completed_cases')}", flush=True)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'ok',
                    'saved_to': results_path
                }).encode())
            except Exception as e:
                print(f"[SERVER] Error saving results: {e}", flush=True)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'message': str(e)
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        # Concise logging
        msg = format % args
        if 'GET' in msg:
            # Only log non-asset requests
            if any(x in msg for x in ['.png', '.js', '.css', '.ico']):
                return
        print(f"[HTTP] {msg}", flush=True)


if __name__ == '__main__':
    # Clear any previous results
    results_path = os.path.join(DIRECTORY, 'data', 'ab_pilot_results.json')
    if os.path.exists(results_path):
        os.remove(results_path)
        print(f"[SERVER] Cleared previous results", flush=True)

    server = http.server.HTTPServer(('0.0.0.0', PORT), ABPilotHandler)
    print(f"[SERVER] A/B Pilot server running on http://127.0.0.1:{PORT}", flush=True)
    print(f"[SERVER] Open http://127.0.0.1:{PORT}/index.html in your browser", flush=True)
    print(f"[SERVER] Serving from: {DIRECTORY}", flush=True)
    print(f"[SERVER] Pages symlink: {os.path.exists(os.path.join(DIRECTORY, 'pages'))}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.", flush=True)
        server.shutdown()
