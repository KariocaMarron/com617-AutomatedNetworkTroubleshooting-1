from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging
import os
import sys

# Allow imports from the python/ directory
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from models import Alert
from classifier import classify_alert
from runbook_selector import select_runbook
from ansible_runner import run_playbook
from mattermost_notifier import send_incident_report

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'MARR Alert Receiver'}), 200

@app.route('/alert', methods=['POST'])
def receive_alert():
    payload = request.get_json(force=True)
    log.info(f"Alert received: {payload}")

    # 1 — Parse into Alert dataclass
    alert = Alert(
        alert_id    = str(payload.get('id', 'unknown')),
        source_node = payload.get('nodeLabel', payload.get('nodeId', 'unknown')),
        severity    = payload.get('severity', 'UNKNOWN').upper(),
        event_uei   = payload.get('uei', ''),
        description = payload.get('description', ''),
        timestamp   = datetime.now(timezone.utc),
        interface   = payload.get('ifDescr'),
        raw_payload = payload,
    )

    # 2 — Classify fault
    fault_type = classify_alert(alert)
    log.info(f"Classified as: {fault_type}")

    # 3 — Select and run Ansible playbook
    playbook = select_runbook(fault_type)
    diag_out, rc = run_playbook(
        playbook,
        alert.source_node,
        extra_vars={'alert_interface': alert.interface or 'eth1'}
    )

    # 4 — Send report to Mattermost
    send_incident_report(alert, fault_type, playbook or 'none', diag_out, rc)

    return jsonify({
        'status'    : 'processed',
        'alert_id'  : alert.alert_id,
        'fault_type': fault_type,
        'playbook'  : playbook,
        'diag_rc'   : rc
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('RECEIVER_PORT', 5000))
    log.info(f"MARR Alert Receiver starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
