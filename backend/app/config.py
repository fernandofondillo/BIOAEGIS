"""
BIOFISH AI — FastAPI Backend
Agentes biológicos + Simulación BIOSIS + BioChat
"""
import os
from loguru import logger

# Configuración
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")

logger.add("/tmp/biofish.log", rotation="10 MB", level="INFO")

def get_groq_client():
    from groq import Groq
    return Groq(api_key=GROQ_API_KEY)

def get_minimax_client():
    import openai
    return openai.OpenAI(
        api_key=MINIMAX_API_KEY,
        base_url="https://api.minimax.io/anthropic/v1"
    )