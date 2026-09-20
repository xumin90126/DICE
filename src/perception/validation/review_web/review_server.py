"""
P7.2 Minimal Review Server — serves the simplified Human Review web UI.

Uses the EXISTING P7.2 validation backend (ValidationTask, ValidationRecord,
ValidatedEvidence) UNCHANGED. This server is only a transport layer:
  - serves candidate data + page image to the browser
  - receives Human decisions + reviewer_note
  - creates ValidationRecord via existing create_validation_record()
  - derives Evidence via existing derive_evidence()

No new data models. No auto-ACCEPT. No LLM.
"""
from __future__ import annotations

import json
import os
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import fitz

# Ensure imports work — review_server.py is 4 levels below dice2 root
DICE2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
DICE2 = os.path.normpath(DICE2)
sys.path.insert(0, DICE2)

from perception.sandbox.validation import (
    create_validation_record, derive_evidence, build_audit_chain,
    DECISION_ACCEPT, DECISION_REJECT, DECISION_NEED_REVIEW,
    DATASET_HUMAN_VALIDATION,
)
from perception.sandbox.validation.review_web.suggestion import build_candidate_payload
from perception.sandbox.validation.calibration_filter import calibrate_candidates
from perception.sandbox.p7_2_runner import (
    load_arxiv_toc_candidates, build_span_text_lookup,
    ARXIV_BIO, CALIB,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEWER_ID = "human_web_ui"
HOST = "127.0.0.1"
PORT = 5072

# ── Global state (per server session) ────────────────────────────────────────
_state = {
    "candidates": [],
    "span_lookup": {},
    "page_png_path": "",
    "page_width": 0,
    "page_height": 0,
    "records": [],       # list of (task_dict, record_dict)
    "evidence": [],
    "audit_chains": [],
    "lock": threading.Lock(),
}


def init_state():
    """Load candidates, build span lookup, render page PNG, run calibration."""
    print("[server] Loading 33 candidates...")
    candidates, spans, case = load_arxiv_toc_candidates()
    span_lookup = build_span_text_lookup(ARXIV_BIO, "arxiv_toc", 2)

    # Add candidate_text to each for calibration display
    for c in candidates:
        sid = c["span_ids"][0] if c["span_ids"] else ""
        c["candidate_text"] = span_lookup.get(sid, "")

    # Run calibration filter
    calibrated, calib_report = calibrate_candidates(candidates)
    print(f"[server] Calibration: {calib_report['original_candidate_count']} → {calib_report['calibrated_candidate_count']} candidates (↓{calib_report['reduction_rate']}%)")

    # Render page PNG at 150 DPI
    doc = fitz.open(ARXIV_BIO)
    page = doc[1]  # p2
    pw, ph = page.rect.width, page.rect.height
    pix = page.get_pixmap(dpi=150)
    png_path = os.path.join(CALIB, "arxiv_toc_p2_page.png")
    pix.save(png_path)
    doc.close()

    _state["candidates"] = candidates               # raw P7.1 (33)
    _state["calibrated"] = calibrated                # calibrated (10)
    _state["calibration_report"] = calib_report
    _state["span_lookup"] = span_lookup
    _state["page_png_path"] = png_path
    _state["page_width"] = pw
    _state["page_height"] = ph
    print(f"[server] {len(candidates)} raw + {len(calibrated)} calibrated, page {pw}x{ph}")


def get_candidates_payload(use_calibrated=True):
    """Build payload for candidates (calibrated by default)."""
    source = _state["calibrated"] if use_calibrated else _state["candidates"]
    sl = _state["span_lookup"]
    total = len(source)
    return [
        build_candidate_payload(
            c, sl, "/api/page-image",
            _state["page_width"], _state["page_height"],
            i, total
        )
        for i, c in enumerate(source)
    ]


class ReviewHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default logging

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, code, path, content_type):
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._file(200, os.path.join(HERE, "index.html"), "text/html; charset=utf-8")
        elif path == "/api/candidates":
            # Support ?mode=raw to see original P7.1 candidates (for comparison)
            qs = parse_qs(parsed.query)
            use_calib = qs.get("mode", ["calibrated"])[0] != "raw"
            total = len(_state["calibrated"]) if use_calib else len(_state["candidates"])
            self._json(200, {"candidates": get_candidates_payload(use_calib), "total": total})
        elif path == "/api/calibration-metrics":
            self._json(200, _state["calibration_report"])
        elif path == "/api/page-image":
            self._file(200, _state["page_png_path"], "image/png")
        elif path == "/api/progress":
            with _state["lock"]:
                done = len(_state["records"])
                ev_count = len(_state["evidence"])
            total = len(_state["calibrated"])
            self._json(200, {"completed": done, "total": total, "evidence_count": ev_count})
        elif path == "/api/export":
            with _state["lock"]:
                self._json(200, {
                    "records": [r for _, r in _state["records"]],
                    "evidence": _state["evidence"],
                    "audit_chains": _state["audit_chains"],
                })
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/submit":
            self._json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid JSON"})
            return

        obs_id = data.get("observation_id", "")
        decision_ui = data.get("decision", "")  # "accept" / "reject" / "need_review"
        reviewer_note = data.get("reviewer_note", "")
        duration_seconds = float(data.get("duration_seconds", 0.0))

        # Map UI decision to internal decision
        decision_map = {
            "accept": DECISION_ACCEPT,
            "reject": DECISION_REJECT,
            "need_review": DECISION_NEED_REVIEW,
        }
        if decision_ui not in decision_map:
            self._json(400, {"error": f"invalid decision: {decision_ui}"})
            return
        decision = decision_map[decision_ui]

        # Find the observation — search both raw and calibrated candidates
        cands_raw = _state["candidates"]
        cands_cal = _state["calibrated"]
        obs = None
        for c in cands_cal:
            if c.get("hypothesis_id") == obs_id:
                obs = c
                break
        if obs is None:
            for c in cands_raw:
                if c.get("hypothesis_id") == obs_id:
                    obs = c
                    break
        if obs is None:
            self._json(404, {"error": f"observation not found: {obs_id}"})
            return

        # Server-side dedup: if same observation_id + same decision already submitted, return existing
        with _state["lock"]:
            for task_dict, rec_dict in _state["records"]:
                if rec_dict["observation_id"] == obs_id and rec_dict["reviewer_decision"] == decision:
                    # Return existing record (no duplicate)
                    existing_ev = None
                    for e in _state["evidence"]:
                        if e["observation_id"] == obs_id:
                            existing_ev = e
                            break
                    self._json(200, {
                        "ok": True,
                        "observation_id": obs_id,
                        "decision": decision,
                        "validation_id": rec_dict["validation_id"],
                        "evidence_derived": existing_ev is not None,
                        "evidence_id": existing_ev["evidence_id"] if existing_ev else None,
                        "blocked": existing_ev is None,
                        "duplicate": True,
                    })
                    return

        # Use EXISTING P7.2 backend (unchanged)
        from perception.sandbox.validation import create_validation_task
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

        task = create_validation_task(
            obs, _state["span_lookup"],
            {"png_path": _state["page_png_path"], "bbox_highlight": obs["geometry"]["bbox"]},
            ts, priority=0, dataset_tag=DATASET_HUMAN_VALIDATION,
        )

        record = create_validation_record(
            task, decision,
            reviewer_reason=reviewer_note if reviewer_note else f"UI decision: {decision_ui}",
            reviewer_id=REVIEWER_ID,
            timestamp=ts,
            duration_seconds=duration_seconds,
            reviewer_notes=reviewer_note,
            dataset_tag=DATASET_HUMAN_VALIDATION,
        )

        ev = derive_evidence(obs, task, record, _state["span_lookup"])
        chain = build_audit_chain(ev, record, task, obs).to_dict() if ev else None

        with _state["lock"]:
            _state["records"].append((task.to_dict(), record.to_dict()))
            if ev:
                _state["evidence"].append(ev.to_dict())
                _state["audit_chains"].append(chain)

        result = {
            "ok": True,
            "observation_id": obs_id,
            "decision": decision,
            "validation_id": record.validation_id,
            "evidence_derived": ev is not None,
            "evidence_id": ev.evidence_id if ev else None,
            "blocked": ev is None,
        }
        self._json(200, result)


def run_server():
    init_state()
    server = HTTPServer((HOST, PORT), ReviewHandler)
    print(f"\n{'='*60}")
    print(f"  P7.2 Human Review UI — Simplified")
    print(f"  Open: http://{HOST}:{PORT}/")
    print(f"  Candidates: 33 HEADING_CANDIDATE (arxiv_toc_p2)")
    print(f"  Reviewer: {REVIEWER_ID}")
    print(f"  Backend: P7.2 validation (UNCHANGED)")
    print(f"{'='*60}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] stopped")
        server.server_close()


if __name__ == "__main__":
    run_server()
