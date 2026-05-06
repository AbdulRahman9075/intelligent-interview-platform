from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.db import engine, Base
from app.routes import resume, interview, evaluation,system

# ── System Optimizer ──────────────────────────────────────────────────────────
from app.system_optimiser.middleware import SystemMetricsMiddleware
# ─────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Based Adaptive Interview Intelligence Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── System Optimizer Middleware (must be added after CORS) ────────────────────
app.add_middleware(SystemMetricsMiddleware)
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(resume.router,     prefix="/api/v1", tags=["Resume"])
app.include_router(interview.router,  prefix="/api/v1", tags=["Interview"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["Evaluation"])

# ── System Optimizer Routes ───────────────────────────────────────────────────
app.include_router(system.router,prefix="/api/v1",tags=["System Optimizer"])
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "app": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
