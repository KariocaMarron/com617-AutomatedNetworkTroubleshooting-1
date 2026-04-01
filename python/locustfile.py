from locust import HttpUser, task, between
import random
import uuid

class AlertStorm(HttpUser):
    wait_time = between(0.1, 0.3)

    @task
    def send_alert(self):
        self.client.post("/alert", json={
            "id": str(uuid.uuid4()),
            "nodeLabel": random.choice(["router1", "router2", "router3"]),
            "severity": random.choice(["CRITICAL", "MAJOR", "MINOR", "WARNING"]),
            "source": "loadtest",
            "uei": "uei.opennms.org/generic/traps/SNMP_Link_Down",
            "description": "Synthetic load test alert"
        })

    @task
    def send_link_down(self):
        self.client.post("/alert", json={
            "id": str(uuid.uuid4()),
            "nodeLabel": random.choice(["router1", "router2", "router3"]),
            "severity": "CRITICAL",
            "source": "loadtest",
            "uei": "uei.opennms.org/generic/traps/SNMP_Link_Down",
            "description": "Interface eth1 down",
            "ifDescr": "eth1"
        })

# Author: Jose Batalha De Vasconcelos - COM617 Group 15
