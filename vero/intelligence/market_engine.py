"""
VERO Market Intelligence Engine

Estimates market attractiveness using industry context,
company description, competition, growth indicators,
market maturity, and fragmentation signals.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .industry_engine import classify
from .keyword_library import (
    find_industry_by_alias,
    get_industry,
)


MARKET_PATTERNS: dict[str, dict[str, list[str]]] = {
    "market_growth": {
        "positive": [
            "fast growing market",
            "fast-growing market",
            "rapidly growing market",
            "rapid growth",
            "high growth",
            "growing demand",
            "increasing demand",
            "surging demand",
            "expanding market",
            "market expansion",
            "industry growth",
            "strong growth",
            "accelerating adoption",
            "increasing adoption",
            "rising adoption",
            "digital transformation",
            "regulatory tailwind",
            "regulatory tailwinds",
            "demographic tailwind",
            "demographic tailwinds",
            "labor shortage",
            "labor shortages",
            "aging population",
            "consumer shift",
            "technology adoption",
            "cloud adoption",
            "ai adoption",
            "automation adoption",
            "underserved demand",
            "unmet demand",
            "new market",
            "emerging market",
            "compound annual growth rate",
            "cagr",
            "rapidly growing",
            "fast growing",
            "growing market",
        ],
        "negative": [
            "declining market",
            "shrinking market",
            "falling demand",
            "decreasing demand",
            "slow growth",
            "stagnant market",
            "market contraction",
            "limited growth",
            "mature demand",
            "saturated demand",
            "customer decline",
            "industry decline",
        ],
    },

    "market_maturity": {
        "emerging": [
            "emerging category",
            "emerging market",
            "new category",
            "new market",
            "nascent market",
            "early market",
            "early stage market",
            "early-stage market",
            "category creation",
            "category creator",
            "first of its kind",
            "first-of-its-kind",
            "new technology",
            "recently enabled",
            "newly possible",
            "greenfield opportunity",
            "untapped market",
            "underdeveloped market",
        ],
        "mature": [
            "mature market",
            "established market",
            "well established",
            "well-established",
            "legacy market",
            "traditional industry",
            "existing category",
            "commodity market",
            "standardized market",
            "consolidated market",
            "market leader",
            "incumbent",
            "incumbents",
            "decades old",
            "decades-old",
        ],
    },

    "competitive_intensity": {
        "high": [
            "highly competitive",
            "competitive market",
            "crowded market",
            "crowded category",
            "many competitors",
            "numerous competitors",
            "saturated market",
            "intense competition",
            "competitive landscape",
            "major incumbents",
            "large incumbents",
            "dominant incumbent",
            "dominant incumbents",
            "price competition",
            "pricing pressure",
            "low differentiation",
            "commoditized",
            "commodity product",
            "red ocean",
        ],
        "low": [
            "limited competition",
            "few competitors",
            "little competition",
            "low competition",
            "underserved market",
            "white space",
            "whitespace opportunity",
            "unique category",
            "category creator",
            "first mover",
            "first-mover",
            "uncontested market",
            "greenfield opportunity",
            "fragmented incumbents",
        ],
    },

    "fragmentation": {
        "high": [
            "fragmented market",
            "highly fragmented",
            "many small providers",
            "many local providers",
            "independent providers",
            "regional providers",
            "small competitors",
            "local competitors",
            "no dominant player",
            "no clear leader",
            "market fragmentation",
            "fragmented industry",
            "long tail of providers",
            "long-tail providers",
            "thousands of providers",
            "multiple point solutions",
            "remains fragmented",
            "fragmented across",
            "fragmented across providers",
        ],
        "low": [
            "concentrated market",
            "market concentration",
            "few dominant players",
            "dominated by",
            "dominant players",
            "market leader",
            "market leaders",
            "oligopoly",
            "consolidated market",
            "large incumbents",
            "winner take most",
            "winner-take-most",
            "winner take all",
            "winner-take-all",
        ],
    },

    "market_need": {
        "positive": [
            "pain point",
            "major pain point",
            "urgent problem",
            "critical problem",
            "mission critical problem",
            "mission-critical problem",
            "unmet need",
            "unmet needs",
            "underserved",
            "inefficient",
            "inefficiency",
            "inefficiencies",
            "manual process",
            "manual workflow",
            "time consuming",
            "time-consuming",
            "expensive process",
            "high cost",
            "costly",
            "shortage",
            "labor shortage",
            "staff shortage",
            "provider shortage",
            "poor access",
            "lack of access",
            "low availability",
            "long wait times",
            "administrative burden",
            "workflow burden",
        ],
        "negative": [
            "nice to have",
            "nice-to-have",
            "optional product",
            "low priority",
            "weak demand",
            "limited demand",
            "unclear need",
            "minor inconvenience",
            "nonessential",
            "non-essential",
        ],
    },
}


INDUSTRY_BASELINES: dict[str, dict[str, float]] = {
    "Artificial Intelligence": {
        "market_growth": 7.5,
        "competitive_intensity": 8.0,
        "fragmentation": 6.5,
        "market_need": 6.5,
        "market_maturity": 4.5,
    },
    "Healthcare": {
        "market_growth": 6.5,
        "competitive_intensity": 6.5,
        "fragmentation": 7.0,
        "market_need": 8.0,
        "market_maturity": 7.0,
    },
    "Financial Technology": {
        "market_growth": 6.5,
        "competitive_intensity": 8.0,
        "fragmentation": 5.5,
        "market_need": 7.0,
        "market_maturity": 7.0,
    },
}


@dataclass(slots=True)
class MarketPrediction:
    primary_industry: str | None
    market_growth_score: float
    market_maturity_score: float
    competitive_intensity_score: float
    fragmentation_score: float
    market_need_score: float
    overall_market_score: float
    market_stage: str
    evidence: dict[str, list[str]]
    confidence: float

    def to_dict(self) -> dict[str, object]:
        return {
            "primary_industry": self.primary_industry,
            "market_stage": self.market_stage,
            "overall_score": self.overall_market_score,
            "confidence": self.confidence,
            "scores": {
                "market_growth": self.market_growth_score,
                "market_maturity": self.market_maturity_score,
                "competitive_intensity": (
                    self.competitive_intensity_score
                ),
                "fragmentation": self.fragmentation_score,
                "market_need": self.market_need_score,
            },
            "evidence": self.evidence,
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


def _term_weight(term: str) -> float:
    word_count = len(_normalize_text(term).split())

    if word_count >= 4:
        return 1.5

    if word_count == 3:
        return 1.25

    if word_count == 2:
        return 1.0

    return 0.75


def _resolve_industry(
    text: str,
    industry_name: str | None,
) -> str | None:
    if industry_name is None:
        return classify(text).primary_industry

    ontology = (
        get_industry(industry_name)
        or find_industry_by_alias(industry_name)
    )

    if ontology is None:
        return industry_name

    return str(ontology["name"])


def _collect_matches(
    normalized_text: str,
    terms: list[str],
) -> tuple[list[str], float]:
    matches: list[str] = []
    score = 0.0
    seen: set[str] = set()

    for term in sorted(
        terms,
        key=lambda value: len(_normalize_text(value)),
        reverse=True,
    ):
        normalized_term = _normalize_text(term)

        if (
            normalized_term
            and normalized_term not in seen
            and _contains_term(normalized_text, term)
        ):
            seen.add(normalized_term)
            matches.append(term)
            score += _term_weight(term)

    return matches, score


def _clamp_score(score: float) -> float:
    return max(0.0, min(10.0, score))


def _market_stage(
    maturity_score: float,
    growth_score: float,
) -> str:
    if maturity_score <= 4.0 and growth_score >= 6.5:
        return "Emerging"

    if maturity_score <= 6.5 and growth_score >= 5.0:
        return "Growth"

    if maturity_score >= 7.5 and growth_score <= 5.0:
        return "Mature"

    if maturity_score >= 7.5 and growth_score > 5.0:
        return "Established Growth"

    return "Developing"


def analyze_market(
    text: str,
    industry_name: str | None = None,
    competitor_count: int | None = None,
) -> MarketPrediction:
    """
    Estimate market attractiveness from free text.

    competitor_count can be supplied from the competitor engine.
    It is treated as evidence of competitive intensity, not as an
    exact count of all companies in the market.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if competitor_count is not None and competitor_count < 0:
        raise ValueError("competitor_count cannot be negative.")

    normalized_text = _normalize_text(text)

    primary_industry = _resolve_industry(
        text=text,
        industry_name=industry_name,
    )

    baselines = INDUSTRY_BASELINES.get(
        primary_industry or "",
        {
            "market_growth": 5.0,
            "competitive_intensity": 5.0,
            "fragmentation": 5.0,
            "market_need": 5.0,
            "market_maturity": 5.0,
        },
    )

    evidence: dict[str, list[str]] = {}

    growth_positive, growth_positive_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["market_growth"]["positive"],
    )

    growth_negative, growth_negative_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["market_growth"]["negative"],
    )

    if growth_positive or growth_negative:
        evidence["market_growth"] = (
            growth_positive + growth_negative
        )

    market_growth_score = _clamp_score(
        baselines["market_growth"]
        + growth_positive_score * 0.7
        - growth_negative_score * 0.9
    )

    emerging_matches, emerging_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["market_maturity"]["emerging"],
    )

    mature_matches, mature_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["market_maturity"]["mature"],
    )

    if emerging_matches or mature_matches:
        evidence["market_maturity"] = (
            emerging_matches + mature_matches
        )

    market_maturity_score = _clamp_score(
        baselines["market_maturity"]
        - emerging_score * 0.7
        + mature_score * 0.7
    )

    competition_high, competition_high_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["competitive_intensity"]["high"],
    )

    competition_low, competition_low_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["competitive_intensity"]["low"],
    )

    if competition_high or competition_low:
        evidence["competitive_intensity"] = (
            competition_high + competition_low
        )

    competitor_bonus = 0.0

    if competitor_count is not None:
        if competitor_count >= 8:
            competitor_bonus = 2.0
        elif competitor_count >= 5:
            competitor_bonus = 1.25
        elif competitor_count >= 3:
            competitor_bonus = 0.75

    competitive_intensity_score = _clamp_score(
        baselines["competitive_intensity"]
        + competition_high_score * 0.7
        - competition_low_score * 0.7
        + competitor_bonus
    )

    fragmentation_high, fragmentation_high_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["fragmentation"]["high"],
    )

    fragmentation_low, fragmentation_low_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["fragmentation"]["low"],
    )

    if fragmentation_high or fragmentation_low:
        evidence["fragmentation"] = (
            fragmentation_high + fragmentation_low
        )

    fragmentation_score = _clamp_score(
        baselines["fragmentation"]
        + fragmentation_high_score * 0.7
        - fragmentation_low_score * 0.7
    )

    need_positive, need_positive_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["market_need"]["positive"],
    )

    need_negative, need_negative_score = _collect_matches(
        normalized_text,
        MARKET_PATTERNS["market_need"]["negative"],
    )

    if need_positive or need_negative:
        evidence["market_need"] = (
            need_positive + need_negative
        )

    market_need_score = _clamp_score(
        baselines["market_need"]
        + need_positive_score * 0.7
        - need_negative_score * 0.9
    )

    growth_component = market_growth_score
    need_component = market_need_score
    fragmentation_component = fragmentation_score

    # Lower competition is generally more attractive.
    competition_attractiveness = (
        10.0 - competitive_intensity_score
    )

    # Growth-stage markets are often more attractive than markets
    # that are extremely early or fully mature.
    maturity_attractiveness = max(
        0.0,
        10.0 - abs(market_maturity_score - 6.0) * 1.4,
    )

    overall_market_score = (
        growth_component * 0.30
        + need_component * 0.25
        + competition_attractiveness * 0.20
        + fragmentation_component * 0.10
        + maturity_attractiveness * 0.15
    )

    total_evidence = sum(
        len(items)
        for items in evidence.values()
    )

    evidence_confidence = min(
        1.0,
        total_evidence / 8,
    )

    industry_confidence = (
        1.0
        if primary_industry in INDUSTRY_BASELINES
        else 0.5
    )

    competitor_confidence = (
        1.0
        if competitor_count is not None
        else 0.0
    )

    confidence = (
        evidence_confidence * 0.55
        + industry_confidence * 0.30
        + competitor_confidence * 0.15
    )

    return MarketPrediction(
        primary_industry=primary_industry,
        market_growth_score=round(
            market_growth_score,
            2,
        ),
        market_maturity_score=round(
            market_maturity_score,
            2,
        ),
        competitive_intensity_score=round(
            competitive_intensity_score,
            2,
        ),
        fragmentation_score=round(
            fragmentation_score,
            2,
        ),
        market_need_score=round(
            market_need_score,
            2,
        ),
        overall_market_score=round(
            overall_market_score,
            2,
        ),
        market_stage=_market_stage(
            maturity_score=market_maturity_score,
            growth_score=market_growth_score,
        ),
        evidence=evidence,
        confidence=round(confidence, 3),
    )


__all__ = [
    "MARKET_PATTERNS",
    "INDUSTRY_BASELINES",
    "MarketPrediction",
    "analyze_market",
]