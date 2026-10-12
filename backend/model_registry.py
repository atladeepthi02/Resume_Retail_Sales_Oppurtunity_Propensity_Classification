from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import joblib


def get_model_dir() -> Path:
    path = Path("backend/models")
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_model_artifact(model: Any, transformer: Any, metrics: Dict[str, Any], model_name: str = "retail_propensity_model") -> str:
    artifact_dir = get_model_dir()
    version = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    artifact_path = artifact_dir / f"{model_name}_{version}.joblib"
    payload = {
        "model": model,
        "transformer": transformer,
        "metrics": metrics,
        "model_name": model_name,
        "version": version,
        "saved_at": datetime.utcnow().isoformat(),
    }
    joblib.dump(payload, artifact_path)
    return str(artifact_path)


def load_model_artifact(path: str) -> Dict[str, Any]:
    artifact = joblib.load(path)
    return artifact


def ensure_model_metadata() -> Dict[str, Any]:
    return {
        "model_name": "retail_propensity_model",
        "version": "v1",
        "status": "trained",
    }
