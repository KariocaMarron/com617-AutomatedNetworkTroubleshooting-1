import os
import time
from datetime import datetime

containers = ["clab-com617-lab-r1", "clab-com617-lab-r2"]


def get_container_status(name):
    check = os.popen(f"docker inspect -f '{{{{.State.Running}}}}' {name} 2>/dev/null").read().strip()
    return check == "true"


def determine_runbook(container_name):
    # For now, if the container is down, use the interface/device down runbook
    if "r1" in container_name or "r2" in container_name:
        return "RB-01 Interface Up/Down"
    return "Unknown Runbook"


def run_diagnostics(container_name):
    runbook = determine_runbook(container_name)

    diagnostic_output = [
        f"Fault detected on {container_name}",
        f"Selected runbook: {runbook}",
        "Diagnostic actions:",
        "- Check container state",
        "- Verify recent connectivity status",
        "- Recommend checking interface/link or restarting the device"
    ]

    print(f"{container_name} is DOWN 🚨")
    print(f"Triggering runbook: {runbook}")
    print("Running diagnostics...")
    for line in diagnostic_output[2:]:
        print(line)

    save_report(container_name, runbook, diagnostic_output)


def save_report(container_name, runbook, diagnostic_output):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/{container_name}_{timestamp}.txt"

    with open(filename, "w") as report_file:
        report_file.write("Automated Network Troubleshooting Report\n")
        report_file.write("=" * 40 + "\n")
        report_file.write(f"Timestamp: {datetime.now()}\n")
        report_file.write(f"Affected Node: {container_name}\n")
        report_file.write(f"Runbook Used: {runbook}\n\n")
        for line in diagnostic_output:
            report_file.write(line + "\n")

    print(f"Report saved: {filename}\n")


while True:
    print("\nChecking network status...\n")

    for container in containers:
        if get_container_status(container):
            print(f"{container} is UP")
        else:
            run_diagnostics(container)

    time.sleep(10)



