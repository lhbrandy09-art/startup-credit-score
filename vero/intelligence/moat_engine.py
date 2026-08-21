"""
VERO Competitive Moat Engine

Estimates a startup's defensibility across multiple moat categories
using its company description and previously detected strategic signals.

This is a heuristic engine. Its results should be treated as structured
evidence for investment analysis, not as a final investment decision.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .industry_engine import classify
from .keyword_library import (
    find_industry_by_alias,
    get_industry,
)


MOAT_PATTERNS: dict[str, list[str]] = {
    "technology_moat": [
        "proprietary technology",
        "proprietary model",
        "proprietary algorithm",
        "proprietary software",
        "custom architecture",
        "novel architecture",
        "patented technology",
        "patented",
        "patent pending",
        "patent portfolio",
        "intellectual property",
        "trade secret",
        "technical breakthrough",
        "scientific breakthrough",
        "research platform",
        "research and development",
        "machine learning",
        "artificial intelligence",
        "deep learning",
        "foundation model",
        "large language model",
        "llm",
        "computer vision",
        "clinical nlp",
        "natural language processing",
        "knowledge graph",
        "reasoning engine",
        "recommendation engine",
        "optimization engine",
        "simulation engine",
        "inference engine",
        "real time processing",
        "real-time processing",
        "edge computing",
        "computer infrastructure",
        "developer infrastructure",
        "cloud infrastructure",
        "distributed system",
        "distributed systems",
        "high performance computing",
        "high-performance computing",
        "gpu infrastructure",
        "compiler",
        "robotics",
        "automation platform",
        "advanced manufacturing",
        "synthetic biology",
        "gene editing",
        "drug discovery platform",
    ],

    "data_moat": [
        "proprietary data",
        "proprietary dataset",
        "proprietary datasets",
        "exclusive data",
        "exclusive dataset",
        "unique data",
        "unique dataset",
        "first party data",
        "first-party data",
        "longitudinal data",
        "historical data",
        "clinical data",
        "proprietary clinical data",
        "healthcare data",
        "transaction data",
        "financial data",
        "behavioral data",
        "usage data",
        "training data",
        "real world data",
        "real-world data",
        "patient data",
        "medical records",
        "data network effect",
        "data feedback loop",
        "feedback loop",
        "continuous learning",
        "improves with usage",
        "improves with more data",
        "data advantage",
        "data flywheel",
        "data asset",
        "data assets",
        "millions of records",
        "billions of records",
        "millions of transactions",
        "billions of transactions",
        "exclusive partnership data",
        "customer generated data",
        "customer-generated data",
        "user generated data",
        "user-generated data",
        "annotated data",
        "labeled data",
        "benchmark dataset",
        "data enrichment",
        "data aggregation",
        "data consortium",
    ],

    "switching_costs": [
        "switching costs",
        "high switching costs",
        "system of record",
        "mission critical",
        "mission-critical",
        "core workflow",
        "embedded workflow",
        "embedded in workflow",
        "integrated into workflow",
        "integrated into workflows",
        "integrated into hospital workflows",
        "workflow integration",
        "clinical workflow integration",
        "hospital workflow integration",
        "enterprise integration",
        "deep integration",
        "custom integration",
        "ehr integration",
        "emr integration",
        "erp integration",
        "crm integration",
        "api integration",
        "legacy system integration",
        "historical data",
        "data migration",
        "custom implementation",
        "custom deployment",
        "implementation period",
        "implementation process",
        "employee training",
        "provider training",
        "customer training",
        "annual contract",
        "annual contracts",
        "multi year contract",
        "multi-year contract",
        "multi year contracts",
        "multi-year contracts",
        "enterprise contract",
        "enterprise contracts",
        "long term contract",
        "long-term contract",
        "workflow dependency",
        "operational dependency",
        "platform dependency",
        "high retention",
        "low churn",
        "net revenue retention",
        "expansion revenue",
    ],

    "network_effects": [
        "network effect",
        "network effects",
        "direct network effect",
        "indirect network effect",
        "data network effect",
        "two sided marketplace",
        "two-sided marketplace",
        "multi sided marketplace",
        "multi-sided marketplace",
        "buyers and sellers",
        "supply and demand",
        "marketplace liquidity",
        "liquidity",
        "provider network",
        "supplier network",
        "merchant network",
        "consumer network",
        "professional network",
        "social network",
        "community platform",
        "community driven",
        "community-driven",
        "creator network",
        "developer network",
        "developer ecosystem",
        "partner ecosystem",
        "integration ecosystem",
        "application ecosystem",
        "app ecosystem",
        "platform ecosystem",
        "more valuable with more users",
        "value increases with users",
        "user generated content",
        "user-generated content",
        "user generated data",
        "user-generated data",
        "collaboration platform",
        "referral loop",
        "viral growth",
        "viral loop",
        "word of mouth",
        "word-of-mouth",
        "marketplace flywheel",
        "network flywheel",
    ],

    "brand_moat": [
        "trusted brand",
        "strong brand",
        "recognized brand",
        "category leader",
        "category leadership",
        "market leader",
        "industry leader",
        "leading provider",
        "leading platform",
        "household name",
        "brand recognition",
        "brand loyalty",
        "customer loyalty",
        "trusted by",
        "trusted platform",
        "premium brand",
        "award winning",
        "award-winning",
        "industry award",
        "industry awards",
        "best in class",
        "best-in-class",
        "top rated",
        "top-rated",
        "number one",
        "preferred provider",
        "preferred platform",
        "customer advocacy",
        "strong reputation",
        "industry reputation",
        "thought leadership",
        "organic demand",
        "organic traffic",
        "direct traffic",
        "high net promoter score",
        "high nps",
        "customer love",
    ],

    "regulatory_moat": [
        "regulatory approval",
        "regulatory approvals",
        "fda approved",
        "fda approval",
        "fda cleared",
        "fda clearance",
        "510k clearance",
        "510 k clearance",
        "clinical validation",
        "clinically validated",
        "clinical trial",
        "clinical trials",
        "hipaa compliant",
        "hipaa compliance",
        "hipaa certified",
        "soc 2",
        "soc2",
        "soc 2 type ii",
        "iso 27001",
        "gdpr compliant",
        "gdpr compliance",
        "pci compliant",
        "pci compliance",
        "banking license",
        "bank charter",
        "money transmitter license",
        "insurance license",
        "broker dealer",
        "broker-dealer",
        "regulated entity",
        "government certification",
        "government approval",
        "security clearance",
        "compliance certification",
        "medical device approval",
        "reimbursement approval",
        "insurance reimbursement",
        "patent protection",
        "regulatory expertise",
        "regulatory relationships",
        "compliance infrastructure",
        "quality management system",
        "gmp certified",
        "good manufacturing practice",
    ],

    "distribution_moat": [
        "exclusive distribution",
        "exclusive distributor",
        "exclusive partnership",
        "exclusive partnerships",
        "strategic partnership",
        "strategic partnerships",
        "channel partnership",
        "channel partnerships",
        "distribution agreement",
        "distribution agreements",
        "reseller network",
        "partner network",
        "partner ecosystem",
        "embedded distribution",
        "product led growth",
        "product-led growth",
        "viral distribution",
        "organic acquisition",
        "organic growth",
        "low customer acquisition cost",
        "low cac",
        "inbound demand",
        "direct sales force",
        "enterprise sales team",
        "developer adoption",
        "developer community",
        "open source adoption",
        "open-source adoption",
        "app store distribution",
        "marketplace distribution",
        "platform partnership",
        "bank partnership",
        "hospital partnership",
        "health system partnership",
        "employer partnership",
        "retail partnership",
        "government contract",
        "government contracts",
        "global distribution",
        "international distribution",
        "installed base",
        "existing customer base",
        "cross sell",
        "cross-sell",
        "upsell",
    ],

    "economies_of_scale": [
        "economies of scale",
        "scale advantage",
        "cost advantage",
        "cost advantages",
        "lower unit cost",
        "declining unit cost",
        "marginal cost",
        "near zero marginal cost",
        "near-zero marginal cost",
        "software margins",
        "high gross margin",
        "high gross margins",
        "operating leverage",
        "fixed cost leverage",
        "shared infrastructure",
        "cloud infrastructure",
        "automated operations",
        "automation",
        "self service",
        "self-service",
        "standardized deployment",
        "repeatable deployment",
        "repeatable sales motion",
        "centralized platform",
        "centralized infrastructure",
        "bulk purchasing",
        "purchasing power",
        "volume discount",
        "volume discounts",
        "manufacturing scale",
        "supply chain scale",
        "logistics network",
        "global infrastructure",
        "multi tenant",
        "multi-tenant",
        "shared data platform",
        "shared technology platform",
        "platform leverage",
        "fixed infrastructure",
        "capacity utilization",
        "large installed base",
        "scale efficiencies",
    ],
}


INDUSTRY_MOAT_WEIGHTS: dict[str, dict[str, float]] = {
    "Artificial Intelligence": {
        "technology_moat": 1.15,
        "data_moat": 1.15,
        "network_effects": 1.05,
    },
    "Financial Technology": {
        "regulatory_moat": 1.15,
        "switching_costs": 1.10,
        "distribution_moat": 1.05,
    },
    "Healthcare": {
        "regulatory_moat": 1.20,
        "switching_costs": 1.15,
        "data_moat": 1.10,
        "technology_moat": 1.05,
    },
}


@dataclass(slots=True)
class MoatPrediction:
    primary_industry: str | None
    strongest_moat: str | None
    moat_scores: dict[str, float]
    evidence: dict[str, list[str]]
    overall_moat_score: float
    confidence: float

    def to_dict(self) -> dict[str, object]:
        return {
            "primary_industry": self.primary_industry,
            "strongest_moat": self.strongest_moat,
            "overall_score": self.overall_moat_score,
            "confidence": self.confidence,
            "scores": self.moat_scores,
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
    """
    Give longer, more specific phrases more weight than broad
    one-word indicators.
    """

    normalized_term = _normalize_text(term)
    word_count = len(normalized_term.split())

    if word_count >= 4:
        return 3.5

    if word_count == 3:
        return 3.0

    if word_count == 2:
        return 2.0

    return 1.0


def _resolve_industry(
    text: str,
    industry_name: str | None,
) -> str | None:
    if industry_name is None:
        prediction = classify(text)
        return prediction.primary_industry

    ontology = (
        get_industry(industry_name)
        or find_industry_by_alias(industry_name)
    )

    if ontology is None:
        return None

    return str(ontology["name"])



def _split_evidence_sections(text: str) -> tuple[str, str]:
    """Separate direct/source evidence from VERO-inferred structural evidence.

    Compare-page enrichment appends a section beginning with
    "Structural evidence:". Terms found only in that section should help the
    engine reason about likely moat structure, but should not be treated as
    verified proof at full strength.
    """
    marker = "structural evidence:"
    lowered = text.casefold()

    marker_index = lowered.find(marker)

    if marker_index == -1:
        return text, ""

    direct_text = text[:marker_index]
    inferred_text = text[marker_index + len(marker):]

    return direct_text, inferred_text


def _evidence_strength(
    direct_normalized: str,
    inferred_normalized: str,
    term: str,
) -> tuple[float, str | None]:
    """Return the weight multiplier and provenance for one matched term."""
    if _contains_term(direct_normalized, term):
        return 1.0, "direct"

    if inferred_normalized and _contains_term(
        inferred_normalized,
        term,
    ):
        # Structural inference is intentionally much weaker than direct proof.
        return 0.32, "inferred"

    return 0.0, None

def analyze_moats(
    text: str,
    industry_name: str | None = None,
    minimum_score: float = 0.5,
) -> MoatPrediction:
    """
    Estimate a startup's competitive moats from free text.

    Direct/source evidence receives full weight.
    VERO-inferred structural evidence receives partial weight and cannot,
    by itself, produce a near-perfect moat score.

    Scores remain normalized from 0 to 10. Missing evidence produces
    a score of zero rather than assuming that a moat does not exist.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if minimum_score < 0:
        raise ValueError("minimum_score cannot be negative.")

    normalized_text = _normalize_text(text)

    if not normalized_text:
        return MoatPrediction(
            primary_industry=None,
            strongest_moat=None,
            moat_scores={},
            evidence={},
            overall_moat_score=0.0,
            confidence=0.0,
        )

    direct_text, inferred_text = _split_evidence_sections(text)

    direct_normalized = _normalize_text(direct_text)
    inferred_normalized = _normalize_text(inferred_text)

    primary_industry = _resolve_industry(
        text=text,
        industry_name=industry_name,
    )

    industry_weights = INDUSTRY_MOAT_WEIGHTS.get(
        primary_industry or "",
        {},
    )

    moat_scores: dict[str, float] = {}
    evidence: dict[str, list[str]] = {}

    # Track provenance separately so confidence and caps can distinguish
    # verified evidence from structural inference.
    direct_match_counts: dict[str, int] = {}
    inferred_match_counts: dict[str, int] = {}

    for moat_name, patterns in MOAT_PATTERNS.items():
        matched_terms: list[str] = []
        seen: set[str] = set()

        direct_raw = 0.0
        inferred_raw = 0.0
        direct_count = 0
        inferred_count = 0

        sorted_patterns = sorted(
            patterns,
            key=lambda value: len(_normalize_text(value)),
            reverse=True,
        )

        for pattern in sorted_patterns:
            normalized_pattern = _normalize_text(pattern)

            if (
                not normalized_pattern
                or normalized_pattern in seen
            ):
                continue

            strength, provenance = _evidence_strength(
                direct_normalized=direct_normalized,
                inferred_normalized=inferred_normalized,
                term=normalized_pattern,
            )

            if provenance is None:
                continue

            seen.add(normalized_pattern)

            base_weight = _term_weight(pattern)

            if provenance == "direct":
                direct_count += 1
                direct_raw += base_weight
                matched_terms.append(pattern)
            else:
                inferred_count += 1
                inferred_raw += base_weight * strength
                matched_terms.append(
                    f"{pattern} [inferred]"
                )

        # Synergy should mostly reward multiple direct observations.
        if direct_count >= 2:
            direct_raw += min(
                1.25,
                (direct_count - 1) * 0.25,
            )

        # Inferred-only breadth can help, but only slightly.
        if inferred_count >= 2:
            inferred_raw += min(
                0.45,
                (inferred_count - 1) * 0.08,
            )

        raw_score = direct_raw + inferred_raw

        industry_multiplier = industry_weights.get(
            moat_name,
            1.0,
        )

        weighted_score = raw_score * industry_multiplier

        # Gentler normalization than the previous 0.85 multiplier.
        # Direct evidence can still reach very high scores, but it now
        # requires substantial, specific support.
        normalized_score = weighted_score * 0.68

        # Structural inference alone must never imply an elite moat.
        if direct_count == 0 and inferred_count > 0:
            normalized_score = min(
                normalized_score,
                5.25,
            )

        # One direct phrase plus inferred structure is still not enough
        # for a near-perfect category score.
        elif direct_count == 1:
            normalized_score = min(
                normalized_score,
                7.0,
            )

        normalized_score = min(
            10.0,
            normalized_score,
        )

        if normalized_score >= minimum_score:
            moat_scores[moat_name] = round(
                normalized_score,
                2,
            )
            evidence[moat_name] = matched_terms
            direct_match_counts[moat_name] = direct_count
            inferred_match_counts[moat_name] = inferred_count

    if not moat_scores:
        return MoatPrediction(
            primary_industry=primary_industry,
            strongest_moat=None,
            moat_scores={},
            evidence={},
            overall_moat_score=0.0,
            confidence=0.0,
        )

    ranked_scores = sorted(
        moat_scores.items(),
        key=lambda item: (
            item[1],
            item[0],
        ),
        reverse=True,
    )

    strongest_moat = ranked_scores[0][0]
    top_score = ranked_scores[0][1]

    second_score = (
        ranked_scores[1][1]
        if len(ranked_scores) > 1
        else 0.0
    )

    active_scores = list(moat_scores.values())

    # Overall moat should reward depth plus breadth, but not let one
    # inferred category dominate the whole company score.
    top_three = sorted(
        active_scores,
        reverse=True,
    )[:3]

    top_three_average = (
        sum(top_three) / len(top_three)
    )

    direct_categories = sum(
        1
        for moat_name in moat_scores
        if direct_match_counts.get(moat_name, 0) > 0
    )

    inferred_only_categories = sum(
        1
        for moat_name in moat_scores
        if (
            direct_match_counts.get(moat_name, 0) == 0
            and inferred_match_counts.get(moat_name, 0) > 0
        )
    )

    breadth_bonus = min(
        0.9,
        max(0, direct_categories - 1) * 0.22
        + inferred_only_categories * 0.06,
    )

    overall_moat_score = min(
        10.0,
        top_three_average + breadth_bonus,
    )

    total_direct_matches = sum(
        direct_match_counts.values()
    )
    total_inferred_matches = sum(
        inferred_match_counts.values()
    )

    # Confidence is driven primarily by direct evidence.
    direct_coverage = min(
        1.0,
        total_direct_matches / 8,
    )
    inferred_coverage = min(
        1.0,
        total_inferred_matches / 10,
    )

    category_coverage = min(
        1.0,
        direct_categories / 4,
    )

    score_margin = (
        (top_score - second_score) / top_score
        if top_score
        else 0.0
    )

    confidence = (
        direct_coverage * 0.55
        + category_coverage * 0.25
        + score_margin * 0.10
        + inferred_coverage * 0.10
    )

    # If everything came from inference, cap confidence sharply.
    if total_direct_matches == 0:
        confidence = min(
            confidence,
            0.38,
        )

        # Also prevent an inferred-only company from receiving an
        # overall moat score that looks like verified dominance.
        overall_moat_score = min(
            overall_moat_score,
            5.5,
        )

    elif total_direct_matches <= 2:
        confidence = min(
            confidence,
            0.62,
        )

    return MoatPrediction(
        primary_industry=primary_industry,
        strongest_moat=strongest_moat,
        moat_scores={
            moat_name: score
            for moat_name, score in ranked_scores
        },
        evidence=evidence,
        overall_moat_score=round(
            overall_moat_score,
            2,
        ),
        confidence=round(
            max(0.0, min(1.0, confidence)),
            3,
        ),
    )


__all__ = [
    "MOAT_PATTERNS",
    "INDUSTRY_MOAT_WEIGHTS",
    "MoatPrediction",
    "analyze_moats",
]