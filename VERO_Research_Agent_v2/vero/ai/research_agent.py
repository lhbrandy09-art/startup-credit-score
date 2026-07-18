
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from vero.extractors.website_extractor import (
    WebsitePage,
    extract_website_facts,
    parse_html,
)
from vero.profiles.company_profile import (
    BusinessModelProfile,
    CompanyIdentity,
    CompanyProfile,
    CustomerProfile,
    EvidenceItem,
    FounderProfile,
    ProductProfile,
    SolutionProfile,
)


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/150.0 Safari/537.36"
)

COMMON_PATHS = (
    "",
    "/about",
    "/about-us",
    "/company",
    "/products",
    "/product",
    "/solutions",
    "/features",
    "/pricing",
    "/customers",
    "/industries",
    "/integrations",
    "/careers",
)


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("Website URL cannot be empty.")

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid website URL: {url}")

    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def fetch_html(url: str, timeout: int = 15) -> tuple[str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            raise ValueError(f"Not HTML: {content_type}")

        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read(3_000_000).decode(charset, errors="replace")
        return html, response.geturl()


def discover_internal_pages(
    homepage: WebsitePage,
    base_url: str,
) -> list[str]:
    keywords = (
        "about", "company", "product", "solution", "feature",
        "pricing", "customer", "industry", "integration", "career", "job",
    )

    base_host = urlparse(base_url).netloc
    results: list[str] = []

    for href, text in homepage.links:
        absolute = urljoin(homepage.url, href)
        parsed = urlparse(absolute)

        if parsed.netloc != base_host:
            continue

        combined = f"{parsed.path} {text}".lower()
        if not any(keyword in combined for keyword in keywords):
            continue

        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        if clean_url and clean_url not in results:
            results.append(clean_url)

    return results[:12]


def collect_pages(base_url: str, maximum_pages: int = 10) -> list[WebsitePage]:
    candidates = [f"{base_url}{path}" for path in COMMON_PATHS]
    attempted: set[str] = set()
    pages: list[WebsitePage] = []

    index = 0
    while index < len(candidates) and len(pages) < maximum_pages:
        url = candidates[index]
        index += 1

        if url in attempted:
            continue
        attempted.add(url)

        try:
            html, final_url = fetch_html(url)
            page = parse_html(final_url, html)
            pages.append(page)

            if len(pages) == 1:
                candidates.extend(discover_internal_pages(page, base_url))

        except HTTPError as exc:
            if exc.code != 404:
                print(f"[skip] {url}: HTTP {exc.code}")
        except (URLError, TimeoutError, ValueError) as exc:
            print(f"[skip] {url}: {exc}")

    return pages


def make_evidence(
    claim: str,
    source_url: Optional[str],
    confidence: float = 0.75,
    verified: bool = True,
    notes: Optional[str] = None,
) -> EvidenceItem:
    return EvidenceItem(
        claim=claim,
        source_url=source_url,
        source_name="Company website",
        confidence=confidence,
        verified=verified,
        notes=notes,
    )


def build_profile(
    requested_name: str,
    website: str,
    pages: list[WebsitePage],
) -> CompanyProfile:
    facts = extract_website_facts(pages)
    primary_source = pages[0].url if pages else website

    description_evidence = []
    if facts.description:
        description_evidence.append(
            make_evidence(
                f"Company description: {facts.description}",
                primary_source,
                confidence=0.9,
            )
        )

    industry_evidence = []
    if facts.industry:
        industry_evidence.append(
            make_evidence(
                f"VERO inferred the industry as {facts.industry}.",
                primary_source,
                confidence=0.65,
                verified=False,
                notes="Keyword-based website inference.",
            )
        )

    product_evidence = [
        make_evidence(
            f"Product or solution identified: {product}",
            primary_source,
            confidence=0.65,
            verified=False,
            notes="Extracted from website headings.",
        )
        for product in facts.products
    ]

    customer_evidence = [
        make_evidence(
            f"Likely customer type: {customer}",
            primary_source,
            confidence=0.6,
            verified=False,
            notes="Keyword-based website inference.",
        )
        for customer in facts.customer_types
    ]

    pricing_evidence = [
        make_evidence(
            f"Pricing signal detected: {model}",
            facts.pricing_url or primary_source,
            confidence=0.6,
            verified=False,
        )
        for model in facts.pricing_models
    ]

    founders = [
        FounderProfile(
            name=name,
            evidence=[
                make_evidence(
                    f"Leadership name detected: {name}",
                    facts.about_url or primary_source,
                    confidence=0.5,
                    verified=False,
                    notes="Name detected near leadership terminology; review required.",
                )
            ],
        )
        for name in facts.leadership_names
    ]

    profile = CompanyProfile(
        identity=CompanyIdentity(
            name=requested_name or facts.company_name or urlparse(website).netloc,
            website=website,
            description=facts.description,
            industry=facts.industry,
            evidence=description_evidence + industry_evidence,
        ),
        founders=founders,
        solution=SolutionProfile(
            summary=facts.description,
            primary_value_proposition=facts.description,
            evidence=description_evidence.copy(),
        ),
        customers=CustomerProfile(
            customer_type=", ".join(facts.customer_types) or None,
            industries_served=facts.industries_served,
            evidence=customer_evidence,
        ),
        product=ProductProfile(
            product_name=facts.products[0] if facts.products else facts.company_name,
            product_type=", ".join(facts.products[:5]) or None,
            integrations=facts.integrations,
            evidence=product_evidence,
        ),
        business_model=BusinessModelProfile(
            model_type=", ".join(facts.pricing_models) or None,
            pricing_model=", ".join(facts.pricing_models) or None,
            evidence=pricing_evidence,
        ),
        evidence=[
            make_evidence(
                f"VERO researched {len(pages)} public website pages.",
                primary_source,
                confidence=1.0,
            )
        ],
    )

    profile.external_environment.recent_events.append(
        {
            "type": "website_metadata",
            "social_links": facts.social_links,
            "careers_url": facts.careers_url,
            "pricing_url": facts.pricing_url,
            "about_url": facts.about_url,
            "source_pages": facts.source_pages,
        }
    )

    profile.ai_analysis.missing_information = [
        "Verified founder biographies",
        "Revenue and growth",
        "Customer retention",
        "Funding history",
        "Market size",
        "Named competitors",
        "Unit economics",
    ]

    profile.update_data_quality()
    return profile


def safe_filename(name: str) -> str:
    result = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower())
    return result.strip("_") or "company"


def research_company(
    company_name: str,
    website: str,
    output_path: Path,
) -> CompanyProfile:
    normalized = normalize_url(website)
    pages = collect_pages(normalized)

    if not pages:
        raise RuntimeError(
            "VERO could not access any usable HTML pages. "
            "The website may block automated requests or require JavaScript."
        )

    profile = build_profile(company_name, normalized, pages)
    profile.save_json(output_path)
    return profile


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VERO Research Agent v2"
    )
    parser.add_argument("company", help="Company name")
    parser.add_argument("website", help="Company website")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    output_path = Path(
        args.output
        or f"vero/data/companies/{safe_filename(args.company)}_profile.json"
    )

    try:
        profile = research_company(args.company, args.website, output_path)
    except Exception as exc:
        print(f"\nResearch failed: {exc}", file=sys.stderr)
        return 1

    print("\nVERO Research Agent v2 complete")
    print(f"Company: {profile.identity.name}")
    print(f"Industry: {profile.identity.industry or 'Unknown'}")
    print(f"Description: {profile.identity.description or 'Not found'}")
    print(f"Products: {profile.product.product_type or 'Not found'}")
    print(f"Customers: {profile.customers.customer_type or 'Not found'}")
    print(f"Pricing: {profile.business_model.pricing_model or 'Not found'}")
    print(f"Integrations found: {len(profile.product.integrations)}")
    print(f"Leadership names found: {len(profile.founders)}")
    print(f"Completeness: {profile.data_quality.completeness:.1%}")
    print(f"Saved profile: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
