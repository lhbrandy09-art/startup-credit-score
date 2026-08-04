"""
VERO Subindustry Classification Engine

Identifies the most relevant subindustries inside a predicted
primary industry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .industry_engine import IndustryPrediction, classify
from .keyword_library import (
    find_industry_by_alias,
    get_industry,
)


@dataclass(slots=True)
class SubindustryPrediction:
    primary_industry: str | None
    primary_subindustry: str | None
    secondary_subindustries: list[str]
    confidence: float
    scores: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return {
            "primary_industry": self.primary_industry,
            "primary_subindustry": self.primary_subindustry,
            "secondary_subindustries": self.secondary_subindustries,
            "confidence": self.confidence,
            "scores": self.scores,
        }


def _normalize_text(text: str) -> str:
    """
    Normalize text for safer phrase matching.
    """

    text = text.casefold()
    text = re.sub(r"[-_/]", " ", text)
    text = re.sub(r"[^a-z0-9+\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _contains_term(
    normalized_text: str,
    term: str,
) -> bool:
    """
    Check whether a full term appears in normalized text.

    Word boundaries reduce false matches such as:
    'ai' matching the letters inside another word.
    """

    normalized_term = _normalize_text(term)

    if not normalized_term:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(normalized_term)
        + r"(?![a-z0-9])"
    )

    return re.search(pattern, normalized_text) is not None


def classify_subindustries(
    text: str,
    industry_name: str | None = None,
    max_results: int = 5,
) -> SubindustryPrediction:
    """
    Classify text into subindustries.

    If industry_name is not supplied, VERO first determines the
    primary industry using the industry engine.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if max_results < 1:
        raise ValueError("max_results must be at least 1.")

    normalized_text = _normalize_text(text)

    if not normalized_text:
        return SubindustryPrediction(
            primary_industry=None,
            primary_subindustry=None,
            secondary_subindustries=[],
            confidence=0.0,
            scores={},
        )

    industry_prediction: IndustryPrediction | None = None

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

    if primary_industry is None:
        return SubindustryPrediction(
            primary_industry=None,
            primary_subindustry=None,
            secondary_subindustries=[],
            confidence=0.0,
            scores={},
        )

    ontology = (
        get_industry(primary_industry)
        or find_industry_by_alias(primary_industry)
    )

    if ontology is None:
        return SubindustryPrediction(
            primary_industry=primary_industry,
            primary_subindustry=None,
            secondary_subindustries=[],
            confidence=0.0,
            scores={},
        )

    subindustries = ontology.get("subindustries", {})

    if not isinstance(subindustries, dict):
        return SubindustryPrediction(
            primary_industry=primary_industry,
            primary_subindustry=None,
            secondary_subindustries=[],
            confidence=0.0,
            scores={},
        )

    scores: dict[str, float] = {}

    for subindustry_name, keywords in subindustries.items():
        score = 0.0
        matched_terms: set[str] = set()

        normalized_name = _normalize_text(
            str(subindustry_name)
        )

        if _contains_term(normalized_text, normalized_name):
            matched_terms.add(normalized_name)
            score += 8.0

        if isinstance(keywords, list):
            for keyword in keywords:
                normalized_keyword = _normalize_text(
                    str(keyword)
                )

                if (
                    normalized_keyword
                    and normalized_keyword not in matched_terms
                    and _contains_term(
                        normalized_text,
                        normalized_keyword,
                    )
                ):
                    matched_terms.add(normalized_keyword)

                    word_count = len(
                        normalized_keyword.split()
                    )

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
            scores[str(subindustry_name)] = round(
                score,
                2,
            )

    if not scores:
        return SubindustryPrediction(
            primary_industry=primary_industry,
            primary_subindustry=None,
            secondary_subindustries=[],
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
    )

    ranked_scores = ranked_scores[:max_results]

    primary_subindustry = ranked_scores[0][0]
    top_score = ranked_scores[0][1]

    second_score = (
        ranked_scores[1][1]
        if len(ranked_scores) > 1
        else 0.0
    )

    secondary_subindustries = [
        subindustry
        for subindustry, score in ranked_scores[1:]
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

    return SubindustryPrediction(
        primary_industry=primary_industry,
        primary_subindustry=primary_subindustry,
        secondary_subindustries=secondary_subindustries,
        confidence=round(confidence, 3),
        scores={
            subindustry: score
            for subindustry, score in ranked_scores
        },
    )


__all__ = [
    "SubindustryPrediction",
    "classify_subindustries",
]