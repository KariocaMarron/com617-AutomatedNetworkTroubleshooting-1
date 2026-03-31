# Runbook RB-01: Interface Up/Down

## 1. Fault Type
Interface Operational Status Change (Up ↔ Down)

---

## 2. Description
This runbook is triggered when a network interface changes its operational state unexpectedly.  
The purpose is to automatically collect diagnostic information to help determine the cause of the issue.

Possible causes include:
- Physical link failure
- Administrative shutdown
- Hardware faults
- Configuration issues
- Neighbour device failure

This runbook focuses on **diagnostic data collection only**, not automatic remediation.

---

## 3. Trigger Condition
This runbook is triggered when a monitoring system (e.g., OpenNMS) detects:

- `linkDown` event  
- `linkUp` event  
- Interface status change alert  

The alert should include:
- Device hostname or IP address  
- Interface identifier  
- Timestamp of event  

---

## 4. Diagnostic Objectives
The automated diagnostics aim to:

- Confirm current interface status  
- Determine if the interface is administratively shut down  
- Identify input/output errors  
- Detect interface instability (flapping)  
- Verify connectivity to neighbouring device  

---

## 5. Diagnostic Commands
The following commands will be executed on the affected device:

- `show ip interface brief`  
- `show interface <interface>`  
- `show running-config interface <interface>`  
- `show logging | include <interface>`  
- `show cdp neighbors` (or `show lldp neighbors`)  

---

## 6. Data to Collect
The system should collect and report:

- Interface operational state (up/down)  
- Administrative status  
- Error counters (e.g., CRC, input/output errors)  
- Last state change timestamp  
- Speed and duplex settings  
- Neighbour device information (if available)  

---

## 7. Fault Classification Logic

| Condition | Likely Cause |
|----------|-------------|
| Interface down + administratively down | Manual shutdown |
| Interface down + high error count | Physical cable or hardware issue |
| Interface flapping repeatedly | Unstable link |
| Interface down + no neighbour detected | Remote device failure |

---

## 8. Escalation Criteria
The issue should be escalated if:

- The interface is part of a critical network path  
- Hardware errors exceed acceptable thresholds  
- The interface flaps multiple times within a short period  
- A core or distribution device is affected  

---

## 9. Expected Output
The system should generate a structured report including:

- Alert summary  
- Affected device and interface  
- Current interface state  
- Key diagnostic findings  
- Preliminary fault classification  
- Recommended next steps  

### Example Output
Interface Gig0/1 on Router1 is down. No administrative shutdown detected. High CRC errors observed. Likely physical layer issue. Manual inspection recommended.
