from __future__ import annotations

from typing import Dict, List


def build_workflow_summary(tasks: List[str]) -> Dict[str, object]:
    return {"status": "ready", "tasks": tasks}
