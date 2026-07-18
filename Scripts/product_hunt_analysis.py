import pandas as pd

df = pd.read_csv("outputs/yc_product_hunt_enriched.csv")

print("\nPRODUCT HUNT COUNTS")
print(df["Product_Hunt_Present"].value_counts())

print("\nPRODUCT HUNT SUCCESS RATES")
ph_analysis = df.groupby("Product_Hunt_Present")["Raised_Next_Round"].apply(
    lambda x: (x == "Yes").mean() * 100
)

print(ph_analysis)

print("\nSAMPLE MATCHES")
print(
    df[df["Product_Hunt_Present"] == "Yes"][
        ["name", "Product_Hunt_URL", "Raised_Next_Round"]
    ].head(20)
)
