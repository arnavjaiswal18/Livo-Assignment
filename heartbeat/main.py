"""
main.py — Entry point for the Heartbeat dashboard.

Starts a Flask web server that:
  • Serves the digest dashboard at http://localhost:5050
  • Runs a background thread that rebuilds the digest every 30 minutes
  • Exposes a /api/digest JSON endpoint for programmatic access

Usage:
    python main.py
    python main.py --port 8080
    DEMO_MODE=false python main.py   # use real API keys

Auto-opens the browser on first launch.
"""

import argparse
import sys
import threading
import time
import webbrowser
from datetime import datetime
from typing import Optional

# ── Flask ──────────────────────────────────────────────────────────────────────
try:
    from flask import Flask, jsonify, Response
except ImportError:
    print("[ERROR] Flask not installed. Run: pip install flask")
    sys.exit(1)

# ── Internal ───────────────────────────────────────────────────────────────────
import config
from processors.digest   import build_digest
from processors.renderer import render_html
from collectors.models   import Digest

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)

# Shared digest state (protected by a lock for thread safety)
_lock            = threading.Lock()
_current_digest: Optional[Digest] = None


def _refresh_digest():
    global _current_digest
    while True:
        print(f"\n[Heartbeat] Rebuilding digest at {datetime.now().strftime('%H:%M:%S')} …")
        try:
            digest = build_digest()
            with _lock:
                _current_digest = digest
            print(f"[Heartbeat] Digest ready — {digest.urgent_count} urgent, {digest.info_count} info.")
        except Exception as e:
            print(f"[Heartbeat] Digest build failed: {e}")
        time.sleep(config.DIGEST_INTERVAL_MINS * 60)


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():
    """Render the live HTML digest dashboard."""
    global _current_digest
    with _lock:
        digest = _current_digest

    if digest is None:
        # First-run: build synchronously so the page never shows empty
        digest = build_digest()
        with _lock:
            _current_digest = digest

    html = render_html(digest)
    return Response(html, mimetype="text/html")


@app.route("/api/digest")
def api_digest():
    """Return the current digest as JSON (for CLI / notification integrations)."""
    global _current_digest
    with _lock:
        digest = _current_digest

    if digest is None:
        return jsonify({"error": "Digest not yet built"}), 503

    def item_to_dict(item):
        return {
            "source":    item.source,
            "level":     item.level,
            "title":     item.title,
            "body":      item.body,
            "timestamp": item.timestamp.isoformat(),
            "link":      item.link,
            "age_minutes": item.age_minutes(),
        }

    return jsonify({
        "generated_at": digest.generated_at.isoformat(),
        "urgent_count": digest.urgent_count,
        "info_count":   digest.info_count,
        "urgent": [item_to_dict(i) for i in digest.urgent],
        "info":   [item_to_dict(i) for i in digest.info],
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok", "demo_mode": config.DEMO_MODE})


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Heartbeat digest dashboard")
    parser.add_argument("--host", default=config.DASHBOARD_HOST, help="Host to bind")
    parser.add_argument("--port", type=int, default=config.DASHBOARD_PORT, help="Port to listen on")
    parser.add_argument("--no-browser", action="store_true", help="Skip auto-opening browser")
    args = parser.parse_args()

    mode = "DEMO" if config.DEMO_MODE else "LIVE"
    print(f"""
╔══════════════════════════════════════════════════╗
║           Heartbeat  ·  30-min Digest           ║
╠══════════════════════════════════════════════════╣
║  Mode    : {mode:<38}║
║  URL     : http://{args.host}:{args.port:<28}║
║  Interval: every {config.DIGEST_INTERVAL_MINS} minutes{'':<30}║
╚══════════════════════════════════════════════════╝
""")

    # Start background refresh thread
    t = threading.Thread(target=_refresh_digest, daemon=True)
    t.start()

    # Give the first digest a moment to build before opening browser
    if not args.no_browser:
        def _open():
            time.sleep(1.5)
            url = f"http://{args.host}:{args.port}"
            print(f"[Heartbeat] Opening browser → {url}")
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    app.run(host=args.host, port=args.port, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
