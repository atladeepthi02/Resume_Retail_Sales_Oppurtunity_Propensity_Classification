from __future__ import annotations

from typing import Dict


def prepare_prediction_context(payload: Dict[str, object]) -> Dict[str, object]:
    return {"status": "ready", "payload": payload}
