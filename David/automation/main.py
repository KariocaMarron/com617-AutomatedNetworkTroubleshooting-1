import os
import time

devices = {
    "r1": "172.20.20.3",
    "r2": "172.20.20.2"
}

def ping_device(ip):
    response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
    return response == 0

while True:
    print("\nChecking network status...\n")

    for name, ip in devices.items():
        if ping_device(ip):
            print(f"{name} ({ip}) is UP")
        else:
            print(f"{name} ({ip}) is DOWN 🚨")
            # Placeholder for automation
            print(f"Running diagnostics for {name}...")

    time.sleep(10)X
