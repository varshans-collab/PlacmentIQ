# Dockerfile for PlacementIQ backend
# Place this file in the ROOT of the repo (same level as backend/, frontend/, data/)

FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies first (better Docker layer caching)
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the project the backend needs to run
# (adjust these COPY lines if your model artifacts live somewhere else,
#  e.g. models/, artifacts/ - check what train_model.py saves and where)
COPY backend/ backend/
COPY data/ data/

EXPOSE 8000

# Render (and most hosts) inject a $PORT env var - fall back to 8000 for local testing
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir backend
