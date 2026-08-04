"""
VERO Business Quality Engine

Evaluates how attractive a business model is from an investor's
perspective.

This engine does NOT measure market size or moat.

Instead it evaluates qualities such as:

• recurring revenue
• scalability
• customer stickiness
• gross margins
• implementation complexity
• sales complexity
• capital efficiency
• expansion revenue
• unit economics
"""

from __future__ import annotations

import re

from dataclasses import dataclass

from .industry_engine import classify
from .keyword_library import (
    find_industry_by_alias,
    get_industry,
)


# ---------------------------------------------------------
# Dataclass
# ---------------------------------------------------------

@dataclass(slots=True)
class BusinessQualityPrediction:

    primary_industry: str | None

    quality_scores: dict[str, float]

    strongest_quality: str | None

    overall_quality_score: float

    evidence: dict[str, list[str]]

    confidence: float

    def to_dict(self):

        return {

            "primary_industry": self.primary_industry,

            "strongest_quality": self.strongest_quality,

            "overall_score": self.overall_quality_score,

            "confidence": self.confidence,

            "scores": self.quality_scores,

            "evidence": self.evidence,
        }


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

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

    return re.search(
        pattern,
        normalized_text,
    ) is not None


def _term_weight(term: str) -> float:

    words = len(
        _normalize_text(term).split()
    )

    if words >= 4:
        return 2.0

    if words == 3:
        return 1.7

    if words == 2:
        return 1.3

    return 1.0


def _resolve_industry(
    text: str,
    industry_name: str | None,
):

    if industry_name is None:

        prediction = classify(text)

        return prediction.primary_industry

    ontology = (
        get_industry(industry_name)
        or find_industry_by_alias(industry_name)
    )

    if ontology is None:
        return industry_name

    return ontology["name"]


# ---------------------------------------------------------
# Quality Categories
# ---------------------------------------------------------

QUALITY_CATEGORIES = [

    "recurring_revenue",

    "gross_margin",

    "scalability",

    "customer_stickiness",

    "sales_complexity",

    "implementation_complexity",

    "capital_efficiency",

    "expansion_revenue",

    "unit_economics",

]

QUALITY_PATTERNS = {

    "recurring_revenue": [

        "subscription",
        "subscriptions",
        "monthly subscription",
        "annual subscription",
        "subscription revenue",
        "recurring revenue",
        "monthly recurring revenue",
        "mrr",
        "annual recurring revenue",
        "arr",
        "enterprise contract",
        "enterprise contracts",
        "multi year contract",
        "multi-year contract",
        "annual contract",
        "annual contracts",
        "seat license",
        "seat licenses",
        "per seat",
        "per-seat",
        "usage based pricing",
        "usage-based pricing",
        "api billing",
        "platform fee",
        "software license",
        "renewal",
        "renewals",
        "contract renewal",
        "long term customer",
        "long-term customer",
    ],

    "gross_margin": [

        "software platform",
        "software only",
        "digital platform",
        "digital product",
        "cloud platform",
        "cloud native",
        "cloud-native",
        "saas",
        "enterprise saas",
        "api",
        "automation",
        "artificial intelligence",
        "machine learning",
        "no inventory",
        "asset light",
        "asset-light",
        "minimal hardware",
        "high margin",
        "gross margin",
        "gross margins",
        "software margins",
        "low variable cost",
        "low marginal cost",
        "high operating leverage",
    ],

    "scalability": [

        "scalable",
        "highly scalable",
        "cloud infrastructure",
        "multi tenant",
        "multi-tenant",
        "automation",
        "self service",
        "self-service",
        "platform",
        "api",
        "repeatable",
        "repeatable sales",
        "repeatable deployment",
        "standardized deployment",
        "global deployment",
        "distributed infrastructure",
        "software platform",
        "digital platform",
        "remote deployment",
        "instant deployment",
        "automated onboarding",
    ],

    "customer_stickiness": [

        "mission critical",
        "mission-critical",
        "system of record",
        "workflow integration",
        "deep integration",
        "embedded workflow",
        "customer retention",
        "high retention",
        "low churn",
        "net revenue retention",
        "expansion revenue",
        "historical data",
        "data migration",
        "custom implementation",
        "training",
        "staff training",
        "clinical workflow",
        "enterprise workflow",
        "switching costs",
    ],

    "sales_complexity": [

        "enterprise sales",
        "enterprise sales team",
        "hospital procurement",
        "government procurement",
        "buying committee",
        "procurement process",
        "request for proposal",
        "rfp",
        "pilot program",
        "sales cycle",
        "long sales cycle",
        "enterprise contract",
        "implementation team",
        "legal review",
        "security review",
        "compliance review",
        "multiple stakeholders",
        "cio approval",
        "board approval",
    ],

    "implementation_complexity": [

        "implementation",
        "deployment",
        "onboarding",
        "customer onboarding",
        "migration",
        "data migration",
        "ehr integration",
        "emr integration",
        "erp integration",
        "crm integration",
        "workflow integration",
        "training",
        "consulting",
        "custom integration",
        "professional services",
        "configuration",
        "change management",
    ],

    "capital_efficiency": [

        "asset light",
        "asset-light",
        "software only",
        "minimal hardware",
        "bootstrapped",
        "capital efficient",
        "capital-light",
        "low infrastructure cost",
        "cloud infrastructure",
        "outsourced manufacturing",
        "digital product",
        "automation",
        "self service",
        "high gross margin",
        "minimal inventory",
    ],

    "expansion_revenue": [

        "upsell",
        "upsells",
        "cross sell",
        "cross-sell",
        "seat expansion",
        "account expansion",
        "enterprise expansion",
        "additional modules",
        "additional seats",
        "premium tier",
        "premium features",
        "land and expand",
        "land-and-expand",
        "multi product",
        "multi-product",
        "platform expansion",
    ],

    "unit_economics": [

        "ltv",
        "cac",
        "customer acquisition cost",
        "lifetime value",
        "payback period",
        "gross retention",
        "net retention",
        "net revenue retention",
        "high gross margin",
        "efficient sales",
        "efficient growth",
        "organic acquisition",
        "low acquisition cost",
        "high retention",
        "repeat customer",
        "repeat customers",
    ],

}

INDUSTRY_QUALITY_BASELINES = {

    "Artificial Intelligence": {

        "recurring_revenue": 6.5,
        "gross_margin": 8.5,
        "scalability": 8.5,
        "customer_stickiness": 6.0,
        "sales_complexity": 6.0,
        "implementation_complexity": 5.0,
        "capital_efficiency": 7.0,
        "expansion_revenue": 6.5,
        "unit_economics": 6.5,
    },

    "Healthcare": {

        "recurring_revenue": 6.5,
        "gross_margin": 7.5,
        "scalability": 6.5,
        "customer_stickiness": 8.0,
        "sales_complexity": 8.5,
        "implementation_complexity": 8.0,
        "capital_efficiency": 5.5,
        "expansion_revenue": 7.0,
        "unit_economics": 6.5,
    },

    "Financial Technology": {

        "recurring_revenue": 6.0,
        "gross_margin": 8.0,
        "scalability": 8.0,
        "customer_stickiness": 7.0,
        "sales_complexity": 6.5,
        "implementation_complexity": 5.5,
        "capital_efficiency": 7.0,
        "expansion_revenue": 6.5,
        "unit_economics": 6.5,
    },

}

def _collect_matches(
    normalized_text: str,
    terms: list[str],
) -> tuple[list[str], float]:
    matches: list[str] = []
    matched_normalized: list[str] = []
    score = 0.0

    sorted_terms = sorted(
        terms,
        key=lambda value: len(_normalize_text(value)),
        reverse=True,
    )

    for term in sorted_terms:
        normalized_term = _normalize_text(term)

        if not normalized_term:
            continue

        # Prevent shorter phrases from being counted when they are
        # already contained inside a longer matched phrase.
        if any(
            normalized_term in existing_term
            for existing_term in matched_normalized
        ):
            continue

        if _contains_term(normalized_text, term):
            matches.append(term)
            matched_normalized.append(normalized_term)
            score += _term_weight(term)

    return matches, score


def _clamp_score(score: float) -> float:
    return max(0.0, min(10.0, score))


def analyze_business_quality(
    text: str,
    industry_name: str | None = None,
) -> BusinessQualityPrediction:
    """
    Evaluate the quality of a startup's business model.

    High scores are favorable for most categories.

    For sales complexity and implementation complexity, the stored
    score represents business attractiveness:

    - 10 means low complexity
    - 0 means very high complexity
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    normalized_text = _normalize_text(text)

    primary_industry = _resolve_industry(
        text=text,
        industry_name=industry_name,
    )

    default_baselines = {
        "recurring_revenue": 5.0,
        "gross_margin": 5.0,
        "scalability": 5.0,
        "customer_stickiness": 5.0,
        "sales_complexity": 5.0,
        "implementation_complexity": 5.0,
        "capital_efficiency": 5.0,
        "expansion_revenue": 5.0,
        "unit_economics": 5.0,
    }

    baselines = INDUSTRY_QUALITY_BASELINES.get(
        primary_industry or "",
        default_baselines,
    )

    evidence: dict[str, list[str]] = {}
    raw_scores: dict[str, float] = {}

    for category in QUALITY_CATEGORIES:
        matches, match_score = _collect_matches(
            normalized_text,
            QUALITY_PATTERNS[category],
        )

        if matches:
            evidence[category] = matches

        baseline = baselines.get(category, 5.0)

        if category in {
            "sales_complexity",
            "implementation_complexity",
        }:
            # Industry baselines describe the expected complexity level.
            # Convert that into an attractiveness score where lower
            # complexity is better.
            baseline_attractiveness = 10.0 - baseline

            score = baseline_attractiveness - match_score * 0.25
        else:
            score = baseline + match_score * 0.45

        raw_scores[category] = _clamp_score(score)

    quality_scores = {
        category: round(score, 2)
        for category, score in sorted(
            raw_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    }

    strongest_quality = (
        next(iter(quality_scores))
        if quality_scores
        else None
    )

    QUALITY_WEIGHTS = {
        "recurring_revenue": 0.15,
        "gross_margin": 0.14,
        "scalability": 0.14,
        "customer_stickiness": 0.13,
        "sales_complexity": 0.10,
        "implementation_complexity": 0.08,
        "capital_efficiency": 0.10,
        "expansion_revenue": 0.08,
        "unit_economics": 0.08,
    }

    overall_quality_score = sum(
        raw_scores[category] * QUALITY_WEIGHTS[category]
        for category in QUALITY_CATEGORIES
    )

    total_evidence = sum(
        len(items)
        for items in evidence.values()
    )

    evidence_confidence = min(
        1.0,
        total_evidence / 30,
    )

    category_coverage = min(
        1.0,
        len(evidence) / 12,
    )

    industry_confidence = (
        1.0
        if primary_industry in INDUSTRY_QUALITY_BASELINES
        else 0.5
    )

    confidence = (
        evidence_confidence * 0.50
        + category_coverage * 0.30
        + industry_confidence * 0.20
    )

    return BusinessQualityPrediction(
        primary_industry=primary_industry,
        quality_scores=quality_scores,
        strongest_quality=strongest_quality,
        overall_quality_score=round(
            overall_quality_score,
            2,
        ),
        evidence=evidence,
        confidence=round(confidence, 3),
    )


__all__ = [
    "QUALITY_CATEGORIES",
    "QUALITY_PATTERNS",
    "INDUSTRY_QUALITY_BASELINES",
    "BusinessQualityPrediction",
    "analyze_business_quality",
]