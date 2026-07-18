import pandas as pd
from pathlib import Path

source_files = [
    "outputs/yc_github_metrics.csv",
    "outputs/product_hunt_startups.csv",
    # add more source CSVs here later:
    # "outputs/product_hunt_startups.csv",
    # "outputs/techstars_startups.csv",
    # "outputs/500global_startups.csv",
    # "outputs/wellfound_startups.csv",
]

frames = []

for file in source_files:
    path = Path(file)

    if path.exists():
        df = pd.read_csv(path)
        frames.append(df)
        print(f"Loaded {file}: {len(df)} rows")
    else:
        print(f"Missing: {file}")

master = pd.concat(frames, ignore_index=True)

master["name_clean"] = master["name"].astype(str).str.lower().str.strip()

master = master.drop_duplicates(subset=["name_clean"])

master.to_csv("outputs/master_startup_database.csv", index=False)

print("Master database saved.")
print("Rows:", len(master))
