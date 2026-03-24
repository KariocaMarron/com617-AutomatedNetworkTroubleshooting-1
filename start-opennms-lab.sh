#!/bin/bash
echo "=========================================="
echo "  OpenNMS PYU Lab - Startup Script"
echo "  Jose Vasconcelos - KariocaMarron"
echo "=========================================="
echo "Estimated time: ~5 minutes"
echo ""

# 1. Core infrastructure (PostgreSQL, ActiveMQ, OpenNMS)
echo "[1/8] Starting core infrastructure..."
cd ~/pyu-opennms_lab/horizon && docker compose up -d
echo "Waiting 120s for PostgreSQL + OpenNMS to initialize..."
sleep 120

# 2. Minions (need OpenNMS + ActiveMQ ready)
echo "[2/8] Starting Minions..."
cd ~/pyu-opennms_lab/minions/hamhung && docker compose up -d
sleep 5
cd ~/pyu-opennms_lab/minions/chongjin && docker compose up -d
sleep 5

# 3. LDAP
echo "[3/8] Starting LDAP..."
cd ~/pyu-opennms_lab/ldap && docker compose up -d
sleep 5

# 4. DNS/DHCP
echo "[4/8] Starting DNS/DHCP..."
cd ~/pyu-opennms_lab/dns-dhcp && docker compose up -d
sleep 5

# 5. Semaphore
echo "[5/8] Starting Semaphore..."
cd ~/pyu-opennms_lab/semaphore && docker compose up -d
sleep 5

# 6. FOG Server
echo "[6/8] Starting FOG Server..."
cd ~/pyu-opennms_lab/fog && docker compose up -d
sleep 5

# 7. VLE
echo "[7/8] Starting VLE..."
cd ~/pyu-opennms_lab/vle && docker compose up -d
sleep 5

# 8. Simulated network devices (router/switch)
echo "[8/8] Starting simulated network devices..."
cd ~/pyu-opennms_lab/simulated-devices && docker compose up -d
sleep 5

# Final wait for stabilization
echo ""
echo "Waiting 60s for all services to stabilize..."
sleep 60

# Health check
echo ""
echo "=========================================="
echo "  Final Health Check"
echo "=========================================="
curl -s -o /dev/null -w "OpenNMS: HTTP %{http_code}\n" http://localhost:8980/opennms/login.jsp
curl -s -u admin:admin "http://localhost:8980/opennms/rest/nodes?limit=0" | grep -o 'totalCount="[0-9]*"' | sed 's/totalCount="/Nodes: /;s/"$//'
docker ps --format "{{.Names}}" | grep minion | while read m; do echo "Minion: $m ✓"; done
echo ""
echo "Container count: $(docker ps -q | wc -l)"
echo ""
echo "=========================================="
echo "  Lab Ready!"
echo "=========================================="
echo "OpenNMS: http://localhost:8980/opennms (admin/admin)"
echo "VLE:     http://localhost:8081"
echo "=========================================="
