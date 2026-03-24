# Maps fault type to Ansible playbook name
# Add new fault types here as the project expands
RUNBOOK_MAP = {
    'link_down' : 'diagnose_link_down',
    'bgp_loss'  : 'diagnose_bgp_neighbour_loss',
    'high_cpu'  : 'diagnose_high_cpu',
    'link_up'   : None,    # No diagnostic action needed
    'unknown'   : 'diagnose_link_down',  # Safe default
}

def select_runbook(fault_type: str) -> str:
    """Select the appropriate Ansible playbook for a given fault type."""
    return RUNBOOK_MAP.get(fault_type, 'diagnose_link_down')
