@echo off
title PROYECTO INFINITO — Deploy a Render
chcp 65001 >nul

echo =============================================
echo   PROYECTO INFINITO — Deploy a Render (Gratis)
echo =============================================
echo.
echo ─── Requisitos ───
echo 1. Cuenta gratuita en https://render.com
echo    (No requiere tarjeta de crÈdito)
echo.
echo 2. Repositorio en GitHub (ya lo tienes):
echo    https://github.com/aonetworkcrm-art/infinito_tokenizacion_casa
echo.
echo ─── Pasos para desplegar ───
echo.
echo PASO 1: Abre https://dashboard.render.com
echo.
echo PASO 2: Haz clic en "New +" → "Blueprint"
echo.
echo PASO 3: Conecta tu repositorio de GitHub:
echo    aonetworkcrm-art/infinito_tokenizacion_casa
echo.
echo PASO 4: Render detectar· autom·ticamente render.yaml
echo    y configurar· el servicio.
echo.
echo PASO 5: Haz clic en "Apply"
echo.
echo PASO 6: Espera 2-3 minutos a que Render construya
echo    el contenedor Docker y lo despliegue.
echo.
echo ─── DespuÈs del deploy ───
echo.
echo Obtendr·s una URL como:
echo   https://proyecto-infinito-api.onrender.com
echo.
echo Para conectarla a la DApp:
echo   1. Abre la DApp en el navegador
echo   2. Ve al tab SHADOW SILO
echo   3. Haz clic en "API Endpoint"
echo   4. Selecciona el preset "Render"
echo   5. Pega la URL: https://proyecto-infinito-api.onrender.com
echo   6. Guarda
echo.
echo ─── Probar el API ───
echo.
echo Una vez desplegado, prueba:
echo   curl https://proyecto-infinito-api.onrender.com/api/health
echo.
echo DeberÌas recibir:
echo   {"status":"ok","platform":"render","version":"1.0.0",...}
echo.
echo ─── Notas del Free Tier ───
echo.
echo • 750 horas/mes (suficiente para 24/7)
echo • Se duerme tras 15 min sin actividad
echo • Primer request tarde ~30-60s (cold start)
echo • La DApp ya maneja el cold start autom·ticamente
echo   (reintenta con 3s, 6s, 12s de espera)
echo.
echo =============================================
pause
