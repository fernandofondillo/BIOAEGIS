"""
BIOFISH AI — FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.routers import twin, simulate, chat, trajectory

app = FastAPI(
    title="BIOFISH AI",
    description="Motor de simulación biológica multi-agente para longevidad y salud",
    version="1.0.0",
)

# CORS — permitir frontend Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://biofish.vercel.app",
        "https://biofish-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(twin.router, prefix="/api/v1/twin", tags=["Twin"])
app.include_router(simulate.router, prefix="/api/v1/simulate", tags=["Simulate"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(trajectory.router, prefix="/api/v1/trajectory", tags=["Trajectory"])

@app.get("/")
async def root():
    return {
        "name": "BIOFISH AI",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

logger.info("BIOFISH AI backend started")