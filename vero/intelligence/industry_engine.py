"""
VERO Industry Classification Engine

Determines the primary industry of a company using the
VERO ontology library.
"""

from __future__ import annotations

from dataclasses import dataclass

from .keyword_library import (
    KNOWLEDGE,
    search_industries,
)


@dataclass(slots=True)
class IndustryPrediction:
    primary_industry: str | None
    secondary_industries: list[str]
    confidence: float
    scores: dict[str, float]
    def to_dict(self) -> dict[str, object]:
        return {
            "primary_industry": self.primary_industry,
            "secondary_industries": self.secondary_industries,
            "confidence": self.confidence,
            "scores": self.scores,
        }


def classify(
    text: str,
) -> IndustryPrediction:
    """
    Classify free text into industries.

    Market/domain industries are favored over enabling technologies
    when both are present.
    """

    matches = search_industries(
        text,
        include_scores=True,
    )

    if not matches:
        return IndustryPrediction(
            primary_industry=None,
            secondary_industries=[],
            confidence=0.0,
            scores={},
        )

    scores = {
        industry: float(score)
        for industry, score in matches
    }

    normalized_text = text.casefold()

    domain_indicators = {
        "Healthcare": [
            "clinical",
            "hospital",
            "hospitals",
            "patient",
            "patients",
            "physician",
            "doctor",
            "medical",
            "health system",
            "healthcare",
            "care delivery",
        ],
        "Financial Technology": [
            "payment",
            "payments",
            "bank",
            "banking",
            "lending",
            "credit",
            "insurance",
            "financial institution",
            "fintech",
            "transaction",
        ],
        "Artificial Intelligence": [
            "artificial intelligence",
            "machine learning",
            "foundation model",
            "generative ai",
            "large language model",
            "computer vision",
            "natural language processing",
        ],
    }

    # Add domain-context bonuses.
    for industry, indicators in domain_indicators.items():
        bonus = 0.0

        for indicator in indicators:
            if indicator in normalized_text:
                bonus += 2.0

        if bonus:
            scores[industry] = scores.get(industry, 0.0) + bonus

    # AI is often an enabling technology rather than the target market.
    enabling_ai_terms = [
        "ai-powered",
        "powered by ai",
        "uses ai",
        "using ai",
        "ai-enabled",
        "machine-learning-powered",
    ]

    domain_industries = [
        industry
        for industry in scores
        if industry != "Artificial Intelligence"
        and scores[industry] > 0
    ]

    if (
        "Artificial Intelligence" in scores
        and domain_industries
        and any(
            term in normalized_text
            for term in enabling_ai_terms
        )
    ):
        scores["Artificial Intelligence"] *= 0.65

    ranked_matches = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    primary = ranked_matches[0][0]

    top_score = ranked_matches[0][1]
    second_score = (
        ranked_matches[1][1]
        if len(ranked_matches) > 1
        else 0.0
    )

    secondary = [
        industry
        for industry, score in ranked_matches[1:]
        if (
            score >= top_score * 0.35
            and score >= 10.0
        )
    ]

    total_score = sum(
        score
        for _, score in ranked_matches
    )

    share_confidence = (
        top_score / total_score
        if total_score
        else 0.0
    )

    margin_confidence = (
        (top_score - second_score) / top_score
        if top_score
        else 0.0
    )

    confidence = (
        share_confidence * 0.65
        + margin_confidence * 0.35
    )

    return IndustryPrediction(
        primary_industry=primary,
        secondary_industries=secondary,
        confidence=round(confidence, 3),
        scores={
            industry: round(score, 2)
            for industry, score in ranked_matches
        },
    )