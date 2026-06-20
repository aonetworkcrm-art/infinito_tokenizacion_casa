#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║           PROYECTO INFINITO — CENTRO DE MANDO              ║
║  Sistema Integrado: DAO + Whale Watcher + SEO + Treasury   ║
╚══════════════════════════════════════════════════════════════╝

Autor: Romny (El Joker) + Buffy (Codebuff AI)
Version: 1.0.0 - Junio 2026
"""

import sys
import time
import os
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
from typing import Optional, Dict, List

getcontext().prec = 28
getcontext().rounding = ROUND_HALF_DOWN


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"


def c(text, color, bold=False):
    prefix = Colors.BOLD if bold else ""
    return prefix + color + str(text) + Colors.RESET


def section(title):
    line = c("=" * 58, Colors.CYAN, bold=True)
    print("\n" + line)
    print("  " + title)
    print(line)


def press_enter():
    input("\n  " + c("[Press Enter to continue]", Colors.DIM) + "  ")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# ─── MODULE IMPORTS ───
from modulos.infinito_dao import InfinitoDAO, BeneficiaryRole, Decimal as DAODec
from modulos.whale_watcher import WhaleWatcher
from modulos.seo_oracle import SEOOracle
from modulos.treasury_flow import TreasuryFlow, IncomeSource, ExpenseCategory, Decimal as TDec


# ============================================================
# 1. INFINITO DAO
# ============================================================
def demo_infinito_dao():
    section("INFINITO DAO - Tokenomica Familiar")
    dao = InfinitoDAO(property_value_usd=DAODec("103000"))

    s = dao.get_summary()
    print("\n" + c("Estado Inicial de la DAO:", Colors.YELLOW, bold=True))
    print("   Propiedad: " + c("$" + s["property_value_usd"] + " USD", Colors.GREEN))
    print("   Total Supply: " + c(s["total_supply"] + " TI", Colors.CYAN))
    print("   Pool de Herederos: " + c(s["pool_herederos_remaining"] + " TI", Colors.MAGENTA))

    print("\n" + c("Agregando miembros de la familia...", Colors.YELLOW, bold=True))
    dao.add_beneficiary("0xREYMOND_WALLET", "Reymond (Hermano)", BeneficiaryRole.HEREDERO)
    r = dao.distribute_from_pool("0xREYMOND_WALLET", DAODec("50000"),
                                  "Gestion y cuidado de la propiedad",
                                  caller_address="0xJOKER_MAIN")
    if r["success"]:
        print("   Reymond: " + c(r["amount_distributed"] + " TI", Colors.GREEN) + " distribuidos")

    dao.add_beneficiary("0xJOHAN_WALLET", "Joohan (Hermano menor)", BeneficiaryRole.HEREDERO)
    r = dao.distribute_from_pool("0xJOHAN_WALLET", DAODec("25000"),
                                  "Participacion en el sistema",
                                  caller_address="0xJOKER_MAIN")
    if r["success"]:
        print("   Joohan: " + c(r["amount_distributed"] + " TI", Colors.GREEN) + " distribuidos")

    print("\n" + c("Simulando contribucion: Reymond invierte en construccion...", Colors.YELLOW, bold=True))
    r = dao.apply_contribution("0xREYMOND_WALLET", DAODec("50000"),
                                dilution_factor=DAODec("1.2"),
                                description="Inversion en construccion de segundo nivel")
    if r["success"]:
        print("   Tokens ganados: " + c(r["tokens_earned"], Colors.GREEN) + " TI")
        print("   Nuevo valor propiedad: " + c("$" + r["new_property_value"], Colors.GREEN))

    print("\n" + c("Portafolios Familiares:", Colors.YELLOW, bold=True))
    for addr in ["0xJOKER_MAIN", "0xREYMOND_WALLET", "0xJOHAN_WALLET"]:
        p = dao.get_portfolio(addr)
        if p:
            pct = float(p["percentage"])
            pct_color = Colors.GREEN if pct > 10 else Colors.CYAN
            print("   " + c(p["name"], Colors.BOLD) + " (" + p["role"] + "):")
            print("      Tokens: " + c(p["tokens"], Colors.CYAN) + " TI  " +
                  str(c(p["percentage"] + "%", pct_color, bold=True)))

    print("\n" + c("Caza de Ballena ($500,000 USD):", Colors.YELLOW, bold=True))
    w = dao.calculate_whale_share(DAODec("500000"), DAODec("0.05"))
    print("   Profit bruto (2%): " + c("$" + w["gross_profit"], Colors.GREEN))
    print("   Profit neto: " + c("$" + w["net_profit"], Colors.GREEN, bold=True))

    print("\n" + c("Distribucion de Dividendos ($50,000 ingreso SEO):", Colors.YELLOW, bold=True))
    d = dao.distribute_dividends(DAODec("50000"), source="seo_content")
    print("   70% -> Tesoreria DAO: " + c("$" + d["dao_treasury"], Colors.GREEN))
    print("   20% -> Gas/Operaciones: " + c("$" + d["gas_treasury"], Colors.CYAN))
    print("   10% -> Airdrops: " + c("$" + d["airdrops_pool"], Colors.MAGENTA))

    press_enter()
    return dao


# ============================================================
# 2. WHALE WATCHER
# ============================================================
def demo_whale_watcher():
    section("WHALE WATCHER - Radar de Ballenas en Mempool")
    watcher = WhaleWatcher(network="polygon_amoy_testnet")

    print("\n" + c("Escaneando mempool de Polygon (simulacion)...", Colors.YELLOW, bold=True))
    whales = watcher.simulate_mempool_scan(count=150)

    print("\n" + c("Ballenas detectadas: " + str(len(whales)), Colors.CYAN, bold=True))
    print("-" * 50)

    whale_types = {}
    for w in whales:
        whale_types[w.category.value] = whale_types.get(w.category.value, 0) + 1

    for cat_name in sorted(whale_types.keys()):
        count = whale_types[cat_name]
        cat_sum = sum(w.value_usd for w in whales if w.category.value == cat_name)
        cat_float = float(cat_sum)
        emoji = {"juvenil": "  ", "azul": "  ", "dorada": "  ", "mitica": "   "}.get(cat_name, "  ")
        print("   " + cat_name.upper() + ": " + c(str(count), Colors.GREEN) +
              " ballenas  Total: " + c("${:,.2f}".format(cat_float), Colors.CYAN))

    print("\n" + c("Analizando oportunidades de Flash Loan...", Colors.YELLOW, bold=True))
    opps_found = 0
    for whale in whales:
        if whale.is_flash_loan_opportunity:
            opp = watcher.analyze_flash_loan_opportunity(whale)
            if opp and opp.is_profitable:
                opps_found += 1
                if opps_found <= 5:
                    risk_color = Colors.GREEN if opp.risk_score < 0.4 else (
                        Colors.YELLOW if opp.risk_score < 0.6 else Colors.RED)
                    print("\n   " + whale.category_emoji + " " + c(whale.value_formatted, Colors.CYAN))
                    print("      Profit: " + c("${:,.2f}".format(float(opp.net_profit_usd)), Colors.GREEN) +
                          "  ROI: " + c("{:.1f}%".format(float(opp.roi_percent)), Colors.GREEN, bold=True) +
                          "  Riesgo: " + c("{:.2f}".format(opp.risk_score), risk_color))

    summary = watcher.get_whale_summary()
    print("\n" + c("Resumen de Caza:", Colors.YELLOW, bold=True))
    print("   Detectadas: "   + c(str(summary["total_whales_detected"]), Colors.GREEN))
    print("   Rentables: "    + c(str(summary["profitable_opportunities"]), Colors.GREEN, bold=True))
    print("   Profit total: " + c("${:,.2f}".format(summary["total_profits_usd"]), Colors.GREEN, bold=True))

    press_enter()
    return watcher


# ============================================================
# 3. SEO ORACLE
# ============================================================
def demo_seo_oracle():
    section("SEO ORACLE - Investigacion de Nichos CPC")
    oracle = SEOOracle()

    print("\n" + c("TOP 5 Nichos por Rentabilidad:", Colors.YELLOW, bold=True))
    print("-" * 55)
    print("  #  Nicho" + " " * 32 + "CPC     Score")
    print("-" * 55)
    ranked = oracle.rank_niches_by_profitability()
    for i, n in enumerate(ranked[:5], 1):
        name = n["name"][:38]
        print("  " + c(str(i), Colors.GREEN, bold=True) + "  " +
              c(name, Colors.CYAN) + " " * (38 - len(name)) + " " +
              c("${:.0f}".format(n["cpc_avg"]), Colors.GREEN) + "  " +
              c(str(n["profitability_score"]), Colors.MAGENTA))

    print("\n" + c("Proyeccion de Ingresos (Top 3 Nichos):", Colors.YELLOW, bold=True))
    plan = oracle.create_content_plan(["personal-injury-law", "asset-recovery", "cybersecurity-compliance"])
    mvis = plan["total_monthly_visitors"]
    mrev = plan["total_monthly_revenue"]["avg"]
    arev = plan["total_yearly_revenue"]["avg"]
    print("   Visitantes/mes: " + c("{:,}".format(mvis), Colors.CYAN))
    print("   Ingreso mensual: " + c("${:,.2f}".format(mrev), Colors.GREEN, bold=True))
    print("   Ingreso anual: " + c("${:,.2f}".format(arev), Colors.GREEN, bold=True))

    print("\n" + c("Detalle por Nicho:", Colors.YELLOW, bold=True))
    for proj in plan["nodes"]:
        nc = proj["confidence"]
        cf = Colors.GREEN if nc in ("alta", "muy_alta") else Colors.YELLOW
        name = proj["niche"][:38]
        print("   " + c(name, Colors.CYAN) + "  " +
              "CPC: " + c("${:.0f}".format(proj["cpc_range"]["avg"]), Colors.GREEN) + "  " +
              c("${:>10,.2f}/mes".format(proj["monthly_revenue"]["avg"]), Colors.GREEN) + "  " +
              c(nc, cf))

    press_enter()
    return oracle


# ============================================================
# 4. TREASURY FLOW
# ============================================================
def demo_treasury_flow():
    section("TREASURY FLOW - Gestion de Tesoreria")
    treasury = TreasuryFlow()

    print("\n" + c("Simulando ingresos semanales...", Colors.YELLOW, bold=True))
    treasury.record_income(TDec("15500"), IncomeSource.SEO_CONTENT, "SEO Week 1")
    treasury.record_income(TDec("8500"), IncomeSource.SEO_CONTENT, "SEO Week 2")
    treasury.record_income(TDec("35000"), IncomeSource.MEV_WHALE, "Whale capture")
    treasury.record_income(TDec("12000"), IncomeSource.FLASH_LOAN, "Flash loan arbitrage")

    treasury.record_expense(TDec("1200"), ExpenseCategory.VPS_HOSTING, "AlexHost VPS")
    treasury.record_expense(TDec("850"), ExpenseCategory.GAS_FEE, "Gas fees Polygon")
    treasury.record_expense(TDec("600"), ExpenseCategory.BRIBES, "Flashbots bribes")
    treasury.record_expense(TDec("400"), ExpenseCategory.TOOLS, "SEO tools")

    bal = treasury.get_balance_sheet()
    print("\n" + c("Balance General:", Colors.YELLOW, bold=True))
    print("-" * 45)
    print("   Ingresos totales:     " + c("${:>8,.2f}".format(bal["total_income"]), Colors.GREEN, bold=True))
    print("   Gastos totales:       " + c("${:>8,.2f}".format(bal["total_expenses"]), Colors.RED))
    print("   Profit neto:          " + c("${:>8,.2f}".format(bal["net_profit"]), Colors.GREEN, bold=True))
    print("-" * 45)
    print("   Tesoreria DAO:        " + c("${:>8,.2f}".format(bal["dao_treasury"]), Colors.CYAN, bold=True))
    print("   Fondo de Gas:         " + c("${:>8,.2f}".format(bal["gas_treasury"]), Colors.MAGENTA))
    print("   Fondo de Emergencia:  " + c("${:>8,.2f}".format(bal["emergency_fund"]), Colors.YELLOW))

    print("\n" + c("Proyeccion de Crecimiento (12 meses):", Colors.YELLOW, bold=True))
    projs = treasury.project_growth(TDec("65000"), TDec("80000"), months=12)
    print("-" * 60)
    print("  Mes   Ingreso       Gastos    Treasury Acum.")
    print("-" * 60)
    for p in projs[:6]:
        print("  " + c(str(p["month"]), Colors.GREEN, bold=True).rjust(4) +
              "  " + c("${:>8,.2f}".format(p["income"]), Colors.CYAN) +
              "  " + c("${:>8,.2f}".format(p["expenses"]), Colors.RED) +
              "  " + c("${:>10,.2f}".format(p["cumulative_treasury"]), Colors.GREEN, bold=True))
    print("  " + c("...", Colors.DIM))
    p12 = projs[-1]
    print("  " + c("12", Colors.GREEN, bold=True).rjust(4) +
          "  " + c("${:>8,.2f}".format(p12["income"]), Colors.CYAN) +
          "  " + c("${:>8,.2f}".format(p12["expenses"]), Colors.RED) +
          "  " + c("${:>10,.2f}".format(p12["cumulative_treasury"]), Colors.GREEN, bold=True))
    print("-" * 60)

    press_enter()
    return treasury


# ============================================================
# DEMO INTEGRADA
# ============================================================
def demo_sistema_integrado():
    section("DEMO INTEGRADA - Flujo Completo del Sistema")
    print("\n" + c("Simulando un dia tipico de operacion:", Colors.DIM))

    # Paso 1: SEO
    print("\n06:00 AM - " + c("SEO Oracle despierta...", Colors.YELLOW))
    oracle = SEOOracle()
    plan = oracle.create_content_plan(["personal-injury-law", "asset-recovery"])
    seo_monthly = DAODec(str(plan["total_monthly_revenue"]["avg"])) / DAODec("30")
    print("   Ingreso SEO diario: " + c("${:,.2f}".format(float(seo_monthly)), Colors.GREEN, bold=True))

    # Paso 2: DAO
    print("\n08:00 AM - " + c("InfinitoDAO actualiza ledger...", Colors.YELLOW))
    dao = InfinitoDAO(property_value_usd=DAODec("103000"))
    dao.add_beneficiary("0xREYMOND_WALLET", "Reymond", BeneficiaryRole.HEREDERO)
    print("   Propiedad: " + c("$103,000 USD", Colors.GREEN))
    print("   Pool familiar: " + c("140,000 TI", Colors.CYAN))

    # Paso 3: MEV
    print("\n12:00 PM - " + c("Whale Watcher escanea mempool...", Colors.YELLOW))
    watcher = WhaleWatcher()
    whales = watcher.simulate_mempool_scan(count=200)

    profitable = 0
    total_mev = DAODec("0")
    for whale in whales:
        if whale.is_flash_loan_opportunity:
            opp = watcher.analyze_flash_loan_opportunity(whale)
            if opp and opp.is_profitable:
                profitable += 1
                total_mev += opp.net_profit_usd

    print("   Ballenas: " + c(str(len(whales)), Colors.GREEN))
    print("   Oportunidades: " + c(str(profitable), Colors.GREEN, bold=True))
    print("   Profit MEV: " + c("${:,.2f}".format(float(total_mev)), Colors.GREEN, bold=True))

    # Paso 4: Treasury
    print("\n06:00 PM - " + c("Treasury Flow distribuye ganancias...", Colors.YELLOW))
    treasury = TreasuryFlow()

    daily_total_val = float(seo_monthly) + float(total_mev)

    treasury.record_income(daily_seo, IncomeSource.SEO_CONTENT, "SEO diario")
    treasury.record_income(total_mev, IncomeSource.MEV_WHALE, "MEV diario")

    print("   Ingreso del dia: " + c("${:,.2f}".format(daily_total_val), Colors.GREEN, bold=True))
    print("      70% -> Tesoreria DAO: " + c("${:,.2f}".format(daily_total_val * 0.70), Colors.CYAN))
    print("      20% -> Gas:           " + c("${:,.2f}".format(daily_total_val * 0.20), Colors.MAGENTA))
    print("      10% -> Airdrops:      " + c("${:,.2f}".format(daily_total_val * 0.10), Colors.YELLOW))

    anual_total = daily_total_val * 365
    print("\n" + c("Proyeccion Anual:", Colors.YELLOW, bold=True))
    print("   " + c("${:>12,.2f}".format(anual_total), Colors.GREEN, bold=True) + " / anio")

    print("\n" + c("Sistema Integrado Operacional", Colors.GREEN, bold=True))
    press_enter()


# ============================================================
# MENU PRINCIPAL
# ============================================================
def show_header():
    clear_screen()
    print()
    print(c("=" * 58, Colors.CYAN, bold=True))
    print(c("  PROYECTO INFINITO - CENTRO DE MANDO", Colors.CYAN, bold=True))
    print(c("  DAO + Whale Watcher + SEO + Treasury", Colors.DIM))
    print(c("-" * 58, Colors.CYAN))
    print(c('  "Mientras todos dormian, yo construia el futuro"', Colors.DIM))
    print(c("=" * 58, Colors.CYAN, bold=True))


def menu_option(num, text, desc=""):
    print("  " + c("[" + str(num) + "]", Colors.GREEN, bold=True) + " " + c(text, Colors.CYAN))
    if desc:
        print("       " + c(desc, Colors.DIM))


def main_menu():
    while True:
        show_header()
        print("\n" + c("SELECCIONA UN MODULO:", Colors.YELLOW, bold=True))
        print()
        menu_option(1, "Infinito DAO", "Tokenomica familiar - Distribucion - Vesting")
        menu_option(2, "Whale Watcher", "Radar de ballenas - Flash loans - MEV")
        menu_option(3, "SEO Oracle", "Nichos CPC - Proyecciones - Plan de contenido")
        menu_option(4, "Treasury Flow", "Contabilidad - Flujo de caja - Proyecciones")
        print()
        menu_option(5, "DEMO INTEGRADA", "Flujo completo: SEO -> MEV -> DAO -> Treasury")
        print()
        menu_option(0, "Salir", "Cerrar el Centro de Mando")
        print()

        try:
            choice = input("  " + c(">", Colors.GREEN) + " Opcion: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n" + c("Hasta luego, Joker.", Colors.CYAN))
            sys.exit(0)

        if choice == "1":
            demo_infinito_dao()
        elif choice == "2":
            demo_whale_watcher()
        elif choice == "3":
            demo_seo_oracle()
        elif choice == "4":
            demo_treasury_flow()
        elif choice == "5":
            demo_sistema_integrado()
        elif choice == "0":
            print("\n" + c("Hasta luego, Joker. El sistema sigue corriendo.", Colors.CYAN, bold=True))
            print(c('  "La era del relajo se acabo. Empezamos a facturar."', Colors.DIM))
            print()
            break
        else:
            print("\n  " + c("Opcion invalida.", Colors.RED))
            press_enter()


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n" + c("Hasta luego, Joker.", Colors.CYAN))
        sys.exit(0)
