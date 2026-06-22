#!/usr/bin/env python3
"""
🤖 OpenRouter IA — Generación de Contenido SEO
==============================================
Endpoint que llama a OpenRouter para generar artículos SEO completos
usando modelos de IA gratuitos (Gemini Flash Lite).

Instalación:
    pip install openai

Variables de entorno:
    OPENROUTER_API_KEY   → Tu API key de OpenRouter (sk-or-v1-...)
    OPENROUTER_MODEL     → Modelo a usar (default: google/gemini-2.0-flash-lite-preview)

Uso:
    POST /api/seo/generate
    Body: { "niche_name": "Abogados de Accidentes",
            "niche_cat": "Servicios Legales",
            "cpc": 220,
            "keywords": ["car accident lawyer","personal injury attorney"] }
"""

import os
import json
import logging
from typing import Optional, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException

logger = logging.getLogger("openrouter")

router = APIRouter(prefix="/seo", tags=["OpenRouter IA"])

# ─── Config ───
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-lite-preview")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"


# ─── Header donde el frontend puede enviar su propia API Key ───
REQUEST_KEY_HEADER = "X-OpenRouter-Key"


# ─── Modelos ───

class GenerateRequest(BaseModel):
    niche_name: str = Field(..., description="Nombre del nicho (ej: Abogados de Accidentes)")
    niche_cat: str = Field("Servicios Legales", description="Categoría del nicho")
    cpc: float = Field(100, description="CPC promedio del nicho en USD")
    keywords: List[str] = Field(default_factory=list, description="Keywords principales")
    language: str = Field("es", description="Idioma: es | en")
    api_key: Optional[str] = Field(None, description="API Key de OpenRouter (opcional, fallback a env var)")


class GenerateResponse(BaseModel):
    success: bool
    title: str
    content: str
    meta_description: str
    faqs: List[dict]
    niche_name: str
    niche_cat: str
    cpc: float


# ─── Prompt SEO ───

def build_seo_prompt(niche_name: str, niche_cat: str, cpc: float, keywords: list, language: str) -> str:
    """Construye el prompt para OpenRouter que genera un artículo SEO completo."""
    
    kw_str = ", ".join(keywords[:8]) if keywords else niche_name
    lang_instruction = "Responde en español." if language == "es" else "Answer in English."
    
    prompt = f"""[INSTRUCCIÓN] {lang_instruction}
Eres un redactor SEO experto. Genera un artículo completo y listo para publicar sobre:

NICHO: {niche_name}
CATEGORÍA: {niche_cat}
CPC PROMEDIO: ${cpc:.0f} USD
KEYWORDS PRINCIPALES: {kw_str}

REQUISITOS DEL ARTÍCULO:
1. Título SEO optimizado (máx 70 caracteres, incluye keyword principal)
2. Meta description (máx 160 caracteres, optimizada para CTR)
3. Contenido: 6-8 párrafos informativos, estilo humano natural, tono profesional pero accesible. Incluye la keyword principal en el primer párrafo.
4. 3 preguntas frecuentes con respuestas detalladas (FAQ)

RESPONDE EXACTAMENTE EN ESTE FORMATO JSON (sin markdown, sin código adicional):
{{
  "title": "Título del artículo aquí",
  "meta_description": "Meta description aquí (máx 160 chars)",
  "content": "Párrafo 1.\\n\\nPárrafo 2.\\n\\nPárrafo 3.\\n\\nPárrafo 4.\\n\\nPárrafo 5.\\n\\nPárrafo 6.",
  "faqs": [
    {{"question": "Pregunta 1?", "answer": "Respuesta detallada 1"}},
    {{"question": "Pregunta 2?", "answer": "Respuesta detallada 2"}},
    {{"question": "Pregunta 3?", "answer": "Respuesta detallada 3"}}
  ]
}}

IMPORTANTE: Solo responde con el JSON. Sin texto adicional. Sin explicaciones. Sin markdown."""
    return prompt


# ─── Llamada a OpenRouter ───

def call_openrouter(prompt: str, api_key_override: Optional[str] = None) -> dict:
    """Llama a OpenRouter con el prompt y devuelve el JSON parseado.
    
    Args:
        prompt: El prompt a enviar
        api_key_override: API Key opcional desde el request (prioritaria sobre env var)
    """
    
    # Usar la key del request si se proporcionó, sino la env var
    api_key = api_key_override or OPENROUTER_API_KEY
    
    if not api_key:
        raise HTTPException(status_code=400, detail="API Key de OpenRouter no configurada. Configúrala en la DApp o en variables de entorno de Vercel.")
    
    try:
        from openai import OpenAI
    except ImportError:
        raise HTTPException(status_code=500, detail="openai package not installed. Run: pip install openai")
    
    try:
        client = OpenAI(
            base_url=OPENROUTER_BASE,
            api_key=api_key,
            timeout=60.0,
        )
        
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "Eres un redactor SEO experto. Siempre respondes en JSON válido sin markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2048,
            extra_headers={
                "HTTP-Referer": "https://proyectoinfinito.com",
                "X-OpenRouter-Title": "Proyecto Infinito - Shadow Silo IA",
            },
        )
        
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=502, detail="OpenRouter returned empty content")
        
        content = content.strip()
        if content.startswith("```"):
            if "\n" in content:
                content = content.split("\n", 1)[1]
            else:
                content = content[3:]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
        content = content.strip()
        
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                content = content[start:end]
                result = json.loads(content)
            else:
                raise HTTPException(status_code=502, detail=f"OpenRouter returned invalid JSON")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        raise HTTPException(status_code=502, detail=f"Error llamando a OpenRouter: {str(e)}")


# ─── Endpoint ───

@router.post("/generate", response_model=GenerateResponse)
def generate_seo_content(req: GenerateRequest):
    """
    🤖 Genera un artículo SEO completo usando OpenRouter (IA gratis).
    
    Llama a OpenRouter con un prompt SEO experto y devuelve:
    - title: Título optimizado
    - content: 6-8 párrafos de contenido
    - meta_description: Meta description optimizada
    - faqs: 3 preguntas frecuentes con respuestas
    
    La API Key se toma en este orden:
    1. Campo api_key en el body del request
    2. Variable de entorno OPENROUTER_API_KEY
    """
    try:
        prompt = build_seo_prompt(
            niche_name=req.niche_name,
            niche_cat=req.niche_cat,
            cpc=req.cpc,
            keywords=req.keywords,
            language=req.language,
        )
        
        # Pasar la API Key del request si el usuario la proporcionó
        result = call_openrouter(prompt, api_key_override=req.api_key)
        
        return GenerateResponse(
            success=True,
            title=result.get("title", req.niche_name),
            content=result.get("content", ""),
            meta_description=result.get("meta_description", f"Guía sobre {req.niche_name}"),
            faqs=result.get("faqs", []),
            niche_name=req.niche_name,
            niche_cat=req.niche_cat,
            cpc=req.cpc,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SEO content: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# ─── Endpoint de prueba (sin API key) ───

@router.get("/generate/test")
async def generate_test():
    """Endpoint de prueba para verificar que el módulo funciona sin llamar a OpenRouter."""
    return {
        "success": True,
        "message": "Módulo OpenRouter cargado correctamente",
        "api_key_configured": bool(OPENROUTER_API_KEY),
        "model": OPENROUTER_MODEL,
        "note": "Usa POST /api/seo/generate con el body adecuado para generar contenido real.",
    }
