# Project Scope – Automated Network Troubleshooting System

## 1. Project Overview
This project aims to develop a Proof of Concept (PoC) automated network troubleshooting system. The system will monitor network events, analyse detected faults, execute predefined diagnostic procedures, and generate structured reports to assist network engineers in identifying issues efficiently.

---

## 2. In-Scope Features
The system will include the following functionality:

- Detection of network alerts from monitoring systems (e.g., OpenNMS)
- Support for the following fault types:
  - Interface up/down
  - Neighbour adjacency change
- Automated execution of diagnostic commands using predefined runbooks
- Basic fault classification based on diagnostic results
- Generation of structured diagnostic reports
- Delivery of reports via console output and/or messaging platform (e.g., Mattermost)

---

## 3. Out-of-Scope Features
The following features are excluded from this Proof of Concept:

- Automatic remediation or fixing of network issues
- Support for all network vendors and device types
- Handling of all possible alert types
- Advanced correlation of multiple simultaneous alerts
- Full production-level deployment and scalability
- Complex user interface or dashboard development

---

## 4. Assumptions
The project is based on the following assumptions:

- A simulated network environment (e.g., Containerlab) will be used
- Alerts will be generated and received in a controlled environment
- Standard diagnostic commands will be sufficient for fault analysis
- The system will operate on a limited number of devices

---

## 5. Constraints
The project is subject to the following constraints:

- Limited development time (Sprint-based delivery)
- Limited access to real production network environments
- Dependence on chosen tools (OpenNMS, Ansible, etc.)
- Varying technical complexity across system components
