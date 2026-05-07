from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import ntfrcv
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)

RECEIVER_URL = 'http://172.21.0.1:5000/alert'

# Map trap source IP to clab node label so the receiver can target the correct
# container for diagnostics. Keys are clab-marr-lab IPv4 addresses on marr-net.
IP_TO_NODE = {
    '172.21.0.101': 'clab-marr-lab-router1',
    '172.21.0.102': 'clab-marr-lab-router2',
    '172.21.0.103': 'clab-marr-lab-router3',
    '172.21.0.111': 'clab-marr-lab-solent-2-router',
    '172.21.0.121': 'clab-marr-lab-solent-1-router',
}

snmpEngine = engine.SnmpEngine()
config.addTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpTransport().openServerMode(('0.0.0.0', 162))
)
config.addV1System(snmpEngine, 'public-area', 'public')

def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    # Resolve trap source IP -> node label via lookup table
    source_ip = 'unknown'
    try:
        _, transportAddress = snmpEngine.message_dispatcher.get_transport_info(stateReference)
        source_ip = transportAddress[0]
    except Exception as e:
        log.warning(f'Could not resolve transport info: {e}')
    node_label = IP_TO_NODE.get(source_ip, source_ip)

    log.info(f'SNMP trap received ref={stateReference} from {source_ip} -> {node_label}')
    payload = {
        'id': f'snmp-{stateReference}',
        'source': 'snmp',
        'severity': 'MAJOR',
        'nodeLabel': node_label,
        'uei': 'uei.opennms.org/generic/traps/SNMP_Link_Down',
        'description': 'SNMP trap received',
        'varBinds': [(str(k), str(v)) for k, v in varBinds]
    }
    try:
        r = requests.post(RECEIVER_URL, json=payload, timeout=30)
        log.info(f'Forwarded to receiver status={r.status_code}')
    except Exception as e:
        log.error(f'Failed to forward: {e}')

ntfrcv.NotificationReceiver(snmpEngine, cbFun)
snmpEngine.transportDispatcher.jobStarted(1)
log.info('SNMP listener running on UDP 162')

try:
    snmpEngine.transportDispatcher.runDispatcher()
except KeyboardInterrupt:
    snmpEngine.transportDispatcher.closeDispatcher()

# Author: Jose Batalha De Vasconcelos - COM617 Group 15
