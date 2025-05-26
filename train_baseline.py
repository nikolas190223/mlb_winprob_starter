# train_baseline.py
"""Train a toy logistic‑regression model on the
home‑team indicator.  Produces `model_lr.pkl`.  Replace
this later with real features!"""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss
import joblib

df = pd.read_csv("games.csv")

# TEMP target & feature placeholders
#df["home_win"] = 1  # TODO: pull real game results
df["feature_home_team"] = 1

X = df[["feature_home_team"]]
y = df["home_win"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = LogisticRegression().fit(X_train, y_train)
probs = model.predict_proba(X_test)[:, 1]
print(f"log‑loss baseline: {log_loss(y_test, probs):.3f}")

joblib.dump(model, "model_lr.pkl")
print("Saved model_lr.pkl")
