"""
SEO ORACLE — High-CPC Niche Research & Yield Projection Engine
================================================================
Escanea, analiza y predice el rendimiento de contenido en nichos
de alto CPC para el Proyecto Infinito.

Autor: Romny (El Joker) + Buffy (Codebuff AI)
Versión: 1.0.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
from enum import Enum
import json
import math

getcontext().prec = 28
getcontext().rounding = ROUND_HALF_DOWN


class TrafficDifficulty(Enum):
    """Nivel de dificultad para posicionar tráfico."""
    MUY_BAJA = "muy_baja"
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    MUY_ALTA = "muy_alta"


@dataclass
class HighCPCNiche:
    """Representa un nicho de alto CPC con sus métricas."""
    id: str
    name: str
    category: str
    keywords: List[str]
    cpc_min: Decimal
    cpc_max: Decimal
    cpc_avg: Decimal
    search_volume: str  # "bajo", "medio", "alto", "muy_alto"
    difficulty: TrafficDifficulty
    intent: str  # "informativa", "transaccional", "comercial", "navegacional"
    evergreen_score: int  # 1-10
    language: str  # "es", "en", "ambos"
    description: str = ""
    example_urls: List[str] = field(default_factory=list)

    @property
    def cpc_range_str(self) -> str:
        return f"${self.cpc_min} - ${self.cpc_max}"

    @property
    def profitability_score(self) -> Decimal:
        """Score combinado de rentabilidad (CPC × demanda × evergreen)."""
        volume_map = {'bajo': 2, 'medio': 5, 'alto': 8, 'muy_alto': 10}
        vol_score = Decimal(str(volume_map.get(self.search_volume, 5)))
        return self.cpc_avg * vol_score * Decimal(str(self.evergreen_score))


@dataclass
class ContentNode:
    """Representa un nodo de contenido (post/página)."""
    niche: str
    title: str
    target_keywords: List[str]
    monthly_visitors: int
    ctr_pct: Decimal  # Click-through rate (1-10%)
    cpc_expected: Decimal
    monthly_revenue_est: Decimal



class SEOOracle:
    """
    Motor de inteligencia para investigación y proyección de nichos.
    """

    # Base de datos de nichos pre-cargada con investigación de mercado
    NICHES_DB = [
        HighCPCNiche(
            id="asset-recovery",
            name="Recuperación de Activos Financieros",
            category="Servicios Legales",
            keywords=[
                "asset recovery services for families",
                "recuperar fondos estafados",
                "tracing crypto legal",
                "fund recovery specialist",
                "stolen asset recovery",
                "recuperación de activos financieros",
            ],
            cpc_min=Decimal('100'),
            cpc_max=Decimal('150'),
            cpc_avg=Decimal('125'),
            search_volume="medio",
            difficulty=TrafficDifficulty.ALTA,
            intent="transaccional",
            evergreen_score=9,
            language="ambos",
            description="Personas que perdieron dinero en estafas financieras o cripto "
                        "y buscan servicios profesionales para recuperarlo. Alta urgencia.",
        ),
        HighCPCNiche(
            id="personal-injury-law",
            name="Abogados de Accidentes (Personal Injury)",
            category="Servicios Legales",
            keywords=[
                "truck collision accident attorney",
                "car accident lawyer near me",
                "personal injury attorney",
                "abogado de accidentes de tránsito",
                "mesothelioma law firm assistance",
                "busco abogado para accidente",
            ],
            cpc_min=Decimal('150'),
            cpc_max=Decimal('300'),
            cpc_avg=Decimal('220'),
            search_volume="muy_alto",
            difficulty=TrafficDifficulty.MUY_ALTA,
            intent="transaccional",
            evergreen_score=10,
            language="ambos",
            description="El nicho más caro en publicidad digital. Personas que sufrieron "
                        "accidentes buscan representación legal inmediata.",
        ),
        HighCPCNiche(
            id="cybersecurity-compliance",
            name="Ciberseguridad y Compliance Empresarial",
            category="Tecnología B2B",
            keywords=[
                "SOC 2 compliance certification service",
                "enterprise cybersecurity solutions",
                "managed security service provider",
                "cybersecurity audit firm",
                "penetration testing services",
            ],
            cpc_min=Decimal('140'),
            cpc_max=Decimal('200'),
            cpc_avg=Decimal('170'),
            search_volume="medio",
            difficulty=TrafficDifficulty.ALTA,
            intent="comercial",
            evergreen_score=9,
            language="en",
            description="Empresas que necesitan certificaciones de seguridad y compliance. "
                        "Alto valor por cliente (B2B).",
        ),
        HighCPCNiche(
            id="drug-rehab",
            name="Centros de Rehabilitación",
            category="Salud",
            keywords=[
                "inpatient drug rehab centers",
                "alcohol rehabilitation near me",
                "centro de rehabilitación de drogas",
                "luxury rehab facility",
                "detox center",
            ],
            cpc_min=Decimal('80'),
            cpc_max=Decimal('150'),
            cpc_avg=Decimal('120'),
            search_volume="muy_alto",
            difficulty=TrafficDifficulty.MUY_ALTA,
            intent="transaccional",
            evergreen_score=10,
            language="ambos",
            description="Personas y familias buscando ayuda para adicciones. "
                        "Cada paciente vale miles de dólares para el anunciante.",
        ),
        HighCPCNiche(
            id="life-insurance-seniors",
            name="Seguros de Vida para Adultos Mayores",
            category="Seguros",
            keywords=[
                "life insurance policy for seniors over 70",
                "best life insurance for seniors",
                "final expense insurance",
                "seguro de vida para adultos mayores",
                "burial insurance",
            ],
            cpc_min=Decimal('70'),
            cpc_max=Decimal('120'),
            cpc_avg=Decimal('95'),
            search_volume="muy_alto",
            difficulty=TrafficDifficulty.ALTA,
            intent="comercial",
            evergreen_score=9,
            language="ambos",
            description="Adultos mayores buscando opciones de seguro. Nicho YMYL "
                        "que requiere contenido altamente confiable.",
        ),
        HighCPCNiche(
            id="online-mba",
            name="Educación: MBA y Programas de Posgrado Online",
            category="Educación",
            keywords=[
                "online MBA for working professionals",
                "best executive MBA programs online",
                "accredited online master degree",
                "maestría en línea acreditada",
                "online finance degree",
            ],
            cpc_min=Decimal('70'),
            cpc_max=Decimal('130'),
            cpc_avg=Decimal('100'),
            search_volume="alto",
            difficulty=TrafficDifficulty.MEDIA,
            intent="comercial",
            evergreen_score=8,
            language="ambos",
            description="Profesionales buscando avanzar su educación. Buen CPC "
                        "con dificultad media de posicionamiento.",
        ),
        HighCPCNiche(
            id="high-risk-auto",
            name="Seguros de Auto para Alto Riesgo",
            category="Seguros",
            keywords=[
                "high risk auto insurance quotes",
                "sr22 insurance",
                "non owner car insurance",
                "cheap auto insurance after accident",
                "drivers with suspended license insurance",
            ],
            cpc_min=Decimal('80'),
            cpc_max=Decimal('130'),
            cpc_avg=Decimal('105'),
            search_volume="muy_alto",
            difficulty=TrafficDifficulty.ALTA,
            intent="transaccional",
            evergreen_score=9,
            language="en",
            description="Conductores con historial problemático buscando seguro. "
                        "Muy alta demanda, CPC elevado.",
        ),
        HighCPCNiche(
            id="defi-investment",
            name="Inversiones y Gestión DeFi",
            category="Finanzas",
            keywords=[
                "DeFi asset management platform",
                "yield farming strategies 2026",
                "best crypto investment platform",
                "inversiones en criptomonedas",
                "crypto portfolio management",
            ],
            cpc_min=Decimal('60'),
            cpc_max=Decimal('110'),
            cpc_avg=Decimal('85'),
            search_volume="medio",
            difficulty=TrafficDifficulty.MEDIA,
            intent="comercial",
            evergreen_score=7,
            language="ambos",
            description="Inversores buscando plataformas y estrategias DeFi. "
                        "Contenido educativo con alta conversión.",
        ),
        HighCPCNiche(
            id="mesothelioma",
            name="Mesotelioma y Enfermedades Laborales",
            category="Servicios Legales",
            keywords=[
                "mesothelioma law firm assistance",
                "mesothelioma compensation",
                "asbestos cancer lawyer",
                "compensación por mesotelioma",
                "lung cancer attorney",
            ],
            cpc_min=Decimal('100'),
            cpc_max=Decimal('200'),
            cpc_avg=Decimal('150'),
            search_volume="bajo",
            difficulty=TrafficDifficulty.MUY_ALTA,
            intent="transaccional",
            evergreen_score=10,
            language="ambos",
            description="Nicho ultra específico pero de altísimo CPC. "
                        "Volumen bajo, pero cada conversión vale fortunas.",
        ),
        HighCPCNiche(
            id="enterprise-cyber",
            name="Ciberseguridad Empresarial",
            category="Tecnología B2B",
            keywords=[
                "enterprise cybersecurity solutions",
                "managed detection and response",
                "cloud security solutions for business",
                "zero trust security implementation",
                "ransomware protection services",
            ],
            cpc_min=Decimal('90'),
            cpc_max=Decimal('160'),
            cpc_avg=Decimal('120'),
            search_volume="alto",
            difficulty=TrafficDifficulty.ALTA,
            intent="comercial",
            evergreen_score=9,
            language="en",
            description="Empresas buscando soluciones de ciberseguridad. "
                        "Alto CPC y contratos anuales de gran valor.",
        ),
    ]

    def __init__(self):
        self.nodes: Dict[str, ContentNode] = {}

    def get_top_niches(self, min_cpc: Decimal = Decimal('80')) -> List[HighCPCNiche]:
        """Filtra nichos por CPC mínimo."""
        return [
            n for n in self.NICHES_DB
            if n.cpc_avg >= min_cpc
        ]

    def get_niches_by_category(self, category: str) -> List[HighCPCNiche]:
        """Filtra nichos por categoría."""
        return [n for n in self.NICHES_DB if n.category == category]

    def rank_niches_by_profitability(self) -> List[Dict]:
        """Ranking de nichos por rentabilidad proyectada."""
        ranked = []
        for niche in self.NICHES_DB:
            ranked.append({
                'id': niche.id,
                'name': niche.name,
                'cpc_range': niche.cpc_range_str,
                'cpc_avg': float(niche.cpc_avg),
                'profitability_score': float(niche.profitability_score),
                'evergreen': niche.evergreen_score,
                'difficulty': niche.difficulty.value,
                'language': niche.language,
            })

        ranked.sort(key=lambda x: x['profitability_score'], reverse=True)
        return ranked

    def calculate_yield_projection(
        self,
        niche_id: str,
        monthly_visitors: int,
        ctr_pct: Decimal = Decimal('2.0'),  # 2% default
        nodes_count: int = 1
    ) -> Optional[Dict]:
        """
        Calcula la proyección de ingresos para un nicho específico.

        Args:
            niche_id: ID del nicho
            monthly_visitors: Tráfico mensual estimado por nodo
            ctr_pct: Click-through rate esperado (%)
            nodes_count: Número de nodos (posts/páginas)

        Returns:
            Dict con proyección detallada o None si no encuentra el nicho
        """
        niche = next((n for n in self.NICHES_DB if n.id == niche_id), None)
        if not niche:
            return None

        monthly_visitors_total = monthly_visitors * nodes_count
        clicks_total = int(monthly_visitors_total * (float(ctr_pct) / 100))
        revenue_low = Decimal(str(clicks_total)) * niche.cpc_min
        revenue_high = Decimal(str(clicks_total)) * niche.cpc_max
        revenue_avg = Decimal(str(clicks_total)) * niche.cpc_avg

        yearly_revenue_low = revenue_low * 12
        yearly_revenue_high = revenue_high * 12
        yearly_revenue_avg = revenue_avg * 12

        return {
            'niche': niche.name,
            'nodes_count': nodes_count,
            'monthly_visitors_total': monthly_visitors_total,
            'ctr_pct': str(ctr_pct),
            'clicks_monthly': clicks_total,
            'cpc_range': {
                'min': float(niche.cpc_min),
                'max': float(niche.cpc_max),
                'avg': float(niche.cpc_avg),
            },
            'monthly_revenue': {
                'low': float(revenue_low),
                'avg': float(revenue_avg),
                'high': float(revenue_high),
            },
            'yearly_revenue': {
                'low': float(yearly_revenue_low),
                'avg': float(yearly_revenue_avg),
                'high': float(yearly_revenue_high),
            },
            'confidence': self._calculate_confidence(niche)
        }

    def _calculate_confidence(self, niche: HighCPCNiche) -> str:
        """Calcula nivel de confianza basado en datos del nicho."""
        score = 0
        if niche.evergreen_score >= 8:
            score += 3
        if niche.search_volume in ('alto', 'muy_alto'):
            score += 3
        if niche.difficulty in (TrafficDifficulty.MEDIA, TrafficDifficulty.BAJA):
            score += 2
        if niche.intent == 'transaccional':
            score += 2

        if score >= 8:
            return "muy_alta"
        elif score >= 6:
            return "alta"
        elif score >= 4:
            return "media"
        else:
            return "baja"

    def create_content_plan(self, selected_niches: List[str]) -> Dict:
        """
        Genera un plan de contenido con proyecciones para nichos seleccionados.

        Args:
            selected_niches: Lista de IDs de nichos

        Returns:
            Dict con el plan completo
        """
        plan = {
            'nodes': [],
            'total_monthly_revenue': {'low': 0, 'avg': 0, 'high': 0},
            'total_yearly_revenue': {'low': 0, 'avg': 0, 'high': 0},
            'total_monthly_visitors': 0,
            'total_clicks': 0,
        }

        for niche_id in selected_niches:
            # Proyección conservadora: 2,000 visitas/mes por nodo
            projection = self.calculate_yield_projection(
                niche_id=niche_id,
                monthly_visitors=2000,
                ctr_pct=Decimal('2.0'),
                nodes_count=3  # 3 nodos por nicho
            )

            if projection:
                plan['nodes'].append(projection)
                plan['total_monthly_revenue']['low'] += projection['monthly_revenue']['low']
                plan['total_monthly_revenue']['avg'] += projection['monthly_revenue']['avg']
                plan['total_monthly_revenue']['high'] += projection['monthly_revenue']['high']
                plan['total_yearly_revenue']['low'] += projection['yearly_revenue']['low']
                plan['total_yearly_revenue']['avg'] += projection['yearly_revenue']['avg']
                plan['total_yearly_revenue']['high'] += projection['yearly_revenue']['high']
                plan['total_monthly_visitors'] += projection['monthly_visitors_total']
                plan['total_clicks'] += projection['clicks_monthly']

        return plan

    def get_evergreen_multiplier(self, years_active: int) -> Decimal:
        """
        Calcula el multiplicador de ingresos para contenido evergreen
        que sigue generando tráfico año tras año.

        Args:
            years_active: Años que el contenido ha estado activo

        Returns:
            Factor multiplicador (asume 10% de caída anual por obsolescencia)
        """
        decay = Decimal('0.9') ** Decimal(str(years_active))
        # Contenido evergreen típicamente retiene 70-90% del tráfico anual
        return (Decimal('1') + decay * Decimal(str(years_active - 1))).quantize(
            Decimal('0.01')
        )

    def export_report(self, filepath: str = "seo_oracle_report.json"):
        """Exporta el reporte completo de investigación a JSON."""
        data = {
            'niches': [
                {
                    'id': n.id,
                    'name': n.name,
                    'category': n.category,
                    'keywords': n.keywords[:5],  # Top 5 keywords
                    'cpc_range': n.cpc_range_str,
                    'cpc_avg': float(n.cpc_avg),
                    'search_volume': n.search_volume,
                    'difficulty': n.difficulty.value,
                    'evergreen_score': n.evergreen_score,
                }
                for n in self.NICHES_DB
            ],
            'ranking': self.rank_niches_by_profitability(),
            'generated_at': __import__('time').time()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {'success': True, 'filepath': filepath}


# =============================================
# DEMO / EJEMPLO DE USO
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 SEO ORACLE — High-CPC Niche Research Engine")
    print("=" * 60)

    oracle = SEOOracle()

    # 1. Mostrar ranking de nichos por rentabilidad
    print("\n🏆 Ranking de Nichos por Rentabilidad:")
    print("-" * 50)
    ranked = oracle.rank_niches_by_profitability()
    for i, n in enumerate(ranked[:5], 1):
        print(f"{i}. {n['name']}")
        print(f"   CPC Avg: ${n['cpc_avg']:.2f} | Score: {n['profitability_score']:.0f}")
        print(f"   Dificultad: {n['difficulty']} | Evergreen: {n['evergreen']}/10")
        print()

    # 2. Proyección para un nicho específico (Recuperación de Activos)
    projection = oracle.calculate_yield_projection(
        niche_id="asset-recovery",
        monthly_visitors=5000,
        ctr_pct=Decimal('2.0'),
        nodes_count=5
    )
    if projection:
        print(f"\n📈 Proyección: {projection['niche']}")
        print(f"   Visitantes/mes: {projection['monthly_visitors_total']:,}")
        print(f"   Clicks/mes: {projection['clicks_monthly']:,}")
        print(f"   Ingreso mensual: ${projection['monthly_revenue']['avg']:,.2f}")
        print(f"   Ingreso anual: ${projection['yearly_revenue']['avg']:,.2f}")
        print(f"   Confianza: {projection['confidence']}")

    # 3. Plan de contenido completo (top 5 nichos)
    print("\n📋 Plan de Contenido (Top 3 Nichos):")
    plan = oracle.create_content_plan(
        ["personal-injury-law", "asset-recovery", "cybersecurity-compliance"]
    )
    print(f"   Visitantes totales/mes: {plan['total_monthly_visitors']:,}")
    print(f"   Clicks totales/mes: {plan['total_clicks']:,}")
    print(f"   Ingreso mensual estimado: ${plan['total_monthly_revenue']['avg']:,.2f}")
    print(f"   Ingreso anual estimado: ${plan['total_yearly_revenue']['avg']:,.2f}")

    print("\n" + "=" * 60)
    print("✅ SEO Oracle — Sistema Listo")
    print("=" * 60)
