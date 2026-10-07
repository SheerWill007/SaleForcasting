from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent

DATA_DIR = Path(os.getenv("SF_DATA_DIR", BACKEND_DIR / "data"))
MODEL_DIR = Path(os.getenv("SF_MODEL_DIR", BACKEND_DIR / "models"))
FRONTEND_DIST = Path(os.getenv("SF_FRONTEND_DIST", ROOT_DIR / "frontend" / "out"))

SAMPLE_DATASET = DATA_DIR / "superstore_dataset.csv"
UPLOAD_DIR = DATA_DIR / "uploads"
MODEL_PATH = MODEL_DIR / "model.joblib"

MAX_UPLOAD_MB = 25
CORS_ORIGINS = [o.strip() for o in os.getenv("SF_CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

# Port for production deployment (Render sets this automatically)
PORT = int(os.getenv("PORT", "8000"))
