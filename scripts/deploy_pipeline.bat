@echo off
title 🚀 PROYECTO INFINITO — Pipeline Completo: Netlify + Vercel + OpenRouter
chcp 65001 >nul
echo ╔══════════════════════════════════════════════════════════════╗
echo ║   🚀 PROYECTO INFINITO — Pipeline Completo                 ║
echo ║   Netlify (DApp) + Vercel (API Python) + OpenRouter (IA)   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: ─── 1. Verificar herramientas ───
echo [1/5] 🔍 Verificando herramientas...
where vercel >nul 2>&1
if %errorlevel% neq 0 (
    echo   ⚠️ Vercel CLI no instalado. Instalando...
    npm install -g vercel
)
echo   ✅ Vercel CLI disponible

:: ─── 2. Variables de entorno ───
echo.
echo [2/5] 🔑 Configurar OpenRouter API Key
echo.
echo   Necesitas una API Key de OpenRouter para generar contenido SEO con IA.
echo   Regístrate gratis: https://openrouter.ai/keys
echo.
set /p OR_KEY="   Ingresa tu OpenRouter API Key (sk-or-v1-...): "
if "%OR_KEY%"=="" (
    echo   ⚠️ Sin API Key. El modo local seguirá funcionando sin IA.
    echo   Puedes configurarla después desde el dashboard de Vercel:
    echo   https://vercel.com/ -> Settings -> Environment Variables
) else (
    echo   Configurando OPENROUTER_API_KEY en Vercel...
    echo %OR_KEY%| vercel env add OPENROUTER_API_KEY production 2>nul
    if %errorlevel% neq 0 (
        echo   ⚠️ No se pudo configurar automáticamente.
        echo   Configúrala manualmente en: https://vercel.com/ -> Settings -> Environment Variables
    ) else (
        echo   ✅ OPENROUTER_API_KEY configurada en Vercel
    )
)

:: ─── 3. Deploy API a Vercel ───
echo.
echo [3/5] ▲ Desplegando API Python a Vercel...
cd /d "%~dp0.."
echo   Ejecutando: vercel --prod --yes
echo   (Puede pedir login la primera vez)
call vercel --prod --yes
if %errorlevel% neq 0 (
    echo   ⚠️ Error en deploy. Ejecuta manualmente: vercel --prod
    pause
    exit /b 1
)
echo   ✅ API desplegada en Vercel

:: ─── 4. Configurar DApp ───
echo.
echo [4/5] 🌐 Actualizando DApp con URL de Vercel...
echo.
echo   La DApp usa la URL de Vercel como endpoint automáticamente.
echo   Si cambia la URL, actúalizala en la DApp:
echo   Shadow Silo → API Endpoint → preset Vercel
echo.
echo   URL típica: https://proyecto-infinito-api.vercel.app
echo.

:: ─── 5. Deploy DApp a Netlify ───
echo [5/5] 📦 Desplegando DApp a Netlify...
echo.
echo   La DApp es un sitio estático (HTML+JS). Opciones de deploy:
echo.
echo   Opción A — Netlify Drop (más fácil):
echo     1. Abre https://app.netlify.com/drop
echo     2. Arrastra la carpeta: dapp/
echo     3. Obtienes URL como: https://nombre-aleatorio.netlify.app
echo.
echo   Opción B — Netlify CLI:
echo     netlify deploy --prod --dir=dapp/
echo.
echo   ⚠️ NOTA: La API Python NO funciona en Netlify.
echo     La DApp llama al API desplegada en Vercel automáticamente.
echo.

echo ╔══════════════════════════════════════════════════════════════╗
echo ║   ✅ PIPELINE COMPLETO                                     ║
echo ║                                                            ║
echo ║   📦 DApp Frontend  → Netlify (drop dapp/ folder)          ║
echo ║   🔌 API Python     → Vercel (vercel --prod)               ║
echo ║   🤖 IA OpenRouter → Configurar API Key en Vercel          ║
echo ║                                                            ║
echo ║   Para generar contenido con IA:                            ║
echo ║   1. Abre la DApp (Netlify URL)                            ║
echo ║   2. Ve a Shadow Silo → OpenRouter IA                      ║
echo ║   3. Configura tu API Key                                   ║
echo ║   4. Haz clic en "🤖 Generar con IA"                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
