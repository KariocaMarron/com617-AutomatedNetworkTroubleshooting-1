# COM617 MARR Lab — Shortcut Commands
# Usage: make <target>
# Run from repo root: ~/Solent_Final_Lab/
# Author: Jose Batalha De Vasconcelos - COM617 Group 15

.PHONY: start stop restart status wipe logs test snmp syslog kafka docker-up

start:
	ansible-playbook scripts/lab-start.yml

docker-up:
	docker compose up -d
	docker compose -f mattermost/docker-compose.yml up -d
	cd opennms/horizon && docker compose up -d

stop:
	ansible-playbook scripts/lab-stop.yml

restart: stop start

wipe:
	ansible-playbook scripts/lab-stop.yml --extra-vars "wipe_data=true"

status:
	@echo "--- Docker Compose services ---"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "marr|NAME"
	@echo ""
	@echo "--- Systemd services ---"
	@systemctl is-active marr-receiver marr-syslog marr-snmp
	@echo ""
	@echo "--- Containerlab ---"
	@sudo containerlab inspect --topo containerlab/lab-topology.yml 2>/dev/null || echo "Containerlab not running"
	@echo ""
	@echo "--- Port inventory ---"
	@ss -tlnp | grep -E ':5000|:8065|:8980|:9090|:3000|:8200|:9092|:6380' || true
	@sudo ss -ulnp | grep -E ':162 |:514 ' || true

logs:
	@echo "--- Alert receiver ---"
	@sudo journalctl -u marr-receiver -n 20 --no-pager
	@echo ""
	@echo "--- Syslog listener ---"
	@sudo journalctl -u marr-syslog -n 20 --no-pager
	@echo ""
	@echo "--- SNMP listener ---"
	@docker exec clab-com617-marr-lab-snmp-notifier cat /tmp/snmp.log 2>/dev/null | tail -20 || echo "SNMP log not found"

test:
	@echo "Sending test alert..."
	@curl -s -X POST http://localhost:5000/alert \
		-H 'Content-Type: application/json' \
		-d '{"id":"MAKE-TEST-001","nodeLabel":"router1","severity":"CRITICAL","source":"snmp","uei":"uei.opennms.org/generic/traps/SNMP_Link_Down","description":"Makefile test alert"}' \
		| python3 -m json.tool

snmp:
	@echo "Sending SNMP trap from router1..."
	@docker exec clab-marr-lab-router1 snmptrap -v 2c -c public 172.20.0.14 '' .1.3.6.1.6.3.1.1.5.3
	@sleep 3
	@docker exec clab-com617-marr-lab-snmp-notifier cat /tmp/snmp.log | tail -5

syslog:
	@echo "Sending syslog message from router1..."
	@echo "<134>OSPF neighbour down on eth1" | docker exec -i clab-marr-lab-router1 nc -u -w1 172.20.0.1 514
	@sleep 3
	@sudo journalctl -u marr-syslog -n 5 --no-pager

kafka:
	@echo "--- Kafka topics ---"
	@docker exec marr-kafka kafka-topics --bootstrap-server localhost:9092 --list
	@echo ""
	@echo "--- Last message in raw.alerts ---"
	@docker exec marr-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic raw.alerts --from-beginning --max-messages 1 --timeout-ms 3000 2>/dev/null || echo "No messages"
