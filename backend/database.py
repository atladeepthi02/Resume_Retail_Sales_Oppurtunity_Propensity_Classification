from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


DB_PATH = Path("backend/data/retail_sales.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sales_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT UNIQUE,
            customer_id TEXT,
            product_category TEXT,
            product_interest TEXT,
            opportunity_stage TEXT,
            converted INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT,
            predicted_class INTEGER,
            predicted_label TEXT,
            conversion_probability REAL,
            priority TEXT,
            model_version TEXT,
            prediction_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS model_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT,
            version TEXT,
            metrics TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def insert_prediction(record: Dict[str, Any]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO predictions (opportunity_id, predicted_class, predicted_label, conversion_probability, priority, model_version)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            record.get("opportunity_id"),
            record.get("predicted_class"),
            record.get("predicted_label"),
            record.get("conversion_probability"),
            record.get("priority"),
            record.get("model_version"),
        ),
    )
    conn.commit()
    conn.close()


def fetch_predictions() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT opportunity_id, predicted_class, predicted_label, conversion_probability, priority, model_version, prediction_timestamp FROM predictions ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [
        {
            "opportunity_id": row[0],
            "predicted_class": row[1],
            "predicted_label": row[2],
            "conversion_probability": row[3],
            "priority": row[4],
            "model_version": row[5],
            "prediction_timestamp": row[6],
        }
        for row in rows
    ]
