"""
VERO Entity Extraction Engine

Extracts customers, technologies, products, and competitors
from startup descriptions using the selected industry ontology.
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
class EntityPrediction:
    primary_industry: str | None
    customers: list[str]
    technologies: list[str]
    products: list[str]
    competitors: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "primary_industry": self.primary_industry,
            "customers": self.customers,
            "technologies": self.technologies,
            "products": self.products,
            "competitors": self.competitors,
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


def _extract_matches(
    normalized_text: str,
    values: object,
) -> list[str]:
    if not isinstance(values, list):
        return []

    matches: list[str] = []
    seen: set[str] = set()

    sorted_values = sorted(
        values,
        key=lambda value: len(str(value)),
        reverse=True,
    )

    for value in sorted_values:
        term = str(value).strip()

        if not term:
            continue

        normalized_term = _normalize_text(term)

        if (
            normalized_term not in seen
            and _contains_term(normalized_text, term)
        ):
            seen.add(normalized_term)
            matches.append(term)

    return matches


def extract_entities(
    text: str,
    industry_name: str | None = None,
) -> EntityPrediction:
    """
    Extract ontology entities from a startup description.

    If industry_name is omitted, VERO first predicts the primary
    industry.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    normalized_text = _normalize_text(text)

    if not normalized_text:
        return EntityPrediction(
            primary_industry=None,
            customers=[],
            technologies=[],
            products=[],
            competitors=[],
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

    if primary_industry is None:
        return EntityPrediction(
            primary_industry=None,
            customers=[],
            technologies=[],
            products=[],
            competitors=[],
        )

    ontology = (
        get_industry(primary_industry)
        or find_industry_by_alias(primary_industry)
    )

    if ontology is None:
        return EntityPrediction(
            primary_industry=primary_industry,
            customers=[],
            technologies=[],
            products=[],
            competitors=[],
        )

    return EntityPrediction(
        primary_industry=primary_industry,
        customers=_extract_matches(
            normalized_text,
            ontology.get("customers", []),
        ),
        technologies=_extract_matches(
            normalized_text,
            ontology.get("technologies", []),
        ),
        products=_extract_matches(
            normalized_text,
            ontology.get("products", []),
        ),
        competitors=_extract_matches(
            normalized_text,
            ontology.get("competitors", []),
        ),
    )


__all__ = [
    "EntityPrediction",
    "extract_entities",
]