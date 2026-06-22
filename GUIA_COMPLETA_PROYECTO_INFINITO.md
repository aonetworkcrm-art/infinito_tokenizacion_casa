# 🚀 GUÍA COMPLETA DEL PROYECTO INFINITO

> **Versión**: 1.0 · Junio 2026 · ⚠️ DOCUMENTACIÓN LEGACY  
> **📘 DOCUMENTACIÓN ACTUALIZADA**: `README.md` (incluye OpenRouter IA, Monetag, Posts Públicos)  
> **Arquitecto**: Romny (El Joker)  
> **IA Asistente**: Buffy (Codebuff AI)  
> **Repositorio**: https://github.com/aonetworkcrm-art/infinito_tokenizacion_casa  
> **DApp en vivo**: https://proyecto-infinito.vercel.app

---

## 📑 ÍNDICE

1. [VISIÓN GENERAL](#-visión-general)
2. [ESTRUCTURA DEL PROYECTO](#-estructura-del-proyecto)
3. [DASHBOARD — DApp Familiar](#-dashboard--dapp-familiar)
4. [WHALE RADAR — Mempool en Tiempo Real](#-whale-radar--mempool-en-tiempo-real)
5. [CONTENT LOCKER — Staking](#-content-locker--staking)
6. [GOBERNANZA — Votación Familiar](#-gobernanza--votación-familiar)
7. [SHADOW SILO — SEO + Auto-Pilot](#-shadow-silo--seo--auto-pilot)
8. [WALLET — Conexión MetaMask](#-wallet--conexión-metamask)
9. [HEALTH TRACKER — Salud Familiar](#-health-tracker--salud-familiar)
10. [TOKENÓMICA — InfinitoToken (TI)](#-tokenómica--infinitotoken-ti)
11. [CONTRATOS INTELIGENTES](#-contratos-inteligentes)
12. [MÓDULOS PYTHON (Backend)](#-módulos-python-backend)
13. [API SERVER — FastAPI](#-api-server--fastapi)
14. [TESTS](#-tests)
15. [HOSTING GRATIS (sin VPS)](#-hosting-gratis-sin-vps)
16. [COMANDOS ÚTILES](#-comandos-útiles)

---

## 🏠 VISIÓN GENERAL

Transformar una **propiedad familiar** en Villa Faro, Santo Domingo Este, RD en un **nodo de extracción de valor descentralizado** que integra:

| Pilar | Descripción |
|-------|-------------|
| 🏠 **Tokenización Inmobiliaria** | Casa familiar como activo digital programable (1,000,000 TI) |
| 🐋 **Caza de Ballenas (MEV)** | Extracción de valor del mempool de Polygon |
| 📈 **SEO de Alto CPC** | Granja de contenido nicho con CPC de $60-$300+ |
| 🔗 **DApp Familiar** | Dashboard donde cada miembro ve su participación crecer |
| 💰 **Content Locker** | Sistema de staking para desbloquear contenido premium |
| 🌑 **Shadow Silo** | Generación automática de contenido SEO con Auto-Pilot |

### Ubicación del Activo Base
- **Dirección**: Calle Activo 20-30, Casa #23, Capotillo, Villa Faro, Santo Domingo Este, RD
- **Valor**: $103,000 USD (~6,000,000 DOP)
- **Ocupantes**: Ramón "Monchy" (padre), Nicolasa María (madre), Reymond, Romny, Aisaack, Eseck Abiel, Osock, Judelkis

---

## 📁 ESTRUCTURA DEL PROYECTO

```
proyecto-infinito/
│
├── GUIA_COMPLETA_PROYECTO_INFINITO.md  ← ESTE ARCHIVO
├── proyecto_infinito.md                ← Matriz Maestra original
│
├── dapp/                               ← ★ INTERFAZ WEB (DApp)
│   ├── index.html                      ←   Único HTML con TODO (6 tabs + editor + health tracker)
│   └── abi/                            ←   ABIs del contrato inteligente
│       ├── InfinitoToken.abi.json      ←     ABI completo (13KB)
│       └── InfinitoToken.json          ←     ABI + bytecode (46KB)
│
├── modulos/                            ← ★ CÓDIGO PYTHON (Backend Core)
│   ├── infinito_dao.py                 ←   Tokenómica, distribución, vesting
│   ├── seo_oracle.py                   ←   Nichos de alto CPC, proyecciones
│   ├── whale_watcher.py                ←   Detección de ballenas MEV
│   └── treasury_flow.py               ←   Contabilidad y flujo de tesorería
│
├── api_server.py                       ← ★ API REST (FastAPI — puente Backend ↔ DApp)
│
├── contratos/                          ← ★ SMART CONTRACTS (Solidity)
│   ├── InfinitoToken.sol               ←   ERC-20: TI Token con tax + roles + permits
│   └── DividendDistributor.sol         ←   Distribución automática de dividendos
│
├── blockchain/                         ← ★ HARDHAT (Compilación + Deploy)
│   ├── hardhat.config.js               ←   Config para Polygon Amoy (Chain ID 80002)
│   ├── contracts/InfinitoToken.sol     ←   Copia del contrato para compilar
│   ├── scripts/deploy.js               ←   Script de deploy
│   ├── artifacts/                      ←   ABIs compilados
│   └── .env.example                    ←   Template para variables de entorno
│
├── generar_contenido.py                ← Generador de artículos HTML SEO
│
├── contenido/                          ← Artículos HTML generados
│   ├── guia-abogados-accidentes.html
│   ├── calculadora-indemnizacion-accidente.html
│   ├── accidente-camion-guia-legal.html
│   ├── necesito-abogado-despues-accidente.html
│   └── abogado-accidentes-motocicleta.html
│
├── tests/                              ← ★ TESTS (Playwright + Pytest)
│   ├── test_dapp_frontend.spec.js      ←   44 tests funcionales (DApp)
│   ├── test_visual_regression.spec.js  ←   33 tests de regresión visual
│   ├── test_infinito_dao.py            ←   Tests del DAO
│   ├── test_seo_oracle.py             ←   Tests del SEO Oracle
│   ├── test_whale_watcher.py          ←   Tests del Whale Watcher
│   ├── test_treasury_flow.py          ←   Tests del Treasury Flow
│   ├── test_api_server.py             ←   Tests del API server
│   └── snapshots/chromium/            ←   Imágenes de referencia (33 PNGs)
│
├── documentos/                         ← Documentación
│   ├── reporte_yield.md
│   ├── whitepaper_familiar.md
│   └── whitepaper_tecnico.md
│
├── investigacion/                      ← Investigación de mercado SEO
│
├── package.json                        ← Node.js (Playwright)
├── playwright.config.js                ← Config de Playwright
├── requirements.txt                    ← Python dependencies
└── index.html                          ← Redirección a dapp/index.html
```

---

## 📊 DASHBOARD — DApp Familiar

### 🎯 Propósito
Centro de mando familiar donde se visualiza el estado completo del ecosistema.

### 🖥️ Tabs (6 en total)

| # | Tab | ID | Descripción |
|---|-----|----|-------------|
| 1 | 📊 DASHBOARD | `tab-dashboard` | Visión general del proyecto |
| 2 | 🐋 WHALE RADAR | `tab-whales` | Mempool de Polygon en tiempo real |
| 3 | 🔒 CONTENT LOCKER | `tab-staking` | Staking de tokens TI |
| 4 | 🗳️ GOBERNANZA | `tab-governance` | Votación familiar (PIPs) |
| 5 | 🦊 WALLET | `tab-wallet` | Conexión MetaMask |
| 6 | 🌑 SHADOW SILO | `tab-shadow` | SEO + Auto-Pilot |

### 📋 Secciones del Dashboard

| Sección | Descripción |
|---------|-------------|
| **Header** | Título, stats animados (tokens, ballenas, valor), badge de estado |
| **Panorama General** | Propiedad ($103K), Supply Total (1M TI), Tesorería DAO, Ingreso Mensual |
| **Distribución de Tokens** | 51% Padres, 35% Joker, 14% Pool — con barras de progreso |
| **Miembros de la Familia** | 9 miembros con sus roles y tokens asignados |
| **Wallets Familiares** | Inputs para direcciones de cada miembro (localStorage) |
| **Salud de la Familia** | Cards de estado de salud + Tracker de inyecciones + Síntomas |
| **CT — Control Eléctrico** | Deuda RD$4,000, 9 bombillos, meta LED, ahorro 30% |
| **Proyección de Crecimiento** | Tabla Mes 1-3, Mes 4-6, Año 1, Año 2 |

### 👥 Miembros de la Familia (9)

| Miembro | Rol | Tokens |
|---------|-----|--------|
| 👑 Ramón & Nicolasa | Dueños Vitalicios | 510,000 TI (51%) |
| 🃏 Romny (Joker) | Arquitecto del Sistema | 350,000 TI (35%) |
| 👤 Reymond | Hermano Mediano | — |
| 👤 Joohan | Hermano Menor | — |
| 👤 Charina | Hermana (Padre) | — |
| 👤 Aisaack | Hijo · 14 años | — |
| 👤 Eseck Abiel | Hijo | — |
| 👤 Osock | Hijo | — |
| 👤 Judelkis | Sobrina / Prima | — |

### 💉 Health Tracker — Inyecciones de Mamá

| Funcionalidad | Descripción |
|---------------|-------------|
| **💉 Marcar Inyección** | Botón que registra timestamp de cada inyección |
| **📊 Streak** | Días consecutivos con inyección |
| **⏱️ Horas desde última** | Cuenta regresiva |
| **📋 Total inyecciones** | Contador acumulado |
| **🗑️ Clear** | Borrar historial |
| **📋 Síntomas** | Registrar síntoma con severidad (Leve/Moderado/Grave) |
| **💾 Persistencia** | Todo se guarda en localStorage |

---

## 🐋 WHALE RADAR — Mempool en Tiempo Real

### 🎯 Propósito
Simula un mempool de Polygon mostrando transacciones de alto valor con gas, direcciones from/to, y confianza.

### 📊 Stats del Mempool

| Stat | ID | Descripción |
|------|----|-------------|
| Valor Total | `mp-total-val` | Suma de todas las TX en el mempool |
| TX Pendientes | `mp-tx-count` | Número de transacciones |
| Gas Promedio | `mp-gas-avg` | Gas promedio en Gwei |
| Ballenas >$100K | `mp-whale-count` | TX que superan $100K |

### 🐋 Categorías de Ballenas

| Tipo | Rango | Emoji | Color |
|------|-------|-------|-------|
| Juvenil | $5K - $50K | 🐟 | Verde (lo) |
| Azul | $50K - $250K | 🐋 | Naranja (md) |
| Dorada | $250K - $1M | ✨ | Rojo (hi) |
| Mítica | $1M - $5M | 💎 | Rojo intenso (mega) |

### 🔄 Ciclo de Vida
- **Inicial**: 18 TX generadas
- **Cada 8s**: Se añaden 2-4 TX nuevas y se eliminan las más viejas (máx 25)
- **Top 3**: Las ballenas más grandes aparecen en el ranking 🥇🥈🥉

### 🚨 Alertas Automáticas
- **Ballena Mítica (>$1M)**: 🚨 Alerta roja con valor
- **Ballena Dorada (>$250K)**: 🐋 Alerta naranja
- **Normal**: ✅ Monitoreando

### 💎 Flash Loans (Bloqueados por Staking)
- Ballena Dorada: $420,690 · Profit Est.: $8,413 · ROI: 323%
- Ballena Azul: $184,500 · Profit Est.: $4,153 · ROI: 265%
- Se desbloquean al stakeaer tokens TI en el Content Locker

---

## 🔒 CONTENT LOCKER — Staking

### 🎯 Propósito
Sistema de staking donde los usuarios bloquean tokens TI para desbloquear contenido premium.

### 📊 Stats
| Campo | ID | Descripción |
|-------|----|-------------|
| Tus Tokens | `stake-balance` | Balance disponible (default 100,000 TI) |
| Stakados | `stake-locked` | Tokens bloqueados |
| Dividendos | `stake-dividends` | Ganancias pendientes |

### 🎯 Contenido Premium por Staking

| Requisito | Contenido |
|-----------|-----------|
| 1,000 TI | Whale Tracker Premium |
| 5,000 TI | SEO Yield Dashboard |
| 10,000 TI | Votación de Gobernanza |
| 25,000 TI | Airdrops Prioritarios |

---

## 🗳️ GOBERNANZA — Votación Familiar

### 🎯 Propósito
Sistema de votación para decisiones importantes del DAO familiar.

### ⚖️ Poder de Voto

| Rol | % | Descripción |
|-----|---|-------------|
| 👑 Padres | 51% | Poder de veto vitalicio |
| 🃏 Joker | 35% | Control de protocolo |
| 🌊 Pool Familiar | 14% | Voto ponderado por tokens |

### 📋 Propuestas (PIPs)

| Propuesta | Estado | Descripción |
|-----------|--------|-------------|
| **PIP-1** | ✅ En Votación (72%) | Inversión en construcción de segundo nivel ($50K) |
| **PIP-2** | ⏳ Pendiente | Distribución de airdrops del trimestre ($25K) |
| **PIP-3** | ✅ En Votación (89%) | Compra de VPS AlexHost ($1,200/año) |

### 📊 Historial
- PIP-0: Creación del DAO ✅ 100%
- PIP-0: Distribución Inicial ✅ 100%
- PIP-0: Configuración Whale Watcher ✅ 100%

---

## 🌑 SHADOW SILO — SEO + Auto-Pilot

### 🎯 Propósito
Generación de contenido SEO de alto CPC con persistencia local y Auto-Pilot programable.

### 📊 Stats del Shadow Silo

| Stat | ID | Seed | Descripción |
|------|----|------|-------------|
| Posts Activos | `shadow-posts` | 5 | Nodos evergreen desplegados |
| Palabras Clave | `shadow-keywords` | 12 | CPC ≥ $100 |
| Tráfico Estimado | `shadow-traffic` | 7,000 | Visitas/mes |
| Yield Estimado | `shadow-yield` | $8,190.00 | CPC × CTR × Tráfico |

### 🔍 10 Nichos de Alto CPC (SEO Oracle)

| # | Nicho | CPC Promedio | Categoría | Demanda |
|---|-------|:-----------:|-----------|:-------:|
| 1 | Abogados de Accidentes | **$220** | Servicios Legales | Muy Alta |
| 2 | Ciberseguridad y Compliance | **$170** | Tecnología B2B | Media |
| 3 | Mesotelioma y Enf. Laborales | **$150** | Servicios Legales | Baja |
| 4 | Recuperación de Activos | **$125** | Servicios Legales | Media |
| 5 | Ciberseguridad Empresarial | **$120** | Tecnología B2B | Alta |
| 6 | Centros de Rehabilitación | **$120** | Salud | Muy Alta |
| 7 | Seguros de Auto Alto Riesgo | **$105** | Seguros | Muy Alta |
| 8 | MBA y Posgrados Online | **$100** | Educación | Alta |
| 9 | Seguros de Vida Adultos Mayores | **$95** | Seguros | Muy Alta |
| 10 | Inversiones y Gestión DeFi | **$85** | Finanzas | Media |

### 🤖 Auto-Pilot

| Función | Descripción |
|---------|-------------|
| **Toggle On/Off** | Botón que activa/pausa el Auto-Pilot |
| **Intervalo** | Slider de 1 a 72 horas (default 24h) |
| **Barra de progreso** | % de avance hasta próximo post |
| **Countdown** | "Próximo post: Xh Ym" |
| **Estrategias** | Aleatorio · Mayor CPC · Rotativo (sin repetir) |
| **Log** | Historial de eventos con timestamp |
| **Generar Ahora** | Forzar generación inmediata |
| **Persistencia** | Se reanuda al recargar (localStorage) |
| **Notificaciones** | Alertas cuando se genera un post |

### ✏️ Editor Inline

| Campo | Descripción |
|-------|-------------|
| **Título** | Editable |
| **Nicho/Categoría** | Editable |
| **CPC ($)** | Editable (recalcula yield) |
| **Tráfico/mes** | Editable (recalcula yield) |
| **Yield ($)** | Readonly (autocalculado) |
| **Keywords** | Textarea libre |
| **Meta Description** | Textarea con max 160 chars |
| **Contenido** | Textarea para el cuerpo del artículo |
| **FAQs** | Dinámicas: agregar/eliminar preguntas + respuestas |

#### 📤 Publicación HTML
Al hacer clic en "Publicar & Descargar HTML", genera un archivo `.html` completo con:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  - Meta tags SEO (title, description, keywords)
  - Open Graph (og:title, og:description, og:locale)
  - Twitter Card
  - FAQ Schema JSON-LD
  - Article Schema JSON-LD
  - Canonical URL
  - Estilo Matrix (fondo oscuro, verde neón, tipografía monospace)
</head>
<body>
  - Header con badge del proyecto
  - Contenido del post
  - CTA (Call to Action)
  - FAQ Section
  - Footer
</body>
</html>
```

---

## 🦊 WALLET — Conexión MetaMask

### 🎯 Propósito
Conectar MetaMask para ver balances reales del contrato InfinitoToken en Polygon Amoy.

### 📊 Estado

| Campo | ID | Descripción |
|-------|----|-------------|
| Estado | `wallet-status` | Conectado / No conectado / Error |
| Dirección | `wallet-address` | 0x... (abreviada) |
| Red | `wallet-network` | Polygon Amoy Testnet |
| Balance MATIC | `wallet-matic` | Balance nativo |
| Tokens TI | `wallet-ti` | Balance del contrato |
| Dividendos | `wallet-divs` | Pendientes de reclamar |

### 🔧 Configuración de Wallets Familiares
- Inputs para cada miembro (9 personas)
- Se guardan en localStorage
- Botón "Guardar Wallets"

### ⚙️ Detección de Red
- Chain ID 80002 = Polygon Amoy Testnet
- Escucha cambios de cuenta (`accountsChanged`)
- Escucha cambios de red (`chainChanged`)

---

## 🪙 TOKENÓMICA — InfinitoToken (TI)

### 📊 Distribución Inicial

| Categoría | % | Tokens | Rol |
|-----------|---|--------|-----|
| 👑 **Padres (Vitalicio)** | 51% | 510,000 TI | Soberanía y Protección |
| 🃏 **Joker (Arquitecto)** | 35% | 350,000 TI | Gobernanza y Ejecución |
| 🌊 **Pool de Herederos** | 14% | 140,000 TI | Incentivos familiares |

### 📐 Fórmula de Dilución por Aporte

```
NewShare(i) = CurrentShare(i) + (Contribution(i) / TotalAssetValue) × DilutionFactor
```

### 🔒 Vesting del Joker
- **Cliff**: 180 días (6 meses)
- **Total**: 730 días (2 años)
- **Liberación**: 35% inmediato + 65% en vesting
- **Reclamo**: Cada 1 día después del cliff

### 💰 Distribución de Ganancias (Treasury Split)

| Destino | % |
|---------|---|
| Tesorería DAO | 70% |
| Gas y Operaciones | 20% |
| Airdrops a Stakers | 10% |

---

## 📜 CONTRATOS INTELIGENTES

### 1. InfinitoToken.sol

| Propiedad | Valor |
|-----------|-------|
| **Nombre** | Infinito Token |
| **Símbolo** | TI |
| **Decimales** | 18 |
| **Supply** | 1,000,000 TI |
| **Red** | Polygon Amoy (Chain ID: 80002) |
| **Framework** | OpenZeppelin v5 |
| **Versión Solidity** | ^0.8.24 |

#### Roles
| Rol | Permisos |
|-----|----------|
| `DEFAULT_ADMIN_ROLE` | Admin general (Joker) |
| `MINTER_ROLE` | Mintear nuevos tokens (Joker) |
| `PAUSER_ROLE` | Pausar/reanudar contrato (Joker) |
| `TAX_MANAGER_ROLE` | Gestionar tax (Joker) |
| `TREASURY_ROLE` | Gestionar tesorería (Treasury) |

#### Funciones Principales
| Función | Descripción |
|---------|-------------|
| `mintTokens(to, amount)` | Mintea tokens (solo MINTER) |
| `burnFromPool(amount)` | Quema tokens del pool |
| `updateTreasury(newAddr)` | Cambia tesorería |
| `updateTax(newBps)` | Cambia % de tax (máx 5%) |
| `toggleTax()` | Activa/desactiva tax |
| `setTaxExemption(addr, bool)` | Exime del tax |
| `pause()` / `unpause()` | Pausar/reanudar |
| `domainSeparator()` | Para gasless approvals |

#### Tax de Transferencia
- **Default**: 2% (200 basis points)
- **Máximo**: 5% (500 basis points)
- **Exentos**: Tesorería, Joker
- **Destino**: Tesorería DAO

### 2. DividendDistributor.sol

| Propiedad | Valor |
|-----------|-------|
| **Mecanismo** | Pull-based (holders reclaman) |
| **Distribución** | 70% Tesorería · 10% Airdrops · 20% Ops |

#### Funciones Principales
| Función | Descripción |
|---------|-------------|
| `depositNative()` | Depositar MATIC como dividendos |
| `depositERC20(token, amount)` | Depositar ERC-20 (USDC) |
| `claimDividends(holder)` | Reclamar dividendos |
| `getClaimableDividends(holder)` | Consultar dividendos pendientes |

---

## 🧠 MÓDULOS PYTHON (Backend)

### 1. InfinitoDAO (`modulos/infinito_dao.py`)

Motor de tokenómica con precisión decimal absoluta (28 decimales).

| Función | Descripción |
|---------|-------------|
| `add_beneficiary(addr, name, role)` | Agrega miembro |
| `distribute_from_pool(addr, amount, reason)` | Distribuye tokens del pool |
| `apply_contribution(addr, usd, factor)` | Aplica contribución y calcula tokens |
| `claim_vested_tokens(addr)` | Reclama vesting del Joker |
| `distribute_dividends(profit, source)` | Distribuye ganancias |
| `calculate_whale_share(valor, stake, profit%)` | Calcula participación en caza |

### 2. SEOOracle (`modulos/seo_oracle.py`)

Investigador de nichos de alto CPC con proyecciones de yield.

| Función | Descripción |
|---------|-------------|
| `get_top_niches(min_cpc)` | Filtra nichos por CPC mínimo |
| `rank_niches_by_profitability()` | Ranking por rentabilidad |
| `calculate_yield_projection(id, visitors, ctr, nodes)` | Proyección de ingresos |
| `create_content_plan(niches[])` | Plan de contenido completo |
| `get_evergreen_multiplier(years)` | Multiplicador por años |

### 3. WhaleWatcher (`modulos/whale_watcher.py`)

Detector de ballenas en el mempool con análisis de flash loans.

| Función | Descripción |
|---------|-------------|
| `detect_whale(hash, from, to, value, gas)` | Clasifica transacción |
| `analyze_flash_loan_opportunity(whale)` | Analiza oportunidad de arbitraje |
| `simulate_mempool_scan(count)` | Simula escaneo del mempool |
| `get_whale_summary()` | Resumen de ballenas detectadas |

### 4. TreasuryFlow (`modulos/treasury_flow.py`)

Sistema de contabilidad y gestión de flujo de tesorería.

| Función | Descripción |
|---------|-------------|
| `record_income(amount, source)` | Registra ingreso y distribuye automáticamente |
| `record_expense(amount, category)` | Registra gasto |
| `distribute_to_family(addr, %)` | Distribuye a miembros |
| `get_balance_sheet()` | Balance general |
| `get_weekly_report()` | Reporte semanal |
| `project_growth(seo, mev, months)` | Proyección de crecimiento |

---

## 🌐 API SERVER — FastAPI

### 📡 Endpoints

El API corre en `http://localhost:8000` y expone estos endpoints:

#### InfinitoDAO (`/api/dao/`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/summary` | GET | Resumen del DAO |
| `/portfolio/{address}` | GET | Portafolio de un miembro |
| `/members` | GET/POST | Lista / Agrega miembros |
| `/distribute` | POST | Distribuye tokens del pool |
| `/contribute` | POST | Registra contribución |
| `/dividends` | POST | Distribuye ganancias |
| `/claim-vesting` | POST | Reclama vesting |
| `/whale-share` | GET | Calcula share de ballena |

#### Whale Watcher (`/api/whales/`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/scan` | POST | Escanea mempool simulado |
| `/summary` | GET | Resumen de ballenas |
| `/opportunities` | GET | Oportunidades de flash loan |

#### SEO Oracle (`/api/seo/`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/niches` | GET | Lista nichos disponibles |
| `/ranking` | GET | Ranking por rentabilidad |
| `/projection` | POST | Proyección de ingresos |
| `/content-plan` | POST | Plan de contenido |
| `/evergreen-multiplier/{years}` | GET | Multiplicador evergreen |

#### Treasury (`/api/treasury/`)
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/balance` | GET | Balance general |
| `/income` | POST | Registrar ingreso |
| `/expense` | POST | Registrar gasto |
| `/projection` | GET | Proyección de crecimiento |
| `/weekly` | GET | Reporte semanal |
| `/profitability` | GET | Métricas de rentabilidad |

#### Sistema
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Estado del sistema |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc |

---

## 🧪 TESTS

### 📊 Resumen

| Suite | Tipo | Cantidad | Herramienta |
|-------|------|:---------:|:-----------:|
| DApp Frontend | Funcional | **44** | Playwright |
| Regresión Visual | Snapshots | **33** | Playwright |
| SEO Oracle | Unitario | ~40 | Pytest |
| Infinito DAO | Unitario | ~30 | Pytest |
| Whale Watcher | Unitario | ~20 | Pytest |
| Treasury Flow | Unitario | ~20 | Pytest |
| **TOTAL** | | **~187** | |

### ▶️ Cómo Ejecutar

```bash
# Todos los tests funcionales de la DApp
cd /c/proyecto-infinito
npx playwright test tests/test_dapp_frontend.spec.js --reporter=list

# Regresión visual (con regeneración de snapshots)
npx playwright test tests/test_visual_regression.spec.js --update-snapshots --reporter=list

# Tests Python
pytest tests/test_seo_oracle.py -v
pytest tests/test_infinito_dao.py -v
pytest tests/test_whale_watcher.py -v
pytest tests/test_treasury_flow.py -v
pytest tests/test_api_server.py -v
```

### 📸 Snapshots de Regresión Visual (33)

Los snapshots se guardan en `tests/snapshots/chromium/` y cubren:

| Grupo | Cantidad | Descripción |
|-------|:--------:|-------------|
| Dashboard | 6 | Completo, tarjetas, tabla, miembros, header, responsive |
| Whale Radar | 4 | Completo, stats, feed, flash loans |
| Staking | 5 | Completo, tarjetas, premium, después de stakear |
| Gobernanza | 7 | Completo, poder voto, propuestas, votación, historial |
| Wallet | 2 | Completo, botón conectar |
| Tabs | 2 | Navegación entre tabs |
| Shadow Silo | 1 | Tab completo |
| Responsive | 3 | Tablet (768px), Mobile (375px) |
| Flujo Completo | 1 | Stake → desbloquear → votar |
| Flow | 1 | Dashboard inicial |
| **TOTAL** | **33** | |

---

## 🆓 HOSTING GRATIS (sin VPS)

### Opciones para hostear el backend (FastAPI)

| Plataforma | ¿24/7 Gratis? | ¿Se Duerme? | ¿Requiere Tarjeta? | Ideal para... |
|------------|:----------:|:----------:|:----------------:|:--------------|
| **Render** | ✅ 750h/mes | 😴 15 min inactivo | ❌ No | APIs simples con cold start aceptable |
| **Vercel** | ✅ Sí | 🚀 Serverless | ❌ No | APIs con bajo tráfico, sin WebSockets |
| **PythonAnywhere** | ✅ Sí | ❌ No (always-on) | ❌ No | Apps Python pequeñas, sin APIs externas |
| **Cloudflare Tunnel + PC en casa** | ✅ 100% | ❌ No | ❌ No | La mejor opción si tienes una PC encendida |
| **Google Cloud Run** | ✅ Capa gratis | 😴 Scale-to-zero | ✅ Sí requiere | APIs profesionales |
| **Railway** | ❌ Retirado | — | — | Ya no tiene free tier |
| **Fly.io** | ❌ Retirado | — | — | Ya no acepta nuevos gratis |

### Recomendación

| Tu situación | Mejor opción |
|-------------|--------------|
| No tienes tarjeta de crédito | **Render** (acepta dormir 30s al despertar) |
| Quieres 100% gratis sin límites | **Cloudflare Tunnel** en tu PC |
| Solo para el Shadow Silo (llamadas esporádicas) | **Vercel** serverless |

---

## 🌐 CLOUDFLARE TUNNEL — Exponer Backend sin VPS

### 🎯 Propósito
Exponer el API Server (FastAPI) local a internet **sin VPS, sin abrir puertos, sin IP pública**. Cloudflare crea un túnel HTTPS seguro desde tu PC a su red CDN global.

### 📦 Requisitos
- Windows 10/11
- Una cuenta gratuita de Cloudflare (https://cloudflare.com)
- Cloudflared instalado (ya está: `winget install Cloudflare.cloudflared`)

### 🚀 Cómo Usar

#### 1. Primera vez (autenticación)
Ejecuta el script de inicio. La primera vez abrirá el navegador para que te loguees en Cloudflare:

```bash
cd /c/proyecto-infinito
scripts/iniciar_tunnel.bat
```

#### 2. Obtener la URL del túnel
Cuando el túnel esté corriendo, busca en la terminal una línea como:
```
INFERIRE... https://infinito-api-nombre-aleatorio.trycloudflare.com
```

#### 3. Configurar la DApp
En el Shadow Silo de la DApp:
1. Haz clic en "🌐 API Endpoint"
2. Pega la URL del túnel (ej: `https://infinito-api-nombre-aleatorio.trycloudflare.com`)
3. Haz clic en "💾 Guardar"
4. Ahora "Generar Siguiente Post" usará el túnel primero

### 🔄 Orden de Conexión (Auto-Fallback)

```
1. http://localhost:8000 (API local — cuando estás desarrollando)
2. https://tu-tunnel.trycloudflare.com (si configuraste URL del túnel)
3. Datos locales embebidos (SHADOW_NICHES — siempre funciona, sin internet)
```

### 📁 Archivos

| Archivo | Descripción |
|---------|-------------|
| `scripts/iniciar_tunnel.bat` | Script principal: inicia API + Tunnel |
| `scripts/config_tunnel.yml` | Template de configuración del túnel |

### ⚙️ El Script Hace Todo Esto:

```
1. Verifica si cloudflared está autenticado
   - Si NO: abre navegador para login
2. Verifica si el túnel 'infinito-api' existe
   - Si NO: lo crea automáticamente
3. Crea la configuración del túnel (→ localhost:8000)
4. Instala uvicorn si no está
5. Inicia el FastAPI Server (ventana separada)
6. Inicia el Cloudflare Tunnel
7. Muestra la URL pública en la terminal
8. Al cerrar, detiene todo
```

### 💡 Notas
- **Sin tarjeta de crédito**: Cloudflare Tunnel es completamente gratis
- **Sin puertos abiertos**: No necesitas configurar el router
- **HTTPS automático**: Cloudflare maneja los certificados SSL
- **24/7**: El túnel funciona mientras tu PC esté encendida y el script corriendo

### ❌ Para Detener
Solo cierra la ventana del túnel (Ctrl+C). El script apagará el API automáticamente.

---

## 🛠️ COMANDOS ÚTILES

### DApp

```bash
# Abrir la DApp en el navegador
start "" "file:///c/proyecto-infinito/dapp/index.html"

# O abrir desde GitHub Pages
# https://aonetworkcrm-art.github.io/infinito_tokenizacion_casa/
```

### Tests

```bash
# Tests funcionales (44)
cd /c/proyecto-infinito
npx playwright test tests/test_dapp_frontend.spec.js --reporter=list

# Regresión visual (33)
npx playwright test tests/test_visual_regression.spec.js --update-snapshots --reporter=list

# Tests Python
pytest tests/ -v
```

### API Server

```bash
# Iniciar el servidor
cd /c/proyecto-infinito
uvicorn api_server:app --reload --port 8000

# Abrir documentación
# http://localhost:8000/docs
```

### Blockchain (Hardhat)

```bash
# Compilar contrato
cd /c/proyecto-infinito/blockchain
npx hardhat compile

# Desplegar en Polygon Amoy (requiere PRIVATE_KEY en .env)
npx hardhat run scripts/deploy.js --network amoy
```

### Generar Contenido SEO

```bash
# Generar 5 artículos principales
cd /c/proyecto-infinito
python generar_contenido.py

# Generar todos los artículos
python generar_contenido.py --all

# Ver lista de artículos disponibles
python generar_contenido.py --list
```

### Git

```bash
# Ver estado
cd /c/proyecto-infinito
git status

# Hacer commit
git add -A
git commit -m "mensaje"
git push origin master
```

---

## 🔗 ENLACES IMPORTANTES

| Recurso | URL |
|---------|-----|
| **DApp en vivo** | https://aonetworkcrm-art.github.io/infinito_tokenizacion_casa/ |
| **Repositorio GitHub** | https://github.com/aonetworkcrm-art/infinito_tokenizacion_casa |
| **Polygon Amoy Explorer** | https://amoy.polygonscan.com |
| **Polygon Amoy Faucet** | https://faucet.polygon.technology |
| **MetaMask** | https://metamask.io |
| **Codebuff AI** | https://codebuff.com |

---

> *"Mientras todos dormían, yo estaba en el techo construyendo el futuro."*  
> — El Joker, Junio 2026
