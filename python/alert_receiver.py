from flask import Flask, request, jsonify
from datetime import datetime, timezone
from pathlib import Path
import logging
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv(dotenv_path=BASE_DIR / ".env")

from models import Alert
from classifier import classify_alert
from runbook_selector import select_runbook
from ansible_runner import run_playbook
from mattermost_notifier import send_incident_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)
app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "MARR Alert Receiver"}), 200

@app.route("/alert", methods=["POST"])
def receive_alert():
    payload = request.get_json(force=True)
    log.info(f"Alert received: {payload}")
    alert = Alert(
        alert_id    = str(payload.get("id", "unknown")),
        source_node = payload.get("nodeLabel", payload.get("nodeId", "unknown")),
        severity    = payload.get("severity", "UNKNOWN").upper(),
        event_uei   = payload.get("uei", ""),
        description = payload.get("description", ""),
        timestamp   = datetime.now(timezone.utc),
        interface   = payload.get("ifDescr"),
        raw_payload = payload,
    )
    fault_type = classify_alert(alert)
    log.info(f"Classified as: {fault_type}")
    playbook = select_runbook(fault_type)
    diag_out, rc = run_playbook(playbook, alert.source_node,
                                extra_vars={"alert_interface": alert.interface or "eth1"})
    send_incident_report(alert, fault_type, playbook or "none", diag_out, rc)
    return jsonify({"status": "processed", "alert_id": alert.alert_id,
                    "fault_type": fault_type, "playbook": playbook, "diag_rc": rc}), 200

if __name__ == "__main__":
    port = int(os.getenv("RECEIVER_PORT", 5000))
    log.info(f"MARR Alert Receiver starting on port {port}")
    log.info(f"Loading .env from: {BASE_DIR / '.env'}")
    log.info(f"Mattermost URL: {os.getenv('MATTERMOST_WEBHOOK_URL', 'NOT SET')}")
    app.run(host="0.0.0.0", port=port, debug=False)
