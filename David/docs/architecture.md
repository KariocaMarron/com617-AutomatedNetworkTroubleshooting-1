# System Architecture – Automated Network Troubleshooting

## 1. Overview
This project uses a modular architecture to detect network faults, execute automated diagnostics, and deliver structured troubleshooting reports.

## 2. Main Components
- Containerlab: provides the simulated network environment
- OpenNMS: monitors the network and generates alerts
- Python logic layer: receives alerts, classifies faults, and selects the appropriate runbook
- Ansible: executes diagnostic commands automatically
- Mattermost: receives structured incident reports

## 3. System Workflow
1. A fault occurs in the Containerlab network
2. OpenNMS detects the event and generates an alert
3. The Python logic layer analyses the alert
4. The correct runbook/playbook is selected
5. Ansible executes the diagnostic commands
6. The results are formatted into a report
7. The report is sent to Mattermost or another output channel

## 4. Supported Faults
- Interface up/down
- Neighbour change

## 5. Scope Notes
This architecture is designed as a Proof of Concept and focuses on automated diagnostics rather than automated remediation.
