import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

df = pd.read_csv("outputs/yc_product_hunt_enriched.csv")

df["combined_text"] = (
    df["one_liner"].fillna("") + " " +
    df["long_description"].fillna("") + " " +
    df["tags"].fillna("")
)

y = (df["Raised_Next_Round"] == "Yes").astype(int)

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Creating embeddings...")
embeddings = model.encode(
    df["combined_text"].tolist(),
    show_progress_bar=True
)

clf = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=3000, class_weight="balanced")
)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

print("\nRunning 5-fold cross-validation...")

auc_scores = cross_val_score(
    clf,
    embeddings,
    y,
    cv=cv,
    scoring="roc_auc"
)

print("\nEMBEDDING MODEL ROC AUC SCORES")
print(auc_scores)

print("\nAVERAGE ROC AUC")
print(round(auc_scores.mean(), 3))

print("\nSTANDARD DEVIATION")
print(round(auc_scores.std(), 3))
