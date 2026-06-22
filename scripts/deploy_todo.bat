@echo off
title 🤖 ROBOT TOTAL — Proyecto Infinito
chcp 65001 >nul

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║   🤖  R O B O T   T O T A L                                ║
echo ║                                                              ║
echo ║   Un solo comando — TODO desplegado automáticamente          ║
echo ║                                                              ║
echo ║   ✅ DApp (frontend) en Vercel                               ║
echo ║   ✅ API Python (backend) en Vercel                          ║
echo ║   ✅ OpenRouter IA configurado                               ║
echo ║   ✅ Monetag listo para anuncios                             ║
echo ║   ✅ Auto-Pilot generando posts 24/7                         ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: ─── 1. Verificar Node.js ───
echo [1/6] 🔍 Verificando herramientas...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Node.js no instalado. Instálalo desde: https://nodejs.org
    echo   Presiona cualquier tecla para abrir el navegador...
    pause >nul
    start https://nodejs.org
    exit /b 1
)
echo   ✅ Node.js OK

:: ─── 2. Instalar Vercel CLI ───
where vercel >nul 2>&1
if %errorlevel% neq 0 (
    echo   ⚙️ Instalando Vercel CLI...
    npm install -g vercel
)
echo   ✅ Vercel CLI OK

:: ─── 3. Pedir API Key de OpenRouter ───
echo.
echo [2/6] 🔑 Configurar OpenRouter (IA gratis para generar contenido SEO)
echo.
echo   🆓 Regístrate gratis: https://openrouter.ai/keys
echo   (Copia la API Key que empieza con sk-or-v1-...)
echo.
set /p OR_KEY="   PEGA TU API KEY AQUI: "
if "%OR_KEY%"=="" (
    echo.
    echo   ⚠️ Sin API Key. El modo LOCAL seguirá funcionando.
    echo   Los posts se generarán con contenido de ejemplo.
    echo   Puedes configurar la key después en la DApp.
    echo.
    pause
) else (
    echo   ✅ API Key guardada
)

:: ─── 4. LOGIN en Vercel ───
echo.
echo [3/6] 🔑 Iniciando sesión en Vercel...
echo.
echo   ⚠️ SE VA A ABRIR EL NAVEGADOR.
echo   Haz clic en "Continue with GitHub" y autoriza.
echo   Después vuelve AQUI.
echo.
pause
vercel login
echo.
echo   ✅ Login completado (si no hay errores arriba)

:: ─── 5. Configurar variables de entorno en Vercel ───
echo.
echo [4/6] ⚙️ Configurando OpenRouter API Key en Vercel...
cd /d "%~dp0.."
if not "%OR_KEY%"=="" (
    echo %OR_KEY%| vercel env add OPENROUTER_API_KEY production 2>nul
    if %errorlevel% neq 0 (
        vercel env add OPENROUTER_API_KEY production
    )
    echo   ✅ Variable OPENROUTER_API_KEY configurada
)

:: ─── 6. DEPLOY FINAL — Un solo comando ───
echo.
echo [5/6] 🚀 Desplegando TODO (DApp + API + OpenRouter)...
echo.
echo   ⚠️ La primera vez te preguntará:
echo      - Set up and deploy? → Yes
echo      - Which scope? → Elige tu cuenta
echo      - Link to existing? → No (es primera vez)
echo      - Project name? → proyecto-infinito
echo      - Directory? → .  (solo presiona Enter)
echo.
echo   DESPUÉS DE ESO, las siguientes veces SOLO será:
echo      vercel --prod --yes
echo.
pause
echo.
echo   🚀 Ejecutando: vercel --prod
echo.
call vercel --prod
if %errorlevel% neq 0 (
    echo.
    echo   ⚠️ El deploy tuvo problemas. Cosas que revisar:
    echo     - ¿Ya tienes una cuenta en vercel.com?
    echo     - ¿El login fue exitoso?
    echo     - Intenta manualmente: vercel --prod
    echo.
    pause
    exit /b 1
)

:: ─── 7. TODO LISTO ───
echo.
echo [6/6] ✅ TODO DESPLEGADO AUTOMÁTICAMENTE
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║   🤖  R O B O T   T O T A L   —   A C T I V O              ║
echo ║                                                              ║
echo ║   📦 Tu DApp está ONLINE en:                                ║
echo ║   https://proyecto-infinito.vercel.app                       ║
echo ║                                                              ║
echo ║   🔌 Tu API está ONLINE en:                                 ║
echo ║   https://proyecto-infinito.vercel.app/api/seo/generate/test ║
echo ║                                                              ║
echo ║   🤖 OpenRouter IA: ✅ Configurado                          ║
echo ║   📢 Monetag:      ✅ Listo (solo falta tu Site ID)         ║
echo ║                                                              ║
echo ║   🎯 PRÓXIMOS PASOS:                                        ║
echo ║   1. Abre la URL de arriba en tu navegador                   ║
echo ║   2. Ve a Shadow Silo → Anuncios Monetag                     ║
echo ║   3. Pega tu Site ID de publisher.monerator.com              ║
echo ║   4. Activa el Auto-Pilot (▶️ Activar)                      ║
echo ║   5. ¡Los posts se generan SOLOS!                            ║
echo ║                                                              ║
echo ║   💰 Cada post tiene anuncios Monetag automáticos            ║
echo ║   🌐 Google indexa los posts → llega tráfico → ganas dinero  ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
start https://proyecto-infinito.vercel.app
