import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def extract_links(url):
    soup = get_soup(url)

    links = set()

    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])

        if href.startswith("http"):
            links.add(href)

    return sorted(links)


def save_links(url, output):

    links = extract_links(url)

    pd.DataFrame({"url": links}).to_csv(output, index=False)

    print("Saved", len(links), "links")