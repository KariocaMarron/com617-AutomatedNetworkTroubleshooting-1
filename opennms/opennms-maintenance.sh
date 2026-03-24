#!/bin/bash
#===============================================================================
# OpenNMS PYU Lab - Maintenance & Documentation Script
# Jose Vasconcelos - Jan 2026 | GitHub: KariocaMarron
# COM615 Network Management - Pyongyang University
#===============================================================================

LAB_DIR="$HOME/pyu-opennms_lab"
LOG_DIR="$LAB_DIR/maintenance_logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$LOG_DIR"

show_menu() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     OpenNMS PYU Lab - Maintenance & Documentation Tool        ║${NC}"
    echo -e "${BLUE}║     Jose Vasconcelos - KariocaMarron - COM615                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}[1]${NC} Start Lab (Full Stack)"
    echo -e "${GREEN}[2]${NC} Stop Lab (Graceful Shutdown)"
    echo -e "${GREEN}[3]${NC} Restart Lab"
    echo -e "${GREEN}[4]${NC} Health Check & Status Report"
    echo -e "${GREEN}[5]${NC} Backup Configuration"
    echo -e "${GREEN}[6]${NC} Export System Documentation"
    echo -e "${GREEN}[7]${NC} Verify Static IPs"
    echo -e "${GREEN}[8]${NC} Test SNMP Connectivity"
    echo -e "${GREEN}[9]${NC} View Container Logs"
    echo -e "${GREEN}[10]${NC} Force Rescan All Nodes"
    echo -e "${GREEN}[11]${NC} Generate Full System Report"
    echo -e "${GREEN}[0]${NC} Exit"
    echo ""
    read -p "Select option: " choice
    handle_choice $choice
}

start_lab() {
    echo -e "${YELLOW}Starting OpenNMS PYU Lab...${NC}"
    echo "Estimated time: ~5 minutes"
    
    # 1. Core infrastructure
    echo -e "${BLUE}[1/8]${NC} Starting core infrastructure..."
    cd "$LAB_DIR/horizon" && docker compose up -d
    echo "Waiting 120s for PostgreSQL + OpenNMS..."
    sleep 120
    
    # 2. Minions
    echo -e "${BLUE}[2/8]${NC} Starting Minions..."
    cd "$LAB_DIR/minions/hamhung" && docker compose up -d
    sleep 5
    cd "$LAB_DIR/minions/chongjin" && docker compose up -d
    sleep 5
    
    # 3. LDAP
    echo -e "${BLUE}[3/8]${NC} Starting LDAP..."
    cd "$LAB_DIR/ldap" && docker compose up -d
    sleep 5
    
    # 4. DNS/DHCP
    echo -e "${BLUE}[4/8]${NC} Starting DNS/DHCP..."
    cd "$LAB_DIR/dns-dhcp" && docker compose up -d
    sleep 5
    
    # 5. Semaphore
    echo -e "${BLUE}[5/8]${NC} Starting Semaphore..."
    cd "$LAB_DIR/semaphore" && docker compose up -d
    sleep 5
    
    # 6. FOG Server
    echo -e "${BLUE}[6/8]${NC} Starting FOG Server..."
    cd "$LAB_DIR/fog" && docker compose up -d
    sleep 5
    
    # 7. VLE
    echo -e "${BLUE}[7/8]${NC} Starting VLE..."
    cd "$LAB_DIR/vle" && docker compose up -d
    sleep 5
    
    # 8. Network devices
    echo -e "${BLUE}[8/8]${NC} Starting simulated network devices..."
    cd "$LAB_DIR/simulated-devices" && docker compose up -d
    sleep 3
    cd "$LAB_DIR/network-devices" && docker compose up -d
    sleep 5
    
    echo -e "${GREEN}Lab started successfully!${NC}"
    health_check
}

stop_lab() {
    echo -e "${YELLOW}Stopping OpenNMS PYU Lab...${NC}"
    
    cd "$LAB_DIR/network-devices" && docker compose down 2>/dev/null
    cd "$LAB_DIR/simulated-devices" && docker compose down 2>/dev/null
    cd "$LAB_DIR/vle" && docker compose down 2>/dev/null
    cd "$LAB_DIR/fog" && docker compose down 2>/dev/null
    cd "$LAB_DIR/semaphore" && docker compose down 2>/dev/null
    cd "$LAB_DIR/dns-dhcp" && docker compose down 2>/dev/null
    cd "$LAB_DIR/ldap" && docker compose down 2>/dev/null
    cd "$LAB_DIR/minions/chongjin" && docker compose down 2>/dev/null
    cd "$LAB_DIR/minions/hamhung" && docker compose down 2>/dev/null
    cd "$LAB_DIR/horizon" && docker compose down 2>/dev/null
    
    echo -e "${GREEN}Lab stopped successfully!${NC}"
}

health_check() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                    HEALTH CHECK REPORT                        ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    # Container count
    RUNNING=$(docker ps -q | wc -l)
    echo -e "\n${YELLOW}Containers Running:${NC} $RUNNING"
    
    # OpenNMS status
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8980/opennms/login.jsp 2>/dev/null)
    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓${NC} OpenNMS Horizon: UP (HTTP $HTTP_CODE)"
    else
        echo -e "${RED}✗${NC} OpenNMS Horizon: DOWN (HTTP $HTTP_CODE)"
    fi
    
    # Node count
    NODES=$(curl -s -u admin:admin "http://localhost:8980/opennms/rest/nodes?limit=0" 2>/dev/null | grep -oP 'totalCount="[0-9]*"' | grep -oP '[0-9]+')
    echo -e "${YELLOW}Monitored Nodes:${NC} ${NODES:-0}"
    
    # Minion status
    echo -e "\n${YELLOW}Minion Status:${NC}"
    for minion in hamhung-minion chongjin-minion; do
        if docker ps --format '{{.Names}}' | grep -q "$minion"; then
            echo -e "  ${GREEN}✓${NC} $minion: Running"
        else
            echo -e "  ${RED}✗${NC} $minion: Stopped"
        fi
    done
    
    # Services status
    echo -e "\n${YELLOW}Service Status:${NC}"
    declare -A services=(
        ["pyu-horizon"]="OpenNMS"
        ["pyu-postgres"]="PostgreSQL"
        ["pyu-activemq"]="ActiveMQ"
        ["pyu-vle"]="VLE"
        ["pyu-ldap"]="LDAP"
        ["pyu-dns-dhcp"]="DNS/DHCP"
        ["pyu-semaphore"]="Semaphore"
    )
    
    for container in "${!services[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            echo -e "  ${GREEN}✓${NC} ${services[$container]}: Running"
        else
            echo -e "  ${RED}✗${NC} ${services[$container]}: Stopped"
        fi
    done
    
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

verify_static_ips() {
    echo -e "\n${BLUE}Verifying Static IP Assignments...${NC}\n"
    
    declare -A expected_ips=(
        ["pyu-py-router"]="172.18.0.2"
        ["pyu-vle"]="172.18.0.3"
        ["pyu-ldap-admin"]="172.18.0.4"
        ["pyu-py-switch"]="172.18.0.5"
        ["pyu-ldap"]="172.18.0.6"
        ["pyu-semaphore-db"]="172.18.0.7"
        ["pyu-fog-db"]="172.18.0.8"
        ["pyu-activemq"]="172.18.0.9"
        ["pyu-postgres"]="172.18.0.10"
        ["pyu-horizon"]="172.18.0.11"
        ["pyu-dns-dhcp"]="172.18.0.12"
        ["hamhung-minion"]="172.18.0.13"
        ["chongjin-minion"]="172.18.0.14"
        ["pyu-semaphore"]="172.18.0.16"
        ["pyu-fog-server"]="172.18.0.17"
        ["pyu-core-switch"]="172.18.0.20"
        ["pyu-dist-switch"]="172.18.0.21"
        ["pyu-firewall"]="172.18.0.22"
        ["hamhung-router"]="172.18.0.30"
        ["hamhung-switch"]="172.18.0.31"
        ["hamhung-web"]="172.18.0.32"
        ["chongjin-router"]="172.18.0.40"
        ["chongjin-switch"]="172.18.0.41"
        ["chongjin-web"]="172.18.0.42"
    )
    
    MISMATCHES=0
    for container in "${!expected_ips[@]}"; do
        ACTUAL_IP=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container" 2>/dev/null)
        EXPECTED="${expected_ips[$container]}"
        
        if [ -z "$ACTUAL_IP" ]; then
            echo -e "${YELLOW}⚠${NC} $container: Not running"
        elif [ "$ACTUAL_IP" == "$EXPECTED" ]; then
            echo -e "${GREEN}✓${NC} $container: $ACTUAL_IP"
        else
            echo -e "${RED}✗${NC} $container: Expected $EXPECTED, Got $ACTUAL_IP"
            ((MISMATCHES++))
        fi
    done
    
    echo ""
    if [ $MISMATCHES -eq 0 ]; then
        echo -e "${GREEN}All static IPs verified correctly!${NC}"
    else
        echo -e "${RED}$MISMATCHES IP mismatches found!${NC}"
    fi
}

test_snmp() {
    echo -e "\n${BLUE}Testing SNMP Connectivity...${NC}\n"
    
    SNMP_HOSTS=(
        "172.18.0.2:pyu-py-router"
        "172.18.0.5:pyu-py-switch"
        "172.18.0.20:pyu-core-switch"
        "172.18.0.21:pyu-dist-switch"
        "172.18.0.22:pyu-firewall"
        "172.18.0.30:hamhung-router"
        "172.18.0.31:hamhung-switch"
        "172.18.0.40:chongjin-router"
        "172.18.0.41:chongjin-switch"
    )
    
    for entry in "${SNMP_HOSTS[@]}"; do
        IP="${entry%%:*}"
        NAME="${entry##*:}"
        
        RESULT=$(snmpget -v2c -c public -t 2 "$IP" 1.3.6.1.2.1.1.1.0 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} $NAME ($IP): SNMP OK"
        else
            echo -e "${RED}✗${NC} $NAME ($IP): SNMP FAILED"
        fi
    done
}

backup_config() {
    BACKUP_DIR="$LAB_DIR/backups/backup_$TIMESTAMP"
    mkdir -p "$BACKUP_DIR"
    
    echo -e "${YELLOW}Creating backup to $BACKUP_DIR...${NC}"
    
    # Backup docker-compose files
    find "$LAB_DIR" -name "docker-compose.yml" -exec cp --parents {} "$BACKUP_DIR/" \;
    
    # Backup IP allocation
    cp "$LAB_DIR/IP_ALLOCATION.md" "$BACKUP_DIR/" 2>/dev/null
    
    # Export current container IPs
    docker inspect --format '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -q) > "$BACKUP_DIR/current_ips.txt" 2>/dev/null
    
    # Export OpenNMS node list
    curl -s -u admin:admin "http://localhost:8980/opennms/rest/nodes" > "$BACKUP_DIR/opennms_nodes.xml" 2>/dev/null
    
    # Create tarball
    tar -czf "$LAB_DIR/backups/backup_$TIMESTAMP.tar.gz" -C "$LAB_DIR/backups" "backup_$TIMESTAMP"
    rm -rf "$BACKUP_DIR"
    
    echo -e "${GREEN}Backup created: $LAB_DIR/backups/backup_$TIMESTAMP.tar.gz${NC}"
}

export_documentation() {
    DOC_FILE="$LAB_DIR/SYSTEM_DOCUMENTATION_$TIMESTAMP.md"
    
    echo -e "${YELLOW}Generating system documentation...${NC}"
    
    cat > "$DOC_FILE" << DOCEOF
# OpenNMS PYU Lab - System Documentation
Generated: $(date)
Jose Vasconcelos - KariocaMarron - COM615

## Container Status
\`\`\`
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null)
\`\`\`

## IP Allocation
$(cat "$LAB_DIR/IP_ALLOCATION.md" 2>/dev/null || echo "IP_ALLOCATION.md not found")

## Current Container IPs
\`\`\`
$(docker inspect --format '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -q) 2>/dev/null | sort)
\`\`\`

## OpenNMS Node Summary
- Total Nodes: $(curl -s -u admin:admin "http://localhost:8980/opennms/rest/nodes?limit=0" 2>/dev/null | grep -oP 'totalCount="[0-9]*"' | grep -oP '[0-9]+' || echo "N/A")
- HTTP Status: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8980/opennms/login.jsp 2>/dev/null)

## Docker Compose Files
$(find "$LAB_DIR" -name "docker-compose.yml" -exec echo "- {}" \;)

## Network Configuration
\`\`\`
$(docker network inspect kafka_pyu-main --format '{{.Name}}: {{range .IPAM.Config}}{{.Subnet}}{{end}}' 2>/dev/null)
\`\`\`

---
End of Documentation
DOCEOF

    echo -e "${GREEN}Documentation saved to: $DOC_FILE${NC}"
}

force_rescan() {
    echo -e "${YELLOW}Triggering rescan for all nodes...${NC}"
    
    NODE_IDS=$(curl -s -u admin:admin "http://localhost:8980/opennms/rest/nodes" | grep -oP 'id="[0-9]+"' | grep -oP '[0-9]+')
    
    for id in $NODE_IDS; do
        curl -s -X PUT -u admin:admin "http://localhost:8980/opennms/api/v2/nodes/$id/rescan" > /dev/null 2>&1
        echo -e "  Rescanned node $id"
    done
    
    echo -e "${GREEN}All nodes rescanned!${NC}"
}

generate_full_report() {
    REPORT_FILE="$LOG_DIR/full_report_$TIMESTAMP.txt"
    
    echo -e "${YELLOW}Generating full system report...${NC}"
    
    {
        echo "==============================================================================="
        echo "OpenNMS PYU Lab - Full System Report"
        echo "Generated: $(date)"
        echo "==============================================================================="
        echo ""
        
        echo "=== CONTAINER STATUS ==="
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        
        echo "=== IP VERIFICATION ==="
        verify_static_ips 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
        echo ""
        
        echo "=== SNMP CONNECTIVITY ==="
        test_snmp 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
        echo ""
        
        echo "=== OPENNMS HEALTH ==="
        curl -s -u admin:admin "http://localhost:8980/opennms/rest/health" 2>/dev/null
        echo ""
        
        echo "=== DISK USAGE ==="
        docker system df
        echo ""
        
        echo "==============================================================================="
        echo "End of Report"
        echo "==============================================================================="
    } > "$REPORT_FILE"
    
    echo -e "${GREEN}Full report saved to: $REPORT_FILE${NC}"
    cat "$REPORT_FILE"
}

view_logs() {
    echo -e "\n${YELLOW}Select container to view logs:${NC}"
    docker ps --format "{{.Names}}" | nl
    echo ""
    read -p "Enter number: " num
    
    CONTAINER=$(docker ps --format "{{.Names}}" | sed -n "${num}p")
    if [ -n "$CONTAINER" ]; then
        docker logs --tail 50 "$CONTAINER"
    else
        echo -e "${RED}Invalid selection${NC}"
    fi
}

handle_choice() {
    case $1 in
        1) start_lab ;;
        2) stop_lab ;;
        3) stop_lab && sleep 5 && start_lab ;;
        4) health_check ;;
        5) backup_config ;;
        6) export_documentation ;;
        7) verify_static_ips ;;
        8) test_snmp ;;
        9) view_logs ;;
        10) force_rescan ;;
        11) generate_full_report ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# Main
if [ "$1" == "--health" ]; then
    health_check
elif [ "$1" == "--start" ]; then
    start_lab
elif [ "$1" == "--stop" ]; then
    stop_lab
elif [ "$1" == "--verify-ips" ]; then
    verify_static_ips
elif [ "$1" == "--backup" ]; then
    backup_config
elif [ "$1" == "--report" ]; then
    generate_full_report
else
    show_menu
fi
