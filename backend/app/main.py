from __future__ import annotations

import io
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.agents.workflow import run_agent_workflow
from backend.app.models import (
    BatchPredictionRequest,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    RecommendationRequest,
    RecommendationResponse,
    WorkflowRequest,
    WorkflowResponse,
)
from backend.data_loader import generate_synthetic_data
from backend.database import init_db, insert_prediction
from backend.explainability import explain_prediction, summarize_feature_importance
from backend.model_registry import ensure_model_metadata, save_model_artifact
from backend.predict import predict_batch, predict_single
from backend.prompt_manager import get_prompt
from backend.sales_recommendation import build_recommendation
from backend.schema_mapper import map_schema
from backend.security import validate_guardrails
from backend.train import train_model
from backend.validation import validate_dataset

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("retail_sales_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.dataset = generate_synthetic_data(n_rows=1500, random_state=42)
    app.state.data_summary = validate_dataset(app.state.dataset)
    app.state.model_artifact = train_model(app.state.dataset, target_col="converted")
    app.state.model_metrics = app.state.model_artifact["metrics"]
    app.state.model_status = "trained"
    app.state.model_version = "v1"
    app.state.prediction_history: List[Dict[str, Any]] = []
    app.state.model_metadata = ensure_model_metadata()
    logger.info("Application startup complete: default synthetic dataset and model loaded.")
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def handle_global_exception(request, exc: Exception):
    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "The server encountered an unexpected error.",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, version="0.1.0")


@app.post("/api/data/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    payload = await file.read()
    frame = pd.read_csv(io.BytesIO(payload))
    summary = validate_dataset(frame)
    app.state.dataset = frame
    app.state.data_summary = summary
    return {
        "message": "Dataset uploaded successfully.",
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "summary": summary,
    }


@app.get("/api/data/summary")
async def get_data_summary():
    if not hasattr(app.state, "dataset"):
        app.state.dataset = generate_synthetic_data()
    return {"summary": validate_dataset(app.state.dataset)}


@app.post("/api/data/profile")
async def data_profile():
    dataset = getattr(app.state, "dataset", generate_synthetic_data())
    profile = validate_dataset(dataset)
    return {
        "schema_mapping": map_schema(list(dataset.columns)),
        "summary": profile,
    }


@app.post("/api/model/train")
async def train_model_endpoint():
    dataset = getattr(app.state, "dataset", None)
    if dataset is None or dataset.empty:
        dataset = generate_synthetic_data(n_rows=1500, random_state=42)
    model_artifact = train_model(dataset, target_col="converted")
    app.state.model_artifact = model_artifact
    app.state.model_metrics = model_artifact["metrics"]
    app.state.model_status = "trained"
    app.state.model_version = "v1"
    save_model_artifact(model_artifact["model"], model_artifact["transformer"], model_artifact["metrics"])
    return {
        "status": "trained",
        "model_version": app.state.model_version,
        "metrics": model_artifact["metrics"],
    }


@app.get("/api/model/metrics")
async def model_metrics():
    if not hasattr(app.state, "model_metrics"):
        raise HTTPException(status_code=400, detail="No model metrics are available yet.")
    return app.state.model_metrics


@app.get("/api/model/status")
async def model_status():
    return {
        "status": getattr(app.state, "model_status", "not_trained"),
        "model_version": getattr(app.state, "model_version", "v1"),
    }


@app.post("/api/predict")
async def predict(payload: PredictionRequest):
    if not hasattr(app.state, "model_artifact"):
        raise HTTPException(status_code=400, detail="Model has not been trained yet.")

    feature_row = payload.model_dump(exclude_none=True)
    custom = feature_row.pop("custom_features", {})
    if custom:
        feature_row.update(custom)

    default_values = {
        "opportunity_id": "OPP-DEFAULT",
        "customer_id": "CUST-DEFAULT",
        "customer_segment": "SMB",
        "region": "North",
        "product_category": "Electronics",
        "product_interest": "Medium",
        "previous_purchases": 1,
        "purchase_frequency": 2.0,
        "avg_order_value": 200.0,
        "sales_channel": "Online",
        "lead_source": "Website",
        "sales_rep": "REP-01",
        "interactions": 3,
        "days_since_last_interaction": 30,
        "discount_offered": 0.0,
        "opportunity_age": 45,
        "historical_sales_value": 500.0,
        "previous_conversion_history": 0,
        "opportunity_stage": "Qualified",
        "follow_up_status": "Warm",
    }
    for key, value in default_values.items():
        feature_row.setdefault(key, value)

    model = app.state.model_artifact["model"]
    transformer = app.state.model_artifact["transformer"]
    predicted_class, probability = predict_single(model, feature_row, transformer)
    priority = "High" if probability >= 0.7 else "Medium" if probability >= 0.4 else "Low"

    response = PredictionResponse(
        opportunity_id=str(feature_row.get("opportunity_id", "OPP-DEFAULT")),
        predicted_class=int(predicted_class),
        predicted_label="Likely to convert" if predicted_class == 1 else "Unlikely to convert",
        conversion_probability=float(probability),
        priority=priority,
        model_version=str(app.state.model_version),
    )
    app.state.prediction_history.append(response.model_dump())
    insert_prediction(response.model_dump())
    return response


@app.post("/api/predict/batch")
async def predict_batch_endpoint(payload: BatchPredictionRequest):
    if not hasattr(app.state, "model_artifact"):
        raise HTTPException(status_code=400, detail="Model has not been trained yet.")

    rows = []
    for record in payload.opportunities:
        feature_row = record.model_dump(exclude_none=True)
        custom = feature_row.pop("custom_features", {})
        if custom:
            feature_row.update(custom)
        rows.append(feature_row)

    model = app.state.model_artifact["model"]
    transformer = app.state.model_artifact["transformer"]
    predictions = predict_batch(model, rows, transformer)
    return {"predictions": predictions, "count": len(predictions)}


@app.get("/api/opportunities")
async def list_opportunities():
    dataset = getattr(app.state, "dataset", generate_synthetic_data())
    sample = dataset.head(25).to_dict(orient="records")
    return {"items": sample, "total": len(sample)}


@app.get("/api/opportunities/{opportunity_id}")
async def get_opportunity(opportunity_id: str):
    dataset = getattr(app.state, "dataset", generate_synthetic_data())
    row = dataset[dataset["opportunity_id"] == opportunity_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    return row.iloc[0].to_dict()


@app.get("/api/opportunities/{opportunity_id}/explanation")
async def get_explanation(opportunity_id: str):
    dataset = getattr(app.state, "dataset", generate_synthetic_data())
    row = dataset[dataset["opportunity_id"] == opportunity_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    model = app.state.model_artifact["model"]
    feature_names = [col for col in dataset.columns if col not in {"converted", "opportunity_id"}]
    summary = explain_prediction(model, feature_names, row.iloc[0].to_dict())
    return {"opportunity_id": opportunity_id, "explanation": summary}


@app.get("/api/opportunities/prioritized")
async def prioritized_opportunities():
    dataset = getattr(app.state, "dataset", generate_synthetic_data())
    model = app.state.model_artifact["model"]
    transformer = app.state.model_artifact["transformer"]
    ranked = []
    for _, row in dataset.head(25).iterrows():
        feature_row = row.drop(labels=["converted"], errors="ignore").to_dict()
        predicted_class, probability = predict_single(model, feature_row, transformer)
        ranked.append(
            {
                "opportunity_id": row.get("opportunity_id", "UNKNOWN"),
                "customer_id": row.get("customer_id", "UNKNOWN"),
                "probability": float(probability),
                "priority": "High" if probability >= 0.7 else "Medium" if probability >= 0.4 else "Low",
                "predicted_class": int(predicted_class),
            }
        )
    ranked.sort(key=lambda item: item["probability"], reverse=True)
    return {"items": ranked}


@app.get("/api/reports/sales")
async def sales_report():
    dataset = getattr(app.state, "dataset", generate_synthetic_data())
    total = len(dataset)
    converted = int(dataset["converted"].sum())
    conversion_rate = float(converted / total) if total else 0.0
    by_segment = dataset.groupby("customer_segment")["converted"].mean().to_dict()
    by_category = dataset.groupby("product_category")["converted"].mean().to_dict()
    return {
        "total_opportunities": total,
        "converted_opportunities": converted,
        "conversion_rate": conversion_rate,
        "conversion_by_segment": by_segment,
        "conversion_by_category": by_category,
    }


@app.post("/api/recommendations")
async def generate_sales_recommendation(payload: RecommendationRequest):
    recommendation = build_recommendation(
        probability=payload.probability,
        opportunity_stage=payload.opportunity_stage,
        engagement_signal=payload.engagement_signal,
        deal_value=payload.deal_value,
    )
    return RecommendationResponse(**recommendation)


@app.post("/api/agent/workflow")
async def agent_workflow(payload: WorkflowRequest):
    guardrails = validate_guardrails(payload.model_dump())
    if not guardrails["safe"]:
        raise HTTPException(status_code=400, detail={"guardrails": guardrails})

    workflow = run_agent_workflow({"objective": payload.objective, "tenant_id": payload.tenant_id})
    workflow_prompt = get_prompt("supervisor")
    workflow["prompt_version"] = workflow_prompt["version"]
    return WorkflowResponse(**workflow)


@app.get("/api/prompts")
async def list_prompts():
    return {"prompts": {name: data["version"] for name, data in get_prompt.__globals__["PROMPTS"].items()}}


@app.get("/")
async def root():
    return {"message": "Retail Sales Opportunity Propensity API is running."}
