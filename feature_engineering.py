"""
feature_engineering.py
Stub version that creates a features.csv with placeholder stats.
Replace TODO sections with real stat pulls.
"""
import pandas as pd, datetime as dt, numpy as np, pytz

TZ = pytz.timezone("US/Pacific")
TODAY = dt.datetime.now(TZ).date()

def build_stub(days_back: int = 30) -> pd.DataFrame:
    rows = []
    for i in range(1, days_back+1):
        date = TODAY - dt.timedelta(days=i)
        # stub teams
        rows.append(dict(
            gameDate=str(date),
            home="HOME",
            away="AWAY",
            starter_home_xFIP=np.random.uniform(3,5),
            starter_away_xFIP=np.random.uniform(3,5),
            bullpen_home_fip=np.random.uniform(3,5),
            bullpen_away_fip=np.random.uniform(3,5),
            team_home_recent_wRC=np.random.uniform(80,120),
            team_away_recent_wRC=np.random.uniform(80,120),
            park_factor=np.random.uniform(0.9,1.1),
            home_win=np.random.randint(0,2)
        ))
    return pd.DataFrame(rows)

if __name__ == '__main__':
    df = build_stub(30)
    df.to_csv('features.csv', index=False)
    print('features.csv written with', len(df), 'rows')
