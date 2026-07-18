import pandas as pd

df = pd.read_csv("outputs/yc_github_enriched.csv")

print("\nGITHUB COUNTS")
print(df["GitHub_Present"].value_counts())

print("\nGITHUB SUCCESS RATES")
github_analysis = df.groupby("GitHub_Present")["Raised_Next_Round"].apply(
    lambda x: (x == "Yes").mean() * 100
)

print(github_analysis)

print("\nSAMPLE GITHUB MATCHES")
print(
    df[df["GitHub_Present"] == "Yes"][
        ["name", "GitHub_URL", "Raised_Next_Round"]
    ].head(20)
)
