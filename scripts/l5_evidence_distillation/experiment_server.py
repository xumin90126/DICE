#!/usr/bin/env python3
"""Experiment server for L5 Evidence Distillation Experiment.
Serves the 3-condition UI and records judgments with full behavioral metrics.
Port: 8090
"""

import json, os, sys, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

EXPERIMENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(EXPERIMENT_DIR, 'data')
RECORDING_DIR = os.path.join(EXPERIMENT_DIR, 'recording')

os.makedirs(RECORDING_DIR, exist_ok=True)

RESULTS_FILE = os.path.join(RECORDING_DIR, 'experiment_results_live.json')
RAW_EVENTS_FILE = os.path.join(RECORDING_DIR, 'raw_events.jsonl')

class ExperimentHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress logging

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_ui()
        elif self.path == '/api/cases':
            self.serve_cases()
        elif self.path == '/api/results':
            self.serve_results()
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''

        if self.path == '/api/submit':
            self.handle_submit(body)
        elif self.path == '/api/event':
            self.handle_event(body)
        elif self.path == '/api/complete':
            self.handle_complete(body)
        elif self.path == '/api/clear':
            self.handle_clear()
        else:
            self.send_error(404)

    def serve_ui(self):
        ui_path = os.path.join(EXPERIMENT_DIR, 'app', 'experiment_ui.html')
        if os.path.exists(ui_path):
            with open(ui_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_error(404, 'UI not found')

    def serve_cases(self):
        cases_path = os.path.join(DATA_DIR, 'experiment_cases_embedded.json')
        if os.path.exists(cases_path):
            with open(cases_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_error(404, 'Cases not found')

    def serve_results(self):
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = json.dumps({'results': [], 'total': 0})
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def handle_submit(self, body):
        try:
            data = json.loads(body)
        except:
            self.send_error(400, 'Invalid JSON')
            return

        # Load existing results
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
        else:
            results = {'results': [], 'total': 0}

        # Append new result
        data['server_timestamp'] = time.time()
        results['results'].append(data)
        results['total'] = len(results['results'])

        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        count = results['total']
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok', 'count': count}).encode())

    def handle_event(self, body):
        """Append raw event to JSONL file (append-only)."""
        try:
            data = json.loads(body)
        except:
            self.send_error(400, 'Invalid JSON')
            return

        data['server_timestamp'] = time.time()
        with open(RAW_EVENTS_FILE, 'a') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode())

    def handle_complete(self, body):
        try:
            data = json.loads(body)
        except:
            self.send_error(400, 'Invalid JSON')
            return

        # Save completion record
        complete_path = os.path.join(RECORDING_DIR, f"complete_{data.get('participant_id','unknown')}.json")
        with open(complete_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'complete'}).encode())

    def handle_clear(self):
        with open(RESULTS_FILE, 'w') as f:
            json.dump({'results': [], 'total': 0}, f)
        # Don't clear raw events (append-only)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'cleared'}).encode())


if __name__ == '__main__':
    port = 8091
    server = HTTPServer(('127.0.0.1', port), ExperimentHandler)
    print(f"Evidence Distillation Experiment Server running on http://127.0.0.1:{port}")
    print(f"  UI:       http://127.0.0.1:{port}/")
    print(f"  Cases:    http://127.0.0.1:{port}/api/cases")
    print(f"  Results:  http://127.0.0.1:{port}/api/results")
    print(f"  Recording: {RECORDING_DIR}")
    server.serve_forever()
