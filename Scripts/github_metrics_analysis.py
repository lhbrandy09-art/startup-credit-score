import pandas as pd

df = pd.read_csv("outputs/yc_github_metrics.csv")

print("\nGITHUB METRIC SUMMARY")
print(df[[
    "github_followers",
    "github_public_repos",
    "github_total_stars",
    "github_total_forks"
]].describe())

print("\nAVERAGE GITHUB STARS BY OUTCOME")
print(df.groupby("Raised_Next_Round")["github_total_stars"].mean())

print("\nAVERAGE GITHUB FOLLOWERS BY OUTCOME")
print(df.groupby("Raised_Next_Round")["github_followers"].mean())

print("\nAVERAGE GITHUB REPOS BY OUTCOME")
print(df.groupby("Raised_Next_Round")["github_public_repos"].mean())
