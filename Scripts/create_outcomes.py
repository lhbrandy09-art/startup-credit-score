import pandas as pd

df = pd.read_csv("outputs/yc_classified_dataset.csv")

# Determine success
def determine_success(stage):
    stage = str(stage).lower()

    successful_stages = [
        "series a",
        "series b",
        "series c",
        "growth"
    ]

    for s in successful_stages:
        if s in stage:
            return "Yes"

    return "No"

df["Raised_Next_Round"] = df["stage"].apply(determine_success)

# Save updated dataset
df.to_csv("outputs/yc_final_dataset.csv", index=False)

print("Saved final dataset.")

print("\nOutcome counts:")
print(df["Raised_Next_Round"].value_counts())
