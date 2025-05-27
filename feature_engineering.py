"""
feature_engineering.py  – LIVE DATA VERSION
Builds a features.csv with real pitching, bullpen, lineup, and park stats
for every MLB game on a given date (default: tomorrow’s slate).
"""
import pandas as pd, numpy as np, datetime as dt, pytz, requests, time, itertools, re
from bs4 import BeautifulSoup

TZ   = pytz.timezone("US/Pacific")
TODAY = dt.datetime.now(TZ).date()
TOMORROW = TODAY + dt.timedelta(days=1)

# ── MLB team IDs (static) ──────────────────────────────────────────────
TEAM_ID = {t["name"]: t["id"]
           for t in requests.get("https://statsapi.mlb.com/api/v1/teams?sportId=1")
                     .json()["teams"]}

# ── 1. Starter 30-day xFIP ─────────────────────────────────────────────
def probable_starter_id(team, game_date):
    sch = f"https://statsapi.mlb.com/api/v1/schedule?teamId={TEAM_ID[team]}&date={game_date}"
    js  = requests.get(sch, timeout=20).json()
    try:
        g = js["dates"][0]["games"][0]
        side = "home" if g["teams"]["home"]["team"]["name"] == team else "away"
        return g["probablePitchers"][side]["id"]
    except Exception:
        return None

def starter_xfip(pid: int, end_date: str) -> float:
    if pid is None: return np.nan
    start = (dt.date.fromisoformat(end_date) - dt.timedelta(days=30)).isoformat()
    url = (f"https://statsapi.mlb.com/api/v1/people/{pid}/stats?"
           f"stats=pitching&group=pitching&startDate={start}&endDate={end_date}")
    js  = requests.get(url, timeout=30).json()
    try:
        s = js["stats"][0]["splits"][0]["stat"]
        # xFIP ≈ FIP – 0.1*HR + 1.5*BB – 0.7*K  (quick proxy)
        return (float(s["era"]) -
                0.1*float(s.get("homeRuns",0)) +
                1.5*float(s["baseOnBalls"]) -
                0.7*float(s["strikeOuts"]))
    except Exception:
        return np.nan

# ── 2. Bullpen FIP & fatigue index ─────────────────────────────────────
BG_URL = "https://cdn.fangraphs.com/api/roster-resource/bullpen-usage?date={}&json=true"

def bullpen_fip(team, date=TODAY):
    """Return (FIP, last-3-day IP).  NaN, NaN if API offline."""
    try:
        df = pd.read_json(BG_URL.format(date))
        row = df.loc[df.teamName == team]
        if row.empty:
            return np.nan, np.nan
        return float(row.fip), float(row.last3)
    except Exception:
        return np.nan, np.nan

# ── 3. Team 14-day wRC+ (split) ───────────────────────────────────────
LG_URL = (
    "https://cdn.fangraphs.com/api/leaders?"
    "pos=all&stats=bat&qual=y&type=8&team={team}&"
    "startdate={start}&enddate={end}&json=true"
)

def team_wrc(team_name, date_end):
    """Return team wRC+ last 14 days (vs all pitching). NaN if API offline."""
    try:
        end   = dt.date.fromisoformat(date_end)
        start = end - dt.timedelta(days=14)
        url   = LG_URL.format(team=TEAM_ID[team_name],
                              start=start.strftime("%Y-%m-%d"),
                              end=end.strftime("%Y-%m-%d"))
        js = requests.get(url, timeout=20).json()
        return float(js[0]["wRC+"].strip("%"))
    except Exception:
        return np.nan

# ── 4. Park factor (2025) ──────────────────────────────────────────────
PARK = {"Fenway Park": 1.02, "Dodger Stadium": 0.94, "Yankee Stadium": 1.03}

def park_factor(team):   # crude map
    if "Boston" in team: return PARK["Fenway Park"]
    if "Dodgers" in team: return PARK["Dodger Stadium"]
    return 1.00

# ── build dataframe ────────────────────────────────────────────────────
def build_features(g_date=str(TOMORROW)):
    sched = (f"https://statsapi.mlb.com/api/v1/schedule?"
             f"date={g_date}&sportId=1")
    games = requests.get(sched, timeout=30).json()["dates"][0]["games"]
    rows  = []
    for g in games:
        home, away = g["teams"]["home"]["team"]["name"], g["teams"]["away"]["team"]["name"]
        pid_home = probable_starter_id(home, g_date)
        pid_away = probable_starter_id(away, g_date)
        xfip_home = starter_xfip(pid_home, g_date)
        xfip_away = starter_xfip(pid_away, g_date)
        fip_home, fat_home = bullpen_fip(home)
        fip_away, fat_away = bullpen_fip(away)
        wrc_home = team_wrc(home, g_date)
        wrc_away = team_wrc(away, g_date)
        pf = park_factor(home)

        rows.extend([
            dict(gameDate=g_date, home=home, away=away, side="HOME",
                 starter_xfip=xfip_home, bullpen_fip=fip_home,
                 bullpen_fatigue=fat_home, lineup_wrc=wrc_home,
                 park_factor=pf),
            dict(gameDate=g_date, home=home, away=away, side="AWAY",
                 starter_xfip=xfip_away, bullpen_fip=fip_away,
                 bullpen_fatigue=fat_away, lineup_wrc=wrc_away,
                 park_factor=pf),
        ])
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = build_features()
    df["win"] = np.nan   # placeholder; historical label not needed for inference
    df.to_csv("features.csv", index=False)
    print("features.csv rows:", len(df))
