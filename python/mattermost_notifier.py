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

    # Diag Status reflects per-task outcomes, not just play exit code.
    # Play-level rc can be 0 even when individual tasks failed under
    # ignore_errors: yes - see Section 11 (limitations) for the
    # cleaner refactor (structured task results passed through the
    # function signature rather than text-scraped from stdout).
    failed_tasks = diag_output.count('fatal:')
    ok_tasks = diag_output.count('ok: [') + diag_output.count('changed: [')
    total_tasks = ok_tasks + failed_tasks
    if failed_tasks == 0 and rc == 0:
        status_emoji = ':white_check_mark:'
        status_summary = f'all {total_tasks} task(s) ok'
    elif failed_tasks > 0 and ok_tasks > 0:
        status_emoji = ':warning:'
        status_summary = f'{ok_tasks}/{total_tasks} ok, {failed_tasks} failed'
    else:
        status_emoji = ':x:'
        status_summary = f'{failed_tasks} task(s) failed'
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
        f"| **Diag Status** | {status_emoji} {status_summary} (play rc={rc}) |\n"
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


def send_grouped_incident_report(source_key: str, events: list) -> bool:
    """Send a single grouped Mattermost report covering multiple correlated events.

    events: list of payload dicts (the JSON values consumed from Kafka).
            Each must have at minimum 'id', 'severity', 'uei', 'nodeLabel'.
    Fail-safe: returns False on any error; never raises.
    """
    if not WEBHOOK_URL:
        log.warning("MATTERMOST_WEBHOOK_URL not set - skipping grouped notification.")
        return False
    if not events:
        log.warning("send_grouped_incident_report called with no events - skipping.")
        return False

    # Lazy import: keeps backward compatibility if correlator_state is missing.
    try:
        from correlator_state import fetch_event_diag
    except Exception as _e:
        log.warning(f"correlator_state unavailable for grouped report: {_e}")
        def fetch_event_diag(_eid): return None

    # Highest severity wins for the report header.
    severity_rank = {'CRITICAL': 4, 'MAJOR': 3, 'MINOR': 2, 'WARNING': 1}
    top_sev = max(events, key=lambda e: severity_rank.get(e.get('severity', ''), 0))\
        .get('severity', 'WARNING')
    severity_emoji = SEVERITY_EMOJI.get(top_sev, ':white_circle:')

    # Inferred root cause: earliest event by id ordinality (the snmp-N suffix
    # is monotonic in our pipeline).
    def _id_ordinal(ev):
        try:
            return int(str(ev.get('id', '')).rsplit('-', 1)[-1])
        except Exception:
            return 0
    root = min(events, key=_id_ordinal)

    # Build constituent events table.
    rows = [
        "| ID | Severity | UEI | Node |",
        "|---|---|---|---|",
    ]
    for ev in events:
        rows.append(
            f"| `{ev.get('id','?')}` | {ev.get('severity','?')} "
            f"| `{ev.get('uei','?')}` | `{ev.get('nodeLabel','?')}` |"
        )

    # Collapse diagnostic outputs from Redis (truncated per-event).
    diag_blocks = []
    for ev in events:
        eid = ev.get('id', '')
        d = fetch_event_diag(eid)
        if d is None:
            diag_blocks.append(f"[{eid}] (no diagnostic context recorded)")
            continue
        diag_out, rc = d
        snippet = diag_out[:600]
        diag_blocks.append(f"[{eid}] play rc={rc}\n{snippet}")
    diag_collapsed = "\n---\n".join(diag_blocks)

    message = (
        f"### {severity_emoji} Network Incident (correlated)\n"
        f"**Source key**: `{source_key}`  \n"
        f"**Constituent events**: {len(events)}  \n"
        f"**Top severity**: {top_sev}  \n"
        f"**Inferred root-cause event**: `{root.get('id','?')}` "
        f"(`{root.get('uei','?')}`)\n\n"
        + "\n".join(rows) + "\n\n"
        f"**Collapsed diagnostic context (per event):**\n"
        f"```\n{diag_collapsed[:3500]}\n```"
    )

    try:
        resp = requests.post(WEBHOOK_URL, json={'text': message}, timeout=10)
        resp.raise_for_status()
        log.info(f"Grouped Mattermost notification sent for source_key={source_key} "
                 f"(events={len(events)}).")
        return True
    except requests.RequestException as e:
        log.error(f"Grouped Mattermost notification failed: {e}")
        return False
