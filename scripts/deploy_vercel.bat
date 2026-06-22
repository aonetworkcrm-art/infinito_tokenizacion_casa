@echo off
title PROYECTO INFINITO — Deploy a Vercel
chcp 65001 >nul

echo =============================================
echo   PROYECTO INFINITO — Deploy a Vercel
echo =============================================
echo.
echo Requisitos:
echo   - Cuenta gratuita en https://vercel.com
echo   - Node.js instalado (para vercel CLI)
echo     https://nodejs.org/
echo.
echo =============================================
echo.

:: ─── Verificar si Vercel CLI está instalado ───
where vercel >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Vercel CLI no está instalado.
    echo    Instalando globalmente con npm...
    npm install -g vercel
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Error instalando Vercel CLI.
        echo    Instálalo manualmente: npm install -g vercel
        pause
        exit /b
    )
    echo ✅ Vercel CLI instalado
)

echo.
echo 🚀 Pasos a seguir:
echo.
echo 1. Te logueas en Vercel (abre navegador)
echo    vercel login
echo.
echo 2. Desplegar en producción:
echo    vercel --prod
echo.
echo 3. Copiar la URL que te da (ej: proyecto-infinito-xxx.vercel.app)
echo.
echo 4. Pegarla en la DApp → Shadow Silo → API Endpoint
echo.
echo =============================================
echo.
echo ¿Quieres continuar con el deploy?
echo.
pause

echo.
echo 📢 Iniciando login en Vercel...
call vercel login

echo.
echo 🚀 Desplegando a Vercel...
call vercel --prod

echo.
echo =============================================
echo   ✅ Deploy completado
echo   Copia la URL de arriba y pégala en la DApp
echo   (Shadow Silo → 🌐 API Endpoint → Preset Vercel)
echo =============================================
pause
