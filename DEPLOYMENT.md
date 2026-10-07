# 🚀 SalesCast Deployment Checklist

Complete step-by-step guide to deploy SalesCast to production using Vercel (frontend) + Render (backend).

---

## ✅ Pre-Deployment Checklist

Before starting deployment, ensure:

- [ ] Code is pushed to GitHub
- [ ] You have a Render account (https://render.com - free tier available)
- [ ] You have a Vercel account (https://vercel.com - free tier available)
- [ ] No secrets or API keys are committed to the repository

---

## 📦 Part 1: Deploy Backend to Render

### Step 1.1: Create Render Web Service

1. Log in to Render: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select your `Sales-Forecasting` repository
5. Render will detect `render.yaml` automatically

### Step 1.2: Configure Service Settings

If Render doesn't auto-detect, manually configure:

| Setting | Value |
|---------|-------|
| **Name** | `salescast-api` (or your preferred name) |
| **Region** | `Oregon` (or closest to your users) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python` |
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` (can upgrade later) |

### Step 1.3: Set Environment Variables

⚠️ **CRITICAL**: Add this environment variable in Render dashboard:

| Key | Value | Notes |
|-----|-------|-------|
| `SF_CORS_ORIGINS` | `http://localhost:3000` | We'll update this after Vercel deployment |
| `PYTHON_VERSION` | `3.12.0` | Recommended Python version |

**DO NOT SET:**
- `PORT` - Render sets this automatically
- `SF_DATA_DIR` - Uses default `data/`
- `SF_MODEL_DIR` - Uses default `models/`

### Step 1.4: Deploy

1. Click **"Create Web Service"**
2. Wait for the build to complete (3-5 minutes)
3. You'll get a URL like: `https://salescast-api.onrender.com`

### Step 1.5: Verify Backend Deployment

Test these URLs in your browser:

```
✅ Health Check:
https://YOUR-RENDER-URL.onrender.com/api/health

Expected: {"status":"ok","model_loaded":true}

✅ API Documentation:
https://YOUR-RENDER-URL.onrender.com/docs

Expected: Interactive Swagger UI
```

🎉 **Backend deployment complete!** Save your Render URL - you'll need it for the frontend.

---

## 🎨 Part 2: Deploy Frontend to Vercel

### Step 2.1: Import Project to Vercel

1. Log in to Vercel: https://vercel.com
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Vercel will auto-detect Next.js

### Step 2.2: Configure Build Settings

Vercel should auto-detect these, but verify:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Next.js` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` (automatic) |
| **Install Command** | `npm install` |

### Step 2.3: Set Environment Variables

⚠️ **CRITICAL**: Add this environment variable:

| Key | Value | Example |
|-----|-------|---------|
| `NEXT_PUBLIC_API_URL` | Your Render backend URL | `https://salescast-api.onrender.com` |

**Important:**
- No trailing slash: `https://api.onrender.com` ✅
- With trailing slash: `https://api.onrender.com/` ❌
- Replace `salescast-api` with your actual Render service name

### Step 2.4: Deploy

1. Click **"Deploy"**
2. Wait for build to complete (2-4 minutes)
3. You'll get a URL like: `https://your-app.vercel.app`

### Step 2.5: Verify Frontend Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. You should see the landing page
3. Click "Go to Dashboard" or navigate to `/dashboard`
4. **Check browser console (F12) for errors**

---

## 🔄 Part 3: Update Backend CORS

Now that you have your Vercel URL, update the backend to allow requests from it.

### Step 3.1: Update Render Environment Variable

1. Go to Render dashboard: https://dashboard.render.com
2. Select your `salescast-api` service
3. Go to **"Environment"** tab
4. Find `SF_CORS_ORIGINS`
5. Update it to include your Vercel URL:

```
https://your-app.vercel.app,http://localhost:3000
```

**Format:**
- Comma-separated, no spaces
- Include `https://`
- Include `http://localhost:3000` to keep local development working
- Replace `your-app.vercel.app` with your actual Vercel domain

### Step 3.2: Trigger Render Redeploy

1. Click **"Save Changes"**
2. Render will automatically redeploy (takes 1-2 minutes)
3. Wait for the new deployment to go live

---

## ✅ Part 4: Final Verification

### Test Complete Flow

1. **Visit your Vercel frontend:**
   ```
   https://your-app.vercel.app
   ```

2. **Navigate to Dashboard:**
   ```
   https://your-app.vercel.app/dashboard
   ```

3. **Check all pages load:**
   - [ ] Overview - KPIs and charts show data
   - [ ] Insights - Treemap and scatter plot render
   - [ ] Forecast - Historical and forecast charts load
   - [ ] Inventory - Table shows reorder points
   - [ ] Model - Metrics and evaluation charts display
   - [ ] Data - Dataset preview table renders

4. **Test API requests:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Navigate between dashboard pages
   - Verify requests go to your Render URL (not localhost)
   - Verify no CORS errors in console

5. **Test interactivity:**
   - [ ] Change forecast horizon (3/6/12 months)
   - [ ] Adjust date filters on Overview
   - [ ] Upload a CSV file on Data page (optional)
   - [ ] Retrain model on Model page (optional)

### Expected Behavior

✅ **Success indicators:**
- All charts display data
- No red errors in browser console
- Network tab shows successful API calls to Render
- Dashboard is interactive and responsive

❌ **Common issues:**
- "Failed to fetch" → Check `NEXT_PUBLIC_API_URL` is set correctly
- CORS errors → Check `SF_CORS_ORIGINS` includes Vercel domain
- Blank charts → Check Render backend is awake (free tier spins down)

---

## 🐛 Troubleshooting

### Issue: Frontend shows no data

**Symptoms:**
- Dashboard loads but charts are empty
- Browser console shows: `Failed to fetch` or `NetworkError`

**Solutions:**
1. Verify `NEXT_PUBLIC_API_URL` on Vercel
   - Go to Vercel → Project Settings → Environment Variables
   - Confirm it matches your Render URL exactly
   - No trailing slash!
2. Test backend directly:
   ```bash
   curl https://YOUR-RENDER-URL.onrender.com/api/health
   ```
3. Redeploy frontend on Vercel:
   - Go to Vercel → Deployments
   - Click three dots on latest deployment → Redeploy

### Issue: CORS errors in browser console

**Symptoms:**
```
Access to fetch at 'https://...' from origin 'https://...'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header
```

**Solutions:**
1. Check Render environment variable `SF_CORS_ORIGINS`
   - Must include your Vercel domain
   - Format: `https://your-app.vercel.app,http://localhost:3000`
   - No trailing slashes, comma-separated
2. After changing, wait for Render to redeploy (1-2 minutes)
3. Hard refresh your browser (Ctrl+Shift+R)

### Issue: First request takes 30-60 seconds

**Symptoms:**
- Initial page load is very slow
- Subsequent requests are fast

**Explanation:**
- Render free tier spins down after 15 minutes of inactivity
- First request wakes up the service (cold start)
- This is normal behavior on the free tier

**Solutions:**
- Wait for service to wake up (first load is always slow)
- Upgrade to Render Starter plan ($7/mo) for always-on instances
- Use UptimeRobot to ping your API every 10 minutes (keeps it warm)

### Issue: Changes to environment variables not reflected

**For Vercel:**
- Environment variables are baked into the build
- After changing `NEXT_PUBLIC_API_URL`, you must redeploy
- Go to Vercel → Deployments → Redeploy

**For Render:**
- Render auto-redeploys when environment variables change
- Wait 1-2 minutes for the new deployment to go live

### Issue: Model retrains on every Render restart

**Symptoms:**
- Logs show "Training model..." on each deployment
- Uploaded datasets disappear after restarts

**Explanation:**
- Render free tier uses ephemeral storage
- Files (models, uploads) are lost on restart
- This is expected behavior

**Solutions:**
- Accept it - model trains quickly (a few seconds)
- Upgrade to Render with persistent disk add-on (paid)
- Re-upload datasets after restarts if needed

---

## 📊 Monitoring Your Deployment

### Render Dashboard

Monitor your backend:
- View logs: Render Dashboard → Logs tab
- Check metrics: CPU, memory usage
- See deployment history
- Configure alerts (paid plans)

### Vercel Dashboard

Monitor your frontend:
- View deployment logs
- Analytics (pageviews, performance)
- Error tracking (paid plans)
- Runtime logs (paid plans)

### Health Check Endpoints

Set up external monitoring (UptimeRobot, Pingdom, etc.):

```
Backend Health:
https://YOUR-RENDER-URL.onrender.com/api/health

Expected Response:
{"status":"ok","model_loaded":true}
```

---

## 💰 Cost Breakdown

### Free Tier (Current Setup)

| Service | Plan | Limits | Cost |
|---------|------|--------|------|
| Render | Free | 750 hours/month, spins down after 15min inactivity | $0 |
| Vercel | Hobby | 100GB bandwidth, unlimited requests | $0 |
| **Total** | | | **$0/month** |

### Recommended Upgrade (Production)

| Service | Plan | Benefits | Cost |
|---------|------|----------|------|
| Render | Starter | Always-on, no spin-down, 512MB RAM | $7/month |
| Vercel | Hobby | Same as free (sufficient for most) | $0 |
| **Total** | | | **$7/month** |

---

## 🔄 Redeployment & Updates

### When code changes

**Backend:**
1. Push changes to GitHub
2. Render auto-deploys (if auto-deploy is enabled)
3. Or manually trigger deploy in Render dashboard

**Frontend:**
1. Push changes to GitHub
2. Vercel auto-deploys automatically
3. Or manually trigger via Vercel dashboard

### When environment variables change

**Backend (Render):**
- Update in Render dashboard → Environment tab
- Render redeploys automatically

**Frontend (Vercel):**
- Update in Vercel dashboard → Settings → Environment Variables
- Must manually trigger a redeploy (environment variables are baked at build time)

---

## 🎯 Quick Reference

### Your URLs (fill in after deployment)

```
Backend (Render):
https://_________________________.onrender.com

Frontend (Vercel):
https://_________________________.vercel.app

API Health:
https://_________________________.onrender.com/api/health

API Docs:
https://_________________________.onrender.com/docs
```

### Environment Variables Summary

**Render (Backend):**
```bash
SF_CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
PYTHON_VERSION=3.12.0
# PORT is set automatically by Render
```

**Vercel (Frontend):**
```bash
NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com
```

---

## 🎉 Congratulations!

Your SalesCast application is now live in production!

**Next steps:**
- [ ] Share your Vercel URL with users
- [ ] Set up monitoring/alerts
- [ ] Consider upgrading Render to avoid cold starts
- [ ] Test uploading real data on the /dashboard/data page
- [ ] Customize the branding and content as needed

**Need help?**
- Render docs: https://render.com/docs
- Vercel docs: https://vercel.com/docs
- Next.js docs: https://nextjs.org/docs
- FastAPI docs: https://fastapi.tiangolo.com

---

Made with ❤️ by deploying great code to great platforms.
