"""
VERO Competitor Recommendation Engine

Recommends likely competitors based on industry, subindustry,
products, technologies, and ontology data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .entity_engine import extract_entities
from .industry_engine import classify
from .keyword_library import (
    find_industry_by_alias,
    get_industry,
)
from .subindustry_engine import classify_subindustries


@dataclass(slots=True)
class CompetitorPrediction:
    primary_industry: str | None
    primary_subindustry: str | None
    competitors: list[str]
    scores: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return {
            "primary_industry": self.primary_industry,
            "primary_subindustry": self.primary_subindustry,
            "competitors": self.competitors,
            "scores": self.scores,
        }


def _normalize_text(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"[-_/]", " ", text)
    text = re.sub(r"[^a-z0-9+\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


COMPETITOR_SPECIALIZATIONS: dict[str, list[str]] = {
    "Abridge": [
        "medical scribe",
        "clinical notes",
        "clinical documentation",
        "physician documentation",
        "ambient documentation",
        "clinical ai",
    ],
    "Nabla": [
        "medical scribe",
        "clinical notes",
        "clinical documentation",
        "ambient scribe",
        "physician assistant",
        "clinical ai",
    ],
    "Suki": [
        "medical scribe",
        "clinical documentation",
        "voice assistant",
        "physician assistant",
        "clinical notes",
    ],
    "Nuance": [
        "medical scribe",
        "speech recognition",
        "clinical documentation",
        "medical transcription",
        "voice recognition",
    ],
    "Epic": [
        "electronic health record",
        "ehr",
        "hospital software",
        "clinical workflow",
        "health system",
    ],
    "Oracle Health": [
        "electronic health record",
        "ehr",
        "hospital software",
        "clinical workflow",
        "health system",
    ],
    "Athenahealth": [
        "electronic health record",
        "ehr",
        "practice management",
        "medical billing",
        "provider operations",
    ],
    "Viz.ai": [
        "healthcare ai",
        "clinical decision support",
        "medical imaging",
        "radiology ai",
        "stroke detection",
    ],
    "PathAI": [
        "healthcare ai",
        "pathology ai",
        "diagnostics",
        "medical imaging",
        "clinical ai",
    ],
    "Tempus": [
        "precision medicine",
        "oncology",
        "clinical data",
        "healthcare ai",
        "genomics",
    ],
    "Redox": [
        "healthcare interoperability",
        "fhir",
        "hl7",
        "healthcare integration",
        "healthcare api",
    ],
    "Datavant": [
        "healthcare data",
        "clinical data",
        "data interoperability",
        "patient data",
        "health data exchange",
    ],
    "Cedar": [
        "patient billing",
        "healthcare payments",
        "revenue cycle",
        "patient financial experience",
        "medical billing",
    ],
    "AKASA": [
        "revenue cycle",
        "medical billing",
        "healthcare automation",
        "claims automation",
        "hospital operations",
    ],
}


def recommend_competitors(
    text: str,
    industry_name: str | None = None,
    max_results: int = 8,
) -> CompetitorPrediction:
    """
    Recommend likely competitors from a company description.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if max_results < 1:
        raise ValueError("max_results must be at least 1.")

    normalized_text = _normalize_text(text)

    if not normalized_text:
        return CompetitorPrediction(
            primary_industry=None,
            primary_subindustry=None,
            competitors=[],
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

    subindustry_prediction = classify_subindustries(
        text=text,
        industry_name=primary_industry,
    )

    entities = extract_entities(
        text=text,
        industry_name=primary_industry,
    )

    scores: dict[str, float] = {}

    for competitor, patterns in COMPETITOR_SPECIALIZATIONS.items():
        score = 0.0

        for pattern in patterns:
            normalized_pattern = _normalize_text(pattern)

            if normalized_pattern in normalized_text:
                word_count = len(normalized_pattern.split())

                if word_count >= 3:
                    score += 4.0
                elif word_count == 2:
                    score += 3.0
                else:
                    score += 1.5

        if (
            subindustry_prediction.primary_subindustry
            and _normalize_text(
                subindustry_prediction.primary_subindustry
            ) in [_normalize_text(value) for value in patterns]
        ):
            score += 4.0

        if competitor in entities.competitors:
            score += 8.0

        if score > 0:
            scores[competitor] = round(score, 2)

    ontology = (
        get_industry(primary_industry)
        or find_industry_by_alias(primary_industry or "")
    )

    if ontology is not None:
        ontology_competitors = ontology.get("competitors", [])

        if isinstance(ontology_competitors, list):
            for competitor in ontology_competitors:
                competitor_name = str(competitor)

                if competitor_name in scores:
                    scores[competitor_name] += 0.5

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            item[1],
            item[0],
        ),
        reverse=True,
    )[:max_results]

    return CompetitorPrediction(
        primary_industry=primary_industry,
        primary_subindustry=(
            subindustry_prediction.primary_subindustry
        ),
        competitors=[
            competitor
            for competitor, _ in ranked
        ],
        scores={
            competitor: round(score, 2)
            for competitor, score in ranked
        },
    )


__all__ = [
    "COMPETITOR_SPECIALIZATIONS",
    "CompetitorPrediction",
    "recommend_competitors",
]