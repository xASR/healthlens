import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_assessment, routes_auth, routes_history, routes_report
from app.core.config import settings
from app.core.firebase_auth import init_firebase
from app.db.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting HealthLens API (%s)", settings.environment)
    init_db()
    init_firebase()
    yield
    logger.info("Shutting down HealthLens API")


app = FastAPI(
    title="HealthLens API",
    description="Explainable AI chronic disease risk screening backend.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, prefix=settings.api_v1_prefix)
app.include_router(routes_assessment.router, prefix=settings.api_v1_prefix)
app.include_router(routes_history.router, prefix=settings.api_v1_prefix)
app.include_router(routes_report.router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check():
    """Simple liveness probe -- also handy for confirming the server is up."""
    return {"status": "ok", "environment": settings.environment}
