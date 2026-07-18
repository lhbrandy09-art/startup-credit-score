import pandas as pd

df = pd.read_csv("outputs/yc_feature_engineered.csv")

# -----------------------------
# HIRING ANALYSIS
# -----------------------------

print("\nHIRING SUCCESS RATES")

hiring_analysis = df.groupby("hiring_binary")[
    "Raised_Next_Round"
].apply(
    lambda x: (x == "Yes").mean() * 100
)

print(hiring_analysis)

# -----------------------------
# BATCH YEAR ANALYSIS
# -----------------------------

print("\nBATCH YEAR SUCCESS RATES")

batch_analysis = df.groupby("batch_year")[
    "Raised_Next_Round"
].apply(
    lambda x: (x == "Yes").mean() * 100
)

print(batch_analysis.sort_index())

# -----------------------------
# TAG COUNT ANALYSIS
# -----------------------------

print("\nAVERAGE TAG COUNT BY SUCCESS")

tag_analysis = df.groupby("Raised_Next_Round")[
    "tag_count"
].mean()

print(tag_analysis)

# -----------------------------
# DESCRIPTION LENGTH ANALYSIS
# -----------------------------

print("\nAVERAGE DESCRIPTION LENGTH BY SUCCESS")

desc_analysis = df.groupby("Raised_Next_Round")[
    "description_length"
].mean()

print(desc_analysis)
