import os, requests, pandas as pd, joblib

API_KEY = os.getenv("ODDS_API_KEY")
if not API_KEY:
    raise SystemExit("ODDS_API_KEY not set")

URL = ("https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/"
       f"?regions=us&markets=h2h&oddsFormat=american&apiKey={API_KEY}")

def implied(american):
    return 100/(american+100) if american > 0 else -american/(-american+100)

json_games = requests.get(URL, timeout=30).json()

model = joblib.load("model_calibrated.pkl")
cols  = joblib.load("feature_cols.pkl")
def dummy(): return pd.DataFrame([{c: 1 for c in cols}])

rows = []
for g in json_games:
    home, away = g["home_team"], g["away_team"]
    prices = g["bookmakers"][0]["markets"][0]["outcomes"]
    a_home = next(o["price"] for o in prices if o["name"] == home)
    a_away = next(o["price"] for o in prices if o["name"] == away)

    prob = model.predict_proba(dummy())[0,1]
    rows.extend([
        dict(game_time=g["commence_time"], home=home, away=away, side="HOME",
             odds=a_home, model_prob=round(prob,3), edge=round(prob - implied(a_home),3)),
        dict(game_time=g["commence_time"], home=home, away=away, side="AWAY",
             odds=a_away, model_prob=round(1-prob,3), edge=round((1-prob) - implied(a_away),3)),
    ])

pd.DataFrame(rows).to_csv("edges.csv", index=False)
print("edges.csv rows:", len(rows))
