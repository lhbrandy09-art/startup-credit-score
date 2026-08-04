"""
VERO Business Model Detection Engine

Detects likely business models from company descriptions using
the VERO ontology library.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .industry_engine import classify
from .keyword_library import (
    find_industry_by_alias,
    get_industry,
)


@dataclass(slots=True)
class BusinessModelPrediction:
    primary_industry: str | None
    primary_business_model: str | None
    secondary_business_models: list[str]
    confidence: float
    scores: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return {
            "primary_industry": self.primary_industry,
            "primary_business_model": self.primary_business_model,
            "secondary_business_models": self.secondary_business_models,
            "confidence": self.confidence,
            "scores": self.scores,
        }


def _normalize_text(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"[-_/]", " ", text)
    text = re.sub(r"[^a-z0-9+\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _contains_term(
    normalized_text: str,
    term: str,
) -> bool:
    normalized_term = _normalize_text(term)

    if not normalized_term:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(normalized_term)
        + r"(?![a-z0-9])"
    )

    return re.search(pattern, normalized_text) is not None


BUSINESS_MODEL_PATTERNS: dict[str, list[str]] = {
    "B2B": [
        "b2b",
        "businesses",
        "companies",
        "enterprises",
        "organizations",
        "teams",
        "employers",
        "providers",
        "hospitals",
        "banks",
        "institutions",
    ],

    "B2C": [
        "b2c",
        "consumers",
        "individuals",
        "patients",
        "families",
        "personal",
        "consumer app",
        "mobile app",
        "direct to consumer",
    ],

    "B2B2C": [
        "b2b2c",
        "through employers",
        "through providers",
        "through banks",
        "through insurers",
        "through health plans",
        "distributed through partners",
        "partner distribution",
    ],

    "SaaS": [
        "saas",
        "software as a service",
        "cloud software",
        "software platform",
        "subscription software",
        "web platform",
        "dashboard",
        "enterprise software",
    ],

    "API": [
        "api",
        "apis",
        "developer api",
        "api platform",
        "infrastructure api",
        "integration api",
        "developer platform",
        "sdk",
    ],

    "Subscription": [
        "subscription",
        "monthly subscription",
        "annual subscription",
        "recurring subscription",
        "membership",
        "monthly fee",
        "annual fee",
    ],

    "Usage-Based Pricing": [
        "usage based",
        "usage-based",
        "pay as you go",
        "pay per use",
        "consumption based",
        "metered billing",
        "per request",
        "per api call",
    ],

    "Per-Seat Pricing": [
        "per seat",
        "per user",
        "per employee",
        "per clinician",
        "per provider",
        "per agent",
        "seat based",
    ],

    "Per-Transaction Pricing": [
        "per transaction",
        "transaction fee",
        "processing fee",
        "payment fee",
        "take rate",
        "percentage of transaction",
        "fee per transaction",
    ],

    "Marketplace": [
        "marketplace",
        "buyers and sellers",
        "connects customers with",
        "connects businesses with",
        "two sided marketplace",
        "two-sided marketplace",
        "provider marketplace",
        "services marketplace",
    ],

    "Enterprise Contract": [
        "enterprise contract",
        "annual contract",
        "multi year contract",
        "multi-year contract",
        "enterprise agreement",
        "custom pricing",
        "contact sales",
        "sales led",
        "sales-led",
        "annual contracts",
        "enterprise contracts",
        "multi year contracts",
        "multi-year contracts",
    ],

    "Licensing": [
        "licensing",
        "license fee",
        "software license",
        "technology licensing",
        "drug licensing",
        "intellectual property licensing",
        "white label",
        "white-label",
    ],

    "Data Licensing": [
        "data licensing",
        "data subscription",
        "data access",
        "data provider",
        "dataset licensing",
        "analytics data",
        "information services",
    ],

    "Hardware Sales": [
        "hardware sales",
        "device sales",
        "medical device sales",
        "equipment sales",
        "sells hardware",
        "physical device",
        "sensor sales",
    ],

    "Advertising": [
        "advertising",
        "ad supported",
        "ad-supported",
        "sponsored content",
        "digital ads",
        "advertiser",
        "advertising revenue",
    ],

    "Freemium": [
        "freemium",
        "free plan",
        "free tier",
        "premium plan",
        "upgrade to premium",
        "paid tier",
    ],

    "Commission": [
        "commission",
        "referral fee",
        "broker fee",
        "success fee",
        "placement fee",
        "percentage commission",
    ],

    "Insurance Reimbursement": [
        "insurance reimbursement",
        "reimbursed by insurance",
        "payer reimbursement",
        "covered by insurance",
        "insurance billing",
        "medical reimbursement",
    ],

    "Value-Based Care": [
        "value based care",
        "value-based care",
        "shared savings",
        "risk based contract",
        "risk-based contract",
        "outcomes based",
        "outcomes-based",
        "capitation",
    ],

    "Transaction Revenue": [
        "transaction revenue",
        "payment processing",
        "interchange revenue",
        "processing revenue",
        "merchant fee",
        "transfer fee",
    ],
}


def classify_business_models(
    text: str,
    industry_name: str | None = None,
    max_results: int = 5,
) -> BusinessModelPrediction:
    """
    Detect likely business models from free text.

    If an industry is not supplied, VERO first classifies it.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if max_results < 1:
        raise ValueError("max_results must be at least 1.")

    normalized_text = _normalize_text(text)

    if not normalized_text:
        return BusinessModelPrediction(
            primary_industry=None,
            primary_business_model=None,
            secondary_business_models=[],
            confidence=0.0,
            scores={},
        )

    if industry_name is None:
        industry_prediction = classify(text)
        primary_industry = industry_prediction.primary_industry
    else:
        ontology = (
            get_industry(industry_name)
            or find_industry_by_alias(industry_name)
        )

        primary_industry = (
            str(ontology["name"])
            if ontology is not None
            else None
        )

    scores: dict[str, float] = {}

    for model_name, patterns in BUSINESS_MODEL_PATTERNS.items():
        score = 0.0
        matched_terms: set[str] = set()

        for pattern in patterns:
            normalized_pattern = _normalize_text(pattern)

            if (
                normalized_pattern
                and normalized_pattern not in matched_terms
                and _contains_term(
                    normalized_text,
                    normalized_pattern,
                )
            ):
                matched_terms.add(normalized_pattern)

                word_count = len(normalized_pattern.split())

                if word_count >= 3:
                    score += 4.0
                elif word_count == 2:
                    score += 3.0
                else:
                    score += 1.5

        if len(matched_terms) >= 2:
            score += min(
                3.0,
                (len(matched_terms) - 1) * 0.75,
            )

        if score > 0:
            scores[model_name] = round(score, 2)

    if primary_industry is not None:
        ontology = (
            get_industry(primary_industry)
            or find_industry_by_alias(primary_industry)
        )

        if ontology is not None:
            industry_models = ontology.get(
                "business_models",
                [],
            )

            if isinstance(industry_models, list):
                for model in industry_models:
                    model_name = str(model)

                    if _contains_term(
                        normalized_text,
                        model_name,
                    ):
                        scores[model_name] = (
                            scores.get(model_name, 0.0)
                            + 2.5
                        )

    if not scores:
        return BusinessModelPrediction(
            primary_industry=primary_industry,
            primary_business_model=None,
            secondary_business_models=[],
            confidence=0.0,
            scores={},
        )

    ranked_scores = sorted(
        scores.items(),
        key=lambda item: (
            item[1],
            item[0],
        ),
        reverse=True,
    )[:max_results]

    primary_business_model = ranked_scores[0][0]
    top_score = ranked_scores[0][1]

    second_score = (
        ranked_scores[1][1]
        if len(ranked_scores) > 1
        else 0.0
    )

    secondary_business_models = [
        model
        for model, score in ranked_scores[1:]
        if score >= top_score * 0.35
    ]

    total_score = sum(
        score
        for _, score in ranked_scores
    )

    score_share = (
        top_score / total_score
        if total_score
        else 0.0
    )

    score_margin = (
        (top_score - second_score) / top_score
        if top_score
        else 0.0
    )

    confidence = (
        score_share * 0.65
        + score_margin * 0.35
    )

    return BusinessModelPrediction(
        primary_industry=primary_industry,
        primary_business_model=primary_business_model,
        secondary_business_models=secondary_business_models,
        confidence=round(confidence, 3),
        scores={
            model: round(score, 2)
            for model, score in ranked_scores
        },
    )


__all__ = [
    "BUSINESS_MODEL_PATTERNS",
    "BusinessModelPrediction",
    "classify_business_models",
]