#!/bin/bash
# MARR Lab - Fault Injection Script
# COM617 Group 15 - Cisco ICP 2026
# Usage: ./inject-fault.sh <fault_type> <router>
# Examples:
#   ./inject-fault.sh link-down router1
#   ./inject-fault.sh link-up router1
#   ./inject-fault.sh bgp-down router1
#   ./inject-fault.sh bgp-up router1

FAULT=$1
ROUTER=$2
CONTAINER="clab-marr-lab-${ROUTER}"
OPENNMS_IP="172.21.0.11"

if [ -z "$FAULT" ] || [ -z "$ROUTER" ]; then
  echo "Usage: $0 <fault_type> <router>"
  echo "  fault_type: link-down | link-up | bgp-down | bgp-up"
  echo "  router:     router1 | router2 | router3"
  exit 1
fi

echo "======================================"
echo "  MARR Fault Injection"
echo "  Fault : $FAULT"
echo "  Router: $ROUTER ($CONTAINER)"
echo "======================================"

case $FAULT in
  link-down)
    echo "[1/2] Shutting down eth1 on $ROUTER..."
    sudo docker exec $CONTAINER ip link set eth1 down
    echo "[2/2] Sending linkDown trap to OpenNMS..."
    docker run --rm --network marr-net alpine sh -c \
      "apk add --no-cache net-snmp-tools -q && \
       snmptrap -v2c -c public ${OPENNMS_IP}:1162 '' \
       .1.3.6.1.6.3.1.1.5.3 \
       .1.3.6.1.2.1.2.2.1.1.1 i 1 \
       .1.3.6.1.2.1.2.2.1.7.1 i 2 \
       .1.3.6.1.2.1.2.2.1.8.1 i 2"
    echo "[DONE] Link-down fault injected on $ROUTER"
    ;;

  link-up)
    echo "[1/2] Bringing up eth1 on $ROUTER..."
    sudo docker exec $CONTAINER ip link set eth1 up
    echo "[2/2] Sending linkUp trap to OpenNMS..."
    docker run --rm --network marr-net alpine sh -c \
      "apk add --no-cache net-snmp-tools -q && \
       snmptrap -v2c -c public ${OPENNMS_IP}:1162 '' \
       .1.3.6.1.6.3.1.1.5.4 \
       .1.3.6.1.2.1.2.2.1.1.1 i 1 \
       .1.3.6.1.2.1.2.2.1.7.1 i 1 \
       .1.3.6.1.2.1.2.2.1.8.1 i 1"
    echo "[DONE] Link-up recovery injected on $ROUTER"
    ;;

  bgp-down)
    echo "[1/2] Clearing BGP session on $ROUTER..."
    sudo docker exec $CONTAINER vtysh -c "clear bgp *"
    echo "[2/2] Sending BGP trap to OpenNMS..."
    docker run --rm --network marr-net alpine sh -c \
      "apk add --no-cache net-snmp-tools -q && \
       snmptrap -v2c -c public ${OPENNMS_IP}:1162 '' \
       .1.3.6.1.2.1.15.7 \
       .1.3.6.1.2.1.15.3.1.2.1 i 6"
    echo "[DONE] BGP-down fault injected on $ROUTER"
    ;;

  bgp-up)
    echo "[1/1] BGP sessions recover automatically after clear"
    echo "      Waiting 15s for BGP to re-establish..."
    sleep 15
    sudo docker exec $CONTAINER vtysh -c "show bgp summary" 2>/dev/null | grep -E "Neighbor|[0-9]+\.[0-9]+"
    echo "[DONE] BGP recovery check complete"
    ;;

  node-down)
    echo "[1/2] Stopping target router container..."
    sudo docker stop $CONTAINER
    echo "[2/2] Sending nodeDown trap to OpenNMS..."
    docker run --rm --network marr-net alpine sh -c       "apk add --no-cache net-snmp-tools -q &&        snmptrap -v2c -c public ${OPENNMS_IP}:1162 ''        .1.3.6.1.6.3.1.1.5.2        .1.3.6.1.2.1.2.2.1.1.1 i 1"
    echo "[DONE] Node-down fault injected on $ROUTER"
    ;;

  node-up)
    echo "[1/1] Starting target router container..."
    sudo docker start $CONTAINER
    sleep 5
    echo "[DONE] Node $ROUTER restarted"
    ;;

  *)
    echo "Unknown fault type: $FAULT"
    exit 1
    ;;
esac
