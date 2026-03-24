import requests
import os
import logging
from models import Alert

log = logging.getLogger(__name__)

WEBHOOK_URL = os.getenv('MATTERMOST_WEBHOOK_URL', '')

SEVERITY_EMOJI = {
    'CRITICAL': ':red_circle:',
    'MAJOR':    ':orange_circle:',
    'MINOR':    ':yellow_circle:',
    'WARNING':  ':white_circle:',
}

def send_incident_report(
    alert: Alert,
    fault_type: str,
    playbook: str,
    diag_output: str,
    rc: int
) -> bool:
    """Send a structured incident report to Mattermost via webhook."""
    if not WEBHOOK_URL:
        log.warning("MATTERMOST_WEBHOOK_URL not set — skipping notification.")
        return False

    status_emoji = ':white_check_mark:' if rc == 0 else ':x:'
    severity_emoji = SEVERITY_EMOJI.get(alert.severity, ':white_circle:')

    message = (
        f"### {severity_emoji} Network Incident Report\n"
        f"| Field | Value |\n"
        f"|---|---|\n"
        f"| **Alert ID** | `{alert.alert_id}` |\n"
        f"| **Node** | `{alert.source_node}` |\n"
        f"| **Severity** | {alert.severity} |\n"
        f"| **Fault Type** | `{fault_type}` |\n"
        f"| **Timestamp** | {alert.timestamp.isoformat()}Z |\n"
        f"| **Playbook** | `{playbook}` |\n"
        f"| **Diag Status** | {status_emoji} rc={rc} |\n"
        f"\n**Description:** {alert.description}\n"
        f"\n**Diagnostic Output:**\n```\n{diag_output[:2000]}\n```"
    )

    try:
        resp = requests.post(
            WEBHOOK_URL,
            json={'text': message},
            timeout=10
        )
        resp.raise_for_status()
        log.info("Mattermost notification sent successfully.")
        return True
    except requests.RequestException as e:
        log.error(f"Mattermost notification failed: {e}")
        return False
