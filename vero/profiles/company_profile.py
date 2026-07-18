from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import json


@dataclass
class EvidenceItem:
    claim: str
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    collected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 0.5
    verified: bool = False
    notes: Optional[str] = None


@dataclass
class FounderProfile:
    name: str
    role: Optional[str] = None
    linkedin_url: Optional[str] = None
    previous_companies: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    domain_experience_years: Optional[float] = None
    previous_startups: list[str] = field(default_factory=list)
    previous_exits: list[str] = field(default_factory=list)
    technical_background: Optional[bool] = None
    founder_market_fit: Optional[str] = None
    reputation_notes: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class CompanyIdentity:
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    countries_served: list[str] = field(default_factory=list)
    industry: Optional[str] = None
    subindustry: Optional[str] = None
    stage: Optional[str] = None
    legal_name: Optional[str] = None
    company_status: Optional[str] = None
    accelerator: Optional[str] = None
    batch: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class ProblemProfile:
    summary: Optional[str] = None
    target_user: Optional[str] = None
    severity: Optional[float] = None
    frequency: Optional[str] = None
    urgency: Optional[float] = None
    cost_of_inaction: Optional[str] = None
    current_alternatives: list[str] = field(default_factory=list)
    willingness_to_pay: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class SolutionProfile:
    summary: Optional[str] = None
    primary_value_proposition: Optional[str] = None
    differentiation: Optional[str] = None
    technical_complexity: Optional[str] = None
    scalability: Optional[str] = None
    time_to_value: Optional[str] = None
    implementation_friction: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class CustomerProfile:
    customer_type: Optional[str] = None
    buyer: Optional[str] = None
    end_user: Optional[str] = None
    industries_served: list[str] = field(default_factory=list)
    customer_size: Optional[str] = None
    geography: list[str] = field(default_factory=list)
    sales_motion: Optional[str] = None
    customer_concentration_risk: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class ProductProfile:
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    maturity: Optional[str] = None
    launch_date: Optional[str] = None
    usability_notes: Optional[str] = None
    reliability_notes: Optional[str] = None
    integrations: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    roadmap_signals: list[str] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class BusinessModelProfile:
    model_type: Optional[str] = None
    revenue_streams: list[str] = field(default_factory=list)
    pricing_model: Optional[str] = None
    recurring_revenue: Optional[bool] = None
    gross_margin: Optional[float] = None
    monetization_strength: Optional[str] = None
    expansion_revenue: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class TractionProfile:
    users: Optional[int] = None
    customers: Optional[int] = None
    monthly_active_users: Optional[int] = None
    annual_revenue: Optional[float] = None
    monthly_recurring_revenue: Optional[float] = None
    annual_recurring_revenue: Optional[float] = None
    revenue_growth_rate: Optional[float] = None
    user_growth_rate: Optional[float] = None
    retention_rate: Optional[float] = None
    churn_rate: Optional[float] = None
    major_customers: list[str] = field(default_factory=list)
    partnerships: list[str] = field(default_factory=list)
    waitlist_size: Optional[int] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class MarketProfile:
    market_name: Optional[str] = None
    tam: Optional[float] = None
    sam: Optional[float] = None
    som: Optional[float] = None
    growth_rate: Optional[float] = None
    market_stage: Optional[str] = None
    demand_trend: Optional[str] = None
    timing: Optional[str] = None
    regulation_notes: Optional[str] = None
    geographic_opportunity: list[str] = field(default_factory=list)
    market_drivers: list[str] = field(default_factory=list)
    market_headwinds: list[str] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class CompetitorProfile:
    name: str
    website: Optional[str] = None
    relationship: Optional[str] = None
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    funding: Optional[float] = None
    notes: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class CompetitionProfile:
    direct_competitors: list[CompetitorProfile] = field(default_factory=list)
    indirect_competitors: list[CompetitorProfile] = field(default_factory=list)
    substitutes: list[str] = field(default_factory=list)
    intensity: Optional[float] = None
    saturation: Optional[str] = None
    pricing_pressure: Optional[str] = None
    competitive_position: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class MoatProfile:
    network_effects: Optional[str] = None
    switching_costs: Optional[str] = None
    proprietary_data: Optional[str] = None
    proprietary_technology: Optional[str] = None
    brand_strength: Optional[str] = None
    distribution_advantage: Optional[str] = None
    intellectual_property: list[str] = field(default_factory=list)
    regulatory_advantage: Optional[str] = None
    community_strength: Optional[str] = None
    overall_strength: Optional[float] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class FinancialProfile:
    total_funding: Optional[float] = None
    last_round_amount: Optional[float] = None
    last_round_date: Optional[str] = None
    valuation: Optional[float] = None
    burn_rate_monthly: Optional[float] = None
    runway_months: Optional[float] = None
    cash_balance: Optional[float] = None
    cac: Optional[float] = None
    ltv: Optional[float] = None
    cac_payback_months: Optional[float] = None
    capital_efficiency: Optional[str] = None
    profitability_status: Optional[str] = None
    debt: Optional[float] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class TeamProfile:
    employee_count: Optional[int] = None
    employee_growth_rate: Optional[float] = None
    hiring_status: Optional[str] = None
    key_roles_open: list[str] = field(default_factory=list)
    technical_team_strength: Optional[str] = None
    sales_team_strength: Optional[str] = None
    team_completeness: Optional[str] = None
    key_person_risk: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class RiskItem:
    category: str
    description: str
    severity: float
    likelihood: float
    time_horizon: Optional[str] = None
    mitigation: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class OpportunityItem:
    category: str
    description: str
    potential_impact: float
    likelihood: float
    time_horizon: Optional[str] = None
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class ExternalEnvironment:
    industry_momentum: Optional[str] = None
    funding_climate: Optional[str] = None
    regulatory_climate: Optional[str] = None
    customer_demand_trend: Optional[str] = None
    technology_trend: Optional[str] = None
    macro_sensitivity: Optional[str] = None
    recent_events: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class HistoricalModelOutput:
    success_probability: Optional[float] = None
    model_version: Optional[str] = None
    prediction_date: Optional[str] = None
    similar_companies: list[str] = field(default_factory=list)
    important_features: list[str] = field(default_factory=list)


@dataclass
class ScoreBreakdown:
    company_quality: Optional[float] = None
    team: Optional[float] = None
    problem: Optional[float] = None
    product: Optional[float] = None
    traction: Optional[float] = None
    market_opportunity: Optional[float] = None
    competitive_strength: Optional[float] = None
    moat: Optional[float] = None
    financial_health: Optional[float] = None
    execution_potential: Optional[float] = None
    external_environment: Optional[float] = None
    risk: Optional[float] = None
    overall_investment_score: Optional[float] = None


@dataclass
class AIAnalysis:
    executive_summary: Optional[str] = None
    investment_thesis: Optional[str] = None
    bull_case: Optional[str] = None
    bear_case: Optional[str] = None
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    questions_to_ask: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    conclusion: Optional[str] = None


@dataclass
class DataQuality:
    completeness: float = 0.0
    confidence: float = 0.0
    known_field_count: int = 0
    total_field_count: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CompanyProfile:
    identity: CompanyIdentity
    founders: list[FounderProfile] = field(default_factory=list)
    team: TeamProfile = field(default_factory=TeamProfile)
    problem: ProblemProfile = field(default_factory=ProblemProfile)
    solution: SolutionProfile = field(default_factory=SolutionProfile)
    customers: CustomerProfile = field(default_factory=CustomerProfile)
    product: ProductProfile = field(default_factory=ProductProfile)
    business_model: BusinessModelProfile = field(default_factory=BusinessModelProfile)
    traction: TractionProfile = field(default_factory=TractionProfile)
    market: MarketProfile = field(default_factory=MarketProfile)
    competition: CompetitionProfile = field(default_factory=CompetitionProfile)
    moat: MoatProfile = field(default_factory=MoatProfile)
    financials: FinancialProfile = field(default_factory=FinancialProfile)
    risks: list[RiskItem] = field(default_factory=list)
    opportunities: list[OpportunityItem] = field(default_factory=list)
    external_environment: ExternalEnvironment = field(default_factory=ExternalEnvironment)
    historical_model: HistoricalModelOutput = field(default_factory=HistoricalModelOutput)
    scores: ScoreBreakdown = field(default_factory=ScoreBreakdown)
    ai_analysis: AIAnalysis = field(default_factory=AIAnalysis)
    evidence: list[EvidenceItem] = field(default_factory=list)
    data_quality: DataQuality = field(default_factory=DataQuality)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save_json(self, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def update_data_quality(self) -> None:
        flat_values: list[Any] = []

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
            else:
                flat_values.append(value)

        profile_dict = self.to_dict()
        profile_dict.pop("data_quality", None)
        walk(profile_dict)

        total = len(flat_values)
        known = sum(v not in (None, "") for v in flat_values)
        self.data_quality.total_field_count = total
        self.data_quality.known_field_count = known
        self.data_quality.completeness = round(known / total, 4) if total else 0.0
        self.data_quality.last_updated = datetime.now(timezone.utc).isoformat()


def create_empty_company_profile(name: str, website: Optional[str] = None) -> CompanyProfile:
    profile = CompanyProfile(
        identity=CompanyIdentity(
            name=name.strip(),
            website=website.strip() if website else None,
        )
    )
    profile.update_data_quality()
    return profile


if __name__ == "__main__":
    sample = create_empty_company_profile("FlatX", "https://flatx.com")
    output = sample.save_json("vero/data/companies/flatx_profile.json")
    print(f"Created profile: {output}")
    print(f"Completeness: {sample.data_quality.completeness:.1%}")
