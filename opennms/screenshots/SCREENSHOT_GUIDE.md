# Screenshot Documentation Guide
**Project:** Pyongyang University Network Monitoring Infrastructure  
**Student:** Jose Vasconcelos (KariocaMarron)  
**Date:** 29 December 2025

---

## Screenshot Checklist

### 1. OpenNMS Dashboard (Priority: HIGH)
**URL:** http://localhost:8980/opennms

**Screenshots needed:**
- [ ] Main dashboard showing node summary
- [ ] Outage summary
- [ ] Alarm summary
- [ ] Surveillance view

**Filename pattern:** `01_opennms_dashboard_*.png`

---

### 2. Node List & Details (Priority: HIGH)
**URL:** http://localhost:8980/opennms/element/nodeList.htm

**Screenshots needed:**
- [ ] Complete node list (39 nodes)
- [ ] Pyongyang node details
- [ ] Hamhung node details
- [ ] Chongjin node details
- [ ] Network device details (showing SNMP data)

**Filename pattern:** `02_nodes_*.png`

---

### 3. Service Monitoring (Priority: HIGH)
**Check each service interface:**

**VLE (port 8081):**
- [ ] http://localhost:8081 - VLE homepage
- [ ] OpenNMS service status for VLE

**LDAP Admin (port 8082):**
- [ ] http://localhost:8082 - phpLDAPadmin interface
- [ ] LDAP tree structure showing university OUs

**DNS/DHCP (port 8083):**
- [ ] http://localhost:8083 - dnsmasq web interface
- [ ] DNS configuration display

**Semaphore (port 8084):**
- [ ] http://localhost:8084 - Semaphore dashboard
- [ ] Project view (if any created)

**FOG Server (port 8085):**
- [ ] http://localhost:8085 - FOG interface
- [ ] Features display

**Filename pattern:** `03_services_*.png`

---

### 4. Network Topology (Priority: MEDIUM)
**URL:** http://localhost:8980/opennms/topology

**Screenshots needed:**
- [ ] Full network topology view
- [ ] Pyongyang campus zoom
- [ ] Hamhung campus connections
- [ ] Chongjin campus connections

**Filename pattern:** `04_topology_*.png`

---

### 5. Remote Campus Web Servers (Priority: MEDIUM)

**Hamhung Web Server:**
- [ ] http://172.18.0.32 or via OpenNMS

**Chongjin Web Server:**
- [ ] http://172.18.0.42 or via OpenNMS

**Filename pattern:** `05_campuses_*.png`

---

### 6. Monitoring Details (Priority: MEDIUM)
**URL:** http://localhost:8980/opennms

**Screenshots needed:**
- [ ] Service availability report
- [ ] Performance graphs (if any)
- [ ] Event list
- [ ] Categories view showing Pyongyang/Hamhung/Chongjin

**Filename pattern:** `06_monitoring_*.png`

---

### 7. Container Infrastructure (Priority: LOW)
**Terminal commands:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker stats --no-stream
```

**Screenshots needed:**
- [ ] Container list showing all 24 containers
- [ ] Resource usage statistics

**Filename pattern:** `07_infrastructure_*.png`

---

## Access Information Quick Reference

| Service | URL | Credentials |
|---------|-----|-------------|
| OpenNMS | http://localhost:8980/opennms | admin/admin |
| VLE | http://localhost:8081 | N/A |
| LDAP Admin | http://localhost:8082 | cn=admin,dc=pyu,dc=edu,dc=kp / admin |
| DNS/DHCP | http://localhost:8083 | N/A |
| Semaphore | http://localhost:8084 | admin/admin |
| FOG Server | http://localhost:8085 | N/A |
| Hamhung Web | http://172.18.0.32 | N/A |
| Chongjin Web | http://172.18.0.42 | N/A |

---

## Screenshot Instructions

### For Browser Screenshots:
1. Open service in browser
2. Press F11 for full-screen (optional)
3. Use browser screenshot tool or:
   - **Firefox:** Right-click → "Take Screenshot"
   - **Chrome:** Ctrl+Shift+P → "Capture screenshot"
4. Save with descriptive filename

### For Terminal Screenshots:
1. Make terminal window appropriately sized
2. Run command
3. Use screenshot tool (e.g., `gnome-screenshot`, `scrot`)
4. Or use: `gnome-screenshot -w` (current window)

### Tips:
- Use high resolution (at least 1920x1080)
- Ensure text is readable
- Include relevant context (URLs, timestamps)
- Remove sensitive information if any
- Use consistent naming convention

---

## Estimated Time

- OpenNMS screenshots: 10 minutes
- Service screenshots: 10 minutes  
- Network topology: 5 minutes
- Remote campuses: 3 minutes
- Infrastructure: 2 minutes

**Total: ~30 minutes**

---

## After Screenshots

Once collected, create an index document showing:
1. Screenshot thumbnails
2. Brief descriptions
3. What each screenshot demonstrates
4. How it relates to case study requirements

---

**Status:** Ready for screenshot collection  
**Priority Order:** OpenNMS → Services → Topology → Campuses → Infrastructure
