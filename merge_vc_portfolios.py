import pandas as pd

master = pd.read_csv("Outputs/final_startup_graph.csv")
vc = pd.read_csv("Data/vc_portfolio_startups.csv")

combined = pd.concat([master, vc], ignore_index=True)

combined["name_clean"] = (
    combined["name"]
    .astype(str)
    .str.lower()
    .str.strip()
)

combined = combined.drop_duplicates(subset=["name_clean"], keep="first")

combined.to_csv("Outputs/final_startup_graph.csv", index=False)

print(f"Merged successfully! Total startups: {len(combined):,}")
print(f"VC rows added before dedupe: {len(vc):,}")