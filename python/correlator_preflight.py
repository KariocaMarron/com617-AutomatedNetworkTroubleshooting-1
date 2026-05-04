"""
Phase 1 read-only consumer skeleton.
Subscribes to snmp.traps, prints events, exits cleanly.
This is NOT the real correlator. Throwaway diagnostic probe.
COM617 Group 15 - 3 May 2026 - lab session.
"""
import json
import logging
import sys
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("correlator_preflight")

BOOTSTRAP = "localhost:9092"
TOPIC = "snmp.traps"
GROUP_ID = "marr-correlator-preflight"
IDLE_TIMEOUT_MS = 30_000
MAX_MESSAGES = 10

def main() -> int:
    log.info(f"Connecting to {BOOTSTRAP}, topic={TOPIC}, group={GROUP_ID}")
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=BOOTSTRAP,
            group_id=GROUP_ID,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            consumer_timeout_ms=IDLE_TIMEOUT_MS,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            client_id="marr-correlator-preflight",
        )
    except KafkaError as e:
        log.error(f"Kafka connection failed: {e}")
        return 2

    log.info(f"Consumer ready. Will exit after {IDLE_TIMEOUT_MS//1000}s idle "
             f"or {MAX_MESSAGES} messages.")

    count = 0
    try:
        for msg in consumer:
            count += 1
            ev = msg.value
            log.info(
                "[%d] partition=%d offset=%d id=%s severity=%s uei=%s nodeLabel=%s",
                count, msg.partition, msg.offset,
                ev.get("id"), ev.get("severity"), ev.get("uei"), ev.get("nodeLabel"),
            )
            if count >= MAX_MESSAGES:
                log.info(f"Reached MAX_MESSAGES ({MAX_MESSAGES}); exiting.")
                break
    except KeyboardInterrupt:
        log.info("Interrupted by user; exiting.")
    finally:
        consumer.close()

    log.info(f"Total messages consumed: {count}")
    return 0 if count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
