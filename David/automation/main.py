import os
import time
from datetime import datetime

containers = ["clab-com617-lab-r1", "clab-com617-lab-r2"]
last_status = {}


def get_container_status(name):
    check = os.popen(f"docker inspect -f '{{{{.State.Running}}}}' {name} 2>/dev/null").read().strip()
    return check == "true"


def determine_runbook(container_name):
    if "r1" in container_name or "r2" in container_name:
        return "RB-01 Interface Up/Down"
    return "Unknown Runbook"


def run_command(command):
    return os.popen(command).read().strip()


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


def report_recovery(container_name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/{container_name}_recovery_{timestamp}.txt"

    print(f"{container_name} has recovered ✅")
    print("Service restored.")
    print("Generating recovery report...\n")

    with open(filename, "w") as report_file:
        report_file.write("Automated Network Troubleshooting Recovery Report\n")
        report_file.write("=" * 50 + "\n")
        report_file.write(f"Timestamp: {datetime.now()}\n")
        report_file.write(f"Recovered Node: {container_name}\n")
        report_file.write("Status: UP\n")
        report_file.write("Service restored successfully.\n")
        report_file.write("Recovery detected automatically by the monitoring script.\n")

    print(f"Recovery report saved: {filename}\n")


try:
    while True:
        print("\nChecking network status...\n")

        for container in containers:
            current_status = get_container_status(container)
            previous_status = last_status.get(container)

            if previous_status is None:
                last_status[container] = current_status

                if current_status:
                    print(f"{container} is UP")
                else:
                    print(f"{container} is DOWN 🚨")
                continue

            if previous_status and not current_status:
                run_diagnostics(container)

            elif not previous_status and current_status:
                report_recovery(container)

            else:
                if current_status:
                    print(f"{container} is still UP")
                else:
                    print(f"{container} is still DOWN")

            last_status[container] = current_status

        time.sleep(10)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")
