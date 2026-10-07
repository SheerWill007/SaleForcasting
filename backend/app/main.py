"""FastAPI backend for the Sales Forecasting dashboard.

Run from the `backend/` folder:
    uvicorn app.main:app --reload

For production (Render):
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Any, Optional

import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import analytics, config, ml
from .data import DatasetError, Filters
from .state import state

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    state.startup()
    yield


app = FastAPI(title="Sales Forecasting API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_filters(
    start: Optional[date] = None,
    end: Optional[date] = None,
    region: list[str] = Query(default_factory=list),
    category: list[str] = Query(default_factory=list),
    segment: list[str] = Query(default_factory=list),
) -> Filters:
    return Filters(start=start, end=end, regions=region, categories=category, segments=segment)


def _df() -> pd.DataFrame:
    if state.df is None:
        raise HTTPException(503, "Dataset not loaded yet")
    return state.df


def _round_records(df: pd.DataFrame, decimals: int = 2) -> list[dict[str, Any]]:
    out = df.copy()
    for col in out.select_dtypes(include="number").columns:
        out[col] = out[col].round(decimals)
    return out.replace({np.nan: None}).to_dict(orient="records")


def _series_mask(df: pd.DataFrame, product: str | None, region: str | None) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    if product:
        mask &= df["Product ID"] == product
    if region:
        mask &= df["Region"] == region
    return mask


# ------------------------------------------------------------------ dataset
@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model_loaded": state.bundle is not None}


@app.get("/api/dataset")
def dataset_info() -> dict[str, Any]:
    df = _df()
    return {
        **state.source,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "min_date": df["Order Date"].min().date().isoformat(),
        "max_date": df["Order Date"].max().date().isoformat(),
        "products": int(df["Product ID"].nunique()),
        "regions": int(df["Region"].nunique()),
        "preview": _round_records(
            df.head(8).assign(**{c: df[c].head(8).dt.strftime("%Y-%m-%d") for c in ["Order Date", "Ship Date"] if c in df})
        ),
    }


@app.post("/api/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    if len(content) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File too large (max {config.MAX_UPLOAD_MB} MB)")
    try:
        state.upload(content, file.filename or "upload.csv")
    except DatasetError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {"dataset": dataset_info(), "metrics": state.bundle["metrics"]}


@app.post("/api/dataset/reset")
def reset_dataset() -> dict[str, Any]:
    state.reset_to_sample()
    return {"dataset": dataset_info(), "metrics": state.bundle["metrics"]}


@app.get("/api/filters")
def filters() -> dict[str, Any]:
    return analytics.filter_options(_df())


# ------------------------------------------------------------------ analytics
@app.get("/api/overview")
def overview(f: Filters = Depends(get_filters)) -> dict[str, Any]:
    return analytics.overview(f.apply(_df()))


@app.get("/api/insights")
def insights(f: Filters = Depends(get_filters)) -> dict[str, Any]:
    return analytics.insights(f.apply(_df()))


# ------------------------------------------------------------------ model
@app.get("/api/model")
def model_info() -> dict[str, Any]:
    b = state.bundle
    return {
        "metrics": b["metrics"],
        "feature_importance": b["feature_importance"],
        "trained_at": b["trained_at"],
        "features": b["features"],
        "ensemble": {"ridge": ml.RIDGE_WEIGHT, "gbr": ml.GBR_WEIGHT},
    }


@app.get("/api/model/evaluation")
def model_evaluation(product: Optional[str] = None, region: Optional[str] = None) -> dict[str, Any]:
    ev = state.bundle["evaluation"]
    ev = ev[_series_mask(ev, product, region)]
    by_month = (
        ev.groupby("YearMonth")
        .agg(actual=("actual", "sum"), predicted=("predicted", "sum"), abs_error=("error", lambda e: e.abs().sum()))
        .reset_index()
    )
    by_month["error"] = by_month["actual"] - by_month["predicted"]
    hist_counts, edges = np.histogram(ev["error"], bins=12) if len(ev) else ([], [0])
    rows = ev.rename(columns={"Product Name": "product", "YearMonth": "month", "Region": "region"})
    return {
        "by_month": _round_records(by_month),
        "error_histogram": [
            {"bin": f"{edges[i]:.0f} to {edges[i + 1]:.0f}", "count": int(c)} for i, c in enumerate(hist_counts)
        ],
        "rows": _round_records(rows[["month", "product", "region", "actual", "predicted", "error"]].sort_values(["month", "product", "region"])),
    }


@app.post("/api/model/retrain")
def retrain() -> dict[str, Any]:
    state.retrain()
    return model_info()


# ------------------------------------------------------------------ forecasting
@app.get("/api/forecast")
def forecast(
    horizon: int = Query(6, ge=1, le=24),
    product: Optional[str] = None,
    region: Optional[str] = None,
    history_months: int = Query(24, ge=0, le=120),
) -> dict[str, Any]:
    fc = state.forecast(horizon)
    fc = fc[_series_mask(fc, product, region)]
    monthly = state.monthly[_series_mask(state.monthly, product, region)]

    hist = monthly.groupby("YearMonth").agg(actual=("Total_Quantity", "sum"), sales=("Total_Sales", "sum")).reset_index()
    hist["YearMonth"] = hist["YearMonth"].astype(str)
    if history_months:
        hist = hist.tail(history_months)

    agg = (
        fc.groupby("YearMonth")
        .agg(
            predicted=("predicted", "sum"),
            sigma=("sigma", lambda s: float(np.sqrt((s**2).sum()))),
            expected_sales=("expected_sales", "sum"),
        )
        .reset_index()
    )
    agg["lower"] = (agg["predicted"] - ml.INTERVAL_Z * agg["sigma"]).clip(lower=0)
    agg["upper"] = agg["predicted"] + ml.INTERVAL_Z * agg["sigma"]

    detail = fc.assign(
        lower=(fc["predicted"] - ml.INTERVAL_Z * fc["sigma"]).clip(lower=0),
        upper=fc["predicted"] + ml.INTERVAL_Z * fc["sigma"],
    ).rename(columns={"Product ID": "product_id", "Product Name": "product", "Region": "region", "Category": "category", "YearMonth": "month"})

    return {
        "history": _round_records(hist.rename(columns={"YearMonth": "month"})),
        "forecast": _round_records(agg.drop(columns="sigma").rename(columns={"YearMonth": "month"})),
        "detail": _round_records(detail[["month", "product_id", "product", "category", "region", "predicted", "lower", "upper", "expected_sales"]]),
        "totals": {
            "units": round(float(fc["predicted"].sum()), 1),
            "sales": round(float(fc["expected_sales"].sum()), 2),
            "last_year_units": round(float(hist["actual"].tail(horizon).sum()), 1) if len(hist) else 0.0,
            "last_year_sales": round(float(hist["sales"].tail(horizon).sum()), 2) if len(hist) else 0.0,
        },
    }


@app.get("/api/inventory")
def inventory(
    service_level: float = Query(0.95, ge=0.5, le=0.999),
    lead_time: Optional[float] = Query(None, ge=0, le=365, description="Override replenishment lead time (days)"),
    product: Optional[str] = None,
    region: Optional[str] = None,
) -> dict[str, Any]:
    fc = state.forecast(1)
    plan = ml.inventory_plan(fc, state.monthly, service_level, lead_time)
    plan = plan[_series_mask(plan, product, region)].sort_values("reorder_point", ascending=False)
    rows = plan.rename(columns={"Product ID": "product_id", "Product Name": "product", "Region": "region", "Category": "category", "YearMonth": "month"})
    return {
        "service_level": service_level,
        "z": round(float(ml.NormalDist().inv_cdf(service_level)), 3),
        "month": str(plan["YearMonth"].iloc[0]) if len(plan) else None,
        "rows": _round_records(
            rows[["product_id", "product", "category", "region", "predicted", "daily_demand", "lead_time", "sigma", "demand_cv", "safety_stock", "reorder_point"]],
            3,
        ),
    }


# ------------------------------------------------------------------ frontend
if config.FRONTEND_DIST.exists():
    # Serves the Next.js static export (frontend/out): /forecast -> forecast.html, etc.
    dist = config.FRONTEND_DIST.resolve()
    app.mount("/_next", StaticFiles(directory=dist / "_next"), name="next-assets")

    @app.api_route("/{path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(404)
        path = path.strip("/")
        candidates = [path, f"{path}.html", f"{path}/index.html"] if path else ["index.html"]
        # RSC prefetch payloads: ".../__next.insights.__PAGE__.txt" is exported as ".../__next.insights/__PAGE__.txt"
        head, _, name = path.rpartition("/")
        if name.startswith("__next.") and name.endswith(".txt"):
            nested = "__next." + name[len("__next.") : -len(".txt")].replace(".", "/") + ".txt"
            candidates.append(f"{head}/{nested}" if head else nested)
        for candidate in candidates:
            file = (dist / candidate).resolve()
            if file.is_file() and dist in file.parents:
                return FileResponse(file)
        not_found = dist / "404.html"
        return FileResponse(not_found if not_found.exists() else dist / "index.html", status_code=404)
