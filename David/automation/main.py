import os
import time

containers = ["clab-com617-lab-r1", "clab-com617-lab-r2"]

def is_container_running(name):
    result = os.system(f"docker inspect -f '{{{{.State.Running}}}}' {name} > /dev/null 2>&1")
    return result == 0

while True:
    print("\nChecking network status...\n")

    for container in containers:
        check = os.popen(f"docker inspect -f '{{{{.State.Running}}}}' {container}").read().strip()

        if check == "true":
            print(f"{container} is UP")
        else:
            print(f"{container} is DOWN 🚨")
            print(f"Running diagnostics for {container}...")

    time.sleep(10)



