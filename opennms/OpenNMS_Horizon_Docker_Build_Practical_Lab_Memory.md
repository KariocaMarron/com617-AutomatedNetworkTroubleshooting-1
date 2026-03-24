# OpenNMS Horizon Docker Build - Practical Lab Memory
## Complete Rebuild, Repair, and Operations Guide

**Project:** pyu-opennms_lab  
**Repository:** https://github.com/KariocaMarron/opennms-pyu-monitoring  
**Author:** Jose Vasconcelos (Karioka / KariocaMarron)  
**Document Version:** 1.0  
**Last Updated:** 5 January 2026

---

# SECTION A: PRE-INSTALLATION REQUIREMENTS

## A.1 Operating System Requirements

| Requirement | Specification |
|-------------|---------------|
| OS | Ubuntu 24.04 LTS (or compatible Debian-based) |
| Architecture | x86_64 (64-bit) |
| RAM | Minimum 8GB, Recommended 16GB |
| Disk | Minimum 50GB free space |
| Network | Internet access for Docker image pulls |

## A.2 Required Software

### A.2.1 Docker Engine

**Minimum Version:** 24.0 or later

**Installation Commands:**
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
docker --version
```

### A.2.2 Supporting Tools
```bash
sudo apt install -y curl git jq net-tools snmp snmp-mibs-downloader nano vim
```

### A.2.3 Tool Version Summary

| Tool | Minimum Version | Package |
|------|-----------------|---------|
| Docker | 24.0+ | docker-ce |
| Docker Compose | 2.20+ | docker-compose-plugin |
| curl | 7.x | curl |
| git | 2.x | git |
| jq | 1.6+ | jq |
| snmpget | 5.9+ | snmp |

---

# SECTION B: REPOSITORY & FILE STRUCTURE

## B.1 Repository Location

**Local Path:** ~/pyu-opennms_lab/  
**Remote:** https://github.com/KariocaMarron/opennms-pyu-monitoring.git

## B.2 Directory Structure
```
pyu-opennms_lab/
├── horizon/                    # Core OpenNMS stack
│   ├── docker-compose.yml      # PostgreSQL + ActiveMQ + Horizon
│   └── overlay/                # OpenNMS configuration overlays
├── minions/                    # Remote polling agents
│   ├── hamhung/
│   │   ├── docker-compose.yml
│   │   ├── minion-startup.sh
│   │   └── opennms.properties.d/
│   └── chongjin/
│       ├── docker-compose.yml
│       ├── minion-startup.sh
│       └── opennms.properties.d/
├── ldap/                       # LDAP authentication
│   └── docker-compose.yml
├── dns-dhcp/                   # DNS/DHCP services
│   ├── docker-compose.yml
│   └── dnsmasq.conf
├── semaphore/                  # Ansible Semaphore UI
│   └── docker-compose.yml
├── fog/                        # FOG imaging server
│   ├── docker-compose.yml
│   └── fog-web/
├── vle/                        # Virtual Learning Environment
│   ├── docker-compose.yml
│   └── vle-content/
├── simulated-devices/          # Pyongyang campus devices
│   └── docker-compose.yml
├── network-devices/            # Remote campus devices
│   ├── docker-compose.yml
│   ├── hamhung-web/
│   └── chongjin-web/
├── opennms-maintenance.sh      # Main operations script
├── start-opennms-lab.sh        # Startup script
├── stop-opennms-lab.sh         # Shutdown script
└── IP_ALLOCATION.md            # Static IP documentation
```

## B.3 What Must Never Be Deleted

| Item | Reason |
|------|--------|
| horizon/overlay/ | Custom OpenNMS configurations |
| Docker volumes | Persistent data (database, metrics) |
| *.yml files | Container definitions |
| IP_ALLOCATION.md | IP address reference |
| minion-startup.sh | Minion configuration scripts |

---

# SECTION C: STARTUP CHECKLIST

## C.1 Pre-Start Verification

[ ] Step 1: Verify Docker is running
```bash
sudo systemctl status docker
```
Expected: Active: active (running)

[ ] Step 2: Check available disk space
```bash
df -h /var/lib/docker
```
Expected: >20GB free

[ ] Step 3: Verify Docker network exists
```bash
docker network ls | grep kafka_pyu-main
```
If missing:
```bash
docker network create --subnet=172.18.0.0/16 kafka_pyu-main
```

## C.2 Startup Sequence

### Method A: Use Maintenance Script (Recommended)

[ ] Step 1: Run the maintenance script
```bash
~/pyu-opennms_lab/opennms-maintenance.sh --start
```
Wait approximately 5 minutes for full startup.

### Method B: Manual Startup

[ ] Step 1: Start core infrastructure
```bash
cd ~/pyu-opennms_lab/horizon && docker compose up -d
```
WAIT: 120 seconds

[ ] Step 2: Verify core is healthy
```bash
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost:8980/opennms/login.jsp
```
Expected: HTTP 200

[ ] Step 3: Start Hamhung Minion
```bash
cd ~/pyu-opennms_lab/minions/hamhung && docker compose up -d
```

[ ] Step 4: Start Chongjin Minion
```bash
cd ~/pyu-opennms_lab/minions/chongjin && docker compose up -d
```

[ ] Step 5: Start LDAP
```bash
cd ~/pyu-opennms_lab/ldap && docker compose up -d
```

[ ] Step 6: Start DNS/DHCP
```bash
cd ~/pyu-opennms_lab/dns-dhcp && docker compose up -d
```

[ ] Step 7: Start Semaphore
```bash
cd ~/pyu-opennms_lab/semaphore && docker compose up -d
```

[ ] Step 8: Start FOG Server
```bash
cd ~/pyu-opennms_lab/fog && docker compose up -d
```

[ ] Step 9: Start VLE
```bash
cd ~/pyu-opennms_lab/vle && docker compose up -d
```

[ ] Step 10: Start Simulated Devices
```bash
cd ~/pyu-opennms_lab/simulated-devices && docker compose up -d
```

[ ] Step 11: Start Network Devices
```bash
cd ~/pyu-opennms_lab/network-devices && docker compose up -d
```

[ ] Step 12: Wait 60 seconds for stabilisation

## C.3 Post-Start Verification

[ ] Check container count (expected: 24)
```bash
docker ps -q | wc -l
```

[ ] Verify OpenNMS Web UI
```bash
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost:8980/opennms/login.jsp
```

[ ] Check node count
```bash
curl -s -u admin:admin "http://localhost:8980/opennms/rest/nodes?limit=0" | grep -oP 'totalCount="[0-9]+"'
```

[ ] Run health check
```bash
~/pyu-opennms_lab/opennms-maintenance.sh --health
```

---

# SECTION D: SHUTDOWN CHECKLIST

## D.1 Safe Shutdown Sequence

### Method A: Use Scripts (Recommended)

[ ] Run stop script
```bash
~/pyu-opennms_lab/stop-opennms-lab.sh
```

### Method B: Manual Shutdown (Reverse Order)

[ ] Step 1: Stop network devices
```bash
cd ~/pyu-opennms_lab/network-devices && docker compose down
cd ~/pyu-opennms_lab/simulated-devices && docker compose down
```

[ ] Step 2: Stop application services
```bash
cd ~/pyu-opennms_lab/vle && docker compose down
cd ~/pyu-opennms_lab/fog && docker compose down
cd ~/pyu-opennms_lab/semaphore && docker compose down
cd ~/pyu-opennms_lab/dns-dhcp && docker compose down
cd ~/pyu-opennms_lab/ldap && docker compose down
```

[ ] Step 3: Stop Minions
```bash
cd ~/pyu-opennms_lab/minions/chongjin && docker compose down
cd ~/pyu-opennms_lab/minions/hamhung && docker compose down
```

[ ] Step 4: Stop core infrastructure (LAST)
```bash
cd ~/pyu-opennms_lab/horizon && docker compose down
```

## D.2 What NOT To Do

- Never stop PostgreSQL before OpenNMS
- Never use docker compose down -v unless intentionally deleting data
- Never force-kill containers during normal operations

---

# SECTION E: DOCKER COMPOSE CONTROL

## E.1 Common Commands

| Action | Command |
|--------|---------|
| Start service | cd <dir> && docker compose up -d |
| Stop service | cd <dir> && docker compose down |
| Restart service | cd <dir> && docker compose restart |
| View logs | docker logs <container> --tail 100 |
| Rebuild | cd <dir> && docker compose up -d --force-recreate |

## E.2 Removing Volumes (DESTRUCTIVE)

WARNING: This PERMANENTLY DELETES DATA

Single service:
```bash
cd <directory> && docker compose down -v
```

All orphaned:
```bash
docker volume prune
```

---

# SECTION F: TROUBLESHOOTING & RECOVERY

## F.1 OpenNMS Web UI Not Accessible

Diagnostic:
```bash
docker ps | grep pyu-horizon
docker logs pyu-horizon --tail 100
netstat -tlnp | grep 8980
```

Common causes:
- Container not started
- Still initialising (wait 2-3 minutes)
- PostgreSQL not ready

## F.2 Minion Not Connecting

Diagnostic:
```bash
docker logs hamhung-minion --tail 100
docker exec hamhung-minion ping -c 3 pyu-horizon
docker exec hamhung-minion ping -c 3 pyu-activemq
```

Common causes:
- ActiveMQ not running
- Network connectivity issue
- Configuration error

## F.3 Services Showing DOWN

Diagnostic:
```bash
ping <container-ip>
snmpget -v2c -c public <container-ip> 1.3.6.1.2.1.1.1.0
```

Common causes:
- IP address changed (verify with --verify-ips)
- SNMP not running
- Wrong community string

## F.4 Log Locations

| Service | Command |
|---------|---------|
| OpenNMS | docker logs pyu-horizon |
| PostgreSQL | docker logs pyu-postgres |
| ActiveMQ | docker logs pyu-activemq |
| Minions | docker logs hamhung-minion |

## F.5 Recovery Without Rebuilding

Restart specific service:
```bash
docker restart <container-name>
```

Force recreate (preserves volumes):
```bash
cd ~/pyu-opennms_lab/<dir> && docker compose up -d --force-recreate
```

Complete lab restart:
```bash
~/pyu-opennms_lab/stop-opennms-lab.sh
sleep 10
~/pyu-opennms_lab/opennms-maintenance.sh --start
```

---

# SECTION G: STATIC IP ALLOCATION

| IP Address | Container | Service |
|------------|-----------|---------|
| 172.18.0.2 | pyu-py-router | SNMP Simulator |
| 172.18.0.3 | pyu-vle | VLE |
| 172.18.0.4 | pyu-ldap-admin | phpLDAPadmin |
| 172.18.0.5 | pyu-py-switch | SNMP Simulator |
| 172.18.0.6 | pyu-ldap | OpenLDAP |
| 172.18.0.7 | pyu-semaphore-db | MySQL |
| 172.18.0.8 | pyu-fog-db | MySQL |
| 172.18.0.9 | pyu-activemq | ActiveMQ |
| 172.18.0.10 | pyu-postgres | PostgreSQL |
| 172.18.0.11 | pyu-horizon | OpenNMS |
| 172.18.0.12 | pyu-dns-dhcp | dnsmasq |
| 172.18.0.13 | hamhung-minion | Minion |
| 172.18.0.14 | chongjin-minion | Minion |
| 172.18.0.16 | pyu-semaphore | Ansible UI |
| 172.18.0.17 | pyu-fog-server | FOG |
| 172.18.0.20 | pyu-core-switch | SNMP |
| 172.18.0.21 | pyu-dist-switch | SNMP |
| 172.18.0.22 | pyu-firewall | SNMP |
| 172.18.0.30 | hamhung-router | SNMP |
| 172.18.0.31 | hamhung-switch | SNMP |
| 172.18.0.32 | hamhung-web | Web |
| 172.18.0.40 | chongjin-router | SNMP |
| 172.18.0.41 | chongjin-switch | SNMP |
| 172.18.0.42 | chongjin-web | Web |

---

# SECTION H: ACCESS CREDENTIALS

## H.1 OpenNMS
- URL: http://localhost:8980/opennms
- Username: admin
- Password: admin

## H.2 LDAP
- URL: http://localhost:8082
- Login DN: cn=admin,dc=pyu,dc=edu,dc=kp
- Password: admin

## H.3 ActiveMQ
- URL: http://localhost:8161
- Username: admin
- Password: admin

## H.4 Semaphore
- URL: http://localhost:8084
- Username: admin
- Password: admin

## H.5 PostgreSQL
- Host: pyu-postgres
- Port: 5432
- Database: opennms
- Username: opennms
- Password: opennms

---

# SECTION I: MAINTENANCE SCRIPT

## I.1 Interactive Menu
```bash
~/pyu-opennms_lab/opennms-maintenance.sh
```

Options:
1. Start Lab
2. Stop Lab
3. Restart Lab
4. Health Check
5. Backup Configuration
6. Export Documentation
7. Verify Static IPs
8. Test SNMP
9. View Logs
10. Force Rescan Nodes
11. Generate Report
0. Exit

## I.2 Command-Line Options

| Command | Purpose |
|---------|---------|
| --start | Start all services |
| --stop | Stop all services |
| --health | Run health check |
| --verify-ips | Verify static IPs |
| --backup | Create backup |
| --report | Generate report |

---

*End of Practical Lab Memory*

**Author:** Jose Vasconcelos (Karioka)  
**GitHub:** KariocaMarron
