from models import Alert

# UEI keyword to fault type mapping — extend this dict for new alert types
UEI_FAULT_MAP = {
    'linkdown'            : 'link_down',
    'linkup'              : 'link_up',
    'snmp_link_down'      : 'link_down',
    'bgp'                 : 'bgp_loss',
    'bgpbackwardtransition': 'bgp_loss',
    'highthreshold'       : 'high_cpu',
    'interfaceindexchange': 'link_down',
    'ospf'                : 'link_down',
}

def classify_alert(alert: Alert) -> str:
    """Classify an alert into a fault type based on UEI keywords."""
    uei_lower = alert.event_uei.lower()
    for keyword, fault in UEI_FAULT_MAP.items():
        if keyword in uei_lower:
            return fault

    # Fallback: severity-based classification
    if alert.severity == 'CRITICAL':
        return 'link_down'
    if alert.severity == 'MAJOR':
        return 'bgp_loss'
    if alert.severity == 'MINOR':
        return 'high_cpu'

    return 'unknown'
