<#
╔══════════════════════════════════════════════════════════════════╗
║    PROYECTO INFINITO — DEPLOY AUTOMATIZADO (PowerShell)        ║
║    Generar contenido → Deploy Netlify → Indexar Google → Run   ║
╚══════════════════════════════════════════════════════════════════╝

USO:
    .\deploy.ps1                    # Deploy completo (generar + netlify + indexar)
    .\deploy.ps1 -Mode full         # Ídem
    .\deploy.ps1 -Mode content      # Solo generar contenido
    .\deploy.ps1 -Mode netlify      # Solo deploy a Netlify
    .\deploy.ps1 -Mode index        # Solo Google Indexing API
    .\deploy.ps1 -Mode start        # Solo arrancar sistema
    .\deploy.ps1 -Help              # Mostrar ayuda

REQUISITOS:
    - Netlify CLI: npm install -g netlify-cli
    - Google Service Account JSON en ./google-service-account.json
    - Python 3.8+
    - Node.js 18+

CONFIGURACIÓN (variables de entorno):
    $env:NETLIFY_AUTH_TOKEN   = "token_de_api_netlify"
    $env:NETLIFY_SITE_ID      = "id_del_sitio_en_netlify"
    $env:GOOGLE_SERVICE_JSON  = "ruta_al_json_de_service_account"
    $env:SITE_URL             = "https://misitio.com"
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("full","content","netlify","index","start","help")]
    [string]$Mode = "full"
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$CONENT_DIR = "$ROOT\contenido"
$DAPP_DIR = "$ROOT\dapp"
$TIMESTAMP = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Banner {
    Clear-Host
    Write-Host "╔" -NoNewline -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════" -NoNewline -ForegroundColor Cyan
    Write-Host "╗" -ForegroundColor Cyan
    Write-Host "║  PROYECTO INFINITO — Deploy Automatizado" -ForegroundColor Cyan
    Write-Host "║  $TIMESTAMP" -ForegroundColor DarkGray
    Write-Host "╚" -NoNewline -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════" -NoNewline -ForegroundColor Cyan
    Write-Host "╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Msg)
    Write-Host "  → $Msg" -ForegroundColor Yellow
}

function Write-OK {
    param([string]$Msg)
    Write-Host "  ✅ $Msg" -ForegroundColor Green
}

function Write-Error {
    param([string]$Msg)
    Write-Host "  ❌ $Msg" -ForegroundColor Red
}

function Write-Skip {
    param([string]$Msg)
    Write-Host "  ⏭️  $Msg" -ForegroundColor DarkGray
}

function Test-Command {
    param([string]$Cmd)
    return (Get-Command $Cmd -ErrorAction SilentlyContinue) -ne $null
}

# ═══════════════════════════════════════════════════════════
# PASO 1: GENERAR CONTENIDO
# ═══════════════════════════════════════════════════════════

function Step-GenerateContent {
    Write-Step "[1/4] Generando contenido SEO..."

    if (-not (Test-Path "$ROOT\generar_contenido.py")) {
        Write-Error "No se encontró generar_contenido.py. Saltando."
        return $false
    }

    Write-Host "       ejecutando: python generar_contenido.py --all" -ForegroundColor DarkGray
    $result = & python "$ROOT\generar_contenido.py" --all 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error generando contenido: $result"
        return $false
    }

    # Contar archivos generados
    $count = @(Get-ChildItem "$CONENT_DIR\*.html" -ErrorAction SilentlyContinue).Count
    Write-OK "$count artículos HTML generados en $CONENT_DIR"
    return $true
}

# ═══════════════════════════════════════════════════════════
# PASO 2: PREPARAR ARCHIVOS PARA NETLIFY
# ═══════════════════════════════════════════════════════════

function Step-PrepareNetlify {
    Write-Step "[2/4] Preparando archivos para Netlify..."

    $NETLIFY_DIR = "$ROOT\netlify-deploy"
    if (Test-Path $NETLIFY_DIR) {
        Remove-Item -Recurse -Force $NETLIFY_DIR
    }
    New-Item -ItemType Directory -Force -Path $NETLIFY_DIR | Out-Null

    # 1. Copiar DApp
    if (Test-Path "$DAPP_DIR\index.html") {
        Copy-Item "$DAPP_DIR\index.html" "$NETLIFY_DIR\index.html"
        Write-OK "DApp copiada"
    }

    # 2. Copiar contenido generado
    if (Test-Path $CONENT_DIR) {
        $CONTENT_TARGET = "$NETLIFY_DIR\contenido"
        New-Item -ItemType Directory -Force -Path $CONTENT_TARGET | Out-Null
        Copy-Item "$CONENT_DIR\*.html" $CONTENT_TARGET
        $artCount = @(Get-ChildItem "$CONTENT_TARGET\*.html").Count
        Write-OK "$artCount artículos de contenido copiados"
    }

    # 3. Crear _redirects para SPA
    $redirectsContent = @"
/*    /index.html   200
/contenido/*    /contenido/:splat   200
"@
    $redirectsContent | Out-File -FilePath "$NETLIFY_DIR\_redirects" -Encoding utf8

    # 4. Crear netlify.toml
    $tomlContent = @"
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/contenido/*"
  [headers.values]
    Cache-Control = "public, max-age=3600, s-maxage=86400"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"@
    $tomlContent | Out-File -FilePath "$NETLIFY_DIR\netlify.toml" -Encoding utf8

    $totalFiles = @(Get-ChildItem "$NETLIFY_DIR" -Recurse -File).Count
    Write-OK "Archivos preparados en $NETLIFY_DIR ($totalFiles archivos)"
    return $NETLIFY_DIR
}

# ═══════════════════════════════════════════════════════════
# PASO 3: DEPLOY A NETLIFY
# ═══════════════════════════════════════════════════════════

function Step-NetlifyDeploy {
    param([string]$DeployDir)
    Write-Step "[3/4] Desplegando a Netlify..."

    if (-not (Test-Command "netlify")) {
        Write-Error "Netlify CLI no instalado. Ejecuta: npm install -g netlify-cli"
        Write-Host "       Puedes hacer deploy manual en: https://app.netlify.com/drop" -ForegroundColor DarkGray
        return $false
    }

    $netlifyToken = $env:NETLIFY_AUTH_TOKEN
    $netlifySiteId = $env:NETLIFY_SITE_ID

    if (-not $netlifyToken) {
        Write-Error "Variable NETLIFY_AUTH_TOKEN no configurada"
        return $false
    }

    if ($netlifySiteId) {
        Write-Host "       Deploy a sitio existente: $netlifySiteId" -ForegroundColor DarkGray
        $result = & netlify deploy --prod --dir=$DeployDir --auth=$netlifyToken --site=$netlifySiteId 2>&1
    } else {
        Write-Host "       Creando nuevo sitio Netlify..." -ForegroundColor DarkGray
        $result = & netlify deploy --prod --dir=$DeployDir --auth=$netlifyToken 2>&1
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error en deploy Netlify: $result"
        return $false
    }

    # Extraer URL del deploy
    $url = $null
    foreach ($line in $result) {
        if ($line -match "Website URL:\s+(https?://\S+)") {
            $url = $matches[1]
        }
        if ($line -match "Live Draft URL:\s+(https?://\S+)") {
            $url = $matches[1]
        }
    }

    if ($url) {
        Write-OK "Deploy exitoso → $url"
        return $url
    } else {
        Write-OK "Deploy exitoso"
        return $true
    }
}

# ═══════════════════════════════════════════════════════════
# PASO 4: GOOGLE INDEXING API
# ═══════════════════════════════════════════════════════════

function Step-GoogleIndexing {
    param([string]$SiteUrl)
    Write-Step "[4/4] Enviando URLs a Google Indexing API..."

    $serviceJson = $env:GOOGLE_SERVICE_JSON
    $siteUrl = if ($SiteUrl) { $SiteUrl } else { $env:SITE_URL }

    if (-not $serviceJson) {
        Write-Error "Variable GOOGLE_SERVICE_JSON no configurada"
        Write-Host "       Para configurar:" -ForegroundColor DarkGray
        Write-Host "       1. Crea un service account en Google Cloud Console" -ForegroundColor DarkGray
        Write-Host "       2. Descarga el JSON y configura la variable" -ForegroundColor DarkGray
        Write-Host "       3. Añade el correo como propietario en Search Console" -ForegroundColor DarkGray
        return $false
    }

    if (-not $siteUrl) {
        Write-Error "Variable SITE_URL no configurada. Usa --SiteUrl o configura SITE_URL"
        return $false
    }

    # Verificar que existe el JSON
    if (-not (Test-Path $serviceJson)) {
        Write-Error "No se encontró el archivo: $serviceJson"
        return $false
    }

    # Buscar URLs a indexar
    $urls = @()
    $urls += "$siteUrl/"  # Home/DApp
    if (Test-Path $CONENT_DIR) {
        foreach ($file in Get-ChildItem "$CONENT_DIR\*.html") {
            $slug = $file.BaseName
            $urls += "$siteUrl/contenido/$slug"
        }
    }

    Write-Host "       URLs a indexar: $($urls.Count)" -ForegroundColor DarkGray

    # Crear script temporal de Node.js para la Indexing API
    $indexScript = @"
const { google } = require('googleapis');
const key = require('$serviceJson'.replace(/\\\\/g, '/'));

async function indexUrls() {
    const jwtClient = new google.auth.JWT(
        key.client_email,
        null,
        key.private_key,
        ['https://www.googleapis.com/auth/indexing'],
        null
    );

    try {
        await jwtClient.authorize();
        const tokens = await jwtClient.getAccessToken();
        
        const urls = JSON.parse(process.argv[2]);
        let success = 0, fails = 0;

        for (const url of urls) {
            try {
                const response = await fetch('https://indexing.googleapis.com/v3/urlNotifications:publish', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + tokens.access_token
                    },
                    body: JSON.stringify({
                        url: url,
                        type: 'URL_UPDATED'
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    success++;
                    process.stdout.write('  ✅ Indexada: ' + url + '\\n');
                } else {
                    fails++;
                    process.stdout.write('  ⚠️  Falló: ' + url + ' — ' + (data.error?.message || 'error') + '\\n');
                }
            } catch (e) {
                fails++;
                process.stdout.write('  ❌ Error: ' + url + ' — ' + e.message + '\\n');
            }
        }
        process.stdout.write('\\n  📊 Resultado: ' + success + ' indexadas, ' + fails + ' fallidas\\n');
    } catch (e) {
        process.stderr.write('Error de autenticación: ' + e.message + '\\n');
        process.exit(1);
    }
}
indexUrls();
"@

    $scriptPath = "$env:TEMP\google-index-$(Get-Random).js"
    $urlsJson = $urls | ConvertTo-Json -Compress
    $indexScript | Out-File -FilePath $scriptPath -Encoding utf8

    try {
        $result = & node $scriptPath $urlsJson 2>&1
        $result | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }

        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error en Google Indexing API"
        } else {
            Write-OK "Indexación completada"
        }
    } finally {
        if (Test-Path $scriptPath) { Remove-Item $scriptPath -Force }
    }

    return $true
}

# ═══════════════════════════════════════════════════════════
# PASO 5: ARRANCAR SISTEMA
# ═══════════════════════════════════════════════════════════

function Step-StartSystem {
    Write-Step "[Opcional] Arrancando sistema local..."

    Write-Host "       Para arrancar el sistema:" -ForegroundColor DarkGray
    Write-Host "       " -NoNewline; Write-Host "uvicorn api_server:app --reload --port 8000" -ForegroundColor Green
    Write-Host "       " -NoNewline; Write-Host "Swagger: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "       " -NoNewline; Write-Host "DApp:    file:///$DAPP_DIR/index.html" -ForegroundColor Cyan
    Write-Host "       " -NoNewline
    Write-Host ""
    Write-Host "       ¿Arrancar ahora? (s/n): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "s" -or $response -eq "S") {
        Write-Host "       Arrancando API server en http://localhost:8000..." -ForegroundColor Green
        Start-Process powershell -ArgumentList "-NoExit -Command cd '$ROOT'; uvicorn api_server:app --reload --port 8000"
        Write-OK "API server iniciado en nueva ventana"
    } else {
        Write-Skip "Arranque manual"
    }
}

# ═══════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════

function Show-Help {
    Write-Host ""
    Write-Host "PROYECTO INFINITO — Deploy Automatizado" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "USO:" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1 -Mode full            Deploy completo"
    Write-Host "  .\deploy.ps1 -Mode content         Solo generar contenido"
    Write-Host "  .\deploy.ps1 -Mode netlify         Solo deploy a Netlify"
    Write-Host "  .\deploy.ps1 -Mode index            Solo Google Indexing"
    Write-Host "  .\deploy.ps1 -Mode start            Solo arrancar sistema"
    Write-Host "  .\deploy.ps1 -Help                  Mostrar esta ayuda"
    Write-Host ""
    Write-Host "VARIABLES DE ENTORNO:" -ForegroundColor Yellow
    Write-Host "  NETLIFY_AUTH_TOKEN     Token de API de Netlify"
    Write-Host "  NETLIFY_SITE_ID        ID del sitio en Netlify"
    Write-Host "  GOOGLE_SERVICE_JSON    Ruta al JSON de service account"
    Write-Host "  SITE_URL               URL del sitio (ej: https://misitio.com)"
    Write-Host ""
    Write-Host "REQUISITOS:" -ForegroundColor Yellow
    Write-Host "  netlify-cli:  npm install -g netlify-cli"
    Write-Host "  googleapis:   npm install googleapis"
    Write-Host "  Python 3.8+"
    Write-Host "  Node.js 18+"
    Write-Host ""
    exit 0
}


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if ($Mode -eq "help") { Show-Help }

Write-Banner
Write-Host "  Modo: $Mode" -ForegroundColor Cyan
Write-Host ""

switch ($Mode) {
    "full" {
        Step-GenerateContent
        $dir = Step-PrepareNetlify
        if ($dir) { $url = Step-NetlifyDeploy -DeployDir $dir }
        Step-GoogleIndexing -SiteUrl $url
        Step-StartSystem
    }
    "content" {
        Step-GenerateContent
    }
    "netlify" {
        $dir = Step-PrepareNetlify
        if ($dir) { Step-NetlifyDeploy -DeployDir $dir }
    }
    "index" {
        Step-GoogleIndexing
    }
    "start" {
        Step-StartSystem
    }
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅  DEPLOY COMPLETADO                        ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
