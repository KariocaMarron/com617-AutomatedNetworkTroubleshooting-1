#!/usr/bin/env python3
import requests, json, time, subprocess, os
from datetime import datetime, timezone

OPENNMS_URL = "http://localhost:8980/opennms"
OPENNMS_USER = "admin"
OPENNMS_PASS = "admin"
ANSIBLE_DIR = "/home/cyber/Solent_Final_Lab/ansible"
REPORTS_DIR = "/home/cyber/Solent_Final_Lab/reports"
POLL_INTERVAL = 10

MATTERMOST_WEBHOOK = "http://172.21.0.31:8065/hooks/qn84n14hxjn5u8mjb79rqq7k4a"
SEVERITY_EMOJI = {
    "critical": ":red_circle:",
    "major":    ":large_orange_circle:",
    "normal":   ":large_green_circle:"
}
processed_events = set()

RULES = {
    "SNMP_Link_Down":  {"fault": "link-down",  "severity": "major",    "playbook": "diagnose_link_down.yml"},
    "SNMP_Link_Up":    {"fault": "link-up",     "severity": "normal",   "playbook": "diagnose_link_down.yml"},  # reuse if needed
    "EnterpriseDefault":{"fault": "bgp-change", "severity": "major",    "playbook": "diagnose_bgp_neighbour_loss.yml"},
    "nodeDown":        {"fault": "node-down",   "severity": "critical", "playbook": "diagnose_high_cpu.yml"}   # temporary mapping
}

#RULES = {
#    "SNMP_Link_Down":  {"fault": "link-down",  "severity": "major",    "playbook": "diagnose-link-down.yml"},
#    "SNMP_Link_Up":    {"fault": "link-up",     "severity": "normal",   "playbook": "diagnose-link-up.yml"},
#    "EnterpriseDefault":{"fault": "bgp-change", "severity": "major",    "playbook": "diagnose-bgp.yml"},
#    "nodeDown":        {"fault": "node-down",   "severity": "critical", "playbook": "diagnose-node-down.yml"},
#}

def get_events():
    try:
        r = requests.get(f"{OPENNMS_URL}/rest/events",
            auth=(OPENNMS_USER, OPENNMS_PASS),
            headers={"Accept": "application/json"}, 
            params={"limit": 20, "orderBy": "eventTime", "order": "desc"},
            timeout=5)
        return r.json().get("event", []) if r.status_code == 200 else []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def classify(event):
    uei = event.get("uei", "")
    for key, rule in RULES.items():
        if key in uei:
            return rule
    return None

def run_playbook(playbook, node_ip, fault):
    path = f"{ANSIBLE_DIR}/playbooks/{playbook}"
    if not os.path.exists(path):
        return {"status": "skipped", "reason": "playbook not found"}
    try:
        r = subprocess.run(["ansible-playbook", "-i", f"{ANSIBLE_DIR}/inventory.yml", path,
            "-e", f"target={node_ip}", "-e", f"fault={fault}"],
            capture_output=True, text=True, timeout=60)
        return {"status": "ok" if r.returncode == 0 else "failed", "out": r.stdout[-300:]}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

def get_node_name(event):
    if event.get("nodeLabel"):
        return event["nodeLabel"]
    for p in event.get("parameters", []):
        if p.get("name", "").lower() == "nodelabel":
            return p.get("value")
    if event.get("ipAddress"):
        return event["ipAddress"]
    if event.get("source"):
        return event["source"]
    return "unknown"

def save_report(event, rule, result):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report = {
        "id": f"MARR-{event.get('id')}",
        "time": datetime.now(timezone.utc).isoformat(),
        "fault": rule["fault"],
        "severity": rule["severity"],
        "node": get_node_name(event),
        "source": event.get("ipAddress") or event.get("source", "unknown"),
        "uei": event.get("uei"),
        "diagnostics": result
    }
    path = f"{REPORTS_DIR}/report-{report['id']}.json"
    json.dump(report, open(path, "w"), indent=2)
    print(f"  [REPORT] {path}")
    return report

def notify_mattermost(report):
    emoji = SEVERITY_EMOJI.get(report["severity"], ":white_circle:")
    text = (
        f"{emoji} **MARR ALERT — {report['fault'].upper()}**\n"
        f"| Field | Value |\n"
        f"|---|---|\n"
        f"| Report ID | `{report['id']}` |\n"
        f"| Node | `{report['node']}` |\n"
        f"| Source | `{report['source']}` |\n"
        f"| Severity | {report['severity']} |\n"
        f"| Fault | {report['fault']} |\n"
        f"| Diagnostics | {report['diagnostics']['status']} |\n"
        f"| Time | {report['time']} |"
    )
    try:
        r = requests.post(MATTERMOST_WEBHOOK,
            json={"text": text, "username": "MARR-Bot", "icon_emoji": ":robot:"},
            timeout=5)
        if r.status_code == 200:
            print(f"  [MATTERMOST] Notification sent")
        else:
            print(f"  [MATTERMOST] Failed: {r.status_code}")
    except Exception as e:
        print(f"  [MATTERMOST] Error: {e}")
def process(event):
    eid = event.get("id")
    if eid in processed_events:
        return
    rule = classify(event)
    if not rule:
        return
    processed_events.add(eid)
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {rule['fault'].upper()} | node={get_node_name(event)} | severity={rule['severity']}")
    result = run_playbook(rule["playbook"], event.get("ipAddress","unknown"), rule["fault"])
    report = save_report(event, rule, result)
    notify_mattermost(report)

#def save_report(event, rule, result):
#    os.makedirs(REPORTS_DIR, exist_ok=True)
#    report = {
#        "id": f"MARR-{event.get('id')}",
#        "time": datetime.now(timezone.utc).isoformat(),
#        "fault": rule["fault"],
#        "severity": rule["severity"],
#        "node": event.get("nodeLabel", "unknown"),
#        "node": event.get("nodeLabel", "unknown"),
#        "source": event.get("ipAddress", "unknown"),
#        "source": event.get("ipAddress", "unknown"),
#        "uei": event.get("uei"),
#        "diagnostics": result
#    }
#    path = f"{REPORTS_DIR}/report-{report['id']}.json"
#    json.dump(report, open(path, "w"), indent=2)
#    print(f"  [REPORT] {path}")
#    return report

#def process(event):
#    eid = event.get("id")
#    if eid in processed_events:
#        return
#    rule = classify(event)
#    if not rule:
#        return
#    processed_events.add(eid)
#    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {rule['fault'].upper()} | node={event.get('nodeLabel')} | severity={rule['severity']}")
#    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {rule['fault'].upper()} | node={event.get('nodeLabel')} | severity={rule['severity']}")
#    result = run_playbook(rule["playbook"], event.get("ipAddress","unknown"), rule["fault"])
#    report = save_report(event, rule, result)
    notify_mattermost(report)

def main():
    print("="*50)
    print("  MARR Engine | COM617 Group 15")
    print(f"  Polling OpenNMS every {POLL_INTERVAL}s")
    print("="*50)
    while True:
        for e in get_events():
            process(e)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()

# Jose Vasconcelos - March 2026


