from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    opportunity_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_segment: Optional[str] = None
    region: Optional[str] = None
    product_category: Optional[str] = None
    product_interest: Optional[str] = None
    previous_purchases: Optional[int] = None
    purchase_frequency: Optional[float] = None
    avg_order_value: Optional[float] = None
    sales_channel: Optional[str] = None
    lead_source: Optional[str] = None
    sales_rep: Optional[str] = None
    interactions: Optional[int] = None
    days_since_last_interaction: Optional[int] = None
    discount_offered: Optional[float] = None
    opportunity_age: Optional[int] = None
    historical_sales_value: Optional[float] = None
    previous_conversion_history: Optional[int] = None
    opportunity_stage: Optional[str] = None
    follow_up_status: Optional[str] = None
    custom_features: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PredictionResponse(BaseModel):
    opportunity_id: str
    predicted_class: int
    predicted_label: str
    conversion_probability: float
    priority: str
    model_version: str


class BatchPredictionRequest(BaseModel):
    opportunities: List[PredictionRequest]


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str


class RecommendationRequest(BaseModel):
    probability: float
    opportunity_stage: str = "Qualified"
    engagement_signal: str = "Moderate"
    deal_value: Optional[float] = None


class RecommendationResponse(BaseModel):
    priority: str
    action: str
    rationale: str
    engagement_signal: str
    stage: str
    deal_value: Optional[float]


class WorkflowRequest(BaseModel):
    objective: str = "prioritize opportunities"
    tenant_id: str = "default"


class WorkflowResponse(BaseModel):
    status: str
    tenant_id: str
    objective: str
    selected_agents: List[str]
    workflow_version: str
    warnings: List[str]
