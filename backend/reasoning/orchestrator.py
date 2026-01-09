"""Reasoning orchestration with caching to ensure determinism and efficiency."""

from hashlib import sha256
from typing import Any, Dict, Tuple

from reasoning.client import AzureReasoningClient

_reasoning_client = AzureReasoningClient()
_reasoning_cache: Dict[str, Dict[str, str]] = {}


def _cache_key(snapshot: Dict[str, Any]) -> str:
    # Use stable fields to key the cache; avoid huge payloads
    key_parts = [
        str(snapshot.get("startup_id", "")),
        f"{snapshot.get('risk_score', 0):.2f}",
        str(snapshot.get("severity", "")),
        str(snapshot.get("trend", "")),
        str(snapshot.get("trend_delta", 0)),
    ]
    drivers = snapshot.get("risk_drivers", []) or []
    driver_str = ";".join([f"{d.get('label','')}|{d.get('detail','')}" for d in drivers])
    key_parts.append(driver_str)
    raw = "|".join(key_parts)
    return sha256(raw.encode("utf-8")).hexdigest()


def get_investor_reasoning(snapshot: Dict[str, Any]) -> Dict[str, str]:
    """Return investor reasoning for a given snapshot, cached for determinism."""
    key = _cache_key(snapshot)
    if key in _reasoning_cache:
        return _reasoning_cache[key]

    reasoning = _reasoning_client.generate_reasoning(snapshot)
    _reasoning_cache[key] = reasoning
    return reasoning
