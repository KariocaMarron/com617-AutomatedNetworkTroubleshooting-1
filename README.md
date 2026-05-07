# MARR Lab - Automated Network Alert Triage, Diagnostics, and Reporting

**COM617 Industrial Consulting Project - Group 15**
**Industry Sponsor: Cisco Systems (James Whale, SRE)**
**Academic Supervisor: Craig Gallen, Southampton Solent University**
**Submission Deadline: 8 May 2026**
**Current Release: v4.0**

---

## Overview

MARR (Monitor, Analyse, React, Report) is an automated network alert triage,
diagnostics, and an engineer-ready reporting system built for Cisco Systems as
part of the COM617 Industrial Consulting Project at Southampton Solent University.

The system ingests SNMP traps and syslog messages from a simulated three-site
network, classifies fault events, executes automated Ansible diagnostics,
publishes alerts to Kafka, and delivers structured incident reports to
Mattermost. OpenNMS Horizon (Main Solent) monitors all three sites via dedicated
remote minions at Solent-2 and Solent-1.

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

```
Main Solent
  OpenNMS Horizon (172.21.0.11)
  ActiveMQ       (172.21.0.9)
  router1        (172.21.0.101)  AS 65001
  router2        (172.21.0.102)  AS 65002
  router3        (172.21.0.103)  AS 65003
        |
  +-----+-----+
  |           |
Solent-2     Solent-1
solent-2-minion-01 (172.21.0.20)    solent-1-minion-01 (172.21.0.21)
solent-2-router    (172.21.0.111)   AS 65004
                                   solent-1-router    (172.21.0.121)   AS 65005
```

BGP sessions: full mesh between AS 65001-65002-65003, plus 65001-65004 and 65002-65005.

---

## Pipeline Architecture

```
SNMP trap (UDP 162)        Syslog (UDP 514)
        |                          |
        v                          v
snmp_listener.py         syslog_listener.py
inside snmp-notifier      host systemd service
        |                          |
        +------------+-------------+
                     |
                     v
             alert_receiver.py
              Flask on port 5000
                     |
          +----------+----------+
          |                     |
          v                     v
    Kafka publish          classify_alert()
    raw.alerts / snmp.traps      |
    syslog.events                v
                          select_runbook()
                                 |
                                 v
                          run_playbook()
                          Ansible via docker exec
                                 |
                                 v
                       send_incident_report()
                                 |
                                 v
                            Mattermost
```

---

## Technology Stack

| Component | Technology | Port |
|---|---|---|
| Alert receiver | Python Flask | 5000/tcp |
| SNMP ingestion | pysnmp inside snmp-notifier | 162/udp |
| Syslog ingestion | Python socket via systemd | 514/udp |
| Message broker | Apache Kafka 7.6.0 | 9092/tcp |
| Network monitoring | OpenNMS Horizon 33.0.2 (Main Solent) | 8980/tcp |
| Remote monitoring | OpenNMS Minion 33.0.2 x2 | Internal only |
| Notifications | Mattermost 9.4 | 8065/tcp |
| Metrics | Prometheus 2.51.0 | 9090/tcp |
| Dashboards | Grafana 10.4.0 | 3000/tcp |
| Secrets management | HashiCorp Vault 1.16.1 | 8200/tcp |
| Cache | Redis 7.2 | 6380/tcp |
| Message bus | ActiveMQ 5.18.3 | 61616/tcp |
| Network simulation | Containerlab + FRRouting v8.4.1 | - |
| Automation | Ansible | - |

---

## Network Architecture

### Docker Networks

| Network | Subnet | Purpose |
|---|---|---|
| marr-net | 172.21.0.0/16 | OpenNMS, Mattermost, Minions, FRR routers |
| solent_final_lab_marr-reporting | 172.22.0.0/16 | Platform services (created automatically by Docker Compose) |

Note: marr-net is the shared bridge that connects Docker Compose services to the
containerlab topology. Both systems join it independently. marr-reporting is created
automatically when the platform stack starts - do not create it manually.

### IP Allocation

| Container | IP | Role |
|---|---|---|
| marr-activemq | 172.21.0.9 | ActiveMQ broker - minion IPC |
| marr-postgres | 172.21.0.10 | OpenNMS database |
| marr-horizon (Main Solent) | 172.21.0.11 | OpenNMS Horizon core |
| clab-marr-lab-snmp-notifier | 172.21.0.14 | SNMP trap receiver |
| hamhung-minion | 172.21.0.20 | Solent-2 site remote minion |
| chongjin-minion | 172.21.0.21 | Solent-1 site remote minion |
| marr-mattermost-db | 172.21.0.30 | Mattermost database |
| marr-mattermost | 172.21.0.31 | Notifications |
| clab-marr-lab-router1 | 172.21.0.101 | FRR router - Main Solent (AS 65001) |
| clab-marr-lab-router2 | 172.21.0.102 | FRR router - Main Solent (AS 65002) |
| clab-marr-lab-router3 | 172.21.0.103 | FRR router - Main Solent (AS 65003) |
| clab-marr-lab-solent-2-router | 172.21.0.111 | FRR router - Solent-2 (AS 65004) |
| clab-marr-lab-solent-1-router | 172.21.0.121 | FRR router - Solent-1 (AS 65005) |

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
| 8980 | TCP | OpenNMS Horizon (Main Solent) |
| 9090 | TCP | Prometheus |
| 9092 | TCP | Kafka |
| 61616 | TCP | ActiveMQ broker (internal only) |

---

## System Requirements

- Ubuntu 22.04 or later
- Docker 24.0 or later and Docker Compose v2
- Containerlab 0.74 or later
- Python 3.10 or later
- Ansible core 2.14 or later
- 8 GB RAM minimum (OpenNMS requires 4 GB alone)
- 20 GB free disk space

---

## Installation

### Quick setup (recommended)

Run the setup script once after cloning. It handles all steps automatically
and adapts paths to the current user and machine.

```bash
git clone https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1.git
cd com617-AutomatedNetworkTroubleshooting-1
chmod +x setup.sh
./setup.sh
```

The script performs:
- Prerequisite checks
- Python dependency installation
- Ansible collection installation
- Docker image builds (marr-frr-snmp:v1 and marr-snmp-notifier:v1)
- Docker network creation (marr-net only)
- Systemd service installation with correct paths for the current user
- .env creation from .env.example

After the script completes, configure the Mattermost webhook (see below)
then start the lab.

---

### Manual installation (step by step)

If you prefer to install manually, or the setup script fails at a specific step:

#### 1. Clone the repository
```bash
git clone https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1.git
cd com617-AutomatedNetworkTroubleshooting-1
```

#### 2. Install Python dependencies
```bash
pip3 install flask requests pysnmp fastavro kafka-python locust hvac \
    python-dotenv netmiko prometheus-client --break-system-packages
```

#### 3. Install Ansible collections
```bash
ansible-galaxy collection install community.docker
```

#### 4. Build custom Docker images
```bash
# FRR router image with SNMP support
docker build -f containerlab/Dockerfile.frr-snmp -t marr-frr-snmp:v1 containerlab/

# SNMP notifier image
docker build -f containerlab/snmp-notifier/Dockerfile -t marr-snmp-notifier:v1 containerlab/snmp-notifier/
```

#### 5. Create the management Docker network
```bash
docker network create --driver bridge --subnet 172.21.0.0/16 marr-net
```

Note: do not create marr-reporting manually. Docker Compose creates it
automatically when the platform stack starts.

#### 6. Configure environment variables
```bash
cp .env.example .env
nano .env
```

Set MATTERMOST_WEBHOOK_URL after first boot (see Mattermost webhook setup below).

#### 7. Install systemd services
Replace /home/YOUR_USER and YOUR_USER with your actual username and home directory.

```bash
# Edit the service files to use your username and path before copying
sudo cp systemd/marr-receiver.service /etc/systemd/system/
sudo cp systemd/marr-syslog.service /etc/systemd/system/
sudo cp systemd/marr-snmp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable marr-receiver marr-syslog marr-snmp
```

Warning: the service files in systemd/ contain hardcoded paths for the
original developer machine. If you are installing on a different machine,
use the setup.sh script which rewrites these automatically, or edit the
User= and WorkingDirectory= fields manually before copying.

---

## Mattermost Webhook Setup

The Mattermost webhook must be configured after the first lab start because
the webhook URL is specific to each Mattermost instance.

1. Start the lab: `ansible-playbook scripts/lab-start.yml`
2. Open Mattermost at http://localhost:8065 and complete the first-time setup
3. Go to: Main Menu > Integrations > Incoming Webhooks > Add Incoming Webhook
4. Select the network-alerts channel and click Save
5. Copy the webhook URL (format: http://localhost:8065/hooks/xxxxxxxxxx)
6. Edit .env and set: `MATTERMOST_WEBHOOK_URL=http://localhost:8065/hooks/xxxxxxxxxx`
7. Restart the receiver: `sudo systemctl restart marr-receiver`

---

## Starting the Lab

```bash
ansible-playbook scripts/lab-start.yml
```

### Startup sequence and timing

| Step | Service | Max wait |
|---|---|---|
| Pre-flight | Docker checks, marr-net creation | Immediate |
| 1 | Platform services (Prometheus, Grafana, Vault, Kafka, Redis) + Mattermost | 360 seconds |
| 2 | OpenNMS Horizon (Main Solent) - PostgreSQL, ActiveMQ, Horizon | 600 seconds |
| 3 | Containerlab topology (5 routers + snmp-notifier) | 35 seconds |
| 4 | SNMP listener inside snmp-notifier | Immediate |
| 5 | Systemd services (receiver, syslog, snmp) | Immediate |
| 6 | Minions (Solent-2 and Solent-1) | 360 seconds to register |
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

## Testing the Pipeline

Send a test alert end-to-end:

```bash
curl -s -X POST http://localhost:5000/alert \
  -H 'Content-Type: application/json' \
  -d '{"id":"TEST-001","nodeLabel":"router1","severity":"CRITICAL",
       "uei":"uei.opennms.org/generic/traps/SNMP_Link_Down",
       "description":"Test alert","ifDescr":"eth1"}' | python3 -m json.tool
```

Expected response:
```json
{
    "alert_id": "TEST-001",
    "diag_rc": 0,
    "fault_type": "link_down",
    "playbook": "diagnose_link_down",
    "status": "processed"
}
```

A Network Incident Report should appear in the Mattermost network-alerts channel.

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
| OpenNMS (Main Solent) | http://localhost:8980/opennms | admin / admin |
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
| v4.0 | Minion integration: three-site architecture, Main Solent, Solent-2, Solent-1 |
| v4.1 | Main Solent rebrand, option-2 minion ID rename, lab hardening (idempotent network, snmpd -C fix, portable setup.sh) |

---

## Known Limitations

- Redis runs on port 6380 as system Redis occupies 6379
- Vault runs in dev mode - secrets lost on container restart
- Kafka single broker with replication factor 1 - no message durability
- OpenNMS takes 5 to 8 minutes to start on cold boot
- Minions take 3 to 5 minutes to register after Horizon starts
- OSPF not currently enabled - ospfd=no on all routers
- All fault injection is synthetic - not validated against live Cisco infrastructure
- containerlab 0.74.3 kind:linux nodes do not support capability passthrough - snmpd uses -C flag workaround

---

## Repositories

| Repository | URL |
|---|---|
| Personal | https://github.com/KariocaMarron/com617-AutomatedNetworkTroubleshooting-1 |
| Team | https://github.com/com617-industrial-2025-1/com617-AutomatedNetworkTroubleshooting-1 |

---

*Author: Jose Batalha De Vasconcelos - COM617 Group 15 - April 2026*
