# OpenNMS Report - Academic Project Memory
## COM615 Network Management - Pyongyang University Implementation

**Project Owner:** Jose Vasconcelos (Karioka / KariocaMarron)  
**Module:** COM615 Network Management  
**Institution:** Southampton Solent University  
**Academic Year:** 2024/25  
**Document Version:** 1.0  
**Last Updated:** 5 January 2026

---

## 1. PROJECT PURPOSE & SCOPE

### 1.1 What the Project Is

This project implements a distributed network monitoring solution using **OpenNMS Horizon** for Pyongyang University (PYU), a fictional three-campus educational institution. The implementation is part of the COM615 Network Management module, demonstrating enterprise-grade network monitoring capabilities in a containerised lab environment.

**Project Name:** PyongNet Communications - OpenNMS Implementation  
**Role:** Monitoring Lead (Jose Vasconcelos)

### 1.2 Why It Exists

The project fulfils academic requirements for COM615, demonstrating:
- Practical skills in enterprise network monitoring deployment
- Understanding of distributed monitoring architectures
- Integration of monitoring with automation, security, and virtualisation workflows
- Alignment with FCAPS (Fault, Configuration, Accounting, Performance, Security) model
- Compliance with defined Service Level Agreements (SLAs)

### 1.3 What Problem It Solves

PYU requires continuous monitoring of network infrastructure across three geographically distributed campuses:
- **Pyongyang** (Main Campus) - Central IT Operations Centre (CIOC)
- **Hamhung** (Remote Campus) - Engineering and Technology Focus
- **Chongjin** (Remote Campus) - Science and Research Focus

The solution provides:
- Sub-10-minute fault detection (MTTD)
- Sub-45-minute resolution support (MTTR)
- 97%+ service availability compliance
- Centralised visibility across all campuses
- Automated alerting and escalation

---

## 2. ASSUMPTIONS & CONSTRAINTS

### 2.1 Academic Constraints

| Constraint | Description |
|------------|-------------|
| Word Limit | 5,000 words for academic report |
| Citation Style | Harvard Solent referencing |
| Writing Voice | First person ("I have implemented...") |
| Submission Format | Microsoft Word (.docx) |
| Evidence | Screenshots and diagrams required in appendices |

### 2.2 Lab vs Real-World Distinctions

| Aspect | Lab Implementation | Real-World Equivalent |
|--------|-------------------|----------------------|
| Network Devices | SNMP simulators (tandrup/snmpsim) | Physical Cisco/HP switches and routers |
| WAN Links | Single Docker bridge network | MPLS/VPN connections between sites |
| User Load | None (simulated) | 6,500 students and staff |
| VLE | NGINX placeholder page | Full Moodle LMS installation |
| Database HA | Single PostgreSQL instance | PostgreSQL streaming replication |
| Authentication | Basic LDAP | Active Directory integration |

### 2.3 What Is Simulated vs Implemented

**Fully Implemented (Functional):**
- OpenNMS Horizon 33.0.2 core monitoring
- PostgreSQL 14 metrics database
- ActiveMQ 5.18.3 message broker
- Two Minion collectors (Hamhung, Chongjin)
- SNMP polling and service detection
- ICMP availability monitoring
- HTTP service monitoring
- Event and alarm management
- Static IP addressing for stability

**Simulated (Placeholder/Representative):**
- Network devices (SNMP agents, not real routers/switches)
- VLE (NGINX static page, not full Moodle)
- FOG Server (placeholder web page)
- Inter-campus WAN (flat Docker network)

**Documented Only (Theoretical):**
- PostgreSQL HA failover
- Flow telemetry analysis (NetFlow/sFlow)
- Machine learning anomaly detection
- SIEM integration

---

## 3. ARCHITECTURE SUMMARY

### 3.1 Logical Architecture
```
PYONGYANG CENTRAL CAMPUS (CIOC)
├── OpenNMS Horizon :8980
├── PostgreSQL 14 :5432
├── ActiveMQ Broker :61616
└── Supporting Services
    ├── VLE (NGINX)
    ├── LDAP (OpenLDAP)
    ├── DNS/DHCP (dnsmasq)
    ├── Semaphore (Ansible UI)
    └── SNMP Simulators

HAMHUNG CAMPUS
├── Minion Collector (172.18.0.13)
├── Edge Router (SNMP)
├── Access Switch (SNMP)
└── Web Server

CHONGJIN CAMPUS
├── Minion Collector (172.18.0.14)
├── Edge Router (SNMP)
├── Access Switch (SNMP)
└── Web Server
```

### 3.2 Monitoring Model

**VPE Control Architecture:**
- **V**isibility: Centralised dashboard with campus filtering
- **P**roactive: Sub-10-minute detection thresholds
- **E**scalation: Tiered notification policies

**Polling Strategy:**
- ICMP ping: 30-second intervals
- SNMP collection: 5-minute intervals
- HTTP checks: 5-minute intervals

### 3.3 Role of OpenNMS Horizon

OpenNMS Horizon serves as the Central Monitoring Core, providing:
- Device discovery and provisioning
- SNMP polling and data collection
- Service availability monitoring
- Event correlation and alarm management
- Dashboard visualisation
- SLA reporting

### 3.4 Role of Docker / Docker Compose

Docker provides:
- Isolation: Each service runs in its own container
- Reproducibility: Identical environments across deployments
- Portability: Lab can be rebuilt on any Docker host
- Version Control: Specific image versions pinned

### 3.5 Role of Minions

Minions are distributed polling agents deployed at remote campuses:
- Local device polling (reduces WAN traffic)
- Protocol translation (SNMP, ICMP, etc.)
- Automatic failover to core if disconnected
- Location-aware service assignment

---

## 4. KEY DESIGN DECISIONS

### 4.1 Why Docker Was Chosen

| Factor | Decision Rationale |
|--------|-------------------|
| Reproducibility | Lab can be rebuilt from docker-compose files |
| Isolation | Services don't conflict with host system |
| Version Pinning | Specific versions guaranteed |
| Portability | Works on any Linux system with Docker |
| Academic Value | Demonstrates containerisation competency |

### 4.2 Why ActiveMQ (Not Kafka)

**Original Plan:** Apache Kafka for Minion messaging  
**Implemented:** ActiveMQ Classic 5.18.3

**Rationale:**
- Kafka configuration proved problematic in lab environment
- ActiveMQ provides simpler setup for OpenNMS integration
- Proven compatibility with OpenNMS Horizon 33.0.2
- Adequate performance for academic lab scale

### 4.3 Why PostgreSQL 14

- Official OpenNMS supported version
- Mature, reliable RDBMS
- Adequate performance for metrics storage

### 4.4 Why Java 17

- OpenNMS Horizon 33.0.2 requires Java 17
- Earlier/later versions may have compatibility issues

### 4.5 Why Static IP Addressing

**Problem Discovered:** Docker assigns IPs dynamically, causing:
- Service discovery failures after restarts
- Incorrect monitoring targets
- False outage alerts

**Solution:** Static IPs assigned in docker-compose files

---

## 5. EVIDENCE & VALIDATION APPROACH

### 5.1 What Proves the System Works

| Requirement | Validation Method | Evidence |
|-------------|------------------|----------|
| R1: Device Discovery | Node list showing 45 nodes | Figure 14 |
| R2: Distributed Polling | Minion status = UP | Figure 17 |
| R3: SNMP Monitoring | Service detection | Figure 23 |
| R4: MTTD Compliance | Fault injection tests | Table 8 |
| R8: Dashboard | Screenshot | Figure 18 |

### 5.2 What Counts as Successful

| Metric | Target | Achieved |
|--------|--------|----------|
| MTTD | < 10 minutes | 2m 43s average |
| SLA Availability | >= 97% | 99.76% |
| Monitored Nodes | 650+ (full) | 45 (lab) |
| Minion Connectivity | Both UP | Both UP |

---

## 6. KNOWN LIMITATIONS & FUTURE IMPROVEMENTS

### 6.1 Deliberately Missing Features

| Feature | Reason | Future Enhancement |
|---------|--------|-------------------|
| PostgreSQL HA | Lab complexity | Add streaming replication |
| Real network devices | Cost/access | Use GNS3 or physical lab |
| Full Moodle VLE | Resources | Deploy bitnami/moodle |
| NetFlow analysis | No flow sources | Add softflowd |
| SNMPv3 encryption | Lab simplicity | Implement AuthPriv |

---

## 7. GLOSSARY

### 7.1 Acronyms

| Acronym | Full Form |
|---------|-----------|
| CIOC | Central IT Operations Centre |
| FCAPS | Fault, Configuration, Accounting, Performance, Security |
| ICMP | Internet Control Message Protocol |
| LDAP | Lightweight Directory Access Protocol |
| MTTD | Mean Time to Detect |
| MTTR | Mean Time to Resolve |
| OID | Object Identifier |
| PYU | Pyongyang University |
| SLA | Service Level Agreement |
| SNMP | Simple Network Management Protocol |
| VLE | Virtual Learning Environment |
| VPE | Visibility, Proactive, Escalation |

---

## 8. TEAM INTEGRATION REFERENCES

| Name | Role | Integration Points |
|------|------|-------------------|
| Jose (Karioka) | OpenNMS Monitoring Lead | Core monitoring |
| Bigyan | Ansible Automation Lead | Inventory sync |
| Biloliddin | VMware/Kubernetes Lead | Hypervisor monitoring |
| Sebastian | Network Security Lead | SNMPv3, syslog |

---

## 9. SLA REQUIREMENTS MAPPING

| ID | Requirement | Status |
|----|-------------|--------|
| R1 | Device Discovery | Implemented |
| R2 | Distributed Polling | Implemented |
| R3 | SNMP Monitoring | Implemented |
| R4 | MTTD Compliance | Validated |
| R5 | Alarm Correlation | Configured |
| R6 | Flow Telemetry | Configured |
| R7 | SNMPv3 Security | Documented |
| R8 | Dashboard/Reporting | Implemented |
| R9 | High Availability | Documented |
| R10 | Ansible Integration | Configured |
| R11 | VLE Monitoring | Implemented |

---

*End of Academic Project Memory*

**Author:** Jose Vasconcelos (Karioka)  
**GitHub:** KariocaMarron
