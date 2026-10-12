from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np


def summarize_feature_importance(model: Any, feature_names: List[str]) -> List[Tuple[str, float]]:
    """Summarize global feature importance from the trained model."""
    if hasattr(model, "coef_"):
        coefficients = model.coef_[0]
        scores = list(zip(feature_names, coefficients))
    elif hasattr(model, "feature_importances_"):
        scores = list(zip(feature_names, model.feature_importances_))
    else:
        scores = list(zip(feature_names, np.zeros(len(feature_names))))
    ranked = sorted(scores, key=lambda item: abs(item[1]), reverse=True)
    return [(name, float(value)) for name, value in ranked]


def explain_prediction(model: Any, feature_names: List[str], feature_row: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create a business-friendly explanation for a single prediction based on model feature weights."""
    importance = summarize_feature_importance(model, feature_names)
    explanation = []
    for name, score in importance[:5]:
        if name in feature_row:
            explanation.append({"feature": name, "contribution": float(score), "value": feature_row[name]})
    return explanation
