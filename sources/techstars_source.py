import pandas as pd
from sources.schema import normalize

def clean_join(series):
    values = series.dropna().astype(str).str.strip()
    values = [v for v in values if v and v.lower() != "nan"]
    return ", ".join(sorted(set(values)))

def load():
    companies = pd.read_csv("data/companies.csv")
    industries = pd.read_csv("data/industries.csv")
    programs = pd.read_csv("data/program_names.csv")

    industry_map = (
        industries.groupby("company_id")["industry_vertical"]
        .apply(clean_join)
        .reset_index()
    )

    program_map = (
        programs.groupby("company_id")["program_names"]
        .apply(clean_join)
        .reset_index()
    )

    df = companies.merge(industry_map, on="company_id", how="left")
    df = df.merge(program_map, on="company_id", how="left")

    df = df.rename(columns={
        "company_name": "name",
        "brief_description": "description",
        "industry_vertical": "industry",
        "linkedin_url": "linkedin",
        "twitter_url": "twitter",
        "crunchbase_url": "crunchbase",
        "city": "location",
        "first_session_year": "founded_year"
    })

    df["source"] = "Techstars"
    df["accelerator"] = "Techstars"

    return normalize(df, "Techstars")