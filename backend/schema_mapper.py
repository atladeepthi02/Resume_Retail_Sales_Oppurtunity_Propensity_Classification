from __future__ import annotations

from typing import Dict, List


CANONICAL_FEATURES: List[str] = [
    "opportunity_id",
    "customer_id",
    "customer_segment",
    "region",
    "product_category",
    "product_interest",
    "previous_purchases",
    "purchase_frequency",
    "avg_order_value",
    "sales_channel",
    "lead_source",
    "sales_rep",
    "interactions",
    "days_since_last_interaction",
    "discount_offered",
    "opportunity_age",
    "historical_sales_value",
    "previous_conversion_history",
    "opportunity_stage",
    "follow_up_status",
]


def map_schema(raw_columns: List[str]) -> Dict[str, str]:
    """Map raw columns to a canonical retail sales schema using fuzzy name matching."""
    mapping: Dict[str, str] = {}
    normalized = {col.lower().replace(" ", "_"): col for col in raw_columns}
    for canonical in CANONICAL_FEATURES:
        for key, original in normalized.items():
            if key == canonical or canonical in key:
                mapping[canonical] = original
                break
    return mapping
