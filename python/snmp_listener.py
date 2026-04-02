from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import ntfrcv
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)

RECEIVER_URL = 'http://172.21.0.1:5000/alert'

snmpEngine = engine.SnmpEngine()
config.addTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpTransport().openServerMode(('0.0.0.0', 162))
)
config.addV1System(snmpEngine, 'public-area', 'public')

def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    log.info(f'SNMP trap received ref={stateReference}')
    payload = {
        'id': f'snmp-{stateReference}',
        'source': 'snmp',
        'severity': 'MAJOR',
        'nodeLabel': 'unknown',
        'uei': 'uei.opennms.org/generic/traps/SNMP_Link_Down',
        'description': 'SNMP trap received',
        'varBinds': [(str(k), str(v)) for k, v in varBinds]
    }
    try:
        r = requests.post(RECEIVER_URL, json=payload, timeout=5)
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


