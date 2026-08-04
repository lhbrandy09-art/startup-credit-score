from __future__ import annotations

import json
import os
import re
from typing import Any


class ResearchError(RuntimeError):
    """Raised when VERO's external research agent cannot complete."""


class ResearchQuotaError(ResearchError):
    """Raised when the OpenAI API account has no available quota."""


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ResearchError("The AI returned no valid JSON research profile.")
        try:
            value = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ResearchError("The AI research response could not be parsed.") from exc

    if not isinstance(value, dict):
        raise ResearchError("The AI research response was not a JSON object.")

    return value


def _normalise_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _research_error_message(exc: Exception) -> str:
    message = str(exc)
    lowered = message.lower()

    if "insufficient_quota" in lowered or "exceeded your current quota" in lowered:
        raise ResearchQuotaError(
            "OpenAI API quota is unavailable. Add API billing or credits, then retry. "
            "VERO's manual scoring and website/YC import features still work without AI research."
        ) from exc

    if "429" in lowered:
        raise ResearchError(
            "OpenAI temporarily rate-limited the research request. Wait briefly and try again."
        ) from exc

    if "401" in lowered or "invalid_api_key" in lowered or "incorrect api key" in lowered:
        raise ResearchError(
            "The OpenAI API key is invalid. Check .streamlit/secrets.toml and restart Streamlit."
        ) from exc

    if "timeout" in lowered or "timed out" in lowered:
        raise ResearchError(
            "The AI research request timed out. Try again with the official website URL included."
        ) from exc

    raise ResearchError(f"OpenAI research request failed: {message}") from exc


def research_company(
    company_name: str,
    website_url: str = "",
    existing_description: str = "",
    *,
    model: str | None = None,
) -> dict[str, Any]:
    """Research a startup using OpenAI web search and return structured evidence.

    The AI gathers and organises evidence. It does not set VERO's final score.
    """
    name = company_name.strip()
    if not name:
        raise ResearchError("Enter a company name before running AI research.")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ResearchError(
            "OPENAI_API_KEY is missing. Add it to .streamlit/secrets.toml or your environment."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ResearchError(
            "Install the OpenAI package with: python -m pip install openai"
        ) from exc

    chosen_model = model or os.getenv("VERO_AI_MODEL", "gpt-5.4-mini")
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are VERO's startup research analyst. Research the company below using current public web sources.

Company name: {name}
Website: {website_url or 'unknown'}
Existing user description: {existing_description or 'none'}

Rules:
1. Resolve the correct company before extracting facts. Do not mix similarly named companies.
2. Prefer the company website, official documentation, regulator filings, reputable news, investor announcements, GitHub, YC, and Product Hunt.
3. Distinguish verified facts from inference. Never invent metrics.
4. For each material claim, include at least one source URL and source title.
5. Use null or [] when evidence is unavailable.
6. Recent news should focus on the last 24 months when possible.
7. Do not assign a final VERO score. Only produce evidence for deterministic scoring engines.
8. Return ONLY valid JSON with this exact top-level shape:
{{
  "resolved_company_name": "string",
  "official_website": "string or null",
  "one_sentence_summary": "string",
  "industry": "string or null",
  "subindustry": "string or null",
  "business_model": "string or null",
  "customers": ["string"],
  "products": ["string"],
  "pricing": ["string"],
  "leadership": ["string"],
  "funding": ["string"],
  "traction": ["string"],
  "partnerships": ["string"],
  "competitors": ["string"],
  "positive_signals": ["string"],
  "risk_signals": ["string"],
  "recent_news": [
    {{"date": "YYYY-MM-DD or null", "headline": "string", "impact": "positive|negative|neutral", "why_it_matters": "string", "source_url": "string"}}
  ],
  "missing_information": ["string"],
  "research_confidence": 0,
  "sources": [
    {{"title": "string", "url": "string", "source_type": "official|news|database|social|other", "supports": ["string"]}}
  ]
}}

research_confidence must be an integer from 0 to 100 based on source quality, identity resolution, and evidence coverage.
""".strip()

    try:
        response = client.responses.create(
            model=chosen_model,
            tools=[{"type": "web_search"}],
            input=prompt,
        )
    except Exception as exc:
        _research_error_message(exc)
        raise  # unreachable; keeps type checkers satisfied

    output_text = getattr(response, "output_text", "")
    if not output_text:
        raise ResearchError("The AI research response contained no text output.")

    data = _extract_json(output_text)

    list_fields = [
        "customers",
        "products",
        "pricing",
        "leadership",
        "funding",
        "traction",
        "partnerships",
        "competitors",
        "positive_signals",
        "risk_signals",
        "recent_news",
        "missing_information",
        "sources",
    ]
    for field in list_fields:
        data[field] = _normalise_list(data.get(field))

    try:
        data["research_confidence"] = max(
            0,
            min(100, int(data.get("research_confidence", 0))),
        )
    except (TypeError, ValueError):
        data["research_confidence"] = 0

    data["model_used"] = chosen_model
    return data


def research_to_description(report: dict[str, Any]) -> str:
    """Turn verified AI research into evidence text for VERO's engines."""
    lines: list[str] = []

    summary = str(report.get("one_sentence_summary") or "").strip()
    if summary:
        lines.append(summary)

    scalar_fields = {
        "Industry": report.get("industry"),
        "Subindustry": report.get("subindustry"),
        "Business model": report.get("business_model"),
    }
    for label, value in scalar_fields.items():
        if value:
            lines.append(f"{label}: {value}.")

    list_fields = {
        "Customers": report.get("customers", []),
        "Products": report.get("products", []),
        "Pricing": report.get("pricing", []),
        "Funding": report.get("funding", []),
        "Traction": report.get("traction", []),
        "Partnerships": report.get("partnerships", []),
        "Competitors": report.get("competitors", []),
        "Positive signals": report.get("positive_signals", []),
        "Risk signals": report.get("risk_signals", []),
    }
    for label, values in list_fields.items():
        clean = [str(value).strip() for value in values if str(value).strip()]
        if clean:
            lines.append(f"{label}: " + "; ".join(clean) + ".")

    return "\n".join(lines)


__all__ = [
    "ResearchError",
    "ResearchQuotaError",
    "research_company",
    "research_to_description",
]