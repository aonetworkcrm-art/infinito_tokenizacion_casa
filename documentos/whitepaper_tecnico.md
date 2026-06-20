# ⚙️ PROYECTO INFINITO — WHITEPAPER TÉCNICO

> **Versión Técnica** — Para desarrolladores e integradores
> *Arquitectura del sistema, smart contracts, y stack tecnológico*
> Junio 2026

---

## 1. ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────┐
│                   CAPA 1: BLOCKCHAIN                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │ InfinitoToken│  │DividendDist  │  │ WhaleRadar   ││
│  │   ERC-20     │  │  butor.sol   │  │  Oracle.sol  ││
│  └──────────────┘  └──────────────┘  └──────────────┘│
├─────────────────────────────────────────────────────┤
│                   CAPA 2: BACKEND                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │ InfinitoDAO  │  │ TreasuryFlow │  │  SEO Oracle  ││
│  │   Python     │  │   Python     │  │   Python     ││
│  └──────────────┘  └──────────────┘  └──────────────┘│
├─────────────────────────────────────────────────────┤
│                   CAPA 3: FRONTEND                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │   DApp Web   │  │ Whale Radar  │  │ Gov Dashboard││
│  │  (HTML/React)│  │  Dashboard   │  │              ││
│  └──────────────┘  └──────────────┘  └──────────────┘│
└─────────────────────────────────────────────────────┘
```

## 2. SMART CONTRACTS (SOLIDITY)

### InfinitoToken.sol (ERC-20)
- **Network**: Polygon (Mainnet) / Amoy (Testnet)
- **Standard**: ERC-20 con extensiones de burn, mint (solo DAO), y tax
- **Supply**: 1,000,000 TI (fijo)
- **Tax**: 2% en transfers → va a treasury de la DAO

### DividendDistributor.sol
- **Función**: Distribución automática de ganancias
- **Trigger**: Llamada por el backend cuando se genera ingreso
- **Split**: 70% treasury / 20% gas / 10% airdrops
- **Whitelist**: Solo direcciones aprobadas (miembros familiares)

### WhaleRadarOracle.sol
- **Función**: Registro on-chain de ballenas detectadas
- **Data**: Hash de tx, valor, timestamp, categoría
- **Uso**: Verificación pública de la actividad del sistema

## 3. BACKEND (PYTHON)

### Módulos Existentes

| Módulo | Archivo | Función | Dependencias |
|--------|---------|---------|--------------|
| **InfinitoDAO** | `modulos/infinito_dao.py` | Tokenómica, distribución, aportes | web3.py, decimal |
| **WhaleWatcher** | `modulos/whale_watcher.py` | Detección MEV, flash loans | web3.py |
| **SEOOracle** | `modulos/seo_oracle.py` | Investigación de nichos CPC | requests, bs4 |
| **TreasuryFlow** | `modulos/treasury_flow.py` | Contabilidad, flujo de caja | stdlib |

### Infraestructura

```yaml
VPS: AlexHost (o similar)
  CPU: 4+ cores
  RAM: 8GB+
  Storage: 100GB SSD
  OS: Ubuntu 24.04 LTS

Servicios:
  - Python 3.12+ runtime
  - Redis (para cola de tareas)
  - PostgreSQL (para persistencia)
  - Nginx (reverse proxy)
```

## 4. CAPAS DE SEGURIDAD

### Smart Contract
- ✅ OpenZeppelin audited contracts base
- ✅ Multi-sig wallet (Gnosis Safe) para treasury
- ✅ Time-locks para distribuciones grandes
- ✅ Emergency pause para el Joker

### Backend
- ✅ API keys rotativas
- ✅ Rate limiting por IP
- ✅ Logs cifrados
- ✅ Auto-backup a IPFS

### DApp
- ✅ Conexión solo lectura para usuarios
- ✅ Transacciones firmadas con MetaMask
- ✅ No almacenamiento de private keys

## 5. DEPLOYMENT PIPELINE

```
Desarrollo (Testnet):
  ┌─────────┐    ┌──────────┐    ┌───────────┐
  │ Polygon │    │  Free    │    │  GitHub    │
  │  Amoy   │───▶│  Faucet  │───▶│   Pages   │
  └─────────┘    └──────────┘    └───────────┘

Producción (Mainnet):
  ┌─────────┐    ┌──────────┐    ┌───────────┐
  │ Polygon │    │   VPS    │    │  Custom   │
  │ Mainnet │───▶│ AlexHost │───▶│   Domain  │
  └─────────┘    └──────────┘    └───────────┘
```

## 6. INTEGRACIÓN CON PROYECTOS EXISTENTES

| Proyecto | Integración |
|----------|-------------|
| **proyecto-link-seo/** | Dashboard central + token-personal.html + DApp |
| **shadow_silo/** | Motor de contenido automatizado (FastAPI → React) |
| **refineria_ramon/** | OSINT avanzado para detección de ballenas y oportunidades |
| **freebuf prueba 2/** | Sistema de propuestas publicitarias (monetización) |

---

> *Documento técnico v1.0 — Junio 2026*
> *Próxima actualización: Post-deploy en mainnet*
