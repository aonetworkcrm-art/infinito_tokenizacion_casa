# 🐳 Dockerfile — Proyecto Infinito API (Render)
# =================================================
# Render construye y ejecuta este contenedor automáticamente
# cuando configuras "Runtime: Docker" en el dashboard.
#
# Build:       docker build -t infinito-api .
# Run local:   docker run -p 8000:8000 infinito-api

FROM python:3.12-slim

# ─── Evitar que Python escriba .pyc y bufferée stdout ───
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ─── Directorio de trabajo ───
WORKDIR /app

# ─── Copiar dependencias primero (cachea la capa) ───
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Copiar el código de la aplicación ───
COPY api/ ./api/
COPY modulos/ ./modulos/
COPY api_server.py .

# ─── El puerto lo asigna Render via $PORT ───
# Render inyecta la variable de entorno PORT automáticamente
EXPOSE 8000

# ─── Comando de inicio (Gunicorn + Uvicorn workers) ───
# -w 2:    2 workers (dentro del límite de 512MB RAM)
# -k uvicorn.workers.UvicornWorker:  worker ASGI para FastAPI
# --bind 0.0.0.0:$PORT:  Render asigna el puerto
CMD gunicorn -w 2 -k uvicorn.workers.UvicornWorker api.index:app --bind 0.0.0.0:${PORT:-8000} --timeout 120
