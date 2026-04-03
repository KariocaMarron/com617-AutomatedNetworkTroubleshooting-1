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

def run_command(command):
    return os.popen(command).read().strip()

def run_diagnostics(container_name):
    runbook = determine_runbook(container_name)

    print(f"{container_name} is DOWN 🚨")
    print(f"Triggering runbook: {runbook}")
    print("Running real diagnostics...\n")

    inspect_output = run_command(f"docker inspect {container_name} 2>/dev/null")
    logs_output = run_command(f"docker logs --tail 20 {container_name} 2>/dev/null")
    ps_output = run_command("docker ps -a")

    diagnostic_output = [
        f"Fault detected on {container_name}",
        f"Selected runbook: {runbook}",
        "",
        "=== Docker PS -A Output ===",
        ps_output,
        "",
        f"=== Docker Inspect Output for {container_name} ===",
        inspect_output if inspect_output else "No inspect data available.",
        "",
        f"=== Recent Logs for {container_name} ===",
        logs_output if logs_output else "No logs available."
    ]

    print("Collected diagnostics:")
    print("- Docker status captured")
    print("- Container inspection captured")
    print("- Recent logs captured\n")

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



