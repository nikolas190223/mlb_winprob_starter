"""
build_historical.py
Creates historical_features.csv with real win labels (2023-today).

Run once (takes 3-5 min):   python build_historical.py
"""
import pandas as pd, datetime as dt, pytz, requests, time, tqdm, feature_engineering as fe

TZ = pytz.timezone("US/Pacific")
TODAY = dt.datetime.now(TZ).date()

def get_winner(game_pk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    js  = requests.get(url, timeout=30).json()
    try:
        return int(js["liveData"]["linescore"]["teams"]["home"]["isWinner"])
    except Exception:
        home_runs = js["liveData"]["linescore"]["teams"]["home"].get("runs", 0)
        away_runs = js["liveData"]["linescore"]["teams"]["away"].get("runs", 0)
        return int(home_runs > away_runs)

def all_game_pks(start, end):
    pks = []
    curr = start
    bar  = tqdm.tqdm(total=(end - start).days, desc="Schedule")
    while curr <= end:
        url = f"https://statsapi.mlb.com/api/v1/schedule?date={curr}&sportId=1"
        try:
            games = requests.get(url, timeout=30).json()["dates"][0]["games"]
            pks.extend(g["gamePk"] for g in games)
        except Exception:
            pass
        curr += dt.timedelta(days=1)
        bar.update(1)
    bar.close()
    return pks

START = dt.date(2023, 3, 30)          # Opening Day 2023
print("Collecting game IDs …")
game_pks = all_game_pks(START, TODAY - dt.timedelta(days=1))
rows = []

print("Building feature rows …")
for pk in tqdm.tqdm(game_pks, desc="Games"):
    try:
        url = f"https://statsapi.mlb.com/api/v1.1/game/{pk}/feed/live"
        js  = requests.get(url, timeout=30).json()
        date = js["gameData"]["datetime"]["dateTime"][:10]
        home = js["gameData"]["teams"]["home"]["name"]
        away = js["gameData"]["teams"]["away"]["name"]
        winner = get_winner(pk)          # 1 if home, 0 if away

        base = fe.build_features(date)   # tomorrow-style features for that date

        # keep only the two rows matching this matchup
        sub = base.query("home == @home and away == @away").copy()
        sub.loc[sub.side == "HOME", "win"] = winner
        sub.loc[sub.side == "AWAY", "win"] = 1 - winner
        rows.append(sub)
    except Exception:
        pass
    time.sleep(0.25)   # courteous rate-limit

df = pd.concat(rows, ignore_index=True)
df.to_csv("historical_features.csv", index=False)
print("historical_features.csv rows:", len(df))
