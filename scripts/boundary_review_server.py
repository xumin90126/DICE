"""
Boundary Review Experiment Server.
INDEPENDENT from frozen P7.2 review_server.py.
Serves AMBIGUOUS cases for human boundary review.
NO system recommendation shown (anti-confirmation-bias).

Port: 5073 (separate from frozen P7.2 port 5072).
"""
import json, os, time, uuid, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── Paths ──
BASE = os.path.dirname(os.path.abspath(__file__))
CASES_FILE = os.path.join(BASE, "round1_cases.json")
RESULTS_FILE = os.path.join(BASE, "round1_results.json")
IMAGES_DIR = os.path.join(BASE, "page_images")

# ── Load cases ──
with open(CASES_FILE, "r", encoding="utf-8") as f:
    CASES_DATA = json.load(f)

CASES = CASES_DATA["cases"]

# ── Reviewer state ──
_state_lock = threading.Lock()
_state = {
    "results": [],        # list of review records
    "current_index": {},  # reviewer_id -> current case index
    "session_start": {},  # reviewer_id -> {case_id -> start_timestamp_ms}
}

# Load existing results if any
if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        _state["results"] = json.load(f).get("results", [])

def save_results():
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump({"results": _state["results"]}, f, ensure_ascii=False, indent=2)


class BoundaryReviewHandler(SimpleHTTPRequestHandler):

    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # ── Main page ──
        if path == "/" or path == "/index.html":
            html_path = os.path.join(BASE, "boundary_review.html")
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()
            self._send_html(html)
            return

        # ── Get case data ──
        if path == "/api/case":
            reviewer_id = params.get("reviewer_id", ["default"])[0]
            case_index = int(params.get("index", ["0"])[0])

            if case_index >= len(CASES):
                self._send_json({"status": "complete", "total": len(CASES)})
                return

            case = CASES[case_index]
            # Strip ground_truth_label and geometric features (anti-confirmation-bias)
            # Human sees ONLY: doc_id, page, text_a, text_b, image
            public_case = {
                "case_id": case["case_id"],
                "doc_id": case["doc_id"],
                "page": case["page"],
                "text_a": case["text_a"],
                "text_b": case["text_b"],
                "image_url": f"/image/{case['case_id']}_p{case['page']}.png",
                "index": case_index,
                "total": len(CASES),
            }

            # Record session start time
            with _state_lock:
                if reviewer_id not in _state["session_start"]:
                    _state["session_start"][reviewer_id] = {}
                _state["session_start"][reviewer_id][case["case_id"]] = int(time.time() * 1000)

            self._send_json(public_case)
            return

        # ── Serve page images ──
        if path.startswith("/image/"):
            img_name = path.replace("/image/", "")
            img_path = os.path.join(IMAGES_DIR, img_name)
            if os.path.exists(img_path):
                self._send_file(img_path, "image/png")
            else:
                self.send_error(404, "Image not found")
            return

        # ── Get results summary ──
        if path == "/api/results":
            with _state_lock:
                self._send_json({"results": _state["results"], "total": len(_state["results"])})
            return

        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/submit":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            reviewer_id = data.get("reviewer_id", "default")
            case_id = data.get("case_id", "")
            decision = data.get("decision", "")  # MERGE / KEEP_SEPARATE / CANNOT_DETERMINE
            comment = data.get("comment", "")

            # Validate decision
            if decision not in ["MERGE", "KEEP_SEPARATE", "CANNOT_DETERMINE"]:
                self._send_json({"error": "Invalid decision"}, 400)
                return

            # Calculate duration
            decision_time_ms = int(time.time() * 1000)
            start_time_ms = None
            with _state_lock:
                start_map = _state["session_start"].get(reviewer_id, {})
                start_time_ms = start_map.get(case_id)

            duration_ms = None
            if start_time_ms:
                duration_ms = decision_time_ms - start_time_ms

            # Check for duplicate submission (same reviewer + same case + same decision)
            with _state_lock:
                for existing in _state["results"]:
                    if (existing.get("reviewer_id") == reviewer_id
                        and existing.get("case_id") == case_id
                        and existing.get("decision") == decision):
                        # Duplicate — return existing
                        self._send_json({"status": "duplicate", "record": existing})
                        return

                # If same case but different decision, it's an override (allowed)
                # Remove previous record for same reviewer+case
                _state["results"] = [
                    r for r in _state["results"]
                    if not (r.get("reviewer_id") == reviewer_id and r.get("case_id") == case_id)
                ]

                record = {
                    "record_id": str(uuid.uuid4())[:12],
                    "reviewer_id": reviewer_id,
                    "case_id": case_id,
                    "decision": decision,
                    "comment": comment,
                    "start_time_ms": start_time_ms,
                    "decision_time_ms": decision_time_ms,
                    "duration_ms": duration_ms,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                _state["results"].append(record)
                save_results()

            self._send_json({"status": "ok", "record": record})
            return

        self.send_error(404, "Not found")

    def log_message(self, format, *args):
        # Suppress default logging (keep clean)
        pass


def main():
    port = 5073
    server = HTTPServer(("127.0.0.1", port), BoundaryReviewHandler)
    print(f"Boundary Review Experiment Server")
    print(f"  Port: {port}")
    print(f"  Cases: {len(CASES)}")
    print(f"  URL: http://127.0.0.1:{port}")
    print(f"  Results: {RESULTS_FILE}")
    print(f"  NO system recommendation (anti-confirmation-bias)")
    print(f"  Three decisions: MERGE / KEEP_SEPARATE / CANNOT_DETERMINE")
    print()
    server.serve_forever()


if __name__ == "__main__":
    main()
