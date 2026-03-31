from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass
class Alert:
    alert_id:    str
    source_node: str
    severity:    str          # CRITICAL / MAJOR / MINOR / WARNING
    event_uei:   str          # e.g. uei.opennms.org/generic/traps/SNMP_Link_Down
    description: str
    timestamp:   datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interface:   Optional[str] = None
    raw_payload: Optional[dict] = None

@dataclass
class Incident:
    alert:       Alert
    fault_type:  str          # link_down / bgp_loss / high_cpu / unknown
    playbook:    str
    diag_output: Optional[str] = None
    diag_rc:     int = -1
    resolved:    bool = False
