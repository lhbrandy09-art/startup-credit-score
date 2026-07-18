import pandas as pd

companies = pd.read_csv("data/companies.csv")
industries = pd.read_csv("data/industries.csv")
programs = pd.read_csv("data/program_names.csv")

print("Companies:", len(companies))
print("Industries:", len(industries))
print("Programs:", len(programs))

def clean_join(series):
    values = (
        series
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = [v for v in values if v and v.lower() != "nan"]

    return ", ".join(sorted(set(values)))

industry_map = (
    industries
    .groupby("company_id")["industry_vertical"]
    .apply(clean_join)
    .reset_index()
)

program_map = (
    programs
    .groupby("company_id")["program_names"]
    .apply(clean_join)
    .reset_index()
)

master = companies.merge(industry_map, on="company_id", how="left")
master = master.merge(program_map, on="company_id", how="left")

master = master.rename(columns={
    "company_name": "name",
    "brief_description": "description",
    "industry_vertical": "industry",
})

master["source"] = "Techstars"
master["accelerator"] = "Techstars"

final = master[[
    "name",
    "website",
    "description",
    "industry",
    "city",
    "country",
    "program_names",
    "source",
    "accelerator",
    "linkedin_url",
    "twitter_url",
    "crunchbase_url",
    "first_session_year",
    "is_exit"
]].copy()

final.to_csv("outputs/techstars_complete.csv", index=False)

print("Saved complete Techstars dataset.")
print("Rows:", len(final))
print(final.head(10))
