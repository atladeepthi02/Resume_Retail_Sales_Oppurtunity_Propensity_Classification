import pandas as pd

from backend.agents.workflow import run_agent_workflow
from backend.data_loader import generate_synthetic_data
from backend.preprocessing import preprocess_data
from backend.sales_recommendation import build_recommendation
from backend.train import train_model


def test_generate_synthetic_data_creates_valid_dataset():
    df = generate_synthetic_data(n_rows=250, random_state=42)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 250
    assert "converted" in df.columns
    assert "opportunity_id" in df.columns
    assert set(df["converted"].unique()).issubset({0, 1})


def test_preprocessing_produces_features_and_target():
    df = generate_synthetic_data(n_rows=300, random_state=7)
    X_train, X_test, y_train, y_test, transformed = preprocess_data(df, target_col="converted")
    assert len(X_train) > 0
    assert len(X_test) > 0
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)
    assert transformed is not None


def test_training_returns_model_and_metrics():
    df = generate_synthetic_data(n_rows=500, random_state=11)
    result = train_model(df, target_col="converted")
    assert "model" in result
    assert "metrics" in result
    assert result["metrics"]["accuracy"] >= 0
    assert result["metrics"]["f1_score"] >= 0


def test_agent_workflow_returns_structured_status():
    workflow = run_agent_workflow({"objective": "prioritize opportunities", "tenant_id": "tenant-1"})
    assert workflow["status"] == "completed"
    assert "selected_agents" in workflow
    assert "plan" in workflow


def test_recommendation_uses_probability_and_stage():
    recommendation = build_recommendation(0.8, "Proposal", "High engagement", 2500)
    assert "follow-up" in recommendation["action"].lower()
    assert recommendation["priority"] == "High"
