# OpenNMS Telemetry Configuration Summary
## COM615 Network Management - PYU Infrastructure

**Captured:** January 2026  
**OpenNMS Version:** Horizon 33.0.2

---

## Configuration Location

Telemetry is configured in file-based configuration (not UI):
- **Primary config:** `/opt/opennms/etc/telemetryd-configuration.xml`
- **Adapter scripts:** `/opt/opennms/etc/telemetryd-adapters/`

---

## Available Telemetry Listeners

| Protocol | Port | Transport | Status |
|----------|------|-----------|--------|
| **Multi-UDP** | 9999 | UDP | ✅ **ENABLED** |
| NetFlow v5 | 8877 | UDP | Disabled |
| NetFlow v9 | 4729 | UDP | Disabled |
| IPFIX | 4730 | UDP/TCP | Disabled |
| sFlow | 6343 | UDP | Disabled |
| JTI (Juniper) | 50000 | UDP | Disabled |
| NXOS (Cisco) | 50001 | UDP | Disabled |
| BMP | 5000 | TCP | Disabled |
| Graphite | 2003 | UDP | Disabled |
| OpenConfig | Connector | gRPC | Disabled |

---

## Currently Enabled

Only **Multi-UDP-9999** listener is enabled by default.

This is a multi-protocol listener that can accept:
- NetFlow v5, v9
- IPFIX
- sFlow

---

## To Enable Flow Collection for PYU

To enable NetFlow/IPFIX collection from campus routers, modify:
```xml
<!-- In telemetryd-configuration.xml -->
<listener name="Netflow-9-UDP-4729" enabled="true">
```

Or use the Multi-UDP listener (already enabled on port 9999).

---

## Recommendation for PYU

For the three-campus architecture:
1. Keep Multi-UDP-9999 enabled (accepts multiple flow types)
2. Configure campus routers to export flows to CIOC:9999
3. Minions can forward flows to central Horizon

---

**Jose Vasconcelos - KariocaMarron**  
COM615 Network Management  
Southampton Solent University
