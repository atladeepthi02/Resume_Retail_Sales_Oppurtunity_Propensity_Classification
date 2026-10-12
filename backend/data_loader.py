from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


def _sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))


def generate_synthetic_data(n_rows: int = 2000, random_state: int = 42) -> pd.DataFrame:
    """Generate a synthetic retail sales opportunity dataset with a realistic conversion signal."""
    rng = np.random.default_rng(random_state)

    segments = ["SMB", "Retail", "Enterprise", "VIP"]
    regions = ["North", "South", "East", "West", "Central"]
    categories = ["Electronics", "Home", "Apparel", "Beauty", "Sports"]
    channels = ["Online", "In-store", "Partner", "Call Center"]
    lead_sources = ["Website", "Referral", "Trade Show", "Campaign", "Partner"]
    stages = ["Prospecting", "Qualified", "Proposal", "Negotiation", "Closed"]
    follow_up_status = ["Hot", "Warm", "Cold", "Needs Review"]

    records = []
    for idx in range(n_rows):
        segment = rng.choice(segments)
        region = rng.choice(regions)
        category = rng.choice(categories)
        sales_channel = rng.choice(channels)
        lead_source = rng.choice(lead_sources)
        stage = rng.choice(stages)
        status = rng.choice(follow_up_status)

        previous_purchases = int(rng.integers(0, 10))
        purchase_frequency = float(rng.integers(1, 12)) / 10
        avg_order_value = float(rng.uniform(25, 800))
        interactions = int(rng.integers(1, 20))
        days_since_last_interaction = int(rng.integers(1, 180))
        discount_offered = float(rng.uniform(0, 0.4))
        opportunity_age = int(rng.integers(7, 180))
        historical_sales_value = float(previous_purchases * avg_order_value * rng.uniform(0.5, 1.8))
        previous_conversion_history = int(rng.integers(0, 3))
        product_interest = rng.choice(["Low", "Medium", "High", "Very High"])
        customer_id = f"CUST-{idx + 1:05d}"

        engagement_score = (
            (1 if segment == "VIP" else 0.6 if segment == "Enterprise" else 0.4 if segment == "Retail" else 0.2)
            + (0.35 if product_interest in {"High", "Very High"} else 0.15 if product_interest == "Medium" else -0.1)
            + min(interactions, 12) * 0.05
            + (0.4 if sales_channel == "Online" else 0.25 if sales_channel == "In-store" else 0.1)
            - (days_since_last_interaction / 180) * 0.8
            + (previous_purchases * 0.08)
            + (previous_conversion_history * 0.25)
        )

        base_score = (
            engagement_score
            + (0.8 if stage in {"Proposal", "Negotiation"} else 0.3 if stage == "Qualified" else -0.2)
            + (0.3 if lead_source in {"Referral", "Website"} else 0.1)
            + (0.2 if status == "Hot" else 0.05 if status == "Warm" else -0.15)
            - (discount_offered * 1.3)
            + (np.log1p(avg_order_value) - 5) * 0.15
            - (opportunity_age / 180) * 0.5
        )

        probability = _sigmoid(base_score)
        converted = int(rng.random() < probability)

        # Add a few missing-value holes to emulate real datasets
        if rng.random() < 0.05:
            product_interest = np.nan
        if rng.random() < 0.04:
            sales_channel = np.nan
        if rng.random() < 0.03:
            discount_offered = np.nan

        records.append(
            {
                "opportunity_id": f"OPP-{idx + 1:05d}",
                "customer_id": customer_id,
                "customer_segment": segment,
                "region": region,
                "product_category": category,
                "product_interest": product_interest,
                "previous_purchases": previous_purchases,
                "purchase_frequency": purchase_frequency,
                "avg_order_value": avg_order_value,
                "sales_channel": sales_channel,
                "lead_source": lead_source,
                "sales_rep": f"REP-{rng.integers(1, 21):02d}",
                "interactions": interactions,
                "days_since_last_interaction": days_since_last_interaction,
                "discount_offered": discount_offered,
                "opportunity_age": opportunity_age,
                "historical_sales_value": historical_sales_value,
                "previous_conversion_history": previous_conversion_history,
                "opportunity_stage": stage,
                "follow_up_status": status,
                "converted": converted,
            }
        )

    df = pd.DataFrame(records)
    return df


def load_dataset(csv_path: Optional[str] = None, n_rows: int = 2000, random_state: int = 42) -> pd.DataFrame:
    """Load a CSV if provided; otherwise generate synthetic data."""
    if csv_path:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {csv_path}")
        return pd.read_csv(path)
    return generate_synthetic_data(n_rows=n_rows, random_state=random_state)


def save_synthetic_dataset(output_path: str = "backend/data/synthetic/retail_sales_opportunities.csv", n_rows: int = 2000, random_state: int = 42) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_data(n_rows=n_rows, random_state=random_state)
    df.to_csv(path, index=False)
    return str(path)
