# SalesCast

SalesCast is a full-stack sales forecasting and analytics platform. A FastAPI backend ingests transactional sales data, trains and serves a forecasting model, and exposes analytics through a documented REST API. A Next.js frontend presents the results as an interactive dashboard. The system can be run as two separate development servers, or packaged as a single deployable unit in which FastAPI serves the statically exported frontend.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Key Features](#2-key-features)
3. [Architecture](#3-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Prerequisites](#5-prerequisites)
6. [Quick Start](#6-quick-start)
7. [Deployment Modes](#7-deployment-modes)
8. [Configuration](#8-configuration)
9. [API Reference](#9-api-reference)
10. [Forecasting Model](#10-forecasting-model)
11. [Data Requirements](#11-data-requirements)
12. [Testing](#12-testing)
13. [Project Structure](#13-project-structure)
14. [Version Control Guidance](#14-version-control-guidance)
15. [Troubleshooting](#15-troubleshooting)
16. [Reference Materials](#16-reference-materials)
17. [Authors and Team](#17-authors-and-team)

---

## 1. Overview

SalesCast turns historical sales records into actionable insight. It answers three questions:

- What has happened? Aggregated analytics over the loaded dataset.
- What is likely to happen? Forward-looking sales forecasts produced by a trained model.
- How reliable is the forecast? A transparent evaluation view that compares predicted and actual values month by month.

The application ships with a generated sample dataset in the style of the well-known Superstore retail dataset, so it is fully functional immediately after installation, without any external data source. Users may also upload their own data, provided it conforms to the schema described in [Data Requirements](#11-data-requirements).

## 2. Key Features

- **Interactive dashboard.** Multiple dashboard pages built with Recharts, with light and dark themes and smooth scrolling.
- **Forecasting.** A persisted machine learning model that is trained automatically on first start and reloaded on subsequent starts.
- **Model evaluation.** A dedicated evaluation view that reports model quality, including month-by-month comparison of actual and predicted values.
- **Data upload.** Users can supply their own dataset; uploads are stored separately from the bundled sample data.
- **Self-bootstrapping data.** If the sample dataset is absent, the backend generates it on demand using the bundled generator script.
- **Self-documenting API.** Interactive Swagger documentation and an OpenAPI schema are served by the backend.
- **Two run modes.** A hot-reloading development setup, and a single-process production setup in which one server delivers both the API and the user interface.
- **Containerised deployment.** A multi-stage Dockerfile and a Compose definition with persistent volumes.
- **Automated tests.** A pytest suite covering the API.

## 3. Architecture

SalesCast is organised as two cooperating applications.

```
+---------------------+        HTTP / JSON         +-------------------------+
|  Next.js frontend   |  <---------------------->  |  FastAPI backend        |
|  (TypeScript,       |        /api/*              |  (Python)               |
|   Recharts)         |                            |                         |
+---------------------+                            |  analytics  ml  data    |
                                                   |        state            |
                                                   +-----------+-------------+
                                                               |
                                              +----------------+---------------+
                                              |                                |
                                    backend/data/ (CSV, uploads)     backend/models/ (joblib)
```

**Backend.** The FastAPI application is organised into focused modules: configuration (`config`), data loading and validation (`data`), analytics computation (`analytics`), model training and inference (`ml`), and shared application state (`state`). On startup, the application state resolves the dataset (generating the sample data if needed), then loads the persisted model or trains a new one.

**Frontend.** The Next.js application uses the App Router. All backend access is centralised in a single typed client (`src/lib/api.ts`), and the API response shapes are mirrored as TypeScript interfaces.

**Development versus production.** The behaviour of the frontend differs by mode, as defined in `next.config.ts`:

| Mode | Frontend behaviour |
|---|---|
| Development | The Next.js dev server proxies `/api/*`, `/docs` and `/openapi.json` to the FastAPI backend, which avoids cross-origin configuration during development. |
| Production | The frontend is built as a static export (`output: "export"`) into `frontend/out/`, which FastAPI serves directly. No Node.js runtime is required in production. |

## 4. Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn, pandas, NumPy, joblib |
| Frontend | Next.js (App Router), React, TypeScript, Recharts, next-themes, Lenis |
| Testing | pytest |
| Packaging | Docker (multi-stage build), Docker Compose |

## 5. Prerequisites

For local development:

- Python 3.12 or later
- Node.js 22 or later, with npm
- Git

For containerised deployment:

- Docker, and optionally Docker Compose

## 6. Quick Start

### 6.1 Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 6.2 Start the backend

```bash
cd backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On first start, the backend will:

1. Generate the sample dataset if it is not already present.
2. Train the forecasting model and persist it to the model directory.

This initial step takes a few seconds. Subsequent starts reuse the persisted model and are considerably faster.

The backend is now available at `http://127.0.0.1:8000`, with interactive API documentation at `http://127.0.0.1:8000/docs`.

### 6.3 Start the frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

The dashboard is now available at `http://localhost:3000`. Requests to `/api/*` are proxied to the backend automatically.

## 7. Deployment Modes

### 7.1 Single-server mode (static export)

In this mode, FastAPI serves both the API and the compiled user interface from one process on one port.

```bash
# 1. Build the static frontend into frontend/out/
cd frontend
npm ci
npm run build

# 2. Start the backend, pointing it at the build output
cd ../backend
export SF_FRONTEND_DIST=../frontend/out        # Windows PowerShell: $env:SF_FRONTEND_DIST = "../frontend/out"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The complete application is then available at `http://localhost:8000`.

### 7.2 Docker

The provided Dockerfile is a multi-stage build. The first stage uses a Node.js image to produce the static frontend; the final stage uses a slim Python image that contains only the backend and the built frontend. Node.js is not present in the final image.

```bash
docker build -t salescast .
docker run --rm -p 8000:8000 salescast
```

### 7.3 Docker Compose

```bash
docker compose up --build
```

The Compose definition publishes port 8000 and mounts two named volumes so that state survives container restarts:

| Volume | Container path | Purpose |
|---|---|---|
| `sf-data` | `/app/backend/data/uploads` | Datasets uploaded by users |
| `sf-models` | `/app/backend/models` | The trained, persisted model |

To remove the containers while retaining the volumes, run `docker compose down`. To remove the volumes as well and force a clean retrain, run `docker compose down -v`.

Note that the sample dataset is not baked into the image. On the first container start, the backend generates it and trains the model, so the first start is slower than subsequent ones.

## 8. Configuration

All configuration is supplied through environment variables. Every variable has a sensible default, so none is required for local development.

| Variable | Component | Default | Description |
|---|---|---|---|
| `SF_DATA_DIR` | Backend | `backend/data/` | Directory containing the sample dataset and the `uploads/` subdirectory. Override this to relocate data, for example onto a mounted volume. |
| `SF_MODEL_DIR` | Backend | `backend/models/` | Directory in which the trained model is persisted. |
| `SF_FRONTEND_DIST` | Backend | `frontend/out/` | Location of the static frontend build to be served by FastAPI. In the Docker image this is set to `/app/frontend/out`. |
| `SF_CORS_ORIGINS` | Backend | `http://localhost:3000` | Allowed cross-origin request origins. Set this when the frontend is hosted on a different origin from the API. |
| `API_URL` | Frontend (dev server) | `http://127.0.0.1:8000` | Backend address to which the Next.js development server proxies API requests. |
| `NEXT_PUBLIC_API_URL` | Frontend (build time) | empty (relative URLs) | Absolute API base URL embedded at build time. Leave empty when the API and UI share an origin. |

A suggested `.env.example` for local configuration:

```bash
# Backend
SF_DATA_DIR=backend/data
SF_MODEL_DIR=backend/models
SF_FRONTEND_DIST=frontend/out
SF_CORS_ORIGINS=http://localhost:3000

# Frontend
# API_URL=http://127.0.0.1:8000
# NEXT_PUBLIC_API_URL=https://your-api.example.com
```

`NEXT_PUBLIC_API_URL` is read at build time and compiled into the static export. Changing it requires rebuilding the frontend.

## 9. API Reference

The backend exposes a REST API under the `/api` prefix. The authoritative, always-current reference is generated from the code and served by the application itself:

| Resource | URL |
|---|---|
| Interactive documentation (Swagger UI) | `/docs` |
| OpenAPI schema (machine-readable) | `/openapi.json` |
| Health check | `/api/health` |

The health endpoint returns a successful response once the application has started and is suitable for use as a container or load balancer health probe. The API covers dataset summary and analytics, forecasting, model evaluation, and data upload. Because the documentation is generated directly from the route definitions, it cannot drift out of date with the implementation.

In development, the Swagger interface is reachable through the frontend origin (`http://localhost:3000/docs`) as well as directly on the backend, because the development server proxies it.

## 10. Forecasting Model

**Lifecycle.** The model is trained on first start and persisted to `SF_MODEL_DIR` as `model.joblib`. On later starts the persisted file is loaded rather than retrained. To force retraining, delete the model file (or the model volume under Docker) and restart the application.

**Evaluation.** The evaluation view reports model quality and a month-by-month comparison of actual and predicted values, allowing a reader to see precisely where the model performs well and where it does not.

**Design decisions and limitations.** Users should interpret forecasts with the following in mind:

- Forecast accuracy depends directly on the quantity, regularity and quality of the training data. The bundled sample dataset is synthetic and is intended to demonstrate the system, not to represent any real business.
- Forecasts are statistical estimates, not guarantees. They do not account for events absent from the training history, such as promotions, supply disruptions or market shocks.
- The model should be evaluated on the organisation's own data before any forecast is used to inform a business decision.

## 11. Data Requirements

The application accepts tabular sales data in CSV format. The dataset must contain the required columns and may contain a number of optional columns that enable additional analytics. Uploaded files are validated on receipt, and the API returns a descriptive error when a required column is missing. The authoritative column definitions are published in the OpenAPI documentation at `/docs` for the upload endpoint.

Uploaded datasets are stored in `backend/data/uploads/` (or the `uploads/` directory beneath `SF_DATA_DIR`), which is intentionally separate from the bundled sample data.

## 12. Testing

The backend test suite uses pytest and exercises the API through a test client.

```bash
cd backend
pip install pytest
pytest
```

The tests should be run from the `backend` directory so that the `app` package resolves correctly.

## 13. Project Structure

```
.
|-- backend/
|   |-- app/
|   |   |-- main.py              Application entry point and route registration
|   |   |-- config.py            Environment-driven configuration
|   |   |-- data.py              Dataset loading and validation
|   |   |-- analytics.py         Aggregations and analytical computations
|   |   |-- ml.py                Model training, persistence and inference
|   |   `-- state.py             Startup logic and shared application state
|   |-- scripts/
|   |   `-- generate_sample_data.py   Sample dataset generator
|   |-- tests/
|   |   `-- test_api.py          API test suite
|   |-- data/
|   |   `-- uploads/             User-uploaded datasets (runtime)
|   `-- models/                  Persisted model (runtime, generated)
|-- frontend/
|   |-- src/
|   |   |-- app/                 Pages, layout and global styles (App Router)
|   |   |-- components/          Reusable UI components
|   |   `-- lib/api.ts           Typed API client
|   |-- public/                  Static assets
|   |-- next.config.ts           Dev proxy and static export configuration
|   `-- package.json
|-- Dockerfile                   Multi-stage production image
|-- docker-compose.yml           Single-service Compose definition with volumes
`-- README.md
```

The exact module layout within `backend/app/` may evolve; the names above reflect the current organisation of responsibilities.

## 14. Version Control Guidance

Several files are produced at runtime or are large binaries, and should not be committed. The following entries are recommended in the root `.gitignore`:

```gitignore
# Python
__pycache__/
*.pyc
.venv/
.pytest_cache/

# Generated artifacts
backend/models/
backend/data/uploads/
backend/data/superstore_dataset.csv
*.joblib

# Frontend
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/next-env.d.ts
*.tsbuildinfo

# Environment files
.env
.env.local
.env.*.local

# Reference artifacts (large binaries)
*.pbix
*.ipynb

# OS / editor
.DS_Store
Thumbs.db
.vscode/
```

The sample dataset is excluded because it is regenerated on demand by `backend/scripts/generate_sample_data.py`, which is the single source of truth. If the original notebook or Power BI report should be retained in the repository, track them with Git LFS instead of ignoring them.

## 15. Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| Slow first request or first start | The sample data is being generated and the model trained. | Wait a few seconds. This occurs only once per fresh data and model directory. |
| Browser reports a CORS error | The frontend origin is not in the allowed list. | Set `SF_CORS_ORIGINS` to include the frontend origin and restart the backend. |
| Frontend shows no data in development | The backend is not running, or `API_URL` is wrong. | Confirm the backend responds at `/api/health` and that `API_URL` matches its address. |
| Production build serves an API-only application | `SF_FRONTEND_DIST` does not point to a built `out/` directory. | Run `npm run build` in `frontend/` and set `SF_FRONTEND_DIST` to the resulting directory. |
| `npm ci` fails during local or Docker build | `package-lock.json` is missing or out of sync with `package.json`. | Run `npm install` locally to regenerate the lock file, commit it, and rebuild. Also confirm that every dependency version in `package.json` is a published release. |
| Stale predictions after changing data | The persisted model was trained on the previous data. | Delete `model.joblib` (or the model volume) and restart to retrain. |
| `ModuleNotFoundError` when running tests | Tests were launched from the wrong directory. | Run `pytest` from the `backend` directory. |

## 16. Reference Materials

The repository root contains the original analysis that preceded the application: a Jupyter notebook documenting the initial exploration and modelling work, and a Power BI report presenting the same data. They are retained for reference only and are not required to build, run or deploy the application. Both are excluded from the Docker image.

---

## 17. Authors and Team

SalesCast was developed collaboratively. The author who maintains this repository is introduced first, followed by the team members who contributed to the project.

### Author

**William Law II**
Software Engineer | Frontend Engineer and Designer

William Law II is a software engineer whose work spans product development, interface design and design engineering. His projects combine full-stack web development with data and machine learning, and include analytics platforms, fraud detection systems and backend services.

| Resource | Link |
|---|---|
| Portfolio | [willx.tech](https://willx.tech) |
| Projects and writing | [willx.tech/BlogsandProject](https://willx.tech/BlogsandProject) |
| GitHub | [github.com/SheerWill07](https://github.com/SheerWill07) |
| Medium | [medium.com/@williamtecumsehsherman007](https://medium.com/@williamtecumsehsherman007) |
| Email | [williambenjaminlaw007@gmail.com](mailto:williambenjaminlaw007@gmail.com) |

For questions, feedback or collaboration enquiries regarding this project, please contact the author by email or through the portfolio website.

### Team Members

The following individuals contributed to the design, development and delivery of SalesCast.

| Name | GitHub |
|---|---|
| Aditya | [github.com/Aditya43Ux](https://github.com/Aditya43Ux) |
| Gargi | [github.com/Gargi0311](https://github.com/Gargi0311) |
| Aakash | [github.com/Aakash00017](https://github.com/Aakash00017) |

Suggestions, issue reports and contributions from the wider community are welcome through the project repository.

---

Copyright 2026 William Law II and the SalesCast team. All rights reserved.
