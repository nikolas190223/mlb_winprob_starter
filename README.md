# MLB Win Probability – Starter Template

A **minimal end‑to‑end skeleton** you can run on your Mac or deploy
to **Streamlit Community Cloud**.  It pulls yesterday's MLB schedule,
trains a *toy* logistic‑regression model (home‑team indicator only),
and displays predicted home‑win probabilities in a Streamlit table.

## 1 — Setup (conda recommended)

```bash
conda create -y -n mlb python=3.11
conda activate mlb
pip install -r requirements.txt
```

## 2 — Pull data & train

```bash
python data_pull.py
python train_baseline.py
```

> **Note**: the baseline model is just a placeholder.  
> We'll swap in real features (bullpen, wRC+, park factors, injuries)
> and XGBoost in the next iteration.

## 3 — Run the app locally

```bash
streamlit run app.py
```

Point your browser to `http://localhost:8501`.

## 4 — Deploy to Streamlit Community Cloud

1. **Push this folder to GitHub** (public repo is free).
2. Go to <https://share.streamlit.io> → *New app* → pick your repo and `app.py`.
3. Click *Deploy*.  The free tier is enough for demo/testing.

## 5 — Next steps

* Replace the placeholder target (`home_win`) with actual game results.
* Add real engineered features from FanGraphs & the MLB Stats API.
* Switch to an XGBoost model for better calibration.
* Wire in Vegas odds and the +5 % value‑bet filter.

Enjoy!  – Your Friendly ChatGPT
