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

# Correlator integration - fail-safe import.
# If correlator_state cannot be imported (e.g. redis library missing),
# we define stub functions so the receiver continues to work exactly as
# before. The correlator is an enhancement layer; its absence must not
# degrade the existing per-event reporting path.
try:
    from correlator_state import source_key, is_suppressed, record_event_diag
    _correlator_enabled = True
except Exception as _e:
    logging.getLogger(__name__).warning(
        f"Correlator integration disabled (import failed): {_e}"
    )
    def source_key(_payload): return "unknown"
    def is_suppressed(_skey): return False
    def record_event_diag(_eid, _out, _rc): return False
    _correlator_enabled = False

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

    try:
        from kafka import KafkaProducer
        import json
        _producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        topic = "snmp.traps" if payload.get("source") == "snmp" else \
                "syslog.events" if payload.get("source") == "syslog" else "raw.alerts"
        _producer.send(topic, value=payload)
        _producer.flush()
        log.info(f"Published to Kafka topic: {topic}")
    except Exception as e:
        log.warning(f"Kafka publish failed (non-fatal): {e}")

    fault_type = classify_alert(alert)
    log.info(f"Classified as: {fault_type}")
    playbook = select_runbook(fault_type)
    diag_out, rc = run_playbook(playbook, alert.source_node,
                                extra_vars={"alert_interface": alert.interface or "eth1"})

    # Record diagnostic context for the correlator to consume when grouping.
    # No-op if correlator integration is disabled or Redis is unreachable.
    record_event_diag(alert.alert_id, diag_out, rc)

    # Suppression check: if the correlator has claimed a lease for this
    # source key, skip the per-event Mattermost report. The correlator
    # will emit a single grouped report covering this and other events
    # in the same window. Fail-safe: if Redis is unreachable, this
    # returns False and per-event reporting continues unchanged.
    skey = source_key(payload)
    if is_suppressed(skey):
        log.info(f"per-event report suppressed by correlator lease for source_key={skey}")
    else:
        send_incident_report(alert, fault_type, playbook or "none", diag_out, rc)
    return jsonify({"status": "processed", "alert_id": alert.alert_id,
                    "fault_type": fault_type, "playbook": playbook, "diag_rc": rc}), 200

if __name__ == "__main__":
    port = int(os.getenv("RECEIVER_PORT", 5000))
    log.info(f"MARR Alert Receiver starting on port {port}")
    log.info(f"Loading .env from: {BASE_DIR / '.env'}")
    log.info(f"Mattermost URL: {os.getenv('MATTERMOST_WEBHOOK_URL', 'NOT SET')}")
    app.run(host="0.0.0.0", port=port, debug=False)

