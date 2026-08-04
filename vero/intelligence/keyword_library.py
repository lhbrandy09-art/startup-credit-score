"""
VERO Intelligence Knowledge Library

This module combines every industry ontology into one master
knowledge dictionary.

All VERO intelligence engines should import KNOWLEDGE from this file
instead of importing individual ontology modules directly.

Version: 1.0
"""

from __future__ import annotations

from typing import Any

from .ai import AI
from .fintech import FINTECH
from .healthcare import HEALTHCARE


KNOWLEDGE = {
    AI["name"]: AI,
    FINTECH["name"]: FINTECH,
    HEALTHCARE["name"]: HEALTHCARE,
}


def get_industry(industry_name: str) -> dict[str, Any] | None:
    """
    Return an industry ontology by its official name.

    Matching is case-insensitive.

    Example:
        get_industry("artificial intelligence")
    """

    normalized_query = industry_name.strip().casefold()

    for official_name, ontology in KNOWLEDGE.items():
        if official_name.casefold() == normalized_query:
            return ontology

    return None


def find_industry_by_alias(alias: str) -> dict[str, Any] | None:
    """
    Find an industry ontology using an alias.

    Examples:
        find_industry_by_alias("AI")
        find_industry_by_alias("fintech")
        find_industry_by_alias("digital finance")
    """

    normalized_alias = alias.strip().casefold()

    if not normalized_alias:
        return None

    for ontology in KNOWLEDGE.values():
        aliases = ontology.get("aliases", [])

        for industry_alias in aliases:
            if industry_alias.casefold() == normalized_alias:
                return ontology

    return None


def search_industries(
    text: str,
    include_scores: bool = False,
) -> list[str] | list[tuple[str, float]]:
    """
    Search text across the full ontology.

    Results are ranked by total relevance score.

    Set include_scores=True to inspect the score for each industry.
    """

    normalized_text = text.strip().casefold()

    if not normalized_text:
        return []

    industry_scores: dict[str, float] = {}

    for official_name, ontology in KNOWLEDGE.items():
        score = 0.0
        matched_terms: set[str] = set()

        def add_match(term: str, weight: float) -> None:
            nonlocal score

            normalized_term = str(term).strip().casefold()

            if (
                normalized_term
                and normalized_term in normalized_text
                and normalized_term not in matched_terms
            ):
                matched_terms.add(normalized_term)
                score += weight

        add_match(official_name, 10.0)

        aliases = ontology.get("aliases", [])

        if isinstance(aliases, list):
            for alias in aliases:
                add_match(alias, 8.0)

        subindustries = ontology.get("subindustries", {})

        if isinstance(subindustries, dict):
            for subindustry_name, keywords in subindustries.items():
                add_match(subindustry_name, 5.0)

                if isinstance(keywords, list):
                    for keyword in keywords:
                        add_match(keyword, 2.0)

        weighted_fields = {
            "technologies": 2.5,
            "products": 2.5,
            "customers": 2.0,
            "business_models": 1.5,
            "competitors": 2.0,
            "yc_tags": 2.0,
            "github_topics": 1.5,
            "problems_solved": 1.0,
        }

        for field_name, field_weight in weighted_fields.items():
            values = ontology.get(field_name, [])

            if not isinstance(values, list):
                continue

            for value in values:
                add_match(value, field_weight)

        if score > 0:
            industry_scores[official_name] = round(score, 2)

    ranked_matches = sorted(
        industry_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    if include_scores:
        return ranked_matches

    return [
        industry_name
        for industry_name, _score in ranked_matches
    ]
    """
    Search text across the full ontology.

    Checks:
    - official industry name
    - aliases
    - subindustries
    - technologies
    - products
    - customers
    - business models
    - competitors
    - YC tags
    - GitHub topics
    - problems solved

    Returns matching official industry names ordered by score.
    """

    normalized_text = text.strip().casefold()

    if not normalized_text:
        return []

    industry_scores: dict[str, float] = {}

    for official_name, ontology in KNOWLEDGE.items():
        score = 0.0

        # Strong matches
        official_name_normalized = official_name.casefold()

        if official_name_normalized in normalized_text:
            score += 10.0

        aliases = ontology.get("aliases", [])

        if isinstance(aliases, list):
            for alias in aliases:
                normalized_alias = str(alias).strip().casefold()

                if normalized_alias and normalized_alias in normalized_text:
                    score += 8.0

        # Subindustry matching
        subindustries = ontology.get("subindustries", {})

        if isinstance(subindustries, dict):
            for subindustry_name, keywords in subindustries.items():
                normalized_name = str(
                    subindustry_name
                ).strip().casefold()

                if (
                    normalized_name
                    and normalized_name in normalized_text
                ):
                    score += 5.0

                if isinstance(keywords, list):
                    for keyword in keywords:
                        normalized_keyword = str(
                            keyword
                        ).strip().casefold()

                        if (
                            normalized_keyword
                            and normalized_keyword in normalized_text
                        ):
                            score += 2.0

        # General ontology fields
        weighted_fields = {
            "technologies": 2.5,
            "products": 2.5,
            "customers": 2.0,
            "business_models": 1.5,
            "competitors": 2.0,
            "yc_tags": 2.0,
            "github_topics": 1.5,
            "problems_solved": 1.0,
        }

        for field_name, field_weight in weighted_fields.items():
            values = ontology.get(field_name, [])

            if not isinstance(values, list):
                continue

            for value in values:
                normalized_value = str(value).strip().casefold()

                if (
                    normalized_value
                    and normalized_value in normalized_text
                ):
                    score += field_weight

        if score > 0:
            industry_scores[official_name] = score

    ranked_matches = sorted(
        industry_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        industry_name
        for industry_name, _score in ranked_matches
    ]


def get_subindustries(industry_name: str) -> list[str]:
    """
    Return all subindustry names for an industry.
    """

    ontology = (
        get_industry(industry_name)
        or find_industry_by_alias(industry_name)
    )

    if ontology is None:
        return []

    subindustries = ontology.get("subindustries", {})

    if not isinstance(subindustries, dict):
        return []

    return list(subindustries.keys())


def get_industry_signals(
    industry_name: str,
) -> dict[str, float]:
    """
    Return the default intelligence signals for an industry.
    """

    ontology = (
        get_industry(industry_name)
        or find_industry_by_alias(industry_name)
    )

    if ontology is None:
        return {}

    signals = ontology.get("signals", {})

    if not isinstance(signals, dict):
        return {}

    return {
        str(signal_name): float(signal_value)
        for signal_name, signal_value in signals.items()
        if isinstance(signal_value, (int, float))
    }


def get_all_industry_names() -> list[str]:
    """
    Return all official industry names.
    """

    return list(KNOWLEDGE.keys())


def get_all_aliases() -> dict[str, list[str]]:
    """
    Return aliases grouped by official industry name.
    """

    result: dict[str, list[str]] = {}

    for official_name, ontology in KNOWLEDGE.items():
        aliases = ontology.get("aliases", [])

        if isinstance(aliases, list):
            result[official_name] = [
                str(alias)
                for alias in aliases
            ]
        else:
            result[official_name] = []

    return result


def validate_knowledge_library() -> None:
    """
    Validate the combined VERO knowledge library.
    """

    if not isinstance(KNOWLEDGE, dict):
        raise TypeError("KNOWLEDGE must be a dictionary.")

    if not KNOWLEDGE:
        raise ValueError(
            "KNOWLEDGE must contain at least one ontology."
        )

    required_fields = {
        "name",
        "aliases",
        "subindustries",
        "technologies",
        "products",
        "customers",
        "business_models",
        "competitors",
        "signals",
    }

    seen_names: set[str] = set()

    for official_name, ontology in KNOWLEDGE.items():
        if not isinstance(official_name, str):
            raise TypeError(
                "Every KNOWLEDGE key must be a string."
            )

        if not isinstance(ontology, dict):
            raise TypeError(
                f"Ontology {official_name!r} must be a dictionary."
            )

        missing_fields = required_fields.difference(ontology)

        if missing_fields:
            raise ValueError(
                f"Ontology {official_name!r} is missing fields: "
                f"{sorted(missing_fields)}"
            )

        ontology_name = ontology.get("name")

        if ontology_name != official_name:
            raise ValueError(
                f"KNOWLEDGE key {official_name!r} does not match "
                f"ontology name {ontology_name!r}."
            )

        normalized_name = official_name.casefold()

        if normalized_name in seen_names:
            raise ValueError(
                f"Duplicate ontology name: {official_name!r}"
            )

        seen_names.add(normalized_name)

        aliases = ontology.get("aliases")

        if not isinstance(aliases, list):
            raise TypeError(
                f"{official_name!r} aliases must be a list."
            )

        subindustries = ontology.get("subindustries")

        if not isinstance(subindustries, dict):
            raise TypeError(
                f"{official_name!r} subindustries must be a dictionary."
            )

        signals = ontology.get("signals")

        if not isinstance(signals, dict):
            raise TypeError(
                f"{official_name!r} signals must be a dictionary."
            )

        for signal_name, signal_value in signals.items():
            if not isinstance(signal_value, (int, float)):
                raise TypeError(
                    f"{official_name!r} signal "
                    f"{signal_name!r} must be numeric."
                )

            if not 0 <= signal_value <= 1:
                raise ValueError(
                    f"{official_name!r} signal "
                    f"{signal_name!r} must be between 0 and 1."
                )


validate_knowledge_library()


__all__ = [
    "KNOWLEDGE",
    "get_industry",
    "find_industry_by_alias",
    "search_industries",
    "get_subindustries",
    "get_industry_signals",
    "get_all_industry_names",
    "get_all_aliases",
    "validate_knowledge_library",
]