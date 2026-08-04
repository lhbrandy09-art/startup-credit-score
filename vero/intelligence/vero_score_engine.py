"""
VERO Unified Investment Score Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from .profile_engine import CompanyIntelligenceProfile


@dataclass(slots=True)
class VeroScorePrediction:
    overall_score: float
    investment_grade: str
    score_components: dict[str, float]
    strengths: list[str]
    concerns: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "overall_score": self.overall_score,
            "investment_grade": self.investment_grade,
            "score_components": self.score_components,
            "strengths": self.strengths,
            "concerns": self.concerns,
        }


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(minimum, min(maximum, value))


def _get_score(
    scores: dict[str, float],
    key: str,
) -> float:
    return float(scores.get(key, 0.0))


def analyze_vero_score(
    profile: CompanyIntelligenceProfile,
) -> VeroScorePrediction:
    """
    Convert the complete VERO intelligence profile into
    one explainable investment score from 0 to 100.
    """

    business_quality_component = (
        profile.overall_business_quality_score / 10
    ) * 30

    moat_component = (
        profile.overall_moat_score / 10
    ) * 25

    signal_component = (
        profile.overall_signal_score / 100
    ) * 15

    risk_component = (
        (10 - profile.overall_risk_score) / 10
    ) * 20

    average_confidence = (
        profile.industry_confidence
        + profile.subindustry_confidence
        + profile.business_model_confidence
        + profile.moat_confidence
        + profile.business_quality_confidence
        + profile.risk_confidence
    ) / 6

    confidence_component = average_confidence * 10

    overall_score = (
        business_quality_component
        + moat_component
        + signal_component
        + risk_component
        + confidence_component
    )

    overall_score = round(_clamp(overall_score), 2)

    strengths: list[str] = []
    concerns: list[str] = []

    quality_scores = profile.business_quality_scores
    risk_scores = profile.risk_scores

    if _get_score(quality_scores, "recurring_revenue") >= 7:
        strengths.append("Strong recurring revenue model")

    if _get_score(quality_scores, "customer_stickiness") >= 7:
        strengths.append("High customer retention potential")

    if _get_score(quality_scores, "gross_margin") >= 7:
        strengths.append("Attractive gross-margin profile")

    if _get_score(quality_scores, "scalability") >= 7:
        strengths.append("Highly scalable business model")

    if _get_score(risk_scores, "market_timing") <= 3:
        strengths.append("Favorable market timing")

    if profile.overall_moat_score >= 6:
        strengths.append("Strong competitive defensibility")

    if profile.overall_signal_score >= 65:
        strengths.append("Strong strategic signals")

    if _get_score(risk_scores, "go_to_market") >= 7:
        concerns.append("High go-to-market difficulty")

    if _get_score(risk_scores, "regulatory") >= 7:
        concerns.append("Significant regulatory exposure")

    if _get_score(risk_scores, "competition") >= 7:
        concerns.append("Intense competitive environment")

    if _get_score(risk_scores, "capital") >= 7:
        concerns.append("High capital requirements")

    if _get_score(risk_scores, "platform_dependency") >= 7:
        concerns.append("Meaningful platform dependency")

    if profile.overall_moat_score < 3:
        concerns.append("Limited demonstrated moat")

    if profile.business_quality_confidence < 0.40:
        concerns.append("Limited business-quality evidence")

    if overall_score >= 85:
        grade = "Exceptional"

    elif overall_score >= 75:
        grade = "Excellent"

    elif overall_score >= 65:
        grade = "Strong"

    elif overall_score >= 55:
        grade = "Promising"

    elif overall_score >= 45:
        grade = "Developing"

    elif overall_score >= 35:
        grade = "Weak"

    else:
        grade = "High Risk"

    score_components = {
        "business_quality": round(
            business_quality_component,
            2,
        ),
        "moat": round(moat_component, 2),
        "signals": round(signal_component, 2),
        "risk_adjustment": round(risk_component, 2),
        "confidence": round(confidence_component, 2),
    }

    return VeroScorePrediction(
        overall_score=overall_score,
        investment_grade=grade,
        score_components=score_components,
        strengths=strengths,
        concerns=concerns,
    )


__all__ = [
    "VeroScorePrediction",
    "analyze_vero_score",
]