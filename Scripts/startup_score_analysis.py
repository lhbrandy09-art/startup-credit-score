import pandas as pd

df = pd.read_csv("outputs/yc_final_dataset.csv")

print("\nTOTAL STARTUPS")
print(len(df))

print("\nSUCCESS RATE")
success_rate = (
    (df["Raised_Next_Round"] == "Yes").mean() * 100
)

print(f"{success_rate:.2f}%")

# -----------------------------
# AI COMPANY ANALYSIS
# -----------------------------
print("\nAI COMPANY SUCCESS RATES")

ai_analysis = df.groupby("AI_Company")[
    "Raised_Next_Round"
].apply(
    lambda x: (x == "Yes").mean() * 100
)

print(ai_analysis)

# -----------------------------
# BUSINESS TYPE ANALYSIS
# -----------------------------
print("\nBUSINESS TYPE SUCCESS RATES")

business_analysis = df.groupby("Business_Type")[
    "Raised_Next_Round"
].apply(
    lambda x: (x == "Yes").mean() * 100
)

print(business_analysis)

# -----------------------------
# INDUSTRY ANALYSIS
# -----------------------------
print("\nTOP INDUSTRY SUCCESS RATES")

industry_analysis = df.groupby("industry")[
    "Raised_Next_Round"
].apply(
    lambda x: (x == "Yes").mean() * 100
)

industry_counts = df["industry"].value_counts()

# only industries with enough startups
valid_industries = industry_counts[
    industry_counts >= 20
].index

industry_analysis = industry_analysis[
    valid_industries
]

print(industry_analysis.sort_values(ascending=False))

# -----------------------------
# TEAM SIZE ANALYSIS
# -----------------------------
print("\nTEAM SIZE SUCCESS RATES")

team_analysis = df.groupby("team_size")[
    "Raised_Next_Round"
].apply(
    lambda x: (x == "Yes").mean() * 100
)

print(team_analysis.sort_index())

# -----------------------------
# TOP COMPANY ANALYSIS
# -----------------------------
print("\nTOP COMPANY SUCCESS RATES")

top_analysis = df.groupby("top_company")[
    "Raised_Next_Round"
].apply(
    lambda x: (x == "Yes").mean() * 100
)

print(top_analysis)
