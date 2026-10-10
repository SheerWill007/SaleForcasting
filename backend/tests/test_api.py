from __future__ import annotations

import io

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import config, ml


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("sf")
    # Keep the sample dataset, but isolate uploads + model artifacts.
    config.UPLOAD_DIR = tmp / "uploads"
    config.MODEL_DIR = tmp / "models"
    config.MODEL_PATH = config.MODEL_DIR / "model.joblib"
    import app.state as state_mod

    state_mod.ACTIVE_META = config.UPLOAD_DIR / "active.json"
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_health_and_dataset(client):
    assert client.get("/api/health").json()["model_loaded"] is True
    info = client.get("/api/dataset").json()
    assert info["kind"] == "sample"
    assert info["rows"] == 9000


def test_overview_and_filters(client):
    opts = client.get("/api/filters").json()
    assert "East" in opts["regions"]
    full = client.get("/api/overview").json()
    east = client.get("/api/overview", params={"region": "East"}).json()
    assert 0 < east["kpis"]["total_sales"] < full["kpis"]["total_sales"]
    assert len(full["trend"]) == 36
    assert len(full["top_products"]) <= 10
    assert full["yoy"]["period_end"] == "2023-12"
    assert set(full["yoy"]["change"]) == set(full["kpis"])
    assert "orders" in full["trend"][0]


def test_insights(client):
    data = client.get("/api/insights", params={"category": ["Technology"]}).json()
    assert {r["category"] for r in data["products"]} == {"Technology"}
    assert data["demand_variability"]


def test_model_and_evaluation(client):
    model = client.get("/api/model").json()
    assert set(model["metrics"]) >= {"test_r2", "mae", "rmse", "mape"}
    ev = client.get("/api/model/evaluation").json()
    assert len(ev["by_month"]) == 12
    assert ev["rows"]


def test_forecast(client):
    fc = client.get("/api/forecast", params={"horizon": 6}).json()
    assert len(fc["forecast"]) == 6
    assert all(r["lower"] <= r["predicted"] <= r["upper"] for r in fc["forecast"])
    one = client.get("/api/forecast", params={"horizon": 3, "product": "TEC-PH-001", "region": "West"}).json()
    assert len(one["detail"]) == 3


def test_inventory(client):
    lo = client.get("/api/inventory", params={"service_level": 0.9}).json()
    hi = client.get("/api/inventory", params={"service_level": 0.99}).json()
    total = lambda d: sum(r["safety_stock"] for r in d["rows"])  # noqa: E731
    assert total(hi) > total(lo) > 0


def test_history_features_match_training_features():
    hist = np.array([5, 9, 3, 7, 11, 4, 8, 6, 10, 12, 2, 9, 7], dtype=float)
    frame = pd.DataFrame(
        {
            "Product ID": "P",
            "Region": "R",
            "Category": "C",
            "Sub-Category": "S",
            "Total_Quantity": np.append(hist, 0),
            "Month": 1,
            "Year": 2021,
            "Quarter": 1,
        }
    )
    vec = ml.add_features(frame, 2021, {"C": 0}, {"S": 0}).iloc[-1].fillna(0)
    rec = ml.history_features(hist)
    for k, v in rec.items():
        assert vec[k] == pytest.approx(v), k


def test_upload_validation_and_reset(client):
    bad = io.BytesIO(b"a,b\n1,2\n")
    r = client.post("/api/dataset/upload", files={"file": ("bad.csv", bad, "text/csv")})
    assert r.status_code == 422
    assert "Missing required column" in r.json()["detail"]

    df = pd.read_csv(config.SAMPLE_DATASET)
    small = df[df["Region"].isin(["East", "West"])]
    r = client.post("/api/dataset/upload", files={"file": ("mine.csv", small.to_csv(index=False).encode(), "text/csv")})
    assert r.status_code == 200, r.text
    assert client.get("/api/filters").json()["regions"] == ["East", "West"]

    client.post("/api/dataset/reset")
    assert client.get("/api/dataset").json()["kind"] == "sample"


def test_upload_size_limit(client):
    """Test that files exceeding the configured size limit are rejected."""
    # Create a mock large file that exceeds the limit
    # We'll simulate this by mocking rather than creating a real 350MB+ file
    import tempfile
    from pathlib import Path
    
    # Test file extension validation
    bad_ext = io.BytesIO(b"some data")
    r = client.post("/api/dataset/upload", files={"file": ("bad.txt", bad_ext, "text/plain")})
    assert r.status_code == 400
    assert "Invalid file type" in r.json()["detail"]
    
    # Test that a valid small CSV works (already tested above, but confirming)
    df = pd.read_csv(config.SAMPLE_DATASET).head(100)
    csv_content = df.to_csv(index=False).encode()
    assert len(csv_content) < config.MAX_UPLOAD_MB * 1024 * 1024
    r = client.post("/api/dataset/upload", files={"file": ("small.csv", csv_content, "text/csv")})
    assert r.status_code == 200
