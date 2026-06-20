#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║    PROYECTO INFINITO — API REST · FastAPI Backend                  ║
║    Endpoints para: InfinitoDAO · WhaleWatcher · SEOOracle · Treasury ║
╚══════════════════════════════════════════════════════════════════════╝

Arranque:
    uvicorn api_server:app --reload --port 8000

Endpoints disponibles (con servidor corriendo):
    http://localhost:8000/docs    # Swagger UI
    http://localhost:8000/redoc   # ReDoc
"""

import sys
import os
import time
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
from enum import Enum

getcontext().prec = 28
getcontext().rounding = ROUND_HALF_DOWN

# Asegurar que podemos importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ─── Imports de los módulos ─────────────────────────────────────────
from modulos.infinito_dao import InfinitoDAO, BeneficiaryRole
from modulos.whale_watcher import WhaleWatcher
from modulos.seo_oracle import SEOOracle
from modulos.treasury_flow import TreasuryFlow, IncomeSource, ExpenseCategory


# ================================================================
# MODELOS PYDANTIC (Request/Response)
# ================================================================

# ─── DAO Models ───

class DistributeRequest(BaseModel):
    beneficiary_address: str
    amount_tokens: float = Field(gt=0, description="Cantidad de tokens TI")
    reason: str = ""
    caller_address: str = "0xJOKER_MAIN"


class ContributeRequest(BaseModel):
    beneficiary_address: str
    contribution_usd: float = Field(gt=0, description="Valor de la contribución en USD")
    dilution_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    description: str = ""


class DividendsRequest(BaseModel):
    total_profit_usd: float = Field(gt=0)
    source: str = "seo_content"


class AddMemberRequest(BaseModel):
    address: str
    name: str
    role: str = Field(pattern="^(padres_vitalicio|joker_arquitecto|heredero|inversor|miembro)$")


class VestingClaimRequest(BaseModel):
    address: str


# ─── Treasury Models ───

class IncomeRecordRequest(BaseModel):
    amount_usd: float = Field(gt=0)
    source: str = Field(pattern="^(seo_content|mev_whale|flash_loan|airdrop|contribution|staking_reward|other)$")
    description: str = ""


class ExpenseRecordRequest(BaseModel):
    amount_usd: float = Field(gt=0)
    category: str = Field(pattern="^(gas_fee|bribes|vps_hosting|tools|development|marketing|taxes|other)$")
    description: str = ""


class FamilyDistributeRequest(BaseModel):
    member_address: str
    percentage: float = Field(gt=0, le=1.0)
    reason: str = "airdop_distribution"


# ─── Whale Models ───

class ScanRequest(BaseModel):
    count: int = Field(default=100, ge=1, le=1000)


# ─── SEO Models ───

class ProjectionRequest(BaseModel):
    niche_id: str
    monthly_visitors: int = Field(default=5000, ge=100)
    ctr_pct: float = Field(default=2.0, ge=0.1, le=10.0)
    nodes_count: int = Field(default=3, ge=1)


class ContentPlanRequest(BaseModel):
    selected_niches: List[str]


# ================================================================
# ESTADO GLOBAL DE LA APLICACIÓN
# ================================================================

class AppState:
    def __init__(self):
        self.dao: InfinitoDAO = InfinitoDAO()
        self.watcher: WhaleWatcher = WhaleWatcher(network="polygon_amoy_testnet")
        self.oracle: SEOOracle = SEOOracle()
        self.treasury: TreasuryFlow = TreasuryFlow()
        self.start_time: float = time.time()


state = AppState()


# ================================================================
# LIFESPAN (startup/shutdown)
# ================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 60)
    print("  PROYECTO INFINITO — API REST iniciada")
    print("  Endpoints: /api/dao, /api/whales, /api/seo, /api/treasury")
    print(f"  Swagger: http://localhost:8000/docs")
    print("=" * 60)
    yield
    # Shutdown
    print("API detenida.")


# ================================================================
# CREAR APLICACIÓN FASTAPI
# ================================================================

app = FastAPI(
    title="PROYECTO INFINITO — API REST",
    description="""Backend oficial del Proyecto Infinito.
    Expone los 4 módulos principales como endpoints REST:
    - **InfinitoDAO**: Tokenómica familiar, distribución, vesting
    - **WhaleWatcher**: Radar de ballenas, flash loans, MEV
    - **SEOOracle**: Nichos de alto CPC, proyecciones de ingreso
    - **TreasuryFlow**: Contabilidad, flujo de caja, proyecciones
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permitir que la DApp web consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: restringir a tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def _str_to_role(role_str: str) -> BeneficiaryRole:
    mapping = {
        "padres_vitalicio": BeneficiaryRole.PADRES,
        "joker_arquitecto": BeneficiaryRole.JOKER,
        "heredero": BeneficiaryRole.HEREDERO,
        "inversor": BeneficiaryRole.INVERSOR,
        "miembro": BeneficiaryRole.MIEMBRO,
    }
    if role_str not in mapping:
        raise HTTPException(status_code=400, detail=f"Rol inválido: {role_str}")
    return mapping[role_str]


def _str_to_income_source(s: str) -> IncomeSource:
    mapping = {
        "seo_content": IncomeSource.SEO_CONTENT,
        "mev_whale": IncomeSource.MEV_WHALE,
        "flash_loan": IncomeSource.FLASH_LOAN,
        "airdrop": IncomeSource.AIRDROP,
        "contribution": IncomeSource.CONTRIBUTION,
        "staking_reward": IncomeSource.STAKING_REWARD,
        "other": IncomeSource.OTHER,
    }
    if s not in mapping:
        raise HTTPException(status_code=400, detail=f"Fuente de ingreso inválida: {s}")
    return mapping[s]


def _str_to_expense_category(s: str) -> ExpenseCategory:
    mapping = {
        "gas_fee": ExpenseCategory.GAS_FEE,
        "bribes": ExpenseCategory.BRIBES,
        "vps_hosting": ExpenseCategory.VPS_HOSTING,
        "tools": ExpenseCategory.TOOLS,
        "development": ExpenseCategory.DEVELOPMENT,
        "marketing": ExpenseCategory.MARKETING,
        "taxes": ExpenseCategory.TAXES,
        "other": ExpenseCategory.OTHER,
    }
    if s not in mapping:
        raise HTTPException(status_code=400, detail=f"Categoría inválida: {s}")
    return mapping[s]


# ================================================================
# ENDPOINTS: INFINITO DAO
# ================================================================

@app.get("/api/dao/summary", tags=["Infinito DAO"])
def dao_summary():
    """Resumen completo del estado de la DAO: propiedad, tokens, tesorerías."""
    try:
        return state.dao.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dao/portfolio/{address}", tags=["Infinito DAO"])
def dao_portfolio(address: str):
    """Portafolio de un miembro de la familia: tokens, vesting, contribuciones."""
    p = state.dao.get_portfolio(address)
    if not p:
        raise HTTPException(status_code=404, detail=f"Dirección no encontrada: {address}")
    return p


@app.get("/api/dao/members", tags=["Infinito DAO"])
def dao_members():
    """Lista de todos los miembros registrados en la DAO."""
    members = []
    for addr, b in state.dao.ledger.items():
        members.append(state.dao.get_portfolio(addr))
    return {"members": members, "count": len(members)}


@app.post("/api/dao/members", tags=["Infinito DAO"])
def dao_add_member(req: AddMemberRequest):
    """Agrega un nuevo miembro a la DAO."""
    role = _str_to_role(req.role)
    success = state.dao.add_beneficiary(
        address=req.address,
        name=req.name,
        role=role,
    )
    if not success:
        raise HTTPException(status_code=400, detail=f"Dirección ya existe: {req.address}")
    return {"success": True, "address": req.address, "name": req.name, "role": req.role}


@app.post("/api/dao/distribute", tags=["Infinito DAO"])
def dao_distribute(req: DistributeRequest):
    """Distribuye tokens del Pool de Herederos a un beneficiario."""
    result = state.dao.distribute_from_pool(
        beneficiary_address=req.beneficiary_address,
        amount_tokens=Decimal(str(req.amount_tokens)),
        reason=req.reason,
        caller_address=req.caller_address,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Error desconocido"))
    return result


@app.post("/api/dao/contribute", tags=["Infinito DAO"])
def dao_contribute(req: ContributeRequest):
    """Registra una contribución y calcula tokens ganados."""
    result = state.dao.apply_contribution(
        beneficiary_address=req.beneficiary_address,
        contribution_usd=Decimal(str(req.contribution_usd)),
        dilution_factor=Decimal(str(req.dilution_factor)),
        description=req.description,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Error desconocido"))
    return result


@app.post("/api/dao/dividends", tags=["Infinito DAO"])
def dao_dividends(req: DividendsRequest):
    """Distribuye ganancias entre tesorería DAO, gas y airdrops."""
    result = state.dao.distribute_dividends(
        total_profit_usd=Decimal(str(req.total_profit_usd)),
        source=req.source,
    )
    return result


@app.post("/api/dao/claim-vesting", tags=["Infinito DAO"])
def dao_claim_vesting(req: VestingClaimRequest):
    """Reclama tokens liberados por vesting (aplica al Joker)."""
    result = state.dao.claim_vested_tokens(address=req.address)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Error desconocido"))
    return result


@app.get("/api/dao/whale-share", tags=["Infinito DAO"])
def dao_whale_share(
    whale_value_usd: float = Query(..., description="Valor de la ballena en USD"),
    stake_pct: float = Query(0.05, description="Porcentaje del staker (0-1)"),
    profit_pct: float = Query(0.02, description="Porcentaje de profit esperado (0.001-0.1)"),
):
    """Calcula la participación en una caza de ballena."""
    result = state.dao.calculate_whale_share(
        whale_value_usd=Decimal(str(whale_value_usd)),
        stake_percentage=Decimal(str(stake_pct)),
        profit_pct=Decimal(str(profit_pct)),
    )
    # El módulo calculate_whale_share retorna dict sin clave "success" cuando es válido
    if not result.get("success", True):
        raise HTTPException(status_code=400, detail=result.get("error", "Error desconocido"))
    return result


# ================================================================
# ENDPOINTS: WHALE WATCHER
# ================================================================

@app.post("/api/whales/scan", tags=["Whale Watcher"])
def whales_scan(req: ScanRequest = ScanRequest()):
    """Escanea el mempool simulado y devuelve ballenas detectadas."""
    whales = state.watcher.simulate_mempool_scan(count=req.count)
    return {
        "count": len(whales),
        "network": "polygon_amoy_testnet (simulado)",
        "whales": [
            {
                "tx_hash": w.tx_hash,
                "value_usd": float(w.value_usd),
                "value_formatted": w.value_formatted,
                "category": w.category.value,
                "category_emoji": w.category_emoji,
                "is_flash_loan_opportunity": w.is_flash_loan_opportunity,
                "confidence": w.confidence_score,
            }
            for w in whales
        ],
    }


@app.get("/api/whales/summary", tags=["Whale Watcher"])
def whales_summary():
    """Resumen de ballenas detectadas y oportunidades."""
    return state.watcher.get_whale_summary()


@app.get("/api/whales/opportunities", tags=["Whale Watcher"])
def whales_opportunities(min_profit: float = Query(0, description="Profit mínimo en USD")):
    """Lista oportunidades de flash loan rentables."""
    profitable = [
        o for o in state.watcher.opportunities
        if o.is_profitable and float(o.net_profit_usd) >= min_profit
    ]
    return {
        "count": len(profitable),
        "opportunities": [
            {
                "whale_value": float(o.whale_tx.value_usd),
                "whale_category": o.whale_tx.category.value,
                "expected_profit": float(o.expected_profit_usd),
                "gas_cost": float(o.gas_cost_usd),
                "bribe": float(o.bribe_amount_usd),
                "net_profit": float(o.net_profit_usd),
                "roi_pct": float(o.roi_percent),
                "risk_score": o.risk_score,
                "confidence": o.confidence,
                "dex_path": o.dex_path,
            }
            for o in sorted(profitable, key=lambda x: x.net_profit_usd, reverse=True)
        ],
    }


# ================================================================
# ENDPOINTS: SEO ORACLE
# ================================================================

@app.get("/api/seo/niches", tags=["SEO Oracle"])
def seo_niches(min_cpc: float = Query(80, description="CPC mínimo para filtrar")):
    """Lista todos los nichos disponibles con sus métricas."""
    niches = state.oracle.get_top_niches(min_cpc=Decimal(str(min_cpc)))
    return {
        "count": len(niches),
        "niches": [
            {
                "id": n.id,
                "name": n.name,
                "category": n.category,
                "cpc_avg": float(n.cpc_avg),
                "cpc_range": n.cpc_range_str,
                "search_volume": n.search_volume,
                "difficulty": n.difficulty.value,
                "intent": n.intent,
                "evergreen_score": n.evergreen_score,
                "language": n.language,
                "description": n.description,
                "profitability_score": float(n.profitability_score),
                "keywords": n.keywords,
            }
            for n in niches
        ],
    }


@app.get("/api/seo/ranking", tags=["SEO Oracle"])
def seo_ranking():
    """Ranking de nichos por rentabilidad proyectada."""
    return {"ranking": state.oracle.rank_niches_by_profitability()}


@app.post("/api/seo/projection", tags=["SEO Oracle"])
def seo_projection(req: ProjectionRequest):
    """Proyección de ingresos para un nicho específico."""
    result = state.oracle.calculate_yield_projection(
        niche_id=req.niche_id,
        monthly_visitors=req.monthly_visitors,
        ctr_pct=Decimal(str(req.ctr_pct)),
        nodes_count=req.nodes_count,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Nicho no encontrado: {req.niche_id}")
    return result


@app.post("/api/seo/content-plan", tags=["SEO Oracle"])
def seo_content_plan(req: ContentPlanRequest):
    """Plan de contenido completo con proyecciones para nichos seleccionados."""
    plan = state.oracle.create_content_plan(selected_niches=req.selected_niches)
    return plan


@app.get("/api/seo/evergreen-multiplier/{years}", tags=["SEO Oracle"])
def seo_evergreen(years: int):
    """Calcula el multiplicador de ingresos para contenido evergreen."""
    if years < 1 or years > 50:
        raise HTTPException(status_code=400, detail="years must be between 1 and 50")
    mult = state.oracle.get_evergreen_multiplier(years)
    return {"years": years, "multiplier": float(mult)}


# ================================================================
# ENDPOINTS: TREASURY FLOW
# ================================================================

@app.get("/api/treasury/balance", tags=["Treasury"])
def treasury_balance():
    """Balance general: ingresos, gastos, tesorerías."""
    return state.treasury.get_balance_sheet()


@app.post("/api/treasury/income", tags=["Treasury"])
def treasury_income(req: IncomeRecordRequest):
    """Registra un ingreso y lo distribuye automáticamente."""
    source = _str_to_income_source(req.source)
    tx = state.treasury.record_income(
        amount_usd=Decimal(str(req.amount_usd)),
        source=source,
        description=req.description,
    )
    return {
        "success": True,
        "transaction_id": tx.id,
        "amount_usd": float(tx.amount_usd),
        "source": tx.source.value if tx.source else None,
        "timestamp": tx.timestamp,
        "balance": state.treasury.get_balance_sheet(),
    }


@app.post("/api/treasury/expense", tags=["Treasury"])
def treasury_expense(req: ExpenseRecordRequest):
    """Registra un gasto del sistema."""
    category = _str_to_expense_category(req.category)
    tx = state.treasury.record_expense(
        amount_usd=Decimal(str(req.amount_usd)),
        category=category,
        description=req.description,
    )
    return {
        "success": True,
        "transaction_id": tx.id,
        "amount_usd": float(tx.amount_usd),
        "category": tx.expense_category.value if tx.expense_category else None,
        "timestamp": tx.timestamp,
        "balance": state.treasury.get_balance_sheet(),
    }


@app.get("/api/treasury/projection", tags=["Treasury"])
def treasury_projection(
    monthly_seo: float = Query(65000, description="Ingreso mensual SEO esperado"),
    monthly_mev: float = Query(80000, description="Ingreso mensual MEV esperado"),
    months: int = Query(12, ge=1, le=60, description="Meses a proyectar"),
):
    """Proyección de crecimiento de tesorería mes a mes."""
    projs = state.treasury.project_growth(
        monthly_seo_revenue=Decimal(str(monthly_seo)),
        monthly_mev_revenue=Decimal(str(monthly_mev)),
        months=months,
    )
    return {"projections": projs, "total_months": len(projs)}


@app.get("/api/treasury/weekly", tags=["Treasury"])
def treasury_weekly():
    """Reporte semanal de flujo de caja."""
    report = state.treasury.get_weekly_report()
    return {
        "week_number": report.week_number,
        "total_income": float(report.total_income),
        "total_expenses": float(report.total_expenses),
        "net_profit": float(report.net_profit),
        "income_by_source": report.income_by_source,
        "expenses_by_category": report.expenses_by_category,
        "dao_treasury": float(report.dao_treasury_balance),
        "gas_treasury": float(report.gas_treasury_balance),
        "distributed_to_family": float(report.distribution_to_family),
    }


@app.get("/api/treasury/profitability", tags=["Treasury"])
def treasury_profitability(days: int = Query(30, ge=1, le=365)):
    """Métricas de rentabilidad para un período."""
    return state.treasury.get_profitability_metrics(days=days)


@app.post("/api/treasury/distribute-family", tags=["Treasury"])
def treasury_distribute_family(req: FamilyDistributeRequest):
    """Distribuye ganancias a un miembro de la familia."""
    result = state.treasury.distribute_to_family(
        member_address=req.member_address,
        percentage=Decimal(str(req.percentage)),
        reason=req.reason,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Error desconocido"))
    return result


# ================================================================
# ENDPOINT: SYSTEM STATUS
# ================================================================

@app.get("/", tags=["System"])
def root():
    """Estado del sistema."""
    uptime = time.time() - state.start_time
    return {
        "project": "PROYECTO INFINITO",
        "version": "1.0.0",
        "status": "operational",
        "uptime_seconds": round(uptime),
        "uptime_formatted": f"{int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m",
        "modules": {
            "dao": "InfinitoDAO — Tokenómica",
            "whales": "WhaleWatcher — Radar MEV",
            "seo": "SEOOracle — Nichos CPC",
            "treasury": "TreasuryFlow — Contabilidad",
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
    }


@app.get("/api/reset", tags=["System"])
def api_reset():
    """Resetea el estado de todos los módulos (vuelve a estado inicial)."""
    global state
    state = AppState()
    return {
        "success": True,
        "message": "Todos los módulos han sido reinicializados",
        "timestamp": time.time(),
    }


# ================================================================
# MAIN (ejecución directa)
# ================================================================

if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor del Proyecto Infinito...")
    print("Documentación: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
