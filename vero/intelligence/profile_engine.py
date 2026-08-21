
"""
VERO Company Intelligence Profile Engine

Combines VERO intelligence predictions into one structured startup profile.
"""

from __future__ import annotations

from dataclasses import dataclass

from .business_model_engine import (
    BusinessModelPrediction,
    classify_business_models,
)
from .business_quality_engine import (
    BusinessQualityPrediction,
    analyze_business_quality,
)
from .competitor_engine import (
    CompetitorPrediction,
    recommend_competitors,
)
from .entity_engine import (
    EntityPrediction,
    extract_entities,
)
from .industry_engine import (
    IndustryPrediction,
    classify,
)
from .moat_engine import (
    MoatPrediction,
    analyze_moats,
)
from .risk_engine import (
    RiskPrediction,
    analyze_risk,
)
from .signal_engine import (
    SignalPrediction,
    analyze_signals,
)
from .subindustry_engine import (
    SubindustryPrediction,
    classify_subindustries,
)


def _component_status(
    confidence: float,
    evidence_count: int,
    score: float,
) -> str:
    """Describe whether a component score is genuinely supported."""
    confidence = max(0.0, min(1.0, float(confidence)))

    if evidence_count <= 0 or confidence < 0.15:
        return "insufficient_evidence"

    if confidence < 0.40:
        return "low_confidence"

    if score <= 2.5:
        return "supported_low"

    return "supported"


def _flatten_evidence_count(
    evidence: dict[str, list[str]],
) -> int:
    return sum(
        len(values)
        for values in (evidence or {}).values()
        if isinstance(values, list)
    )


@dataclass(slots=True)
class CompanyIntelligenceProfile:
    primary_industry: str | None
    secondary_industries: list[str]
    industry_confidence: float
    industry_scores: dict[str, float]

    primary_subindustry: str | None
    secondary_subindustries: list[str]
    subindustry_confidence: float
    subindustry_scores: dict[str, float]

    primary_business_model: str | None
    secondary_business_models: list[str]
    business_model_confidence: float
    business_model_scores: dict[str, float]

    customers: list[str]
    technologies: list[str]
    products: list[str]
    competitors: list[str]

    positive_signals: list[str]
    risk_indicators: list[str]
    strategic_scores: dict[str, float]
    overall_signal_score: float

    strongest_moat: str | None
    moat_scores: dict[str, float]
    moat_evidence: dict[str, list[str]]
    overall_moat_score: float
    moat_confidence: float
    moat_status: str

    strongest_business_quality: str | None
    business_quality_scores: dict[str, float]
    business_quality_evidence: dict[str, list[str]]
    overall_business_quality_score: float
    business_quality_confidence: float
    business_quality_status: str

    overall_risk_score: float
    risk_confidence: float
    risk_scores: dict[str, float]
    risk_evidence: dict[str, list[str]]
    largest_risks: list[str]
    risk_status: str

    overall_evidence_confidence: float

    def to_dict(self) -> dict[str, object]:
        return {
            "industry": {
                "primary": self.primary_industry,
                "secondary": self.secondary_industries,
                "confidence": self.industry_confidence,
                "scores": self.industry_scores,
            },
            "subindustry": {
                "primary": self.primary_subindustry,
                "secondary": self.secondary_subindustries,
                "confidence": self.subindustry_confidence,
                "scores": self.subindustry_scores,
            },
            "business_model": {
                "primary": self.primary_business_model,
                "secondary": self.secondary_business_models,
                "confidence": self.business_model_confidence,
                "scores": self.business_model_scores,
            },
            "entities": {
                "customers": self.customers,
                "technologies": self.technologies,
                "products": self.products,
                "competitors": self.competitors,
            },
            "signals": {
                "positive": self.positive_signals,
                "risk": self.risk_indicators,
                "scores": self.strategic_scores,
                "overall_score": self.overall_signal_score,
            },
            "moats": {
                "strongest": self.strongest_moat,
                "overall_score": self.overall_moat_score,
                "confidence": self.moat_confidence,
                "status": self.moat_status,
                "scores": self.moat_scores,
                "evidence": self.moat_evidence,
            },
            "business_quality": {
                "strongest": self.strongest_business_quality,
                "overall_score": self.overall_business_quality_score,
                "confidence": self.business_quality_confidence,
                "status": self.business_quality_status,
                "scores": self.business_quality_scores,
                "evidence": self.business_quality_evidence,
            },
            "risk": {
                "overall_score": self.overall_risk_score,
                "confidence": self.risk_confidence,
                "status": self.risk_status,
                "scores": self.risk_scores,
                "evidence": self.risk_evidence,
                "largest_risks": self.largest_risks,
            },
            "evidence": {
                "overall_confidence": self.overall_evidence_confidence,
            },
        }


def build_company_profile(
    text: str,
) -> CompanyIntelligenceProfile:
    """
    Build a structured intelligence profile from a company description.

    A low score and missing evidence are intentionally treated as different
    states. Component status fields make that distinction explicit.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    industry: IndustryPrediction = classify(text)

    subindustry: SubindustryPrediction = classify_subindustries(
        text=text,
        industry_name=industry.primary_industry,
    )

    business_model: BusinessModelPrediction = classify_business_models(
        text=text,
        industry_name=industry.primary_industry,
    )

    entities: EntityPrediction = extract_entities(
        text=text,
        industry_name=industry.primary_industry,
    )

    competitors: CompetitorPrediction = recommend_competitors(
        text=text,
        industry_name=industry.primary_industry,
    )

    signals: SignalPrediction = analyze_signals(
        text=text,
        industry_name=industry.primary_industry,
    )

    moats: MoatPrediction = analyze_moats(
        text=text,
        industry_name=industry.primary_industry,
    )

    business_quality: BusinessQualityPrediction = analyze_business_quality(
        text=text,
        industry_name=industry.primary_industry,
    )

    risk: RiskPrediction = analyze_risk(
        text=text,
        industry_name=industry.primary_industry,
    )

    moat_evidence_count = _flatten_evidence_count(
        moats.evidence
    )
    business_quality_evidence_count = _flatten_evidence_count(
        business_quality.evidence
    )
    risk_evidence_count = _flatten_evidence_count(
        risk.evidence
    )

    moat_status = _component_status(
        confidence=moats.confidence,
        evidence_count=moat_evidence_count,
        score=moats.overall_moat_score,
    )

    business_quality_status = _component_status(
        confidence=business_quality.confidence,
        evidence_count=business_quality_evidence_count,
        score=business_quality.overall_quality_score,
    )

    risk_status = _component_status(
        confidence=risk.confidence,
        evidence_count=risk_evidence_count,
        score=risk.overall_risk,
    )

    overall_evidence_confidence = (
        industry.confidence
        + subindustry.confidence
        + business_model.confidence
        + moats.confidence
        + business_quality.confidence
        + risk.confidence
    ) / 6

    return CompanyIntelligenceProfile(
        primary_industry=industry.primary_industry,
        secondary_industries=industry.secondary_industries,
        industry_confidence=industry.confidence,
        industry_scores=industry.scores,

        primary_subindustry=subindustry.primary_subindustry,
        secondary_subindustries=subindustry.secondary_subindustries,
        subindustry_confidence=subindustry.confidence,
        subindustry_scores=subindustry.scores,

        primary_business_model=business_model.primary_business_model,
        secondary_business_models=business_model.secondary_business_models,
        business_model_confidence=business_model.confidence,
        business_model_scores=business_model.scores,

        customers=entities.customers,
        technologies=entities.technologies,
        products=entities.products,
        competitors=competitors.competitors,

        positive_signals=signals.positive_signals,
        risk_indicators=signals.risk_indicators,
        strategic_scores=signals.strategic_scores,
        overall_signal_score=signals.overall_signal_score,

        strongest_moat=moats.strongest_moat,
        moat_scores=moats.moat_scores,
        moat_evidence=moats.evidence,
        overall_moat_score=moats.overall_moat_score,
        moat_confidence=moats.confidence,
        moat_status=moat_status,

        strongest_business_quality=business_quality.strongest_quality,
        business_quality_scores=business_quality.quality_scores,
        business_quality_evidence=business_quality.evidence,
        overall_business_quality_score=business_quality.overall_quality_score,
        business_quality_confidence=business_quality.confidence,
        business_quality_status=business_quality_status,

        overall_risk_score=risk.overall_risk,
        risk_confidence=risk.confidence,
        risk_scores=risk.risk_scores,
        risk_evidence=risk.evidence,
        largest_risks=risk.largest_risks,
        risk_status=risk_status,

        overall_evidence_confidence=overall_evidence_confidence,
    )


__all__ = [
    "CompanyIntelligenceProfile",
    "build_company_profile",
]