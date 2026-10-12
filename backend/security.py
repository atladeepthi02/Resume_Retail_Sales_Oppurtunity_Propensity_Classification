from __future__ import annotations

from typing import Any, Dict


def validate_guardrails(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run a minimal guardrail check on request content before it reaches model inference."""
    result = {"safe": True, "issues": []}

    for key, value in payload.items():
        if isinstance(value, str) and "<script" in value.lower():
            result["safe"] = False
            result["issues"].append(f"Unsafe input detected in field '{key}'.")
        if isinstance(value, (int, float)) and not (value == value and value < 1e9):
            result["safe"] = False
            result["issues"].append(f"Out-of-range numeric value detected in field '{key}'.")

    return result
