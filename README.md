# OpenNMS PYU Monitoring Lab

**COM615 Network Management - Pyongyang University Infrastructure Monitoring**

## Overview

This repository contains a complete distributed network monitoring solution using OpenNMS Horizon for Pyongyang University's three-campus infrastructure.

| Component | Details |
|-----------|---------|
| **OpenNMS Version** | Horizon 33.0.2 |
| **Monitored Nodes** | 45 |
| **Campuses** | Pyongyang (CIOC), Hamhung, Chongjin |
| **Minions** | 2 (distributed collectors) |
| **Overall Availability** | 99.76%+ |

## Architecture
```
                    ┌─────────────────────────────────────┐
                    │       Pyongyang CIOC (Main)         │
                    │  ┌─────────────────────────────┐    │
                    │  │   OpenNMS Horizon 33.0.2    │    │
                    │  │   PostgreSQL 14             │    │
                    │  │   ActiveMQ 5.18.3           │    │
                    │  └─────────────────────────────┘    │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ Hamhung Campus  │  │ Pyongyang Local │  │ Chongjin Campus │
    │ Minion Collector│  │ Infrastructure  │  │ Minion Collector│
    │ 6 nodes         │  │ 14 nodes        │  │ 6 nodes         │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Quick Start

### Start Lab
```bash
~/pyu-opennms_lab/start-opennms-lab.sh
```

### Stop Lab
```bash
~/pyu-opennms_lab/stop-opennms-lab.sh
```

### Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| OpenNMS | http://localhost:8980/opennms | admin / admin |
| VLE | http://localhost:8081 | - |
| DNS/DHCP | http://localhost:8083 | - |
| Semaphore | http://localhost:8084 | admin / admin |
| LDAP Admin | http://localhost:8085 | - |
| ActiveMQ | http://localhost:8161 | admin / admin |

## Directory Structure
```
pyu-opennms_lab/
├── horizon/              # OpenNMS Horizon + PostgreSQL + ActiveMQ
├── minions/
│   ├── hamhung/          # Hamhung campus Minion
│   └── chongjin/         # Chongjin campus Minion
├── ldap/                 # OpenLDAP authentication
├── dns-dhcp/             # DNS and DHCP services
├── semaphore/            # Ansible automation UI
├── fog/                  # FOG imaging server
├── vle/                  # Virtual Learning Environment
├── network-devices/      # Simulated network infrastructure
├── simulated-devices/    # SNMP simulators
├── requisitions/         # OpenNMS node requisitions
├── screenshots/          # Evidence for COM615 report
├── start-opennms-lab.sh  # Startup script (~5 min)
└── stop-opennms-lab.sh   # Shutdown script
```

## SLA Compliance

| Metric | Target | Achieved |
|--------|--------|----------|
| MTTD (Mean Time to Detect) | < 10 min | ✅ 1-5 min |
| MTTR (Mean Time to Repair) | < 45 min | ✅ Supported |
| Availability | ≥ 97% | ✅ 99.76% |

## Team

| Member | Role |
|--------|------|
| Jose Vasconcelos | OpenNMS Monitoring & Alerting |
| Bigyan | Ansible Automation |
| Biloliddin | VMware/Kubernetes Virtualisation |
| Sebastian | Network Security |

## Author

**Jose Vasconcelos (KariocaMarron)**  
COM615 Network Management  
Southampton Solent University  
January 2026

---
