import pandas as pd

df = pd.read_csv("outputs/yc_classified_dataset.csv")

print("Total startups:", len(df))

print("\nAI Company Counts:")
print(df["AI_Company"].value_counts())

print("\nBusiness Type Counts:")
print(df["Business_Type"].value_counts())

print("\nIndustry Counts:")
print(df["industry"].value_counts().head(15))

print("\nStage Counts:")
print(df["stage"].value_counts())

print("\nBatch Counts:")
print(df["batch"].value_counts().head(20))
