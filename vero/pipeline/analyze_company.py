
import json
from pathlib import Path
from vero.ai.research_agent import build_initial_profile
from vero.ai.investment_memo import generate_investment_memo

ROOT = Path(__file__).resolve().parents[1]

def safe_filename(name: str) -> str:
    cleaned = "".join(c.lower() if c.isalnum() else "_" for c in name)
    return "_".join(x for x in cleaned.split("_") if x)

def analyze_company(company_input: str):
    profile = build_initial_profile(company_input)
    memo = generate_investment_memo(profile)
    slug = safe_filename(profile["company"]["name"])

    company_dir = ROOT/"data"/"companies"
    report_dir = ROOT/"data"/"reports"
    company_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    (company_dir/f"{slug}.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    (report_dir/f"{slug}_report.json").write_text(json.dumps(memo, indent=2), encoding="utf-8")
    return profile, memo
