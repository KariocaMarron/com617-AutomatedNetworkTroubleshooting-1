#!/bin/sh
# Usage: send-trap.sh <fault_type> <router_ip>
# fault_type: link-down | link-up | bgp-down | bgp-up
# Example: send-trap.sh link-down 172.21.0.101

OPENNMS_IP=172.21.0.11
COMMUNITY=public
FAULT=$1
ROUTER=$2

case $FAULT in
  link-down)
    snmptrap -v2c -c $COMMUNITY $OPENNMS_IP ""       linkDown       ifIndex.1 i 1       ifAdminStatus.1 i 2       ifOperStatus.1 i 2
    echo "Sent link-down trap to OpenNMS"
    ;;
  link-up)
    snmptrap -v2c -c $COMMUNITY $OPENNMS_IP ""       linkUp       ifIndex.1 i 1       ifAdminStatus.1 i 1       ifOperStatus.1 i 1
    echo "Sent link-up trap to OpenNMS"
    ;;
  bgp-down)
    snmptrap -v2c -c $COMMUNITY $OPENNMS_IP ""       .1.3.6.1.2.1.15.7       .1.3.6.1.2.1.15.3.1.7.$ROUTER s $ROUTER       .1.3.6.1.2.1.15.3.1.2.$ROUTER i 6
    echo "Sent bgp-down trap to OpenNMS"
    ;;
  bgp-up)
    snmptrap -v2c -c $COMMUNITY $OPENNMS_IP ""       .1.3.6.1.2.1.15.8       .1.3.6.1.2.1.15.3.1.7.$ROUTER s $ROUTER       .1.3.6.1.2.1.15.3.1.2.$ROUTER i 1
    echo "Sent bgp-up trap to OpenNMS"
    ;;
  *)
    echo "Unknown fault type: $FAULT"
    exit 1
    ;;
esac
