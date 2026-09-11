# PlacementIQ — Production Deployment & Configuration Guide

PlacementIQ is an institutional career intelligence and placement intervention simulation platform.

---

## 1. System Requirements & Environment Setup

* **Python**: `3.9` to `3.12` (Python 3.14 compatible)
* **Node.js**: `v18.0.0` or higher
* **Package Managers**: `pip` (Python) and `npm` (Frontend)

---

## 2. Backend Deployment Setup

### Environment Variables
Configure the following optional environment variables for production server binding:

* `HOST` (Default: `0.0.0.0`) — Network interface binding.
* `PORT` (Default: `8000`) — Server listener port.
* `CORS_ORIGINS` (Default: `*`) — Allowed frontend origin URIs.

### Installation & Startup Commands
```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train ML Model & Export Genuine Artifacts (If needed)
python train_model.py

# 4. Start Production Uvicorn Server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Health Check Verification
Verify backend health status:
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","model_loaded":true}
```

---

## 3. Frontend Deployment Setup

### Environment Variables
Set `VITE_API_BASE_URL` during Vite build to point to the production backend URL:

```bash
# Example for production build
export VITE_API_BASE_URL="https://api.placementiq.yourdomain.com"
npm run build
```

### Installation & Build Commands
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install npm dependencies
npm install

# 3. Run Production Build (TypeScript check + Vite bundle)
npm run build

# 4. Preview Production Build Locally
npm run preview
```

---

## 4. SQLite Storage & Persistence Notice

* **Database Engine**: Embedded `sqlite3` (`backend/placementiq.db`).
* **Initial Seed**: Automatically populated with 610 deterministic student records and 4-month historical readiness trajectory snapshots on first boot from `data/demo_cohort_610.json`.
* **State Persistence**: For multi-region container deployments (e.g., Render, Railway, AWS ECS), attach a persistent volume to `backend/placementiq.db` or migrate to PostgreSQL if required for horizontal scaling.

---

## 5. Security & CORS Configuration

* CORS Middleware is configured in `backend/app/main.py`.
* Production origin restrictions can be specified via environment variables or CORS policy updates prior to public staging deployment.
