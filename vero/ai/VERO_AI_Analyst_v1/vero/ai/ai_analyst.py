
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = os.getenv("VERO_AI_MODEL", "gpt-5-mini")


SYSTEM_INSTRUCTIONS = """
You are VERO, a careful venture-research analyst.

You receive a startup profile assembled from public evidence. Analyze only the
information present in the supplied profile.

Non-negotiable rules:
1. Never invent founders, funding, revenue, customers, competitors, dates,
   market sizes, metrics, or events.
2. When evidence is missing, explicitly say it is unknown.
3. Separate directly supported facts from reasonable inferences.
4. Every claim must reference one or more source URLs already present in the
   supplied profile.
5. Do not treat keyword-based inferences as verified facts.
6. Do not give financial advice or claim that an investment will succeed.
7. Return valid JSON only, with no markdown fences or commentary.

Return exactly this JSON shape:
{
  "executive_summary": "string or null",
  "investment_thesis": "string or null",
  "bull_case": "string or null",
  "bear_case": "string or null",
  "pros": [
    {
      "claim": "string",
      "confidence": 0.0,
      "source_urls": ["string"]
    }
  ],
  "cons": [
    {
      "claim": "string",
      "confidence": 0.0,
      "source_urls": ["string"]
    }
  ],
  "risks": [
    {
      "category": "string",
      "description": "string",
      "severity": 0.0,
      "likelihood": 0.0,
      "source_urls": ["string"],
      "is_inference": true
    }
  ],
  "opportunities": [
    {
      "category": "string",
      "description": "string",
      "potential_impact": 0.0,
      "likelihood": 0.0,
      "source_urls": ["string"],
      "is_inference": true
    }
  ],
  "questions_to_ask": ["string"],
  "missing_information": ["string"],
  "conclusion": "string or null",
  "analysis_confidence": 0.0
}

All confidence, severity, likelihood, and impact values must be between 0 and 1.
Keep the analysis useful but conservative.
""".strip()


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Profile not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Profile is not valid JSON: {path}") from exc

    if not isinstance(data, dict):
        raise RuntimeError("The profile JSON must contain an object.")
    return data


def collect_source_urls(value: Any) -> set[str]:
    urls: set[str] = set()

    if isinstance(value, dict):
        for key, child in value.items():
            if key == "source_url" and isinstance(child, str) and child.strip():
                urls.add(child.strip())
            elif key in {"source_pages", "source_urls"} and isinstance(child, list):
                for item in child:
                    if isinstance(item, str) and item.strip():
                        urls.add(item.strip())
            else:
                urls.update(collect_source_urls(child))

    elif isinstance(value, list):
        for child in value:
            urls.update(collect_source_urls(child))

    return urls


def compact_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """
    Remove large empty sections and trim very long strings before sending the
    profile to the model.
    """
    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            result = {}
            for key, child in value.items():
                cleaned = clean(child)
                if cleaned not in (None, "", [], {}):
                    result[key] = cleaned
            return result

        if isinstance(value, list):
            result = [clean(item) for item in value]
            return [item for item in result if item not in (None, "", [], {})]

        if isinstance(value, str):
            value = re.sub(r"\s+", " ", value).strip()
            return value[:2500]

        return value

    cleaned = clean(profile)
    return cleaned if isinstance(cleaned, dict) else profile


def extract_output_text(response_payload: dict[str, Any]) -> str:
    direct = response_payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    pieces: list[str] = []
    for output_item in response_payload.get("output", []):
        if not isinstance(output_item, dict):
            continue
        for content_item in output_item.get("content", []):
            if not isinstance(content_item, dict):
                continue
            text = content_item.get("text")
            if isinstance(text, str):
                pieces.append(text)

    result = "\n".join(pieces).strip()
    if not result:
        raise RuntimeError("The AI response did not contain readable output.")
    return result


def call_openai(
    profile: dict[str, Any],
    model: str = DEFAULT_MODEL,
    timeout: int = 120,
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set it in PowerShell before running "
            "the AI analyst."
        )

    user_input = {
        "task": "Analyze this startup using only the supplied profile evidence.",
        "startup_profile": compact_profile(profile),
    }

    payload = {
        "model": model,
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": json.dumps(user_input, ensure_ascii=False),
    }

    request = Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"OpenAI API returned HTTP {exc.code}: {error_body[:1000]}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach the OpenAI API: {exc}") from exc

    response_payload = json.loads(body)
    text = extract_output_text(response_payload)

    try:
        analysis = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "The model did not return valid JSON. Raw output:\n"
            f"{text[:2000]}"
        ) from exc

    if not isinstance(analysis, dict):
        raise RuntimeError("The model response must be a JSON object.")

    return analysis


def clamp_number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, number))


def validate_sources(
    analysis: dict[str, Any],
    allowed_urls: set[str],
) -> dict[str, Any]:
    """
    Remove source URLs that were not included in the original profile and clamp
    model-generated numeric scores.
    """
    for section in ("pros", "cons", "risks", "opportunities"):
        items = analysis.get(section)
        if not isinstance(items, list):
            analysis[section] = []
            continue

        valid_items = []
        for item in items:
            if not isinstance(item, dict):
                continue

            urls = item.get("source_urls", [])
            if not isinstance(urls, list):
                urls = []

            item["source_urls"] = [
                url for url in urls
                if isinstance(url, str) and url in allowed_urls
            ]

            if "confidence" in item:
                item["confidence"] = clamp_number(item["confidence"])
            if "severity" in item:
                item["severity"] = clamp_number(item["severity"])
            if "likelihood" in item:
                item["likelihood"] = clamp_number(item["likelihood"])
            if "potential_impact" in item:
                item["potential_impact"] = clamp_number(
                    item["potential_impact"]
                )

            valid_items.append(item)

        analysis[section] = valid_items

    analysis["analysis_confidence"] = clamp_number(
        analysis.get("analysis_confidence", 0.0)
    )

    for section in ("questions_to_ask", "missing_information"):
        values = analysis.get(section)
        if not isinstance(values, list):
            analysis[section] = []
        else:
            analysis[section] = [
                str(value).strip()
                for value in values
                if str(value).strip()
            ]

    return analysis


def merge_analysis(
    profile: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    ai_section = profile.setdefault("ai_analysis", {})

    for key in (
        "executive_summary",
        "investment_thesis",
        "bull_case",
        "bear_case",
        "questions_to_ask",
        "missing_information",
        "conclusion",
    ):
        ai_section[key] = analysis.get(key)

    ai_section["pros"] = [
        item.get("claim")
        for item in analysis.get("pros", [])
        if isinstance(item, dict) and item.get("claim")
    ]
    ai_section["cons"] = [
        item.get("claim")
        for item in analysis.get("cons", [])
        if isinstance(item, dict) and item.get("claim")
    ]
    ai_section["analysis_confidence"] = analysis.get(
        "analysis_confidence", 0.0
    )
    ai_section["evidence_analysis"] = {
        "pros": analysis.get("pros", []),
        "cons": analysis.get("cons", []),
    }

    profile["risks"] = [
        {
            "category": item.get("category", "Unknown"),
            "description": item.get("description", ""),
            "severity": item.get("severity", 0.0),
            "likelihood": item.get("likelihood", 0.0),
            "time_horizon": None,
            "mitigation": None,
            "evidence": [
                {
                    "claim": item.get("description", ""),
                    "source_url": url,
                    "source_name": "AI analysis of collected evidence",
                    "confidence": analysis.get("analysis_confidence", 0.0),
                    "verified": not item.get("is_inference", True),
                    "notes": (
                        "AI-generated inference based on collected evidence."
                        if item.get("is_inference", True)
                        else "AI extraction from collected evidence."
                    ),
                }
                for url in item.get("source_urls", [])
            ],
        }
        for item in analysis.get("risks", [])
        if isinstance(item, dict)
    ]

    profile["opportunities"] = [
        {
            "category": item.get("category", "Unknown"),
            "description": item.get("description", ""),
            "potential_impact": item.get("potential_impact", 0.0),
            "likelihood": item.get("likelihood", 0.0),
            "time_horizon": None,
            "evidence": [
                {
                    "claim": item.get("description", ""),
                    "source_url": url,
                    "source_name": "AI analysis of collected evidence",
                    "confidence": analysis.get("analysis_confidence", 0.0),
                    "verified": not item.get("is_inference", True),
                    "notes": (
                        "AI-generated inference based on collected evidence."
                        if item.get("is_inference", True)
                        else "AI extraction from collected evidence."
                    ),
                }
                for url in item.get("source_urls", [])
            ],
        }
        for item in analysis.get("opportunities", [])
        if isinstance(item, dict)
    ]

    return profile


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run VERO's AI analyst on an existing company profile."
    )
    parser.add_argument(
        "profile",
        help="Path to a generated company profile JSON file.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--output",
        help="Optional output path. By default, the existing profile is updated.",
    )
    parser.add_argument(
        "--analysis-output",
        help="Optional path for saving the raw validated AI analysis.",
    )
    args = parser.parse_args()

    profile_path = Path(args.profile)
    output_path = Path(args.output) if args.output else profile_path

    try:
        profile = load_json(profile_path)
        allowed_urls = collect_source_urls(profile)

        print("Running VERO AI Analyst...")
        analysis = call_openai(profile, model=args.model)
        analysis = validate_sources(analysis, allowed_urls)
        merged = merge_analysis(profile, analysis)

        save_json(output_path, merged)

        if args.analysis_output:
            save_json(Path(args.analysis_output), analysis)

    except Exception as exc:
        print(f"\nAI analysis failed: {exc}", file=sys.stderr)
        return 1

    print("\nVERO AI analysis complete")
    print(f"Confidence: {analysis.get('analysis_confidence', 0.0):.0%}")
    print(f"Pros found: {len(analysis.get('pros', []))}")
    print(f"Cons found: {len(analysis.get('cons', []))}")
    print(f"Risks found: {len(analysis.get('risks', []))}")
    print(f"Opportunities found: {len(analysis.get('opportunities', []))}")
    print(f"Updated profile: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
