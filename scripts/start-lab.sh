#!/bin/bash
echo "=========================================="
echo "  MARR Lab - Start Script"
echo "  COM617 Group 15 | Cisco ICP 2026"
echo "=========================================="

echo "[1/4] Starting OpenNMS core stack..."
cd /home/cyber/Solent_Final_Lab/opennms/horizon && docker compose up -d
echo "      Waiting 60s for OpenNMS to initialise..."
sleep 60

echo "[2/4] Starting Mattermost..."
cd /home/cyber/Solent_Final_Lab/mattermost && docker compose up -d
sleep 10

echo "[3/4] Deploying Containerlab topology..."
cd /home/cyber/Solent_Final_Lab/containerlab && sudo containerlab deploy -t lab-topology.yml
sleep 10

echo "[4/4] Starting classifier engine..."
cd /home/cyber/Solent_Final_Lab
nohup python3 python-engine/classifier.py > logs/classifier.log 2>&1 &
echo $! > logs/classifier.pid
echo "      Classifier PID: $(cat logs/classifier.pid)"

echo ""
echo "=========================================="
echo "  Lab Ready!"
echo "  OpenNMS  : http://localhost:8980"
echo "  Mattermost: http://localhost:8065"
echo "  Classifier: tail -f logs/classifier.log"
echo "=========================================="
