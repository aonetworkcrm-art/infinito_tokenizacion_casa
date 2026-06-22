@echo off
title PROYECTO INFINITO — Cloudflare Tunnel + API Server
chcp 65001 >nul

echo =============================================
echo   PROYECTO INFINITO — Tunnel + API Server
echo =============================================
echo.

:: ─── Ubicación de cloudflared ───
set CLOUDFLARED="%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"

:: ─── Rutas del proyecto ───
set PROYECTO_DIR=%~dp0..
set API_SCRIPT=%PROYECTO_DIR%\api_server.py

:: ─── Verificar si cloudflared está autenticado ───
if not exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo ⚠️  Cloudflare no está autenticado.
    echo    Abriendo navegador para login...
    echo    Después de loguearte, vuelve a ejecutar este script.
    echo.
    %CLOUDFLARED% tunnel login
    pause
    exit /b
)

:: ─── Verificar si el túnel existe ───
%CLOUDFLARED% tunnel list 2>nul | findstr "infinito-api" >nul
if %ERRORLEVEL% NEQ 0 (
    echo 🚀 Creando túnel 'infinito-api'...
    %CLOUDFLARED% tunnel create infinito-api
)

:: ─── Obtener ID del túnel ───
for /f "tokens=*" %%a in ('%CLOUDFLARED% tunnel list 2^>nul ^| findstr "infinito-api"') do (
    for /f "tokens=1" %%b in ("%%a") do set TUNNEL_ID=%%b
)

if "%TUNNEL_ID%"=="" (
    echo ❌ No se pudo obtener el ID del túnel
    pause
    exit /b
)

echo 🔗 Tunnel ID: %TUNNEL_ID%

:: ─── Configurar el túnel ───
if not exist "%USERPROFILE%\.cloudflared\%TUNNEL_ID%.json" (
    echo 📝 Creando configuración del túnel...
    (
        echo {
        echo   "tunnel": "%TUNNEL_ID%",
        echo   "ingress": [
        echo     {
        echo       "hostname": "*",
        echo       "service": "http://localhost:8000"
        echo     }
        echo   ]
        echo }
    ) > "%USERPROFILE%\.cloudflared\config.yml"
    echo ✅ Configuración creada
)

:: ─── Verificar si uvicorn está instalado ───
pip show uvicorn >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    pip install uvicorn fastapi
)

:: ─── Iniciar API Server en ventana separada ───
echo.
echo 🚀 Iniciando FastAPI Server (localhost:8000)...
start "INFINITO-API" cmd /c "cd /d %PROYECTO_DIR% && uvicorn api_server:app --reload --host 0.0.0.0 --port 8000"
echo.
echo ⏳ Esperando 3 segundos a que el servidor arranque...
timeout /t 3 /nobreak >nul

:: ─── Probar que el API está funcionando ───
curl -s http://localhost:8000/ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ API Server funcionando en http://localhost:8000
) else (
    echo ⚠️  API Server puede no haber arrancado aún...
)

:: ─── Iniciar el túnel ───
echo.
echo 🌐 Iniciando Cloudflare Tunnel...
echo    Tu API será accesible en: https://infinito-api.trycloudflare.com
echo.
echo    📋 Para ver la URL exacta, busca la línea que dice:
echo       "INFERIRE... https://XXXXX.trycloudflare.com"
echo.
echo    Presiona Ctrl+C en esta ventana para detener el túnel
echo    (El API Server seguirá corriendo en segundo plano)
echo.
%CLOUDFLARED% tunnel run infinito-api

:: ─── Al cerrar, detener el API ───
echo.
echo 🛑 Deteniendo servidores...
taskkill /fi "WINDOWTITLE eq INFINITO-API" /f >nul 2>&1
echo ✅ Todo detenido.
pause
