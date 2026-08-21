"""
VERO Unified Investment Score Engine

Confidence-aware scoring:
- Missing evidence is not treated as a zero-quality company.
- Low-confidence component values are pulled toward neutral.
- Supported weak evidence can still generate a legitimately low score.
"""

from __future__ import annotations

from dataclasses import dataclass

from .profile_engine import CompanyIntelligenceProfile


@dataclass(slots=True)
class VeroScorePrediction:
    overall_score: float
    investment_grade: str
    score_components: dict[str, float]
    component_confidence: dict[str, float]
    component_status: dict[str, str]
    strengths: list[str]
    concerns: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "overall_score": self.overall_score,
            "investment_grade": self.investment_grade,
            "score_components": self.score_components,
            "component_confidence": self.component_confidence,
            "component_status": self.component_status,
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


def _confidence_adjusted_value(
    raw_value: float,
    confidence: float,
    neutral_value: float,
) -> float:
    """
    Pull uncertain component estimates toward neutral.

    Example:
    moat=0/10 with confidence=0.0 becomes 5/10 effective,
    not 0/10. A moat=0/10 with confidence=1.0 remains 0/10.
    """
    confidence = max(0.0, min(1.0, float(confidence)))
    return (
        raw_value * confidence
        + neutral_value * (1.0 - confidence)
    )


def analyze_vero_score(
    profile: CompanyIntelligenceProfile,
) -> VeroScorePrediction:
    """
    Convert the VERO intelligence profile into one explainable score.

    The score distinguishes weak evidence from absent evidence by using each
    component's confidence when translating raw engine values into points.
    """

    # ---------- Confidence-adjusted raw values ----------
    effective_business_quality = _confidence_adjusted_value(
        raw_value=profile.overall_business_quality_score,
        confidence=profile.business_quality_confidence,
        neutral_value=5.0,
    )

    effective_moat = _confidence_adjusted_value(
        raw_value=profile.overall_moat_score,
        confidence=profile.moat_confidence,
        neutral_value=5.0,
    )

    effective_risk = _confidence_adjusted_value(
        raw_value=profile.overall_risk_score,
        confidence=profile.risk_confidence,
        neutral_value=5.0,
    )

    # The signal engine currently has no dedicated confidence output.
    # Use profile-wide evidence confidence rather than treating signal output
    # as equally certain for every company.
    signal_confidence = max(
        0.15,
        min(
            1.0,
            profile.overall_evidence_confidence,
        ),
    )

    effective_signal = _confidence_adjusted_value(
        raw_value=profile.overall_signal_score,
        confidence=signal_confidence,
        neutral_value=50.0,
    )

    # ---------- Components ----------
    business_quality_component = (
        effective_business_quality / 10
    ) * 30

    moat_component = (
        effective_moat / 10
    ) * 25

    signal_component = (
        effective_signal / 100
    ) * 15

    risk_component = (
        (10 - effective_risk) / 10
    ) * 20

    average_confidence = max(
        0.0,
        min(
            1.0,
            profile.overall_evidence_confidence,
        ),
    )

    # Confidence is informative, but no longer acts as a large reward that
    # can distort the company's underlying quality score.
    confidence_component = average_confidence * 10

    overall_score = (
        business_quality_component
        + moat_component
        + signal_component
        + risk_component
        + confidence_component
    )

    overall_score = round(
        _clamp(overall_score),
        2,
    )

    strengths: list[str] = []
    concerns: list[str] = []

    quality_scores = profile.business_quality_scores
    risk_scores = profile.risk_scores

    # ---------- Strengths ----------
    if (
        profile.business_quality_confidence >= 0.35
        and _get_score(quality_scores, "recurring_revenue") >= 7
    ):
        strengths.append("Strong recurring revenue model")

    if (
        profile.business_quality_confidence >= 0.35
        and _get_score(quality_scores, "customer_stickiness") >= 7
    ):
        strengths.append("High customer retention potential")

    if (
        profile.business_quality_confidence >= 0.35
        and _get_score(quality_scores, "gross_margin") >= 7
    ):
        strengths.append("Attractive gross-margin profile")

    if (
        profile.business_quality_confidence >= 0.35
        and _get_score(quality_scores, "scalability") >= 7
    ):
        strengths.append("Highly scalable business model")

    if (
        profile.risk_confidence >= 0.35
        and _get_score(risk_scores, "market_timing") <= 3
    ):
        strengths.append("Favorable market timing")

    if (
        profile.moat_confidence >= 0.40
        and profile.overall_moat_score >= 6
    ):
        strengths.append("Strong competitive defensibility")

    if (
        signal_confidence >= 0.35
        and profile.overall_signal_score >= 65
    ):
        strengths.append("Strong strategic signals")

    # ---------- Concerns ----------
    if (
        profile.risk_confidence >= 0.35
        and _get_score(risk_scores, "go_to_market") >= 7
    ):
        concerns.append("High go-to-market difficulty")

    if (
        profile.risk_confidence >= 0.35
        and _get_score(risk_scores, "regulatory") >= 7
    ):
        concerns.append("Significant regulatory exposure")

    if (
        profile.risk_confidence >= 0.35
        and _get_score(risk_scores, "competition") >= 7
    ):
        concerns.append("Intense competitive environment")

    if (
        profile.risk_confidence >= 0.35
        and _get_score(risk_scores, "capital") >= 7
    ):
        concerns.append("High capital requirements")

    if (
        profile.risk_confidence >= 0.35
        and _get_score(risk_scores, "platform_dependency") >= 7
    ):
        concerns.append("Meaningful platform dependency")

    # Crucial distinction:
    # no moat evidence => unknown
    # supported low moat => genuine concern
    if profile.moat_status == "insufficient_evidence":
        concerns.append("Insufficient evidence to assess competitive moat")
    elif (
        profile.moat_status in {"supported", "supported_low"}
        and profile.moat_confidence >= 0.40
        and profile.overall_moat_score < 3
    ):
        concerns.append("Limited demonstrated moat")

    if profile.business_quality_status == "insufficient_evidence":
        concerns.append("Insufficient evidence to assess business quality")
    elif profile.business_quality_confidence < 0.40:
        concerns.append("Limited business-quality evidence")

    if profile.risk_status == "insufficient_evidence":
        concerns.append("Insufficient evidence to assess risk reliably")

    # ---------- Grade ----------
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
        "moat": round(
            moat_component,
            2,
        ),
        "signals": round(
            signal_component,
            2,
        ),
        "risk_adjustment": round(
            risk_component,
            2,
        ),
        "confidence": round(
            confidence_component,
            2,
        ),
    }

    component_confidence = {
        "business_quality": round(
            profile.business_quality_confidence,
            3,
        ),
        "moat": round(
            profile.moat_confidence,
            3,
        ),
        "signals": round(
            signal_confidence,
            3,
        ),
        "risk": round(
            profile.risk_confidence,
            3,
        ),
        "overall": round(
            average_confidence,
            3,
        ),
    }

    component_status = {
        "business_quality": profile.business_quality_status,
        "moat": profile.moat_status,
        "risk": profile.risk_status,
    }

    return VeroScorePrediction(
        overall_score=overall_score,
        investment_grade=grade,
        score_components=score_components,
        component_confidence=component_confidence,
        component_status=component_status,
        strengths=strengths,
        concerns=concerns,
    )


__all__ = [
    "VeroScorePrediction",
    "analyze_vero_score",
]