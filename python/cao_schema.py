from fastavro import parse_schema, validate
import time

CAO_SCHEMA = parse_schema({
    "type": "record",
    "name": "CanonicalAlertObject",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "severity", "type": {"type": "enum", "name": "Severity",
            "symbols": ["CRITICAL", "MAJOR", "MINOR", "WARNING", "NORMAL"]}},
        {"name": "source", "type": "string"},
        {"name": "nodeLabel", "type": "string"},
        {"name": "timestamp", "type": "long"},
        {"name": "uei", "type": ["null", "string"], "default": None},
        {"name": "description", "type": ["null", "string"], "default": None}
    ]
})

def normalise(raw: dict) -> dict:
    cao = {
        "id": str(raw.get("id", "unknown")),
        "severity": raw.get("severity", "WARNING"),
        "source": raw.get("source", "webhook"),
        "nodeLabel": raw.get("nodeLabel", "unknown"),
        "timestamp": int(time.time() * 1000),
        "uei": raw.get("uei", None),
        "description": raw.get("description", None)
    }
    validate(cao, CAO_SCHEMA)
    return cao

# Author: Jose Batalha De Vasconcelos - COM617 Group 15
