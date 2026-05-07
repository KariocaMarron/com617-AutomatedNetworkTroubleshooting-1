from pathlib import Path
import yaml

from models import Alert

# Load categorisation rule table at import time.
# Rules are externalised to YAML so updates do not require code redeployment (NFR-006).
_RULES_PATH = Path(__file__).parent / "rules" / "categorisation.yaml"
with open(_RULES_PATH) as _f:
    _RULES = yaml.safe_load(_f)

# Public name preserved for backwards compatibility with any importing module.
UEI_FAULT_MAP = _RULES["uei_fault_map"]
_SEVERITY_FALLBACK = _RULES["severity_fallback"]


def classify_alert(alert: Alert) -> str:
    """Classify an alert into a fault type using UEI keyword match with severity fallback."""
    uei_lower = alert.event_uei.lower()
    for keyword, fault in UEI_FAULT_MAP.items():
        if keyword in uei_lower:
            return fault
    return _SEVERITY_FALLBACK.get(alert.severity, _SEVERITY_FALLBACK["default"])
