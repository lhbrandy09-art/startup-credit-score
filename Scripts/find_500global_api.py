import requests
import re

url = "https://500.co/companies"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=15
)

html = response.text

patterns = [
    r'https://[^"\']+api[^"\']+',
    r'https://[^"\']+json[^"\']+',
    r'https://[^"\']+graphql[^"\']+',
]

matches = []

for pattern in patterns:
    found = re.findall(pattern, html)
    matches.extend(found)

print("Potential API endpoints:\n")

for m in sorted(set(matches)):
    print(m)
    