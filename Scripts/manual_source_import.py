import pandas as pd
from pathlib import Path

input_file = "data/manual_startups.csv"
output_file = "outputs/manual_startups_normalized.csv"

if not Path(input_file).exists():
    sample = pd.DataFrame([
        {
            "name": "Example Startup",
            "website": "https://example.com",
            "description": "Example description",
            "industry": "",
            "location": "",
            "accelerator": ""
        }
    ])
    sample.to_csv(input_file, index=False)
    print(f"Created sample file: {input_file}")
    print("Fill this file with startups, then rerun.")
    raise SystemExit

df = pd.read_csv(input_file)

for col in ["name", "website", "description", "industry", "location", "accelerator"]:
    if col not in df.columns:
        df[col] = ""

df["source"] = "Manual / External List"

df.to_csv(output_file, index=False)

print("Saved normalized manual source.")
print("Rows:", len(df))
