from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from finstream.api.routes import auth, dashboard, health, pipeline, quality

app = FastAPI(
    title="finstream API",
    description="Industrial ETL pipeline for financial data processing",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(pipeline.router)
app.include_router(quality.router)
app.include_router(dashboard.router)
app.include_router(health.router)
