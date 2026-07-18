import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("outputs/yc_product_hunt_enriched.csv")

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
    "ai_keyword_count"
    "Product_Hunt_Present",
]

target = "Raised_Next_Round"

model_df = df[features + [target]].dropna().copy()

X = model_df[features]
y = (model_df[target] == "Yes").astype(int)

text_features = "combined_text"

categorical_features = [
    "AI_Company",
    "Business_Type",
    "top_company",
    "hiring_binary"
    "Product_Hunt_Present",
]

numeric_features = [
    "startup_age",
    "tag_count",
    "enterprise_keyword_count",
    "healthcare_keyword_count",
    "ai_keyword_count"
]

preprocessor = ColumnTransformer(
    transformers=[
        ("text", TfidfVectorizer(max_features=500, stop_words="english"), text_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", StandardScaler(), numeric_features)
    ]
)

model = Pipeline(
    steps=[
        ("preprocess", preprocessor),
        ("classifier", LogisticRegression(max_iter=3000, class_weight="balanced"))
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

print("\nREFINED MODEL ACCURACY")
print(f"{accuracy_score(y_test, predictions) * 100:.2f}%")

print("\nROC AUC SCORE")
print(f"{roc_auc_score(y_test, probabilities):.3f}")

print("\nCLASSIFICATION REPORT")
print(classification_report(y_test, predictions))
