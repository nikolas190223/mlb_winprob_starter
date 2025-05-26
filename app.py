# app.py
"""Minimal Streamlit front‑end that shows yesterday's
games and baseline model probabilities."""
import pandas as pd, streamlit as st
import joblib, pathlib

st.set_page_config(page_title="MLB Win Probability Demo", layout="wide")

st.title("MLB Win Probability – Demo App")

games_path = pathlib.Path("games.csv")
if not games_path.exists():
    st.warning("No games.csv found – run data_pull.py first")
    st.stop()

df = pd.read_csv(games_path)

# if the placeholder feature isn't there, create it on the fly
if "feature_home_team" not in df.columns:
    df["feature_home_team"] = 1

model_path = pathlib.Path("model_lr.pkl")
if model_path.exists():
    model = joblib.load(model_path)
    df["pred_home_win"] = model.predict_proba(df[["feature_home_team"]])[:, 1]
else:
    df["pred_home_win"] = 0.5  # placeholder

st.dataframe(df[["gameDate", "away", "home", "pred_home_win"]], hide_index=True)
