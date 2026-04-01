# MARR Lab — Automated Network Alert Triage, Diagnostics, and Reporting

**COM617 Industrial Consulting Project — Group 15**
**Industry Sponsor: Cisco Systems (James Whale, SRE)**
**Southampton Solent University — 2025/26**

---

## Overview

MARR (Monitor, Analyse, Report, Respond) is an automated network alert triage system that:

- Ingests SNMP traps from simulated network devices via OpenNMS
- Classifies fault events by type and severity
- Executes Ansible diagnostic playbooks automatically
- Generates structured JSON incident reports
- Delivers real-time alerts to Mattermost

---

## Team

| Name | Role |
|---|---|
| Jose Batalha De Vasconcelos | Scrum Master |
| Biloliddin Turaev | Lead Developer |
| Akinwunmi Rotimi | QA Lead |
| Akinwunmi Kayode | Systems Integration |

---

## Architecture
```
Fault Injection Script
        |
        v
SNMP Trap → OpenNMS Horizon (event storage)
        |
        v
Python Classifier (polls REST API every 10s)
        |
        v
Ansible Diagnostic Playbook (docker exec → vtysh)
        |
        v
JSON Report (/reports/) + Mattermost Alert
```

### Network

| Component | IP | Port |
|---|---|---|
| OpenNMS Horizon | 172.21.0.11 | 8980 (HTTP), 1162 (SNMP traps) |
| Mattermost | 172.21.0.31 | 8065 |
| router1 (FRRouting AS65001) | 172.21.0.101 | — |
| router2 (FRRouting AS65002) | 172.21.0.102 | — |
| router3 (FRRouting AS65003) | 172.21.0.103 | — |
| Docker network | marr-net | 172.21.0.0/16 |

---

## Prerequisites

- Ubuntu 22.04+
- Docker and Docker Compose
- Containerlab 0.74+
- Python 3.10+
- Ansible 2.14+
- `community.docker` Ansible collection

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1.git
cd com617-AutomatedNetworkTroubleshooting-1
```

### 2. Create the Docker network
```bash
docker network create \
  --driver bridge \
  --subnet 172.21.0.0/16 \
  --gateway 172.21.0.1 \
  marr-net
```

### 3. Start the lab
```bash
./scripts/start-lab.sh
```

This starts OpenNMS, Mattermost, deploys the Containerlab topology, and launches the classifier engine.

### 4. Access the interfaces

| Interface | URL | Credentials |
|---|---|---|
| OpenNMS | http://localhost:8980 | admin / admin |
| Mattermost | http://localhost:8065 | Set during first login |

### 5. Stop the lab
```bash
./scripts/stop-lab.sh
```

---

## Fault Injection

Inject test faults to trigger the full pipeline:
```bash
# Link down on router1
./scripts/inject-fault.sh link-down router1

# Link recovery
./scripts/inject-fault.sh link-up router1

# BGP session clear on router2
./scripts/inject-fault.sh bgp-down router2

# Node down (stops container)
./scripts/inject-fault.sh node-down router3

# Node recovery
./scripts/inject-fault.sh node-up router3
```

---

## Fault Scenarios

| Scenario | Trigger | Classifier Action | Playbook |
|---|---|---|---|
| Link Down | SNMP linkDown trap | Classifies as `link-down` / major | `diagnose-link-down.yml` |
| BGP Change | SNMP EnterpriseDefault trap | Classifies as `bgp-change` / major | `diagnose-bgp.yml` |
| Node Down | SNMP trap + container stop | Classifies as `node-down` / critical | `diagnose-node-down.yml` |

---

## Directory Structure
```
Solent_Final_Lab/
├── opennms/
│   ├── horizon/          # OpenNMS + PostgreSQL + ActiveMQ compose
│   └── overlay/          # OpenNMS config overrides
├── containerlab/
│   ├── lab-topology.yml  # Three-router BGP topology
│   └── configs/          # FRRouting and SNMP configs per router
├── python-engine/
│   └── classifier.py     # Main classification engine
├── ansible/
│   ├── inventory.yml     # Router inventory
│   └── playbooks/        # Diagnostic playbooks
├── mattermost/
│   └── docker-compose.yml
├── reports/              # Generated JSON incident reports
├── scripts/
│   ├── start-lab.sh
│   ├── stop-lab.sh
│   └── inject-fault.sh
└── logs/                 # Classifier runtime logs
```

---

## Classifier Engine

The classifier polls the OpenNMS REST API every 10 seconds. For each new event:

1. Matches the event UEI against the classification rules
2. Selects the appropriate Ansible playbook
3. Executes the playbook via `ansible-playbook`
4. Saves a JSON report to `/reports/`
5. Posts a structured alert to Mattermost
6. Records the event ID to `.processed_events` to prevent duplicate processing

---

## Repositories

| Repository | URL |
|---|---|
| Personal | https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1 |
| Organisation | https://github.com/com617-industrial-2025-1/com617-AutomatedNetworkTroubleshooting-1 |

---

## Known Limitations

- Test environment uses Containerlab with FRRouting — results are simulation-derived and not validated against live Cisco infrastructure
- SNMP agent not embedded in router containers — traps are sent via dedicated injection script
- Python classifier uses a single process — horizontal scaling via RabbitMQ is identified as future work
- Ansible diagnostic output depends on `docker exec` access to Containerlab containers

---

## Acknowledgements

Industry Sponsor: James Whale, Cisco Systems SRE
Academic Tutor: Craig Gallen, Southampton Solent University
