from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from sklearn.linear_model import LogisticRegression

from backend.evaluate import evaluate_model
from backend.preprocessing import preprocess_data


def train_model(df: pd.DataFrame, target_col: str = "converted") -> Dict[str, Any]:
    """Train and evaluate a baseline sales conversion propensity classifier."""
    X_train, X_test, y_train, y_test, transformer = preprocess_data(df, target_col=target_col)

    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    model.fit(X_train, y_train)

    metrics = evaluate_model(model, X_test, y_test)

    result = {
        "model": model,
        "transformer": transformer,
        "metrics": metrics,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "model_name": "logistic_regression",
    }
    return result
