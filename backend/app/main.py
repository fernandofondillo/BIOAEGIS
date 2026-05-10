"""
BioAEGIS FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging, os

from app.routers.simulate import router as simulate_router
from app.routers.parameters import router as parameters_router
from app.routers.interventions import router as interventions_router
from app.routers.memory import router as memory_router
from app.routers.llm import router as llm_router
from app.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bioaegis")

app = FastAPI(
    title="BioAEGIS API",
    description="Sistema de Gemelo Digital Biológico — 18 agentes biológicos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    init_db()
except Exception as e:
    logger.warning(f"[DB]init_db error: {e}")

app.include_router(simulate_router)
app.include_router(parameters_router)
app.include_router(interventions_router)
app.include_router(memory_router)
app.include_router(llm_router)

@app.get("/")
async def root():
    return {
        "name": "BioAEGIS API",
        "version": "1.0.0",
        "status": "online",
        "agents": 18,
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

logger.info("🐟 BioAEGIS backend initialized")
