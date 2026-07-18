
from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import urljoin, urlparse


SOCIAL_DOMAINS = {
    "linkedin.com": "LinkedIn",
    "github.com": "GitHub",
    "twitter.com": "Twitter",
    "x.com": "X",
    "youtube.com": "YouTube",
    "facebook.com": "Facebook",
    "instagram.com": "Instagram",
}

INDUSTRY_TERMS = {
    "Financial Technology": (
        "payments", "fintech", "billing", "banking", "financial services",
        "money movement", "invoicing", "credit", "insurance",
    ),
    "Artificial Intelligence": (
        "artificial intelligence", "machine learning", "generative ai",
        "large language model", "llm", "ai platform",
    ),
    "Healthcare": (
        "healthcare", "clinical", "medical", "patient", "health system",
    ),
    "Cybersecurity": (
        "cybersecurity", "threat detection", "security platform",
        "identity security", "data protection",
    ),
    "Developer Tools": (
        "developer tools", "developer platform", "api", "sdk",
        "software development", "code deployment",
    ),
    "Enterprise Software": (
        "enterprise", "workflow", "automation", "saas",
        "business software", "operations platform",
    ),
    "E-commerce": (
        "e-commerce", "ecommerce", "online store", "commerce platform",
        "retail platform",
    ),
    "Education": (
        "education", "learning platform", "students", "teachers", "schools",
    ),
    "Climate Technology": (
        "climate", "carbon", "renewable energy", "sustainability",
        "clean energy",
    ),
    "Real Estate Technology": (
        "real estate", "property management", "landlords", "renters",
        "proptech",
    ),
}

CUSTOMER_TERMS = {
    "Startups": ("startup", "early-stage company"),
    "Small businesses": ("small business", "smb"),
    "Enterprises": ("enterprise", "global business", "large company"),
    "Developers": ("developer", "engineering team", "software team"),
    "Consumers": ("consumer", "individual user"),
    "Financial institutions": ("bank", "financial institution", "lender"),
    "Healthcare organizations": ("hospital", "clinic", "health system"),
    "Retailers": ("retailer", "merchant", "commerce business"),
}

PRICING_TERMS = {
    "Subscription": ("monthly", "annual plan", "subscription"),
    "Usage-based": ("usage-based", "pay as you go", "per request", "per transaction"),
    "Transaction fee": ("transaction fee", "per successful charge", "processing fee"),
    "Freemium": ("free plan", "free tier", "start for free"),
    "Enterprise contract": ("contact sales", "custom pricing", "enterprise pricing"),
}

ROLE_TERMS = (
    "founder", "co-founder", "chief executive officer", "ceo",
    "chief technology officer", "cto", "chief operating officer", "coo",
    "president",
)


def clean_text(value: str) -> str:
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


class StructuredHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.headings: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.meta: dict[str, str] = {}

        self._ignored_depth = 0
        self._in_title = False
        self._heading_depth = 0
        self._heading_parts: list[str] = []
        self._current_link: Optional[str] = None
        self._current_link_text: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, Optional[str]]],
    ) -> None:
        tag = tag.lower()
        attributes = {key.lower(): value or "" for key, value in attrs}

        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored_depth += 1
            return

        if tag == "title":
            self._in_title = True

        if tag in {"h1", "h2", "h3"}:
            self._heading_depth += 1
            self._heading_parts = []

        if tag == "meta":
            name = (
                attributes.get("name")
                or attributes.get("property")
                or attributes.get("itemprop")
                or ""
            ).lower()
            content = clean_text(attributes.get("content", ""))
            if name and content:
                self.meta[name] = content

        if tag == "a":
            self._current_link = attributes.get("href")
            self._current_link_text = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag in {"script", "style", "noscript", "svg"}:
            if self._ignored_depth:
                self._ignored_depth -= 1
            return

        if tag == "title":
            self._in_title = False

        if tag in {"h1", "h2", "h3"} and self._heading_depth:
            heading = clean_text(" ".join(self._heading_parts))
            if heading:
                self.headings.append(heading)
            self._heading_depth -= 1
            self._heading_parts = []

        if tag == "a" and self._current_link:
            text = clean_text(" ".join(self._current_link_text))
            self.links.append((self._current_link, text))
            self._current_link = None
            self._current_link_text = []

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return

        text = clean_text(data)
        if not text:
            return

        self.text_parts.append(text)

        if self._in_title:
            self.title_parts.append(text)

        if self._heading_depth:
            self._heading_parts.append(text)

        if self._current_link is not None:
            self._current_link_text.append(text)


@dataclass
class WebsitePage:
    url: str
    title: Optional[str]
    description: Optional[str]
    text: str
    headings: list[str] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class WebsiteFacts:
    company_name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    products: list[str] = field(default_factory=list)
    customer_types: list[str] = field(default_factory=list)
    industries_served: list[str] = field(default_factory=list)
    pricing_models: list[str] = field(default_factory=list)
    integrations: list[str] = field(default_factory=list)
    leadership_names: list[str] = field(default_factory=list)
    social_links: dict[str, str] = field(default_factory=dict)
    careers_url: Optional[str] = None
    pricing_url: Optional[str] = None
    about_url: Optional[str] = None
    source_pages: list[str] = field(default_factory=list)


def parse_html(url: str, html: str) -> WebsitePage:
    parser = StructuredHTMLParser()
    parser.feed(html)

    title = (
        parser.meta.get("og:site_name")
        or parser.meta.get("application-name")
        or clean_text(" ".join(parser.title_parts))
        or None
    )

    description = (
        parser.meta.get("description")
        or parser.meta.get("og:description")
        or parser.meta.get("twitter:description")
        or None
    )

    return WebsitePage(
        url=url,
        title=title,
        description=description,
        text=clean_text(" ".join(parser.text_parts)),
        headings=parser.headings,
        links=parser.links,
    )


def infer_category(
    text: str,
    category_terms: dict[str, tuple[str, ...]],
) -> list[str]:
    lowered = text.lower()
    scored: list[tuple[int, str]] = []

    for category, terms in category_terms.items():
        score = sum(lowered.count(term) for term in terms)
        if score:
            scored.append((score, category))

    scored.sort(reverse=True)
    return [category for _, category in scored]


def extract_company_name(pages: list[WebsitePage]) -> Optional[str]:
    for page in pages:
        if page.title:
            name = re.split(r"\s+[|\-–—]\s+", page.title)[0].strip()
            if 1 < len(name) <= 100:
                return name
    return None


def extract_description(pages: list[WebsitePage]) -> Optional[str]:
    for page in pages:
        if page.description and 25 <= len(page.description) <= 600:
            return page.description
    return None


def extract_products(pages: list[WebsitePage]) -> list[str]:
    candidates: list[str] = []
    ignored = {
        "home", "about", "company", "pricing", "customers", "resources",
        "contact", "login", "sign in", "sign up", "careers", "blog",
    }

    for page in pages:
        for heading in page.headings:
            value = clean_text(heading)
            lowered = value.lower()

            if not 3 <= len(value) <= 90:
                continue
            if lowered in ignored:
                continue
            if any(
                keyword in lowered
                for keyword in (
                    "product", "platform", "solution", "payment", "billing",
                    "analytics", "automation", "management", "security",
                    "infrastructure", "connect", "terminal", "identity",
                )
            ):
                candidates.append(value)

    return deduplicate(candidates)[:15]


def extract_integrations(pages: list[WebsitePage]) -> list[str]:
    results: list[str] = []

    for page in pages:
        for href, text in page.links:
            combined = f"{href} {text}".lower()
            if "integration" in combined or "/apps/" in combined:
                value = clean_text(text)
                if 2 <= len(value) <= 80:
                    results.append(value)

    return deduplicate(results)[:20]


def extract_social_links(pages: list[WebsitePage]) -> dict[str, str]:
    results: dict[str, str] = {}

    for page in pages:
        for href, _ in page.links:
            absolute = urljoin(page.url, href)
            hostname = urlparse(absolute).netloc.lower()

            for domain, label in SOCIAL_DOMAINS.items():
                if domain in hostname and label not in results:
                    results[label] = absolute

    return results


def extract_special_urls(pages: list[WebsitePage]) -> dict[str, Optional[str]]:
    results = {"careers": None, "pricing": None, "about": None}

    for page in pages:
        for href, text in page.links:
            absolute = urljoin(page.url, href)
            combined = f"{urlparse(absolute).path} {text}".lower()

            if results["careers"] is None and any(
                term in combined for term in ("careers", "jobs", "join us")
            ):
                results["careers"] = absolute

            if results["pricing"] is None and "pricing" in combined:
                results["pricing"] = absolute

            if results["about"] is None and any(
                term in combined for term in ("about", "company", "our story")
            ):
                results["about"] = absolute

    return results


def extract_leadership_names(pages: list[WebsitePage]) -> list[str]:
    results: list[str] = []
    name_pattern = re.compile(
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b"
    )

    for page in pages:
        sentences = re.split(r"(?<=[.!?])\s+", page.text)
        for sentence in sentences:
            lowered = sentence.lower()
            if not any(role in lowered for role in ROLE_TERMS):
                continue

            for match in name_pattern.findall(sentence):
                if len(match) <= 60:
                    results.append(match)

    return deduplicate(results)[:12]


def extract_industries_served(pages: list[WebsitePage]) -> list[str]:
    results: list[str] = []

    terms = (
        "retail", "healthcare", "financial services", "education",
        "manufacturing", "software", "technology", "media",
        "travel", "hospitality", "real estate", "insurance",
        "government", "nonprofit", "e-commerce",
    )

    text = " ".join(page.text.lower() for page in pages)

    for term in terms:
        if term in text:
            results.append(term.title())

    return results


def deduplicate(values: list[str]) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []

    for value in values:
        cleaned = clean_text(value)
        key = cleaned.lower()

        if cleaned and key not in seen:
            seen.add(key)
            results.append(cleaned)

    return results


def extract_website_facts(pages: list[WebsitePage]) -> WebsiteFacts:
    full_text = " ".join(page.text for page in pages)
    special_urls = extract_special_urls(pages)

    industries = infer_category(full_text, INDUSTRY_TERMS)
    customers = infer_category(full_text, CUSTOMER_TERMS)
    pricing = infer_category(full_text, PRICING_TERMS)

    return WebsiteFacts(
        company_name=extract_company_name(pages),
        description=extract_description(pages),
        industry=industries[0] if industries else None,
        products=extract_products(pages),
        customer_types=customers[:5],
        industries_served=extract_industries_served(pages),
        pricing_models=pricing[:5],
        integrations=extract_integrations(pages),
        leadership_names=extract_leadership_names(pages),
        social_links=extract_social_links(pages),
        careers_url=special_urls["careers"],
        pricing_url=special_urls["pricing"],
        about_url=special_urls["about"],
        source_pages=[page.url for page in pages],
    )
