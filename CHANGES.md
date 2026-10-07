# Production Deployment Changes

This document summarizes all changes made to prepare SalesCast for Vercel + Render deployment.

## Files Modified

### 1. `backend/app/config.py`
**Change:** Added PORT configuration from environment variable
```python
PORT = int(os.getenv("PORT", "8000"))
```
**Reason:** Render requires reading port from `$PORT` environment variable

---

### 2. `backend/app/main.py`
**Changes:**
- Added `allow_credentials=True` to CORS middleware
- Updated docstring with production start command

**Reason:** Enable proper CORS handling for authenticated requests (if needed in future)

---

### 3. `frontend/next.config.ts`
**Change:** Removed static export for production
```typescript
// Before: { output: "export", images: { unoptimized: true } }
// After: {}
```
**Reason:** 
- Static export incompatible with Vercel's dynamic deployment
- Frontend needs to run as a Next.js server on Vercel
- Development proxy still works for local dev

---

### 4. `frontend/src/lib/api.ts`
**Change:** Added production validation for `NEXT_PUBLIC_API_URL`
```typescript
if (typeof window !== "undefined" && !API_BASE && !window.location.hostname.includes("localhost")) {
  console.error("NEXT_PUBLIC_API_URL is not set...");
}
```
**Reason:** Fail loudly when API URL is missing in production (helps catch deployment issues)

---

### 5. `backend/requirements.txt`
**Change:** Pinned all dependency versions
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
pandas==2.2.3
numpy==1.26.4
scikit-learn==1.5.2
joblib==1.4.2
openpyxl==3.1.5
```
**Reason:** Prevent deployment failures from breaking dependency updates

---

### 6. `.env.example`
**Change:** Complete rewrite with production deployment instructions
**Additions:**
- Clear separation between backend and frontend variables
- Detailed comments for each variable
- Production examples
- Deployment notes section

---

### 7. `README.md`
**Changes:**
- Added comprehensive "Production Deployment" section at the top
- Step-by-step Render deployment instructions
- Step-by-step Vercel deployment instructions
- Troubleshooting section
- Cost breakdown
- Reorganized to prioritize deployment over local dev

---

## Files Created

### 1. `render.yaml`
**Purpose:** Render deployment configuration
**Contents:**
- Service definition for FastAPI backend
- Build and start commands
- Environment variable placeholders
- Health check configuration

---

### 2. `backend/.env.example`
**Purpose:** Backend-specific environment variable template
**Contents:** Simplified version with only backend-relevant variables

---

### 3. `frontend/.env.example`
**Purpose:** Frontend-specific environment variable template
**Contents:** Only `NEXT_PUBLIC_API_URL` with clear instructions

---

### 4. `DEPLOYMENT.md`
**Purpose:** Complete step-by-step deployment checklist
**Contents:**
- Pre-deployment checklist
- Detailed Render setup instructions
- Detailed Vercel setup instructions
- CORS configuration steps
- Comprehensive troubleshooting guide
- Monitoring recommendations
- Cost breakdown
- Quick reference template

---

### 5. `CHANGES.md`
**Purpose:** This file - documentation of all changes made

---

## No Changes Required

These files were already production-ready:
- `backend/app/ml.py` - Model code works as-is
- `backend/app/analytics.py` - Analytics logic unchanged
- `backend/app/data.py` - Data processing unchanged
- `backend/app/state.py` - State management works with ephemeral storage
- `frontend/package.json` - Dependencies already correct
- `frontend/tsconfig.json` - TypeScript config unchanged
- All frontend components - No changes needed
- `.gitignore` - Already comprehensive

---

## Deployment Architecture

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
    v          v
┌────────┐  ┌────────┐
│ Render │  │ Vercel │
│        │  │        │
│ Python │  │Next.js │
│FastAPI │  │        │
└───┬────┘  └───┬────┘
    │           │
    │  ┌────────┘
    │  │
    v  v
┌─────────┐
│  User   │
│ Browser │
└─────────┘
```

**Request Flow:**
1. User visits Vercel frontend: `https://your-app.vercel.app`
2. Frontend loads with `NEXT_PUBLIC_API_URL` baked in
3. API requests go directly to Render: `https://your-api.onrender.com/api/*`
4. Render validates CORS origin matches Vercel domain
5. Render returns JSON data
6. Frontend renders charts and UI

---

## Key Configuration Points

### Render Backend
- **Port:** Reads from `$PORT` (set by Render automatically)
- **CORS:** Must include Vercel domain in `SF_CORS_ORIGINS`
- **Storage:** Ephemeral (model/data regenerated on restart)
- **Health Check:** `/api/health`

### Vercel Frontend
- **API URL:** `NEXT_PUBLIC_API_URL` baked at build time
- **Build:** Standard Next.js build (not static export)
- **Root:** `frontend/` directory
- **Environment:** Rebuild required after changing `NEXT_PUBLIC_API_URL`

---

## Testing Checklist

After deployment, verify:

- [ ] `https://YOUR-RENDER-URL.onrender.com/api/health` returns `{"status":"ok"}`
- [ ] `https://YOUR-RENDER-URL.onrender.com/docs` shows Swagger UI
- [ ] `https://YOUR-VERCEL-URL.vercel.app` shows landing page
- [ ] `https://YOUR-VERCEL-URL.vercel.app/dashboard` shows dashboard
- [ ] Browser console has no CORS errors
- [ ] Network tab shows requests going to Render (not localhost)
- [ ] All dashboard pages load data
- [ ] Charts render correctly
- [ ] Filters and interactions work

---

## Rollback Plan

If deployment fails:

1. **Render issues:**
   - Check logs in Render dashboard
   - Verify build command and start command
   - Check environment variables
   - Trigger manual redeploy

2. **Vercel issues:**
   - Check build logs in Vercel dashboard
   - Verify `NEXT_PUBLIC_API_URL` is set
   - Trigger manual redeploy
   - Check browser console for errors

3. **CORS issues:**
   - Verify `SF_CORS_ORIGINS` includes Vercel domain
   - No typos in URLs
   - Protocol (https) matches

---

## Future Enhancements

Potential improvements (not included in this deployment):

- [ ] Add authentication (Auth0, Clerk, etc.)
- [ ] Persistent storage for uploads (S3, Render disk)
- [ ] Database for multi-user support (PostgreSQL)
- [ ] Redis for caching forecasts
- [ ] CI/CD pipeline for automated testing
- [ ] Error tracking (Sentry)
- [ ] Analytics (PostHog, Mixpanel)
- [ ] Custom domain
- [ ] SSL certificate (automatic on Vercel/Render)

---

## Security Notes

✅ **Good:**
- No secrets committed to repository
- Environment variables used for configuration
- CORS properly configured
- `.gitignore` covers sensitive files

⚠️ **Future Considerations:**
- Add rate limiting for API endpoints
- Add authentication for data uploads
- Add input validation for user-uploaded files
- Consider API key for backend access
- Add HTTPS redirect (automatic on Render/Vercel)

---

## Summary

**Total files changed:** 7
**Total files created:** 5
**Breaking changes:** 0
**Deployment time:** ~15 minutes (after reading docs)
**Monthly cost:** $0 (free tier) or $7 (with always-on backend)

**Result:** Production-ready deployment to Vercel + Render with comprehensive documentation.
