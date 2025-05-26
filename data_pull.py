# data_pull.py
"""
Download recent MLB games via the free Stats API, label each with who won,
and write games.csv (with a 'home_win' column).

Run:  python data_pull.py
"""
import datetime as dt
import requests
import pandas as pd
import pytz

# ── date helpers ───────────────────────────────────────────────────────────
TZ = pytz.timezone("US/Pacific")
TODAY = dt.datetime.now(TZ).date()

# ── 1. winner helper ───────────────────────────────────────────────────────
def get_winner(game_pk: int) -> int:
    """
    Return 1 if the home team won, 0 if the away team won.
    Works even when the old 'runs' field is missing.
    """
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    js  = requests.get(url, timeout=30).json()

    # Preferred: boolean flag
    try:
        return int(js["liveData"]["linescore"]["teams"]["home"]["isWinner"])
    except KeyError:
        # Fallback: compare run totals
        teams = js["liveData"]["linescore"]["teams"]
        home_runs = teams["home"].get("runs", 0)
        away_runs = teams["away"].get("runs", 0)
        return int(home_runs > away_runs)

# ── 2. one-day pull ────────────────────────────────────────────────────────
def get_games(date: dt.date) -> pd.DataFrame:
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    js  = requests.get(url, timeout=30).json()
    games = js.get("dates", [{}])[0].get("games", [])
    rows = []
    for g in games:
        game_pk = g["gamePk"]
        rows.append(
            {
                "gamePk":   game_pk,
                "gameDate": str(date),
                "home":     g["teams"]["home"]["team"]["name"],
                "away":     g["teams"]["away"]["team"]["name"],
                "home_win": get_winner(game_pk),
            }
        )
    return pd.DataFrame(rows)

# ── 3. N-day pull helper ───────────────────────────────────────────────────
def get_games_last_n_days(n: int = 7) -> pd.DataFrame:
    """Concatenate get_games(date) for today-1 through today-n."""
    frames = []
    for i in range(1, n + 1):
        date = TODAY - dt.timedelta(days=i)
        frames.append(get_games(date))
    return pd.concat(frames, ignore_index=True)

# ── 4. run when executed directly ──────────────────────────────────────────
if __name__ == "__main__":
    df = get_games_last_n_days(7)            # pull a full week
    df.to_csv("games.csv", index=False)
    print("Saved games.csv with", len(df), "rows")
    print(df["home_win"].value_counts())     # sanity-check 0/1 balance
