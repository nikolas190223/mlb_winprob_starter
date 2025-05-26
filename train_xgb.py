"""
train_xgb.py
Stub XGBoost trainer.
"""
import pandas as pd, joblib, xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV

df = pd.read_csv('features.csv')
X = df.drop(columns=['home_win','gameDate','home','away'])
y = df['home_win']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = xgb.XGBClassifier(n_estimators=50, objective='binary:logistic', eval_metric='logloss')
model.fit(X_train, y_train)

cal = CalibratedClassifierCV(model, cv=3)
cal.fit(X_train, y_train)

joblib.dump(cal, 'model_calibrated.pkl')
joblib.dump(list(X.columns), 'feature_cols.pkl')
print('Model saved')