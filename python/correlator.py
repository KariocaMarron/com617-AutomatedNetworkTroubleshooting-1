#!/usr/bin/env python3
"""
correlator.py
The MARR correlator. Subscribes to the Kafka snmp.traps and raw.alerts
topics, accumulates events into source-key-keyed sliding windows in Redis,
and emits a single grouped Mattermost incident report when two or more
events share a window.

Architectural placement (per Section 9 of the Lab Session Log):
- Runs as a host-side systemd service (marr-correlator) alongside the existing
  marr-receiver, marr-syslog, marr-snmp services.
- Does not modify alert_receiver.py's existing per-event path; instead reads
  from the same Kafka topics the receiver writes to.
- If the correlator dies or is disabled, the per-event reporting flow is
  unaffected: the receiver's suppression check fails open (returns False on
  Redis error or absent lease), so per-event Mattermost notifications resume.

Design notes:
- Source-key strategy is M (synthetic): nodeLabel + ifIndex. See
  correlator_state.source_key() for the canonical implementation.
- Lease acquisition uses Redis SET NX EX for atomic single-emitter semantics.
- Window emission blocks the consumer thread for WINDOW_SECONDS after a
  qualifying group is detected; this is acceptable for single-instance
  deployment and is documented as a known limitation.
- Redis sorted sets accumulate the in-window events; ZADD is idempotent on
  member, so duplicate processing is safe.

COM617 Group 15 - 3 May 2026 - lab session.
"""

import json
import logging
import os
import signal
import sys
import time
import uuid

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import redis
from redis.exceptions import RedisError

from correlator_state import (
    REDIS_HOST, REDIS_PORT, REDIS_TIMEOUT,
    WINDOW_SECONDS,
    KEY_WINDOW, KEY_LEASE, KEY_GROUPED,
    source_key,
)

# Load .env BEFORE importing mattermost_notifier - WEBHOOK_URL is read at
# the notifier's module load time. Without this, systemd-launched correlator
# would see WEBHOOK_URL='' and skip every grouped report. Mirrors the pattern
# used by alert_receiver.py. Diagnosis recorded in Lab Session Log Section 9.
from pathlib import Path as _Path
from dotenv import load_dotenv as _load_dotenv
_BASE_DIR = _Path(__file__).resolve().parent.parent
_load_dotenv(dotenv_path=_BASE_DIR / ".env")

from mattermost_notifier import send_grouped_incident_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [correlator] %(message)s",
)
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPICS = ["snmp.traps", "raw.alerts"]
GROUP_ID = "marr-correlator"
INSTANCE_ID = str(uuid.uuid4())[:8]

# Minimum number of events to trigger grouped emission.
GROUP_THRESHOLD = int(os.getenv("MARR_GROUP_THRESHOLD", "2"))


def _redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=REDIS_TIMEOUT,
        socket_timeout=REDIS_TIMEOUT,
    )


def _build_consumer():
    return KafkaConsumer(
        *TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="latest",   # IMPORTANT: only react to new events
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        client_id=f"marr-correlator-{INSTANCE_ID}",
    )


def _shutdown(signum, _frame):
    log.info(f"Received signal {signum}, shutting down.")
    sys.exit(0)


def emit_grouped_report(skey: str, r: redis.Redis) -> None:
    """Materialise and emit the grouped report for a source key, then clean up.

    Called only by the lease holder. Reads the full sorted set, builds a
    list of event payloads, posts the grouped Mattermost report, and removes
    the window key. The lease key is left to expire naturally so any late
    events arriving in the same source-key bucket are also suppressed for
    the lease's remaining TTL.
    """
    window_key = f"{KEY_WINDOW}:{skey}"
    grouped_marker = f"{KEY_GROUPED}:{skey}"
    try:
        members = r.zrange(window_key, 0, -1)
        events = []
        for m in members:
            try:
                events.append(json.loads(m))
            except json.JSONDecodeError:
                log.warning(f"Skipping malformed window member for {skey}")
        if not events:
            log.warning(f"No events to emit for {skey}; skipping.")
            return
        log.info(f"Emitting grouped report for {skey} with {len(events)} events.")
        ok = send_grouped_incident_report(skey, events)
        if ok:
            r.set(grouped_marker, "1", ex=WINDOW_SECONDS * 2)
        r.delete(window_key)
    except RedisError as e:
        log.error(f"Redis error during emit for {skey}: {e}")
    except Exception as e:
        log.exception(f"Unexpected error during emit for {skey}: {e}")


def process_event(payload: dict, r: redis.Redis) -> None:
    """Add event to its source-key window; if threshold reached, acquire lease
    and schedule emission."""
    skey = source_key(payload)
    window_key = f"{KEY_WINDOW}:{skey}"
    lease_key = f"{KEY_LEASE}:{skey}"
    grouped_marker = f"{KEY_GROUPED}:{skey}"
    now = time.time()

    # Skip if this source-key was already emitted recently (idempotency).
    try:
        if r.exists(grouped_marker):
            log.info(f"Source key {skey} already emitted recently; skipping.")
            return
    except RedisError:
        pass  # fail-safe: continue

    member = json.dumps(payload, sort_keys=True)
    try:
        r.zadd(window_key, {member: now})
        # Window TTL is 2x the configured window so it survives the
        # lease holder's time.sleep(WINDOW_SECONDS) wait. Without this,
        # Redis TTL-expires the window key before zrange reads it, and
        # the grouped emission fires against an empty window. This was
        # observed empirically during Phase 2 Step 7 cascade testing on
        # 3 May 2026; the diagnosis and fix are recorded in the Lab
        # Session Log Section 9 (race-condition finding).
        r.expire(window_key, WINDOW_SECONDS * 2)
        count = r.zcard(window_key)
    except RedisError as e:
        log.error(f"Redis ZADD failed for {skey}: {e}")
        return

    log.info(f"Window for {skey} now has {count} event(s).")

    if count < GROUP_THRESHOLD:
        return

    # Threshold reached - try to acquire the emission lease.
    try:
        won = r.set(lease_key, INSTANCE_ID, nx=True, ex=WINDOW_SECONDS)
    except RedisError as e:
        log.error(f"Redis SET NX failed for {skey}: {e}")
        return

    if not won:
        log.info(f"Lease for {skey} held elsewhere; skipping emission.")
        return

    log.info(f"Lease acquired for {skey}; waiting {WINDOW_SECONDS}s for window to fill.")
    time.sleep(WINDOW_SECONDS)
    emit_grouped_report(skey, r)


def main() -> int:
    log.info(f"MARR correlator starting (instance={INSTANCE_ID}).")
    log.info(f"Kafka bootstrap={KAFKA_BOOTSTRAP}, topics={TOPICS}, group={GROUP_ID}")
    log.info(f"Redis {REDIS_HOST}:{REDIS_PORT}, window={WINDOW_SECONDS}s, "
             f"threshold={GROUP_THRESHOLD}")

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        r = _redis_client()
        if not r.ping():
            log.error("Redis ping failed; exiting.")
            return 2
    except RedisError as e:
        log.error(f"Redis unreachable at startup: {e}")
        return 2

    try:
        consumer = _build_consumer()
    except KafkaError as e:
        log.error(f"Kafka consumer construction failed: {e}")
        return 3

    log.info("Consumer ready; awaiting events.")
    try:
        for msg in consumer:
            try:
                process_event(msg.value, r)
            except Exception as e:
                log.exception(f"process_event failed; continuing: {e}")
    except KeyboardInterrupt:
        log.info("Interrupted; shutting down.")
    finally:
        try:
            consumer.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
