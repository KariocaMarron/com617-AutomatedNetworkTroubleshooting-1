#!/bin/bash
echo "=========================================="
echo "  OpenNMS PYU Lab - Shutdown Script"
echo "  Jose Vasconcelos - KariocaMarron"
echo "=========================================="
cd ~/pyu-opennms_lab/network-devices && docker compose down
cd ~/pyu-opennms_lab/simulated-devices && docker compose down
cd ~/pyu-opennms_lab/vle && docker compose down
cd ~/pyu-opennms_lab/fog && docker compose down
cd ~/pyu-opennms_lab/semaphore && docker compose down
cd ~/pyu-opennms_lab/dns-dhcp && docker compose down
cd ~/pyu-opennms_lab/ldap && docker compose down
cd ~/pyu-opennms_lab/minions/chongjin && docker compose down
cd ~/pyu-opennms_lab/minions/hamhung && docker compose down
cd ~/pyu-opennms_lab/horizon && docker compose down
echo ""
echo "Lab stopped. Data preserved in Docker volumes."
echo "=========================================="
