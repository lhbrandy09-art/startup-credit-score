"""
VERO Risk Engine

Evaluates the primary investment risks associated with a startup.

Outputs risk scores (0-10):

0 = Minimal risk
10 = Extreme risk
"""

from __future__ import annotations

from dataclasses import dataclass

from .industry_engine import classify


# ---------------------------------------------------------
# Dataclass
# ---------------------------------------------------------

@dataclass(slots=True)
class RiskPrediction:

    primary_industry: str | None

    overall_risk: float

    confidence: float

    risk_scores: dict[str, float]

    evidence: dict[str, list[str]]

    largest_risks: list[str]

    def to_dict(self):

        return {

            "primary_industry": self.primary_industry,

            "overall_risk": self.overall_risk,

            "confidence": self.confidence,

            "risks": self.risk_scores,

            "largest_risks": self.largest_risks,

            "evidence": self.evidence,
        }


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _contains_term(text: str, term: str) -> bool:
    return _normalize_text(term) in text


def _term_weight(term: str) -> float:

    words = len(term.split())

    if words >= 4:
        return 2.4

    if words == 3:
        return 2.0

    if words == 2:
        return 1.5

    return 1.0


def _resolve_industry(
    text: str,
    industry_name: str | None,
) -> str | None:

    if industry_name:
        return industry_name

    prediction = classify(text)

    return prediction.primary_industry


# ---------------------------------------------------------
# Risk Categories
# ---------------------------------------------------------

RISK_CATEGORIES = [

    "execution",

    "technology",

    "competition",

    "go_to_market",

    "regulatory",

    "capital",

    "platform_dependency",

    "customer_concentration",

    "market_timing",

]  

RISK_PATTERNS = {

    "execution": [

        "founding team",
        "first time founder",
        "first-time founder",
        "small team",
        "lean team",
        "solo founder",
        "rapid hiring",
        "scaling team",
        "technical founder",
        "non technical founder",
        "non-technical founder",
        "complex product",
        "multiple products",
        "large roadmap",
        "research heavy",
        "research-intensive",
        "clinical validation",
        "pilot program",
        "pilot programs",
        "beta customers",
    ],

    "technology": [

        "artificial intelligence",
        "machine learning",
        "deep learning",
        "large language model",
        "llm",
        "computer vision",
        "robotics",
        "autonomous",
        "clinical nlp",
        "proprietary model",
        "foundation model",
        "generative ai",
        "real time inference",
        "real-time inference",
        "edge computing",
        "distributed systems",
        "quantum",
        "blockchain",
    ],

    "competition": [

        "competitive market",
        "crowded market",
        "fragmented market",
        "market leader",
        "enterprise software",
        "healthcare ai",
        "fintech",
        "consumer app",
        "well funded competitors",
        "well-funded competitors",
        "incumbents",
        "legacy vendors",
        "startup ecosystem",
        "multiple competitors",
        "high competition",
        "competing platforms",
    ],

    "go_to_market": [

        "enterprise sales",
        "hospital procurement",
        "government procurement",
        "long sales cycle",
        "sales cycle",
        "proof of concept",
        "proof-of-concept",
        "pilot deployment",
        "customer education",
        "high touch sales",
        "high-touch sales",
        "channel partner",
        "enterprise onboarding",
        "security review",
        "legal review",
        "procurement committee",
    ],

    "regulatory": [

        "hipaa",
        "fda",
        "soc2",
        "soc 2",
        "pci",
        "pci dss",
        "gdpr",
        "ccpa",
        "iso 27001",
        "iso27001",
        "medical device",
        "clinical trial",
        "insurance reimbursement",
        "healthcare compliance",
        "financial regulation",
        "finra",
        "aml",
        "kyc",
    ],

    "capital": [

        "hardware",
        "manufacturing",
        "robotics",
        "medical device",
        "clinical trial",
        "drug development",
        "inventory",
        "physical infrastructure",
        "capital intensive",
        "capital-intensive",
        "factory",
        "warehouse",
        "custom hardware",
        "expensive deployment",
        "high burn",
        "burn rate",
    ],

    "platform_dependency": [

        "openai",
        "anthropic",
        "google cloud",
        "aws",
        "amazon web services",
        "azure",
        "microsoft azure",
        "apple",
        "google play",
        "app store",
        "stripe",
        "salesforce",
        "shopify",
        "twilio",
        "snowflake",
    ],

    "customer_concentration": [

        "enterprise customer",
        "single customer",
        "major customer",
        "strategic customer",
        "hospital network",
        "government agency",
        "large enterprise",
        "fortune 500",
        "exclusive partnership",
        "exclusive contract",
        "anchor customer",
    ],

    "market_timing": [

        "emerging market",
        "rapidly growing market",
        "fast growing market",
        "early market",
        "nascent market",
        "new category",
        "category creation",
        "market transition",
        "technology shift",
        "industry transformation",
        "ai adoption",
        "digital transformation",
    ],

}

RISK_REDUCERS = {
    "execution": [
        "experienced founders",
        "experienced founder",
        "repeat founder",
        "repeat founders",
        "serial entrepreneur",
        "proven leadership team",
        "experienced management team",
        "successful exit",
        "previous exit",
        "domain expertise",
        "industry expertise",
        "technical expertise",
        "enterprise customers",
        "paying customers",
        "commercial traction",
        "profitable",
    ],

    "technology": [
        "production ready",
        "production-ready",
        "commercially deployed",
        "proven technology",
        "validated technology",
        "clinically validated",
        "peer reviewed",
        "peer-reviewed",
        "high accuracy",
        "reliable infrastructure",
        "patented technology",
        "patent protected",
        "successful deployment",
    ],

    "competition": [
        "category leader",
        "market leader",
        "first mover",
        "first-mover",
        "differentiated product",
        "unique technology",
        "proprietary technology",
        "exclusive data",
        "strong brand",
        "patent portfolio",
        "limited competition",
        "few competitors",
    ],

    "go_to_market": [
        "product led growth",
        "product-led growth",
        "self service",
        "self-service",
        "organic growth",
        "viral growth",
        "short sales cycle",
        "efficient sales",
        "channel partnerships",
        "distribution partnership",
        "existing distribution",
        "high conversion",
        "strong pipeline",
    ],

    "regulatory": [
        "hipaa compliant",
        "hipaa compliance",
        "fda approved",
        "fda approval",
        "fda cleared",
        "fda clearance",
        "soc2 certified",
        "soc 2 certified",
        "soc2 compliant",
        "pci compliant",
        "gdpr compliant",
        "iso 27001 certified",
        "regulatory approval",
        "regulatory clearance",
        "compliance certified",
    ],

    "capital": [
        "capital efficient",
        "capital-efficient",
        "asset light",
        "asset-light",
        "software only",
        "low burn",
        "low burn rate",
        "profitable",
        "cash flow positive",
        "cash-flow positive",
        "bootstrapped",
        "minimal hardware",
        "low infrastructure cost",
    ],

    "platform_dependency": [
        "multi cloud",
        "multi-cloud",
        "cloud agnostic",
        "cloud-agnostic",
        "model agnostic",
        "model-agnostic",
        "multiple providers",
        "provider independent",
        "self hosted",
        "self-hosted",
        "proprietary model",
        "in house model",
        "in-house model",
    ],

    "customer_concentration": [
        "diversified customer base",
        "diverse customer base",
        "thousands of customers",
        "hundreds of customers",
        "broad customer base",
        "multiple enterprise customers",
        "no customer concentration",
        "distributed revenue",
        "global customer base",
    ],

    "market_timing": [
        "rapidly growing market",
        "fast growing market",
        "growing market",
        "strong demand",
        "increasing demand",
        "market adoption",
        "ai adoption",
        "digital transformation",
        "regulatory tailwind",
        "industry tailwind",
        "market expansion",
        "accelerating adoption",
    ],
}

INDUSTRY_RISK_BASELINES = {

    "Artificial Intelligence": {

        "execution": 6.5,
        "technology": 7.0,
        "competition": 8.0,
        "go_to_market": 5.5,
        "regulatory": 3.5,
        "capital": 4.5,
        "platform_dependency": 6.5,
        "customer_concentration": 3.5,
        "market_timing": 3.0,
    },

    "Healthcare": {

        "execution": 6.0,
        "technology": 5.5,
        "competition": 6.5,
        "go_to_market": 7.5,
        "regulatory": 9.0,
        "capital": 6.5,
        "platform_dependency": 2.5,
        "customer_concentration": 5.5,
        "market_timing": 2.5,
    },

    "Financial Technology": {

        "execution": 5.5,
        "technology": 5.0,
        "competition": 7.5,
        "go_to_market": 5.5,
        "regulatory": 8.5,
        "capital": 4.5,
        "platform_dependency": 4.5,
        "customer_concentration": 4.5,
        "market_timing": 3.5,
    },

}

def _collect_matches(
    normalized_text: str,
    terms: list[str],
) -> tuple[list[str], float]:
    matches: list[str] = []
    matched_normalized: list[str] = []
    score = 0.0

    for term in sorted(
        terms,
        key=lambda value: len(_normalize_text(value)),
        reverse=True,
    ):
        normalized_term = _normalize_text(term)

        if not normalized_term:
            continue

        if any(
            normalized_term in existing
            for existing in matched_normalized
        ):
            continue

        if _contains_term(normalized_text, term):
            matches.append(term)
            matched_normalized.append(normalized_term)
            score += _term_weight(term)

    return matches, score


def _clamp(score: float) -> float:
    return max(0.0, min(10.0, score))

def analyze_risk(
    text: str,
    industry_name: str | None = None,
) -> RiskPrediction:
    """
    Evaluate startup investment risk.

    Scores use a 0-10 scale:
    0 = minimal risk
    10 = extreme risk
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    normalized_text = _normalize_text(text)

    primary_industry = _resolve_industry(
        text=text,
        industry_name=industry_name,
    )

    default_baseline = {
        category: 5.0
        for category in RISK_CATEGORIES
    }

    baselines = INDUSTRY_RISK_BASELINES.get(
        primary_industry or "",
        default_baseline,
    )

    evidence: dict[str, list[str]] = {}
    raw_scores: dict[str, float] = {}

    for category in RISK_CATEGORIES:
        risk_matches, _ = _collect_matches(
            normalized_text,
            RISK_PATTERNS[category],
        )

        reducer_matches, reducer_match_score = _collect_matches(
            normalized_text,
            RISK_REDUCERS[category],
        )

        reducer_normalized = [
            _normalize_text(term)
            for term in reducer_matches
        ]

        # A longer, more specific reducer overrides a generic risk phrase.
        # Examples:
        # "HIPAA compliance" overrides "HIPAA"
        # "rapidly growing market" should not count as both positive and negative.
        filtered_risk_matches = [
            term
            for term in risk_matches
            if not any(
                _normalize_text(term) in reducer_term
                for reducer_term in reducer_normalized
            )
        ]

        risk_match_score = sum(
            _term_weight(term)
            for term in filtered_risk_matches
        )

        category_evidence: list[str] = []

        if filtered_risk_matches:
            category_evidence.extend(
                f"+ {term}"
                for term in filtered_risk_matches
            )

        if reducer_matches:
            category_evidence.extend(
                f"- {term}"
                for term in reducer_matches
            )

        if category_evidence:
            evidence[category] = category_evidence

        baseline = baselines.get(category, 5.0)

        score = (
            baseline
            + risk_match_score * 0.40
            - reducer_match_score * 0.45
        )

        raw_scores[category] = _clamp(score)

    risk_scores = {
        category: round(score, 2)
        for category, score in sorted(
            raw_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    }

    largest_risks = [
        category
        for category, score in risk_scores.items()
        if score >= 7.0
    ]

    weights = {
        "execution": 0.15,
        "technology": 0.12,
        "competition": 0.13,
        "go_to_market": 0.13,
        "regulatory": 0.15,
        "capital": 0.10,
        "platform_dependency": 0.08,
        "customer_concentration": 0.07,
        "market_timing": 0.07,
    }

    overall = sum(
        raw_scores[category] * weights[category]
        for category in RISK_CATEGORIES
    )

    total_matches = sum(
        len(items)
        for items in evidence.values()
    )

    evidence_confidence = min(
        1.0,
        total_matches / 30,
    )

    coverage_confidence = min(
        1.0,
        len(evidence) / len(RISK_CATEGORIES),
    )

    industry_confidence = (
        1.0
        if primary_industry in INDUSTRY_RISK_BASELINES
        else 0.5
    )

    confidence = (
        evidence_confidence * 0.45
        + coverage_confidence * 0.35
        + industry_confidence * 0.20
    )

    return RiskPrediction(
        primary_industry=primary_industry,
        overall_risk=round(overall, 2),
        confidence=round(confidence, 3),
        risk_scores=risk_scores,
        evidence=evidence,
        largest_risks=largest_risks,
    )


__all__ = [
    "RiskPrediction",
    "RISK_CATEGORIES",
    "RISK_PATTERNS",
    "RISK_REDUCERS",
    "INDUSTRY_RISK_BASELINES",
    "analyze_risk",
]