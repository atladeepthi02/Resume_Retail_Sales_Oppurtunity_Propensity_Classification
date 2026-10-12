from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd


def predict_single(model: Any, feature_row: Dict[str, Any], transformer: Any) -> Tuple[int, float]:
    """Return the class label and probability for a single feature vector."""
    row_df = pd.DataFrame([feature_row])
    transformed = transformer.transform(row_df)
    probabilities = model.predict_proba(transformed)[0]
    predicted_class = int(model.predict(transformed)[0])
    probability = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])
    return predicted_class, probability


def predict_batch(model: Any, rows: List[Dict[str, Any]], transformer: Any) -> List[Dict[str, Any]]:
    """Return predictions for a list of row dictionaries."""
    results = []
    for row in rows:
        pred_class, probability = predict_single(model, row, transformer)
        results.append(
            {
                "predicted_class": pred_class,
                "predicted_label": "Likely to convert" if pred_class == 1 else "Unlikely to convert",
                "conversion_probability": probability,
            }
        )
    return results
