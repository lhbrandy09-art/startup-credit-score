"""
VERO Startup Signal Engine

Detects positive signals, risk indicators, and strategic
company characteristics from a startup description.
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
class SignalPrediction:
    primary_industry: str | None
    positive_signals: list[str]
    risk_indicators: list[str]
    strategic_scores: dict[str, float]
    overall_signal_score: float

    def to_dict(self) -> dict[str, object]:
        return {
            "primary_industry": self.primary_industry,
            "positive_signals": self.positive_signals,
            "risk_indicators": self.risk_indicators,
            "strategic_scores": self.strategic_scores,
            "overall_signal_score": self.overall_signal_score,
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


STRATEGIC_SIGNAL_PATTERNS: dict[str, dict[str, object]] = {
    "technical_depth": {
        "weight": 1.0,
        "patterns": [
            "machine learning",
            "artificial intelligence",
            "clinical nlp",
            "computer vision",
            "proprietary algorithm",
            "proprietary model",
            "deep learning",
            "foundation model",
            "large language model",
            "llm",
            "api infrastructure",
            "real time processing",
            "real-time processing",
            "data pipeline",
            "workflow automation",
            "patented technology",
            "patent pending",
            "research platform",
        ],
    },

    "regulatory_complexity": {
        "weight": 1.0,
        "patterns": [
            "hipaa",
            "fda",
            "fda cleared",
            "fda approved",
            "510k",
            "510 k",
            "clinical validation",
            "clinical trial",
            "medical device",
            "insurance regulation",
            "banking regulation",
            "financial regulation",
            "compliance platform",
            "regulated industry",
            "soc 2",
            "gdpr",
            "hipaa compliant",
            "hipaa compliance",
            "healthcare compliance",
        ],
    },

    "switching_costs": {
        "weight": 1.0,
        "patterns": [
            "integrated into workflow",
            "workflow integration",
            "embedded workflow",
            "system of record",
            "mission critical",
            "mission-critical",
            "enterprise integration",
            "ehr integration",
            "erp integration",
            "crm integration",
            "historical data",
            "custom implementation",
            "employee training",
            "provider training",
            "multi year contract",
            "multi-year contract",
            "annual contract",
            "integrated into workflows",
            "integrated into hospital workflows",
            "hospital workflow integration",
            "clinical workflow integration",
            "embedded in hospital workflows",
        ],
    },

    "data_moat": {
        "weight": 1.0,
        "patterns": [
            "proprietary data",
            "exclusive data",
            "unique dataset",
            "longitudinal data",
            "clinical data",
            "transaction data",
            "behavioral data",
            "training data",
            "data network effect",
            "feedback loop",
            "data advantage",
            "millions of records",
            "billions of records",
            "real world data",
            "real-world data",
        ],
    },

    "network_effects": {
        "weight": 1.0,
        "patterns": [
            "network effect",
            "network effects",
            "marketplace liquidity",
            "buyers and sellers",
            "two sided marketplace",
            "two-sided marketplace",
            "community platform",
            "creator network",
            "provider network",
            "developer ecosystem",
            "partner ecosystem",
            "user generated data",
            "user-generated data",
        ],
    },

    "enterprise_sales_complexity": {
        "weight": 1.0,
        "patterns": [
            "enterprise sales",
            "sales led",
            "sales-led",
            "annual contract",
            "annual contracts",
            "multi year contract",
            "multi-year contract",
            "procurement process",
            "security review",
            "pilot program",
            "implementation period",
            "custom deployment",
            "hospital system",
            "health system",
            "large enterprise",
            "fortune 500",
            "hospital contracts",
            "contracts with hospitals",
            "hospital procurement",
        ],
    },

    "capital_intensity": {
        "weight": 1.0,
        "patterns": [
            "hardware manufacturing",
            "medical device manufacturing",
            "clinical trials",
            "drug development",
            "laboratory infrastructure",
            "manufacturing facility",
            "inventory",
            "warehouse",
            "fleet",
            "physical infrastructure",
            "capital intensive",
            "capital-intensive",
            "regulatory approval",
        ],
    },

    "recurring_revenue": {
        "weight": 1.0,
        "patterns": [
            "subscription",
            "recurring revenue",
            "annual recurring revenue",
            "arr",
            "monthly recurring revenue",
            "mrr",
            "saas",
            "annual contract",
            "multi year contract",
            "multi-year contract",
            "per seat",
            "per user",
            "pmpm",
        ],
    },
}


def _score_patterns(
    normalized_text: str,
    patterns: list[str],
) -> tuple[float, list[str]]:
    score = 0.0
    matches: list[str] = []
    seen: set[str] = set()

    for pattern in patterns:
        normalized_pattern = _normalize_text(pattern)

        if (
            normalized_pattern
            and normalized_pattern not in seen
            and _contains_term(
                normalized_text,
                normalized_pattern,
            )
        ):
            seen.add(normalized_pattern)
            matches.append(pattern)

            word_count = len(normalized_pattern.split())

            if word_count >= 3:
                score += 3.0
            elif word_count == 2:
                score += 2.0
            else:
                score += 1.0

    if len(matches) >= 2:
        score += min(
            2.0,
            (len(matches) - 1) * 0.5,
        )

    return score, matches


def analyze_signals(
    text: str,
    industry_name: str | None = None,
) -> SignalPrediction:
    """
    Analyze strategic signals and risks in a startup description.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    normalized_text = _normalize_text(text)

    if not normalized_text:
        return SignalPrediction(
            primary_industry=None,
            positive_signals=[],
            risk_indicators=[],
            strategic_scores={},
            overall_signal_score=0.0,
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

    strategic_scores: dict[str, float] = {}

    for category, configuration in (
        STRATEGIC_SIGNAL_PATTERNS.items()
    ):
        patterns = configuration.get("patterns", [])
        weight = float(configuration.get("weight", 1.0))

        if not isinstance(patterns, list):
            continue

        raw_score, _ = _score_patterns(
            normalized_text,
            patterns,
        )

        if raw_score > 0:
            normalized_score = min(
                10.0,
                raw_score * weight,
            )

            strategic_scores[category] = round(
                normalized_score,
                2,
            )

    positive_signals: list[str] = []
    risk_indicators: list[str] = []

    ontology = (
        get_industry(primary_industry)
        or find_industry_by_alias(primary_industry or "")
    )

    if ontology is not None:
        positive_values = ontology.get(
            "positive_signals",
            [],
        )
        risk_values = ontology.get(
            "risk_indicators",
            [],
        )

        if isinstance(positive_values, list):
            for signal in positive_values:
                signal_name = str(signal)

                if _contains_term(
                    normalized_text,
                    signal_name,
                ):
                    positive_signals.append(signal_name)

        if isinstance(risk_values, list):
            for risk in risk_values:
                risk_name = str(risk)

                if _contains_term(
                    normalized_text,
                    risk_name,
                ):
                    risk_indicators.append(risk_name)

    positive_category_names = {
        "technical_depth",
        "switching_costs",
        "data_moat",
        "network_effects",
        "recurring_revenue",
    }

    risk_category_names = {
        "regulatory_complexity",
        "enterprise_sales_complexity",
        "capital_intensity",
    }

    positive_score = sum(
        score
        for category, score in strategic_scores.items()
        if category in positive_category_names
    )

    risk_score = sum(
        score
        for category, score in strategic_scores.items()
        if category in risk_category_names
    )

    ontology_positive_bonus = len(positive_signals) * 1.5
    ontology_risk_penalty = len(risk_indicators) * 1.0

    raw_overall_score = (
        50.0
        + positive_score * 2.5
        + ontology_positive_bonus
        - risk_score * 1.5
        - ontology_risk_penalty
    )

    overall_signal_score = max(
        0.0,
        min(100.0, raw_overall_score),
    )

    return SignalPrediction(
        primary_industry=primary_industry,
        positive_signals=positive_signals,
        risk_indicators=risk_indicators,
        strategic_scores=strategic_scores,
        overall_signal_score=round(
            overall_signal_score,
            2,
        ),
    )


__all__ = [
    "STRATEGIC_SIGNAL_PATTERNS",
    "SignalPrediction",
    "analyze_signals",
]