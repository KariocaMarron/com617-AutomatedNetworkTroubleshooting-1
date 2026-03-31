# Runbook RB-02: Neighbour Change Detection

## 1. Fault Type
Neighbour Adjacency Change (CDP / LLDP / Routing Neighbour)

---

## 2. Description
This runbook is triggered when a neighbouring device relationship changes unexpectedly.  
This includes the loss, addition, or instability of a neighbour connection.

Possible causes include:
- Physical link failure
- Remote device failure
- Routing protocol issues
- Configuration mismatches
- Planned or unplanned topology changes

This runbook focuses on **diagnostic verification and analysis**, not automatic remediation.

---

## 3. Trigger Condition
This runbook is triggered when a monitoring system (e.g., OpenNMS) detects:

- Loss of CDP or LLDP neighbour  
- Routing adjacency down event (e.g., OSPF, BGP)  
- Unexpected new neighbour detected  
- Neighbour state change alert  

The alert should include:
- Device hostname or IP address  
- Interface associated with the neighbour  
- Neighbour device ID (if available)  
- Timestamp of the event  

---

## 4. Diagnostic Objectives
The automated diagnostics aim to:

- Confirm the current neighbour state  
- Verify the status of the associated interface  
- Check routing protocol adjacency (if applicable)  
- Identify configuration inconsistencies  
- Determine whether the issue is local or remote  

---

## 5. Diagnostic Commands

### Layer 2 Neighbour Checks
- `show cdp neighbors`  
- `show lldp neighbors`  
- `show interface <interface>`  

### Routing Adjacency Checks
- `show ip ospf neighbor`  
- `show ip bgp summary`  
- `show ip route`  

### Log Analysis
- `show logging | include neighbor`  

---

## 6. Data to Collect
The system should collect and report:

- Current neighbour list  
- Missing or changed neighbour device ID  
- Interface operational status  
- Routing adjacency state (if applicable)  
- Timestamp of last state change  
- Relevant log entries  

---

## 7. Fault Classification Logic

| Condition | Likely Cause |
|----------|-------------|
| Neighbour lost + interface down | Physical link failure |
| Neighbour lost + interface up | Remote device failure |
| Routing neighbour down + interface up | Protocol or configuration issue |
| Unexpected new neighbour detected | Topology change or misconfiguration |
| Frequent adjacency resets | Network instability |

---

## 8. Escalation Criteria
The issue should be escalated if:

- A core routing adjacency is lost  
- Multiple neighbours drop simultaneously  
- Routing instability is detected  
- A critical network device is affected  

---

## 9. Expected Output
The system should generate a structured report including:

- Event summary  
- Affected device  
- Missing or changed neighbour  
- Interface status  
- Routing adjacency status  
- Diagnostic findings  
- Preliminary fault classification  
- Recommended next steps  

### Example Output
OSPF neighbour 10.1.1.2 on Router1 has transitioned to Down state. The local interface remains operational. No physical errors detected. Likely remote device issue or routing configuration mismatch. Manual verification recommended.
