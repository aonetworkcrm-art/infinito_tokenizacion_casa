#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════
#  PROYECTO INFINITO — DEPLOY AUTOMATIZADO (Bash)
#  Generar contenido → Deploy Netlify → Indexar Google → Run
# ══════════════════════════════════════════════════════════════════
#
# USO:
#   ./deploy.sh                    # Deploy completo
#   ./deploy.sh full               # Ídem
#   ./deploy.sh content            # Solo generar contenido
#   ./deploy.sh netlify            # Solo deploy a Netlify
#   ./deploy.sh index              # Solo Google Indexing API
#   ./deploy.sh start              # Solo arrancar sistema
#   ./deploy.sh help               # Mostrar ayuda
#
# REQUISITOS:
#   Netlify CLI: npm install -g netlify-cli
#   googleapis:  npm install googleapis
#   python3, node, curl
#
# CONFIGURACIÓN (variables de entorno):
#   NETLIFY_AUTH_TOKEN   # Token de API de Netlify
#   NETLIFY_SITE_ID      # ID del sitio en Netlify
#   GOOGLE_SERVICE_JSON  # Ruta al JSON de service account
#   SITE_URL             # URL del sitio (ej: https://misitio.com)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CONTENT_DIR="$ROOT/contenido"
DAPP_DIR="$ROOT/dapp"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Colores
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DARK='\033[2m'
NC='\033[0m'

banner() {
    clear 2>/dev/null || true
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║  PROYECTO INFINITO — Deploy Automatizado        ║"
    echo "║  $TIMESTAMP"
    echo "╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

step() { echo -e "  ${YELLOW}→ $1${NC}"; }
ok()   { echo -e "  ${GREEN}✅ $1${NC}"; }
err()  { echo -e "  ${RED}❌ $1${NC}"; }
skip() { echo -e "  ${DARK}⏭️  $1${NC}"; }

check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        err "$1 no instalado. Instálalo primero."
        return 1
    fi
    return 0
}

# ══════════════════════════════════════════════════════════
# PASO 1: GENERAR CONTENIDO
# ══════════════════════════════════════════════════════════

generate_content() {
    step "[1/4] Generando contenido SEO..."
    if [ ! -f "$ROOT/generar_contenido.py" ]; then
        err "No se encontró generar_contenido.py"
        return 1
    fi
    python3 "$ROOT/generar_contenido.py" --all 2>&1
    local count=$(find "$CONTENT_DIR" -name "*.html" 2>/dev/null | wc -l)
    ok "$count artículos HTML generados en $CONTENT_DIR"
}

# ══════════════════════════════════════════════════════════
# PASO 2: PREPARAR ARCHIVOS PARA NETLIFY
# ══════════════════════════════════════════════════════════

prepare_netlify() {
    step "[2/4] Preparando archivos para Netlify..."
    local netlify_dir="$ROOT/netlify-deploy"
    rm -rf "$netlify_dir"
    mkdir -p "$netlify_dir/contenido"

    # Copiar DApp
    if [ -f "$DAPP_DIR/index.html" ]; then
        cp "$DAPP_DIR/index.html" "$netlify_dir/index.html"
        ok "DApp copiada"
    fi

    # Copiar contenido
    if [ -d "$CONTENT_DIR" ]; then
        cp "$CONTENT_DIR"/*.html "$netlify_dir/contenido/" 2>/dev/null || true
        local art_count=$(ls "$netlify_dir/contenido"/*.html 2>/dev/null | wc -l)
        ok "$art_count artículos de contenido copiados"
    fi

    # _redirects
    cat > "$netlify_dir/_redirects" <<'REDIR'
/*    /index.html   200
/contenido/*    /contenido/:splat   200
REDIR

    # netlify.toml
    cat > "$netlify_dir/netlify.toml" <<'TOML'
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
TOML

    local total=$(find "$netlify_dir" -type f | wc -l)
    ok "Archivos preparados en $netlify_dir ($total archivos)"
    echo "$netlify_dir"
}

# ══════════════════════════════════════════════════════════
# PASO 3: DEPLOY A NETLIFY
# ══════════════════════════════════════════════════════════

netlify_deploy() {
    local deploy_dir="$1"
    step "[3/4] Desplegando a Netlify..."
    check_cmd netlify || { echo "  Alternativa: https://app.netlify.com/drop" ; return 1; }

    if [ -z "${NETLIFY_AUTH_TOKEN:-}" ]; then
        err "NETLIFY_AUTH_TOKEN no configurado"
        return 1
    fi

    if [ -n "${NETLIFY_SITE_ID:-}" ]; then
        netlify deploy --prod --dir="$deploy_dir" --auth="$NETLIFY_AUTH_TOKEN" --site="$NETLIFY_SITE_ID" 2>&1
    else
        netlify deploy --prod --dir="$deploy_dir" --auth="$NETLIFY_AUTH_TOKEN" 2>&1
    fi

    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        err "Error en deploy Netlify"
        return 1
    fi

    ok "Deploy exitoso"
}

# ══════════════════════════════════════════════════════════
# PASO 4: GOOGLE INDEXING API
# ══════════════════════════════════════════════════════════

google_indexing() {
    local site_url="${1:-${SITE_URL:-}}"
    step "[4/4] Google Indexing API..."

    if [ -z "${GOOGLE_SERVICE_JSON:-}" ]; then
        err "GOOGLE_SERVICE_JSON no configurado"
        echo "  Para configurar:"
        echo "  1. Crea un service account en Google Cloud Console"
        echo "  2. Descarga el JSON"
        echo "  3. Añade el correo como propietario en Search Console"
        return 1
    fi

    if [ -z "$site_url" ]; then
        err "SITE_URL no configurado"
        return 1
    fi

    if [ ! -f "$GOOGLE_SERVICE_JSON" ]; then
        err "No se encontró: $GOOGLE_SERVICE_JSON"
        return 1
    fi

    check_cmd node || return 1

    # Build URL list
    local urls=("$site_url/")
    if [ -d "$CONTENT_DIR" ]; then
        for f in "$CONTENT_DIR"/*.html; do
            local slug=$(basename "$f" .html)
            urls+=("$site_url/contenido/$slug")
        done
    fi

    echo "       URLs a indexar: ${#urls[@]}"

    # Build JSON array
    local urls_json="["
    local first=true
    for u in "${urls[@]}"; do
        if [ "$first" = true ]; then first=false; else urls_json+=","; fi
        urls_json+="\"$u\""
    done
    urls_json+="]"

    # Create temp Node.js script
    local script_path=$(mktemp /tmp/google-index-XXXX.js)
    cat > "$script_path" <<'NODESCRIPT'
const { google } = require('googleapis');
const key = require(process.argv[2]);

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
        const urls = JSON.parse(process.argv[3]);
        let success = 0, fails = 0;
        for (const url of urls) {
            try {
                const resp = await fetch('https://indexing.googleapis.com/v3/urlNotifications:publish', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + tokens.access_token
                    },
                    body: JSON.stringify({ url: url, type: 'URL_UPDATED' })
                });
                const data = await resp.json();
                if (resp.ok) { success++; process.stdout.write('  ✅ Indexada: ' + url + '\n'); }
                else { fails++; process.stdout.write('  ⚠️  Falló: ' + url + ' — ' + (data.error?.message || 'error') + '\n'); }
            } catch(e) { fails++; process.stdout.write('  ❌ Error: ' + url + ' — ' + e.message + '\n'); }
        }
        process.stdout.write('\n  📊 Resultado: ' + success + ' indexadas, ' + fails + ' fallidas\n');
    } catch(e) { process.stderr.write('Error: ' + e.message + '\n'); process.exit(1); }
}
indexUrls();
NODESCRIPT

    node "$script_path" "$GOOGLE_SERVICE_JSON" "$urls_json" 2>&1
    local rc=$?
    rm -f "$script_path"

    if [ $rc -eq 0 ]; then ok "Indexación completada"; else err "Error en indexación"; fi
}

# ══════════════════════════════════════════════════════════
# PASO 5: ARRANCAR SISTEMA
# ══════════════════════════════════════════════════════════

start_system() {
    step "[Opcional] Arrancando sistema local..."
    echo -e "       ${GREEN}uvicorn api_server:app --reload --port 8000${NC}"
    echo -e "       ${CYAN}Swagger: http://localhost:8000/docs${NC}"
    echo -e "       ${CYAN}DApp:    file://$DAPP_DIR/index.html${NC}"
    echo ""
    read -p "       ¿Arrancar ahora? (s/n): " -n 1 resp
    echo ""
    if [[ "$resp" == "s" || "$resp" == "S" ]]; then
        echo "       Arrancando API server..."
        (cd "$ROOT" && uvicorn api_server:app --reload --port 8000) &
        ok "API server iniciado en http://localhost:8000"
    else
        skip "Arranque manual"
    fi
}

# ══════════════════════════════════════════════════════════
# HELP
# ══════════════════════════════════════════════════════════

show_help() {
    echo ""
    echo -e "${CYAN}PROYECTO INFINITO — Deploy Automatizado${NC}"
    echo ""
    echo -e "${YELLOW}USO:${NC}"
    echo "  ./deploy.sh full              Deploy completo"
    echo "  ./deploy.sh content           Solo generar contenido"
    echo "  ./deploy.sh netlify           Solo deploy a Netlify"
    echo "  ./deploy.sh index             Solo Google Indexing"
    echo "  ./deploy.sh start             Solo arrancar sistema"
    echo "  ./deploy.sh help              Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}VARIABLES DE ENTORNO:${NC}"
    echo "  NETLIFY_AUTH_TOKEN     Token de API de Netlify"
    echo "  NETLIFY_SITE_ID        ID del sitio en Netlify"
    echo "  GOOGLE_SERVICE_JSON    Ruta al JSON de service account"
    echo "  SITE_URL               URL del sitio"
    echo ""
    echo -e "${YELLOW}REQUISITOS:${NC}"
    echo "  netlify-cli:  npm install -g netlify-cli"
    echo "  googleapis:   npm install googleapis"
    echo "  python3, node, curl"
    echo ""
    exit 0
}

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

MODE="${1:-full}"

case "$MODE" in
    help|-h|--help) show_help ;;
    full)
        banner
        echo -e "  ${CYAN}Modo: full${NC}\n"
        generate_content
        dir=$(prepare_netlify)
        if [ -n "$dir" ]; then netlify_deploy "$dir"; fi
        google_indexing
        start_system
        ;;
    content)
        banner; echo -e "  ${CYAN}Modo: content${NC}\n"
        generate_content
        ;;
    netlify)
        banner; echo -e "  ${CYAN}Modo: netlify${NC}\n"
        dir=$(prepare_netlify)
        if [ -n "$dir" ]; then netlify_deploy "$dir"; fi
        ;;
    index)
        banner; echo -e "  ${CYAN}Modo: index${NC}\n"
        google_indexing
        ;;
    start)
        banner; echo -e "  ${CYAN}Modo: start${NC}\n"
        start_system
        ;;
    *)
        echo -e "${RED}Modo inválido: $MODE${NC}"
        show_help
        ;;
esac

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅  DEPLOY COMPLETADO                        ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
