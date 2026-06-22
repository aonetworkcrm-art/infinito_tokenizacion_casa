"""
🚀 Vercel Serverless Entry Point — Proyecto Infinito API
=========================================================
Vercel detecta automáticamente 'app = FastAPI()' aquí.
No necesita adapters (mangum/vercel-asgi) — Vercel tiene soporte nativo para ASGI.

Endpoints:
  /api/health          → Health check
  /api/seo/generate    → Genera artículo SEO con OpenRouter IA (POST)
  ... (todos los de api_server.py)

Uso local:
    vercel dev          # Prueba local que simula el entorno de producción

Uso en producción:
    vercel --prod       # Despliega a Vercel
"""

import sys
import os

# ─── Asegurar que podemos importar los módulos del proyecto ───
# En Vercel, el directorio raíz es donde está vercel.json
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ─── Importar la aplicación FastAPI desde api_server.py ───
# Vercel busca 'app' como la variable de la aplicación ASGI
from api_server import app

# ─── Importar módulo OpenRouter IA ───
from api_openrouter import router as openrouter_router
app.include_router(openrouter_router, prefix="/api")

# ─── Opcional: endpoint de health check específico de Vercel ───
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "platform": "vercel",
        "version": "1.0.0",
        "project": "PROYECTO INFINITO",
        "modules": ["infinito_dao", "seo_oracle", "whale_watcher", "treasury_flow"],
    }
