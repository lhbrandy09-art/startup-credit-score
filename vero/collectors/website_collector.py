from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class WebsiteCollector:
    """Collect basic website text and metadata."""

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; VEROResearchAgent/1.0)"
        }

    def collect(self, url: str) -> dict[str, Any]:
        if not url:
            raise ValueError("A website URL is required.")

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        title = soup.title.get_text(strip=True) if soup.title else ""

        description_tag = soup.find(
            "meta",
            attrs={"name": "description"},
        )
        description = (
            description_tag.get("content", "").strip()
            if description_tag
            else ""
        )

        text = " ".join(soup.get_text(" ", strip=True).split())
        parsed_url = urlparse(response.url)

        return {
            "url": response.url,
            "domain": parsed_url.netloc,
            "title": title,
            "description": description,
            "text": text,
            "status_code": response.status_code,
        }