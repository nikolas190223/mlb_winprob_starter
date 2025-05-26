"""
edges.py
Stub that reads calibrated model and creates edges.csv with fake odds and edges.
Replace TODO with real Odds API call.
"""
import pandas as pd, numpy as np, joblib, datetime as dt, pytz

TZ = pytz.timezone("US/Pacific")
today = dt.datetime.now(TZ).date()

model = joblib.load('model_calibrated.pkl')
cols = joblib.load('feature_cols.pkl')

# fake single game
X = pd.DataFrame([dict([(c,1) for c in cols])])
prob = model.predict_proba(X)[0,1]
american_odds = 120
implied = 100/(american_odds+100)
edge = prob - implied
df = pd.DataFrame([dict(date=str(today),home='HOME',away='AWAY',odds=american_odds,prob=prob,edge=edge)])
df.to_csv('edges.csv', index=False)
print('edges.csv written')