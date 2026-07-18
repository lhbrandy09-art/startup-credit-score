import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("outputs/yc_github_metrics.csv")

df["combined_text"] = (
    df["one_liner"].fillna("") + " " +
    df["long_description"].fillna("") + " " +
    df["tags"].fillna("")
)

features = [
    "combined_text",
    "AI_Company",
    "Business_Type",
    "top_company",
    "hiring_binary",
    "startup_age",
    "tag_count",
    "enterprise_keyword_count",
    "healthcare_keyword_count",
    "ai_keyword_count",
    "Product_Hunt_Present",
    "github_followers",
    "github_public_repos",
    "github_total_stars",
    "github_total_forks"
]

target = "Raised_Next_Round"

model_df = df[features + [target]].dropna().copy()

X = model_df[features]
y = (model_df[target] == "Yes").astype(int)

preprocessor = ColumnTransformer(
    transformers=[
        ("text", TfidfVectorizer(max_features=1000, stop_words="english"), "combined_text"),
        ("cat", OneHotEncoder(handle_unknown="ignore"), [
            "AI_Company",
            "Business_Type",
            "top_company",
            "hiring_binary",
            "Product_Hunt_Present"
        ]),
        ("num", StandardScaler(), [
            "startup_age",
            "tag_count",
            "enterprise_keyword_count",
            "healthcare_keyword_count",
            "ai_keyword_count",
            "github_followers",
            "github_public_repos",
            "github_total_stars",
            "github_total_forks"
        ])
    ]
)

model = Pipeline(
    steps=[
        ("preprocess", preprocessor),
        ("classifier", LogisticRegression(max_iter=3000, class_weight="balanced"))
    ]
)

model.fit(X, y)

joblib.dump(model, "outputs/startup_credit_score_model.pkl")

print("Saved final model to outputs/startup_credit_score_model.pkl")
