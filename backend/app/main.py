from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.services.model_service import model_service
from app.routers import students, predict, tpo, simulator, tools, auth
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="PLACEMENTIQ — AI Placement Intelligence & Intervention Simulator",
    description="Institutional career intelligence platform with real ML, SHAP XAI, What-If simulation, Placement Flight Simulator, and TPO intervention optimization.",
    version="2.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

# CORS setup for Vite frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    model_service.load_artifacts()

# Include API Routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(predict.router)
app.include_router(tpo.router)
app.include_router(simulator.router)
app.include_router(tools.router)

@app.get("/")
def root():
    return {
        "platform": "PLACEMENTIQ",
        "tagline": "Predict readiness. Explain the gaps. Simulate interventions. Improve placement outcomes.",
        "status": "ONLINE",
        "version": "2.0.0",
        "model_loaded": model_service.is_loaded
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_service.is_loaded
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

