# Sales Forecasting

A full-stack sales analytics and demand-forecasting app built on the Superstore dataset. It turns the analysis in `minor project (1).ipynb` and the `sales forecasting.pbix` Power BI report into a web dashboard.

- **Backend:** FastAPI + pandas + scikit-learn. It runs the notebook's feature engineering and its Ridge + Gradient Boosting ensemble, and serves analytics, forecasts and inventory plans over a REST API.
- **Frontend:** Next.js 16 (App Router) + TypeScript + Recharts, set in Space Grotesk on a near-black and green palette.
  - **Landing page (`/`):** an animated before/after demo that shows a live forecast from the API, live stats and a feature overview.
  - **Dashboard (`/dashboard/*`):** interactive versions of the three Power BI pages, plus Forecast, Inventory and Data pages.
  - **Dashboard extras:** a collapsible sidebar, a ⌘K command palette, keyboard shortcuts, KPI cards with year-over-year deltas and sparklines, auto-generated insights, a dark/light/system theme toggle and Lenis smooth scrolling.

## 🚀 Production Deployment (Vercel + Render)

This application is designed for separate deployment:
- **Frontend** on Vercel (Next.js)
- **Backend** on Render (FastAPI)

### Prerequisites
- A [Render](https://render.com) account (free tier available)
- A [Vercel](https://vercel.com) account (free tier available)
- GitHub repository containing this code

---

### Step 1: Deploy Backend to Render

#### Option A: Using render.yaml (Recommended)

1. **Fork/push this repository to GitHub**

2. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Configure environment variables in Render dashboard:**
   - `SF_CORS_ORIGINS` = `https://your-app.vercel.app,http://localhost:3000`
     - ⚠️ Replace `your-app.vercel.app` with your actual Vercel domain (you'll get this in Step 2)
     - Keep `http://localhost:3000` for local development
   - `PORT` = (leave empty, Render sets this automatically)

4. **Deploy**
   - Render will build and deploy automatically
   - Note your backend URL: `https://salescast-api.onrender.com` (or your chosen name)
   - Test health check: `https://YOUR-RENDER-URL.onrender.com/api/health`
   - View API docs: `https://YOUR-RENDER-URL.onrender.com/docs`

#### Option B: Manual Setup

If you prefer manual configuration:

1. **Create Web Service on Render**
   - Runtime: `Python`
   - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Root Directory: `backend`

2. **Environment Variables:**
   - `SF_CORS_ORIGINS` = your Vercel URL + localhost
   - `PYTHON_VERSION` = `3.12.0`

3. **Health Check Path:** `/api/health`

---

### Step 2: Deploy Frontend to Vercel

1. **Import project to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Vercel will auto-detect Next.js

2. **Configure build settings:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build` (default)
   - **Install Command:** `npm install` (default)

3. **⚠️ CRITICAL: Set environment variable:**
   - Add environment variable:
     - **Key:** `NEXT_PUBLIC_API_URL`
     - **Value:** `https://YOUR-RENDER-URL.onrender.com`
     - ⚠️ Replace with your actual Render backend URL from Step 1
     - No trailing slash!

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your frontend URL will be: `https://your-app.vercel.app`

5. **Update CORS on Render**
   - Go back to Render dashboard
   - Update `SF_CORS_ORIGINS` environment variable to include your Vercel URL:
     - `https://your-app.vercel.app,http://localhost:3000`
   - Render will automatically redeploy

---

### Step 3: Verify Deployment

1. **Backend health check:**
   ```bash
   curl https://YOUR-RENDER-URL.onrender.com/api/health
   # Should return: {"status":"ok","model_loaded":true}
   ```

2. **Test API documentation:**
   - Visit: `https://YOUR-RENDER-URL.onrender.com/docs`

3. **Test frontend:**
   - Visit: `https://your-app.vercel.app`
   - Navigate to `/dashboard`
   - Verify charts load data from backend
   - Check browser console for errors

---

### Important Notes

**Environment Variables:**
- `NEXT_PUBLIC_API_URL` is baked into the frontend build at build time
- If you change your Render URL, you must trigger a new Vercel deployment
- Use Vercel's "Redeploy" button to rebuild with updated environment variables

**Free Tier Limitations:**
- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds (cold start)
- Upgrade to Render Starter plan ($7/mo) for always-on instances

**Data Persistence:**
- Render's ephemeral filesystem means uploaded datasets and trained models are lost on redeployment
- For persistence, consider upgrading to Render's persistent disk add-on
- The app regenerates sample data and retrains the model automatically on startup

---

## 💻 Local Development

Requirements: Python 3.10+ and Node 20+.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

On first start the API trains the model (a few seconds) and caches it in `backend/models/`. 

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 for the landing page and http://localhost:3000/dashboard for the app. 

In dev mode, Next.js proxies `/api` and `/docs` to the backend on port 8000 (override with `API_URL` environment variable).

### Environment Variables for Local Development

Copy the example files:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

For local development, the defaults work out of the box. No changes needed.

---

## Pages

| Page | What it shows | Source |
|------|---------------|--------|
| **Landing** (`/`) | Hero with a before/after toggle (scattered spreadsheets vs. a live forecast card), live dataset stats, features, how it works | New |
| **Overview** | KPI cards with YoY change and sparklines, revenue/profit/units trend, key insights, category, region share, top products. Filters for date, region, category and segment. | Power BI page 1 |
| **Insights** | Sub-category treemap, sales vs profit by product, sales by state (tile map), segment donut, orders by ship mode, demand variability, product table | Power BI page 2 + notebook EDA |
| **Forecast** | 3/6/12-month recursive forecast per product and region, with an approximate 80% interval and expected revenue. CSV export. | New |
| **Inventory** | Safety stock and reorder point per product/region, with adjustable service level and lead time | Notebook's safety-stock idea |
| **Model** | R², MAE, RMSE, MAPE, CV scores, actual vs predicted, prediction error, error distribution, feature importance, holdout table, retrain button | Power BI page 3 |
| **Data** | Upload your own `.xlsx`/`.csv` (the model retrains automatically), restore sample data, preview | New |

## Keyboard shortcuts (dashboard)

| Keys | Action |
|------|--------|
| `Ctrl/⌘ K` | Command palette (navigate, retrain, switch theme, open API docs) |
| `g` then `o` / `i` / `f` / `v` / `m` / `d` | Go to Overview / Insights / Forecast / Inventory / Model / Data |
| `[` | Collapse or expand the sidebar |

## Docker (Single-Server Mode)

For local testing of the bundled deployment (FastAPI serving the static frontend):

```bash
docker compose up --build
```

Then open http://localhost:8000.

**Note:** This Docker setup is for local development only. Production deployments use separate Vercel (frontend) + Render (backend) services.

## Data

The original `superstore_dataset.xlsx` used in the notebook isn't in this repo. So the app ships with **synthetic sample data** in the same 17-column schema: `backend/data/superstore_dataset.csv`, 9,000 orders, 2021–2023, made by `backend/scripts/generate_sample_data.py`.

To use the real data, upload the Excel file on the **Data** page. It's validated, saved to `backend/data/uploads/`, and the model is retrained right away. Required columns are `Order ID, Order Date, Region, Category, Sub-Category, Product ID, Product Name, Sales, Quantity, Profit`. Optional columns (`Ship Date, Ship Mode, Segment, State, Discount, Unit Price, Lead Time (Days)`) are derived or defaulted when missing.

## Model

`backend/app/ml.py` follows the notebook:

1. Aggregate orders to product × region × month.
2. Features: lags 1/2/3/6/12, rolling mean/std over 3/6/12 months, calendar flags (Q4, summer), category codes, average lead time, discount and unit price.
3. Ensemble `0.55 × Ridge(α=10, scaled) + 0.45 × GradientBoosting(300 trees, depth 2)`, clipped at 0.
4. Evaluate on the last 12 months (2023 in the sample data), with 3-fold `TimeSeriesSplit` CV.
5. Refit on all data and forecast recursively month by month.

A few changes were needed to make the notebook's model usable for real forecasts:

- **Lags per product *and* region.** The notebook grouped by `Product ID` only, so `lag_1` was often a different region's value for the same month.
- **Dropped `Num_Orders`.** It's the order count for the same month, so it's unknown when forecasting the future (target leakage).
- **Gap months filled with 0** so lags are true calendar lags.
- **Chronological CV.** The CV ran on product-sorted rows, so its folds weren't time-ordered.
- **Safety stock / reorder point in consistent units.** `SS = z·σ_daily·√L` and `ROP = daily_demand·L + SS`. The notebook mixed monthly σ with daily lead time, multiplied demand by unit price, and overwrote the 95% z (1.645) with 2.326.

Without the leaky feature, scores are lower but honest. Accuracy on your real data will differ from the synthetic sample.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check (always returns 200 when service is up) |
| GET | `/api/filters` | Filter options + date bounds |
| GET | `/api/overview` | KPIs, trend, category/region/product breakdowns |
| GET | `/api/insights` | Sub-category, state, segment, ship mode, product stats |
| GET | `/api/model` | Metrics, feature importance |
| GET | `/api/model/evaluation` | Holdout actual vs predicted (`product`, `region`) |
| POST | `/api/model/retrain` | Retrain on the active dataset |
| GET | `/api/forecast` | `horizon` (1–24), `product`, `region` |
| GET | `/api/inventory` | `service_level`, `lead_time`, `product`, `region` |
| GET | `/api/dataset` | Active dataset info + preview |
| POST | `/api/dataset/upload` | Upload `.csv`/`.xlsx` (multipart `file`) |
| POST | `/api/dataset/reset` | Return to the sample dataset |

`/api/overview` and `/api/insights` accept `start`, `end` (YYYY-MM-DD) and repeatable `region`, `category`, `segment`.

## Tests

```bash
cd backend
pytest
```

## Project layout

```
backend/
  app/            FastAPI app: main.py (routes), ml.py, analytics.py, data.py, state.py
  scripts/        sample-data generator
  data/           sample dataset (+ uploads/)
  tests/
frontend/
  src/app/            / (landing) and /dashboard/{insights,forecast,inventory,model,data}
  src/components/     shell, command palette, providers (theme + Lenis), filter bar, tables, tile map, UI kit
  src/components/landing/  before/after demo, typewriter, scroll reveal, live stats
  src/lib/            API client, formatting, chart theme
render.yaml         Render deployment configuration
minor project (1).ipynb   original analysis notebook
sales forecasting.pbix    original Power BI report
```

## Troubleshooting

### Frontend can't reach backend

**Symptom:** Dashboard loads but shows no data, console errors like "Failed to fetch"

**Solution:**
1. Verify `NEXT_PUBLIC_API_URL` is set correctly on Vercel
2. Check it has no trailing slash: ✅ `https://api.onrender.com` ❌ `https://api.onrender.com/`
3. Trigger a Vercel redeploy after changing environment variables
4. Test backend directly: `curl https://YOUR-RENDER-URL.onrender.com/api/health`

### CORS errors

**Symptom:** Browser console shows "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution:**
1. Update `SF_CORS_ORIGINS` on Render to include your Vercel domain
2. Make sure it includes the full URL with `https://`
3. Example: `https://your-app.vercel.app,http://localhost:3000`
4. Render will auto-redeploy when you change environment variables

### Render cold starts

**Symptom:** First request takes 30-60 seconds, then works fine

**Explanation:** Render free tier spins down after 15 minutes of inactivity

**Solutions:**
- Wait for the service to wake up (first request is always slow)
- Upgrade to Render Starter plan ($7/mo) for always-on instances
- Use a service like UptimeRobot to ping your API every 10 minutes (keeps it warm)

### Model retrains on every Render restart

**Symptom:** Logs show "Training model..." on each deployment

**Explanation:** Render's free tier uses ephemeral storage. Files are lost on restart.

**Solutions:**
- This is expected behavior - the model trains quickly (a few seconds)
- For persistence, upgrade to Render's persistent disk add-on
- Uploaded datasets will also need to be re-uploaded after restarts

---

## License

MIT
