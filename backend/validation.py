from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def validate_dataset(df: pd.DataFrame, target_col: str = "converted") -> Dict[str, Any]:
    """Run validation checks and return a summary report for a dataset."""
    if df is None or df.empty:
        raise ValueError("Dataset is empty or missing.")

    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in the dataset.")

    missing_values = df.isna().sum().to_dict()
    duplicate_count = int(df.duplicated().sum())
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)
    categorical_cols = [col for col in df.columns if col not in numeric_cols]

    outcome_counts = df[target_col].value_counts(dropna=False).to_dict()
    report = {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_count,
        "target_distribution": outcome_counts,
        "class_balance": float(df[target_col].mean()) if df[target_col].notna().any() else 0.0,
        "column_count": int(df.shape[1]),
    }

    return report


def check_target_leakage(df: pd.DataFrame, target_col: str = "converted") -> List[str]:
    """Check for obvious leakage patterns from highly correlated identifiers to the target."""
    warnings: List[str] = []
    for col in df.columns:
        if col == target_col:
            continue
        if df[col].nunique(dropna=True) == len(df) and df[col].dtype.kind in "OU" and df[target_col].dtype.kind in "biufc":
            corr = df[col].astype(str).str.len().corr(df[target_col])
            if pd.notna(corr) and abs(corr) > 0.9:
                warnings.append(f"Potential target leakage signal detected in column '{col}'.")
    return warnings
