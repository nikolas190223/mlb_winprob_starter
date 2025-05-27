import pandas as pd, xgboost as xgb, joblib
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV

# ── load historical data with labels ──────────────────────────────────
df = pd.read_csv("historical_features.csv").dropna(subset=["win"])
y  = df["win"]
X  = df.drop(columns=["win", "gameDate", "home", "away", "side"])

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = xgb.XGBClassifier(
    n_estimators=150, max_depth=4, learning_rate=0.1,
    subsample=0.9, colsample_bytree=0.9,
    objective="binary:logistic", eval_metric="logloss"
)
model.fit(Xtr, ytr)

cal = CalibratedClassifierCV(model, cv=3)
cal.fit(Xtr, ytr)

joblib.dump(cal, "model_calibrated.pkl")
joblib.dump(list(X.columns), "feature_cols.pkl")
print("model trained on", len(df), "historic rows")
