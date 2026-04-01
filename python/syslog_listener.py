import socket
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)

RECEIVER_URL = 'http://localhost:5000/alert'
HOST = '0.0.0.0'
PORT = 5141

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
log.info(f'Syslog listener running on UDP {PORT}')

while True:
    data, addr = sock.recvfrom(4096)
    message = data.decode('utf-8', errors='replace').strip()
    log.info(f'Syslog from {addr[0]}: {message}')
    payload = {
        'id': f'syslog-{addr[0]}-{hash(message)}',
        'source': 'syslog',
        'severity': 'MAJOR' if 'down' in message.lower() else 'WARNING',
        'nodeLabel': addr[0],
        'uei': 'uei.opennms.org/generic/syslog/default',
        'description': message
    }
    try:
        r = requests.post(RECEIVER_URL, json=payload, timeout=5)
        log.info(f'Forwarded to receiver status={r.status_code}')
    except Exception as e:
        log.error(f'Failed to forward: {e}')

# Author: Jose Batalha De Vasconcelos - COM617 Group 15
