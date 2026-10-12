from __future__ import annotations

from typing import Dict, Optional


def build_recommendation(probability: float, opportunity_stage: str, engagement_signal: str, deal_value: Optional[float] = None) -> Dict[str, object]:
    """Create deterministic recommendation outputs based on available probability and evidence."""
    probability = float(probability)
    priority = "High" if probability >= 0.7 else "Medium" if probability >= 0.4 else "Low"

    if probability >= 0.7:
        action = "Schedule a follow-up call and confirm product interest before the next sales touchpoint."
        rationale = "High propensity and active engagement support immediate follow-up."
    elif probability >= 0.4:
        action = "Review customer engagement details and prepare a targeted offer or tailored product pitch."
        rationale = "The opportunity is promising but requires stronger qualification evidence."
    else:
        action = "Pause expensive outreach and re-engage only after additional customer activity or product-fit validation."
        rationale = "The current evidence suggests a low likelihood of conversion without more supporting signals."

    if deal_value is not None and deal_value >= 10000:
        action = "Prioritize the opportunity for executive attention and a high-touch sales plan."

    if opportunity_stage.lower() in {"proposal", "negotiation"}:
        action = "Move quickly with a tailored proposal review and a follow-up close-plan checkpoint."

    return {
        "priority": priority,
        "action": action,
        "rationale": rationale,
        "engagement_signal": engagement_signal,
        "stage": opportunity_stage,
        "deal_value": deal_value,
    }
