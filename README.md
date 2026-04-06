# MARR Lab - Automated Network Alert Triage, Diagnostics, and Reporting

**COM617 Industrial Consulting Project - Group 15**
**Industry Sponsor: Cisco Systems (James Whale, SRE)**
**Academic Supervisor: Craig Gallen, Southampton Solent University**
**Submission Deadline: 8 May 2026**
**Current Release: v4.0**

---

## Overview

MARR (Monitor, Analyse, React, Report) is an automated network alert triage,
diagnostics, and engineer-ready reporting system built for Cisco Systems as
part of COM617 Industrial Consulting Project at Southampton Solent University.

The system ingests SNMP traps and syslog messages from a simulated three-site
network, classifies fault events, executes automated Netmiko diagnostics,
publishes alerts to Kafka, and delivers structured incident reports to
Mattermost. OpenNMS Horizon (Main PYU) monitors all three sites via dedicated
remote minions at Hamhung and Chongjin.

---

## Team

| Name | Role |
|---|---|
| Jose Batalha De Vasconcelos | Scrum Master |
| Biloliddin Turaev | Lead Developer |
| Akinwunmi Rotimi | QA Lead |
| Akinwunmi Kayode | Systems Integration |

---

## Three-Site Architecture


Main PYU
          OpenNMS Horizon (172.21.0.11)
          ActiveMQ (172.21.0.9)
          router1 (172.21.0.101)
          router2 (172.21.0.102)
          router3 (172.21.0.103)
                |
      +---------+---------+
      |                   |
 Hamhung site        Chongjin site

hamhung-minion-01    chongjin-minion-01
(172.21.0.20)        (172.21.0.21)
hamhung-router       chongjin-router
(172.21.0.111)       (172.21.0.121)


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
| Network monitoring | OpenNMS Horizon 33.0.2 (Main PYU) | 8980/tcp |
| Remote monitoring | OpenNMS Minion 33.0.2 x2 | Internal only |
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
| marr-net | 172.21.0.0/16 | OpenNMS, Mattermost, Minions, FRR routers |

### IP Allocation

| Container | IP | Role |
|---|---|---|
| marr-activemq | 172.21.0.9 | ActiveMQ broker - minion IPC |
| marr-postgres | 172.21.0.10 | OpenNMS database |
| marr-horizon (Main PYU) | 172.21.0.11 | OpenNMS Horizon core |
| clab-marr-lab-snmp-notifier | 172.21.0.14 | SNMP trap receiver |
| hamhung-minion | 172.21.0.20 | Hamhung site remote minion |
| chongjin-minion | 172.21.0.21 | Chongjin site remote minion |
| marr-mattermost-db | 172.21.0.30 | Mattermost database |
| marr-mattermost | 172.21.0.31 | Notifications |
| clab-marr-lab-router1 | 172.21.0.101 | FRR router - Main PYU site |
| clab-marr-lab-router2 | 172.21.0.102 | FRR router - Main PYU site |
| clab-marr-lab-router3 | 172.21.0.103 | FRR router - Main PYU site |
| clab-marr-lab-hamhung-router | 172.21.0.111 | FRR router - Hamhung site |
| clab-marr-lab-chongjin-router | 172.21.0.121 | FRR router - Chongjin site |

### Port Register

| Port | Protocol | Service |
|---|---|---|
| 162 | UDP | SNMP trap receiver (inside snmp-notifier) |
| 514 | UDP | Syslog receiver (host systemd) |
| 1162 | UDP | OpenNMS SNMP internal |
| 3000 | TCP | Grafana |
| 5000 | TCP | Alert receiver |
| 6380 | TCP | Lab Redis |
| 8065 | TCP | Mattermost |
| 8161 | TCP | ActiveMQ web console |
| 8200 | TCP | HashiCorp Vault |
| 8980 | TCP | OpenNMS Horizon (Main PYU) |
| 9090 | TCP | Prometheus |
| 9092 | TCP | Kafka |
| 61616 | TCP | ActiveMQ broker (internal only) |

---

## Prerequisites

- Ubuntu 22.04 or later
- Docker and Docker Compose v2
- Containerlab 0.74 or later
- Python 3.10 or later
- Ansible 2.14 or later with community.docker collection

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1.git
cd com617-AutomatedNetworkTroubleshooting-1
```

### 2. Create required Docker networks
```bash
docker network create --driver bridge --subnet 172.22.0.0/24 marr-reporting
docker network create --driver bridge --subnet 172.21.0.0/16 marr-net
```

### 3. Configure environment variables
```bash
cp .env.example .env
nano .env
```

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

### 6. Build custom snmp-notifier image
```bash
docker build -t marr-snmp-notifier:v1 containerlab/snmp-notifier/
```

---

## Starting the Lab
```bash
ansible-playbook scripts/lab-start.yml
```

### Startup sequence and timing

| Step | Service | Max wait |
|---|---|---|
| 1 | Platform services and Mattermost | 360 seconds |
| 2 | OpenNMS Horizon (Main PYU) | 600 seconds |
| 3 | Containerlab topology (5 routers + snmp-notifier) | 35 seconds |
| 4 | SNMP listener inside snmp-notifier | Immediate |
| 5 | Systemd services (receiver, syslog, snmp) | Immediate |
| 6 | Minions (Hamhung and Chongjin) | 360 seconds to register |
| 7 | Health checks | 10 seconds each |
| 8 | Port inventory | Immediate |

---

## Stopping the Lab
```bash
ansible-playbook scripts/lab-stop.yml
```

Full wipe including Docker volumes:
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

## Kafka Topics

| Topic | Routing condition |
|---|---|
| snmp.traps | source field equals snmp |
| syslog.events | source field equals syslog |
| raw.alerts | all other alerts |

---

## Fault Scenarios

| Fault type | Detection | Runbook |
|---|---|---|
| Link down | SNMP linkDown trap | diagnose_link_down |
| BGP change | SNMP bgp trap | diagnose_bgp |
| OSPF neighbour down | Syslog message | diagnose_ospf |
| Node unreachable | SNMP nodeDown trap | diagnose_node_down |

---

## Access Interfaces

| Interface | URL | Credentials |
|---|---|---|
| OpenNMS (Main PYU) | http://localhost:8980/opennms | admin / admin |
| Mattermost | http://localhost:8065 | Set on first login |
| Grafana | http://localhost:3000 | admin / marr2026 |
| Prometheus | http://localhost:9090 | None |
| Vault | http://localhost:8200 | Token from .env |
| ActiveMQ | http://localhost:8161 | admin / admin |

---

## Version History

| Tag | Description |
|---|---|
| v1.0 | Initial lab: OpenNMS, Mattermost, SNMP classification, Containerlab |
| v2.0 | Platform upgrade: Prometheus, Grafana, Kafka, Vault, Redis, real-world ports |
| v3.0 | Full audit: custom snmp-notifier image, correct container names, network IPs |
| v4.0 | Minion integration: three-site architecture, Main PYU, Hamhung, Chongjin |

---

## Known Limitations

- Redis runs on port 6380 as system Redis occupies 6379
- Vault runs in dev mode - secrets lost on container restart
- Kafka single broker with replication factor 1 - no message durability
- OpenNMS takes 5 to 8 minutes to start on cold boot
- Minions take 3 to 5 minutes to register after Horizon starts
- All fault injection is synthetic - not validated against live Cisco infrastructure

---

## Repositories

| Repository | URL |
|---|---|
| Personal | https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1 |
| Team | https://github.com/com617-industrial-2025-1/com617-AutomatedNetworkTroubleshooting-1 |

---

*Author: Jose Batalha De Vasconcelos - COM617 Group 15 - April 2026*
