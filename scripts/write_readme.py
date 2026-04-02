import os

readme = """# MARR Lab - Automated Network Alert Triage, Diagnostics, and Reporting

**COM617 Industrial Consulting Project - Group 15**
**Industry Sponsor: Cisco Systems (James Whale, SRE)**
**Academic Supervisor: Craig Gallen, Southampton Solent University**
**Submission Deadline: 8 May 2026**

---

## Overview

MARR (Monitor, Analyse, React, Report) is an automated network alert triage,
diagnostics, and engineer-ready reporting system built for Cisco Systems as
part of COM617 Industrial Consulting Project at Southampton Solent University.

The system ingests SNMP traps and syslog messages from simulated FRRouting
network devices, classifies fault events by type and severity, executes
automated Netmiko diagnostic playbooks, publishes all alerts to Kafka, and
delivers structured incident reports to Mattermost.

---

## Team

| Name | Role |
|---|---|
| Jose Batalha De Vasconcelos | Scrum Master |
| Biloliddin Turaev | Lead Developer |
| Akinwunmi Rotimi | QA Lead |
| Akinwunmi Kayode | Systems Integration |

---

## Pipeline Architecture

SNMP trap (UDP 162)          Syslog (UDP 514)
|                           |
v                           v
snmp_listener.py          syslog_listener.py
inside snmp-notifier       host systemd service
|                           |
+-----------+---------------+
|
v
alert_receiver.py
Flask on port 5000
|
+----------+----------+
|                     |
v                     v
Kafka topics          classify_alert()
raw.alerts                  |
snmp.traps                  v
syslog.events         select_runbook()
|
v
run_playbook()
via Netmiko SSH
|
v
send_incident_report()
|
v
Mattermost

---

## Technology Stack

| Component | Technology | Port |
|---|---|---|
| Alert receiver | Python Flask | 5000/tcp |
| SNMP ingestion | pysnmp inside snmp-notifier | 162/udp |
| Syslog ingestion | Python socket via systemd | 514/udp |
| Message broker | Apache Kafka 7.6.0 | 9092/tcp |
| Network monitoring | OpenNMS Horizon 33.0.2 | 8980/tcp |
| Notifications | Mattermost 9.4 | 8065/tcp |
| Metrics | Prometheus 2.51.0 | 9090/tcp |
| Dashboards | Grafana 10.4.0 | 3000/tcp |
| Secrets management | HashiCorp Vault 1.16.1 | 8200/tcp |
| Cache | Redis 7.2 | 6380/tcp |
| Message bus | ActiveMQ 5.18.3 | 61616/tcp |
| Network simulation | Containerlab + FRRouting v8.4.1 | - |
| Diagnostics | Netmiko 4.6.0 | SSH |
| Automation | Ansible | - |

---

## Network Architecture

### Docker Networks

| Network | Subnet | Purpose |
|---|---|---|
| solent_final_lab_marr-reporting | 172.22.0.0/24 | Platform services |
| marr-net | 172.21.0.0/16 | OpenNMS, Mattermost, FRR routers |
| marr-mgmt | 172.20.0.0/24 | Containerlab management |

### Running Containers

| Container | Image | Port | Network |
|---|---|---|---|
| marr-prometheus | prom/prometheus:v2.51.0 | 9090/tcp | marr-reporting |
| marr-grafana | grafana/grafana:10.4.0 | 3000/tcp | marr-reporting |
| marr-redis | redis:7.2-alpine | 6380/tcp | marr-reporting |
| marr-vault | hashicorp/vault:1.16.1 | 8200/tcp | marr-reporting |
| marr-kafka | confluentinc/cp-kafka:7.6.0 | 9092/tcp | marr-reporting |
| marr-mattermost | mattermost-team-edition:9.4 | 8065/tcp | marr-net |
| marr-mattermost-db | postgres:14 | 5432/tcp | marr-net |
| marr-horizon | opennms/horizon:33.0.2 | 8980/tcp | marr-net |
| marr-activemq | activemq-classic:5.18.3 | 61616/tcp | marr-net |
| marr-postgres | postgres:14 | 5432/tcp | marr-net |
| clab-marr-lab-router1 | marr-frr-snmp:v1 | 172.21.0.101 | marr-mgmt |
| clab-marr-lab-router2 | marr-frr-snmp:v1 | 172.21.0.102 | marr-mgmt |
| clab-marr-lab-router3 | marr-frr-snmp:v1 | 172.21.0.103 | marr-mgmt |
| clab-com617-marr-lab-snmp-notifier | ubuntu:22.04 | 162/udp | marr-mgmt |

### Port Register

| Port | Protocol | Service |
|---|---|---|
| 162 | UDP | SNMP trap receiver (inside snmp-notifier) |
| 514 | UDP | Syslog receiver (host systemd) |
| 1162 | UDP | OpenNMS SNMP internal |
| 3000 | TCP | Grafana |
| 5000 | TCP | Alert receiver |
| 6379 | TCP | System Redis (localhost only) |
| 6380 | TCP | Lab Redis (Docker) |
| 8065 | TCP | Mattermost |
| 8161 | TCP | ActiveMQ web console |
| 8200 | TCP | HashiCorp Vault |
| 8980 | TCP | OpenNMS Horizon |
| 9090 | TCP | Prometheus |
| 9092 | TCP | Kafka |
| 10514 | UDP | OpenNMS syslog internal |
| 61616 | TCP | ActiveMQ broker |

---

## Prerequisites

- Ubuntu 22.04 or later
- Docker and Docker Compose v2
- Containerlab 0.74 or later
- Python 3.10 or later
- Ansible 2.14 or later with community.docker collection
- Node.js 20 or later (for document generation scripts)

---

## Installation

### 1. Clone both repositories
```bash
git clone https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1.git
cd com617-AutomatedNetworkTroubleshooting-1
```

### 2. Create required Docker networks
```bash
docker network create --driver bridge --subnet 172.22.0.0/24 marr-reporting
docker network create --driver bridge --subnet 172.21.0.0/16 marr-net
docker network create --driver bridge --subnet 172.20.0.0/24 marr-mgmt
```

### 3. Configure environment variables
```bash
cp .env.example .env
nano .env
```

Set MATTERMOST_WEBHOOK_URL and VAULT_DEV_ROOT_TOKEN_ID at minimum.

### 4. Install Python dependencies
```bash
pip3 install flask requests pysnmp fastavro kafka-python locust hvac python-dotenv netmiko prometheus-client --break-system-packages
```

### 5. Install systemd services
```bash
sudo cp systemd/marr-receiver.service /etc/systemd/system/
sudo cp systemd/marr-syslog.service /etc/systemd/system/
sudo cp systemd/marr-snmp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable marr-receiver marr-syslog marr-snmp
```

---

## Starting the Lab

### Recommended - full Ansible startup
```bash
ansible-playbook scripts/lab-start.yml
```

The playbook runs 7 steps in sequence with health check waiting at each stage.

### Alternative - direct Docker start
```bash
make docker-up
```

### Expected startup times

| Service | Typical wait |
|---|---|
| Prometheus, Grafana, Vault, Kafka | Under 10 seconds |
| Redis | Under 5 seconds |
| Mattermost | 30 to 60 seconds |
| OpenNMS Horizon | 5 to 8 minutes |
| FRR routers and OSPF | 35 seconds |

---

## Stopping the Lab

### Normal shutdown - data preserved
```bash
ansible-playbook scripts/lab-stop.yml
```

### Full wipe - removes all Docker volumes
```bash
ansible-playbook scripts/lab-stop.yml --extra-vars "wipe_data=true"
```

---

## Makefile Quick Reference
```bash
make start      # Full Ansible startup
make stop       # Full Ansible shutdown
make restart    # Stop then start
make wipe       # Stop and remove all volumes
make docker-up  # Direct Docker Compose start
make status     # Full lab status
make logs       # Recent logs from all listeners
make test       # Send test alert
make snmp       # Send live SNMP trap from router1
make syslog     # Send live syslog from router1
make kafka      # List topics and show last message
```

---

## Directory Structure


Solent_Final_Lab/
├── containerlab/
│   ├── lab-topology.yml           # Three-router FRR topology
│   └── configs/                   # FRRouting configs per router
├── docs/
│   ├── COM617_Group15_Lab_Implementation_Log_v3.docx
│   └── Sprint1_Deliverables_v4.docx
├── mattermost/
│   └── docker-compose.yml         # Mattermost and PostgreSQL
├── monitoring/
│   └── prometheus.yml             # Prometheus scrape config
├── opennms/
│   └── horizon/
│       ├── docker-compose.yml     # OpenNMS, ActiveMQ, PostgreSQL
│       └── overlay/               # OpenNMS config overrides
├── python/
│   ├── alert_receiver.py          # Flask ingestion endpoint
│   ├── snmp_listener.py           # SNMP trap receiver
│   ├── syslog_listener.py         # Syslog receiver
│   ├── classifier.py              # Fault classification engine
│   ├── runbook_selector.py        # Runbook mapping
│   ├── ansible_runner.py          # Diagnostic executor
│   ├── mattermost_notifier.py     # Incident reporter
│   ├── models.py                  # Alert data model
│   ├── cao_schema.py              # Avro schema validation
│   └── locustfile.py              # Load testing
├── ansible/
│   ├── inventory.yml              # Router inventory
│   └── playbooks/                 # Diagnostic playbooks
├── scripts/
│   ├── lab-start.yml              # Ansible startup playbook (7 steps)
│   ├── lab-stop.yml               # Ansible shutdown playbook
│   ├── write_compose.py           # Compose file utility
│   └── write_readme.py            # README generator
├── systemd/
│   ├── marr-receiver.service      # Alert receiver service unit
│   ├── marr-syslog.service        # Syslog listener service unit
│   └── marr-snmp.service          # SNMP listener service unit
├── reports/                       # Generated JSON incident reports
├── logs/                          # Runtime logs
├── docker-compose.yml             # Platform services
├── Makefile                       # Lab shortcuts
├── .env.example                   # Environment variable template
└── README.md


---

## Environment Variables

Copy .env.example to .env and configure all variables before starting.

| Variable | Purpose | Default |
|---|---|---|
| VAULT_DEV_ROOT_TOKEN_ID | HashiCorp Vault root token | - |
| POSTGRES_USER | Mattermost database user | mattermost |
| POSTGRES_PASSWORD | Mattermost database password | - |
| POSTGRES_DB | Mattermost database name | mattermost |
| MATTERMOST_WEBHOOK_URL | Incoming webhook for notifications | - |
| VAULT_ADDR | Vault server address | http://127.0.0.1:8200 |
| KAFKA_BOOTSTRAP_SERVERS | Kafka broker address | localhost:9092 |
| RECEIVER_PORT | Alert receiver port | 5000 |

---

## Kafka Topics

| Topic | Source | Routing condition |
|---|---|---|
| snmp.traps | SNMP traps | source field equals snmp |
| syslog.events | Syslog messages | source field equals syslog |
| raw.alerts | All other alerts | default catch-all |

---

## Fault Scenarios

| Fault type | Detection method | Runbook |
|---|---|---|
| Link down | SNMP linkDown trap | diagnose_link_down |
| BGP change | SNMP bgp trap | diagnose_bgp |
| OSPF neighbour down | Syslog message | diagnose_ospf |
| Node unreachable | SNMP nodeDown trap | diagnose_node_down |

---

## Testing

### Send a test alert
```bash
make test
```

### Send a live SNMP trap from router1
```bash
make snmp
```

### Send a live syslog message from router1
```bash
make syslog
```

### Verify Kafka received the alert
```bash
make kafka
```

---

## Access Interfaces

| Interface | URL | Default credentials |
|---|---|---|
| OpenNMS | http://localhost:8980/opennms | admin / admin |
| Mattermost | http://localhost:8065 | Set on first login |
| Grafana | http://localhost:3000 | admin / marr2026 |
| Prometheus | http://localhost:9090 | None |
| Vault | http://localhost:8200 | Token from .env |
| ActiveMQ | http://localhost:8161 | admin / admin |

---

## Known Limitations

- Redis runs on port 6380 as system Redis occupies 6379
- Vault runs in dev mode - secrets are lost on container restart
- Kafka single broker with replication factor 1 - no message durability
- OpenNMS takes 5 to 8 minutes to start on cold boot
- All fault injection is synthetic - results not validated against live Cisco infrastructure
- Kubernetes HA not implemented - no horizontal scaling

---

## Repositories

| Repository | URL |
|---|---|
| Personal | https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1 |
| Team | https://github.com/com617-industrial-2025-1/com617-AutomatedNetworkTroubleshooting-1 |

---

*Author: Jose Batalha De Vasconcelos - COM617 Group 15 - 2 April 2026*
"""

path = '/home/cyber/Solent_Final_Lab/README.md'
with open(path, 'w') as f:
    f.write(readme)
print("Done - " + str(len(readme)) + " characters written")


# Author: Jose Batalha De Vasconcelos - COM617 Group 15
