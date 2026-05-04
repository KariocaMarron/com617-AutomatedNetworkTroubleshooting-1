"""
correlator_state.py
Shared state and primitives for the MARR correlator and the alert receiver.
Single source of truth for source-key derivation, Redis connection, and
suppression checks. Both alert_receiver.py and correlator.py import from here.

Design notes:
- Source-key strategy is M (synthetic): nodeLabel + ifIndex. This is documented
  as a deliberate test-time strategy in Section 13 of the Lab Session Log.
- The robust-but-simple ifIndex extraction (option b) scans varBinds for any
  OID matching the ifIndex prefix 1.3.6.1.2.1.2.2.1.1, so it survives trap
  structure variations and is not order-dependent.
- All Redis operations are wrapped to fail-safe: any RedisError is logged and
  treated as "no suppression / no enrichment", so the existing per-event
  reporting path continues to work when Redis is unavailable.

COM617 Group 15 - 3 May 2026 - lab session.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import redis
from redis.exceptions import RedisError

log = logging.getLogger(__name__)

# Tunables
REDIS_HOST = os.getenv("MARR_REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("MARR_REDIS_PORT", "6380"))
REDIS_TIMEOUT = float(os.getenv("MARR_REDIS_TIMEOUT", "1.5"))

WINDOW_SECONDS = int(os.getenv("MARR_CORRELATOR_WINDOW", "30"))
DIAG_TTL_SECONDS = int(os.getenv("MARR_DIAG_TTL", "300"))   # diag context kept for 5 min

KEY_PREFIX = "marr:correlator"
KEY_WINDOW = f"{KEY_PREFIX}:window"
KEY_LEASE = f"{KEY_PREFIX}:lease"
KEY_DIAG = f"{KEY_PREFIX}:diag"
KEY_GROUPED = f"{KEY_PREFIX}:grouped"      # set of source-keys already reported

# OID patterns (kept as constants for grep-ability and future extension)
IFINDEX_OID_PREFIX = "1.3.6.1.2.1.2.2.1.1"      # IF-MIB::ifIndex.<n>


def _client() -> Optional[redis.Redis]:
    """Return a configured Redis client, or None if construction fails."""
    try:
        return redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=REDIS_TIMEOUT,
            socket_timeout=REDIS_TIMEOUT,
        )
    except Exception as e:                                  # noqa: BLE001
        log.warning(f"Redis client construction failed: {e}")
        return None


def extract_ifindex(varbinds: List[List[str]]) -> Optional[str]:
    """
    Scan the varBinds list for an OID matching the ifIndex prefix.
    Returns the ifIndex value as a string, or None if not present.
    Handles arbitrary varbind ordering (option b - robust).
    """
    if not varbinds:
        return None
    for vb in varbinds:
        if not isinstance(vb, (list, tuple)) or len(vb) != 2:
            continue
        oid, value = vb[0], vb[1]
        if isinstance(oid, str) and oid.startswith(IFINDEX_OID_PREFIX + "."):
            return str(value)
    return None


def source_key(payload: Dict[str, Any]) -> str:
    """
    Compute the canonical source key for an event payload.
    Strategy M (synthetic test-time): nodeLabel + ifIndex.
    Falls back to nodeLabel alone if ifIndex cannot be extracted.
    """
    node_label = payload.get("nodeLabel") or "unknown"
    ifindex = extract_ifindex(payload.get("varBinds") or [])
    if ifindex is not None:
        return f"{node_label}::{ifindex}"
    return f"{node_label}"


def is_suppressed(skey: str) -> bool:
    """
    Receiver-side suppression check. Returns True only when an active lease
    is present for this source key. Fail-safe: any Redis error returns False.
    """
    client = _client()
    if client is None:
        return False
    try:
        return bool(client.exists(f"{KEY_LEASE}:{skey}"))
    except RedisError as e:
        log.warning(f"Redis is_suppressed check failed (non-fatal): {e}")
        return False
    finally:
        try:
            if client is not None:
                client.close()
        except Exception:                                   # noqa: BLE001
            pass


def record_event_diag(event_id: str, diag_out: str, rc: int) -> bool:
    """
    Record diagnostic output for an event so the correlator can include it
    in a grouped report. Truncated to keep Redis values small.
    Returns True on success, False on any failure (fail-safe).
    """
    client = _client()
    if client is None:
        return False
    try:
        payload = json.dumps({
            "diag_out": diag_out[:4000],   # truncate to avoid huge values
            "rc": rc,
        })
        client.set(f"{KEY_DIAG}:{event_id}", payload, ex=DIAG_TTL_SECONDS)
        return True
    except RedisError as e:
        log.warning(f"Redis record_event_diag failed (non-fatal): {e}")
        return False
    finally:
        try:
            if client is not None:
                client.close()
        except Exception:                                   # noqa: BLE001
            pass


def fetch_event_diag(event_id: str) -> Optional[Tuple[str, int]]:
    """
    Correlator-side: fetch diagnostic output for an event_id.
    Returns (diag_out, rc) tuple, or None if not present.
    """
    client = _client()
    if client is None:
        return None
    try:
        raw = client.get(f"{KEY_DIAG}:{event_id}")
        if raw is None:
            return None
        d = json.loads(raw)
        return d.get("diag_out", ""), int(d.get("rc", -1))
    except (RedisError, ValueError, TypeError) as e:
        log.warning(f"Redis fetch_event_diag failed (non-fatal): {e}")
        return None
    finally:
        try:
            if client is not None:
                client.close()
        except Exception:                                   # noqa: BLE001
            pass


def healthcheck() -> bool:
    """Quick Redis ping for diagnostics. Returns True if reachable."""
    client = _client()
    if client is None:
        return False
    try:
        return bool(client.ping())
    except RedisError:
        return False
    finally:
        try:
            if client is not None:
                client.close()
        except Exception:                                   # noqa: BLE001
            pass


if __name__ == "__main__":
    # Self-test entry point: prints derived source keys for a sample payload
    # and confirms Redis reachability. Useful for one-shot verification.
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    sample = {
        "id": "snmp-test-1",
        "nodeLabel": "router1",
        "varBinds": [
            ["1.3.6.1.2.1.1.3.0", "12345"],
            ["1.3.6.1.6.3.1.1.4.1.0", "1.3.6.1.6.3.1.1.5.3"],
            ["1.3.6.1.2.1.2.2.1.1.1", "7"],
            ["1.3.6.1.2.1.2.2.1.7.1", "2"],
        ],
    }
    print(f"sample source_key: {source_key(sample)}")
    print(f"sample ifIndex:    {extract_ifindex(sample['varBinds'])}")
    print(f"redis reachable:   {healthcheck()}")
    print(f"is_suppressed dummy-key: {is_suppressed('dummy::1')}")
