import streamlit as st, pandas as pd

st.set_page_config(page_title="MLB Full Board", layout="wide")
st.title("MLB Model vs Market — Full Board")

df = pd.read_csv("edges.csv")
df.sort_values("edge", ascending=False, inplace=True)

show_only = st.checkbox("Show only value bets (edge ≥5 %)", value=False)
view = df[df.edge >= 0.05] if show_only else df

def badge(e): return "🟢 Value" if e >= 0.05 else ""

st.dataframe(
    view.assign(badge=view.edge.map(badge))
        [["game_time","home","away","side","odds","model_prob","edge","badge"]],
    hide_index=True,
)

# Parlay builder
st.subheader("📋 Parlay Builder (value picks only)")
df_val = df[df.edge >= 0.05]

options = {
    i: f"{row.side[0]}: {row.home} vs {row.away} ({int(row.odds):+})"
    for i, row in df_val.iterrows()
}
selected = st.multiselect("Select up to 3 legs", options=list(options.keys()),
                          format_func=lambda k: options[k], max_selections=3)

if st.button("Build Parlay") and selected:
    p = 1.0
    for i in selected: p *= df_val.at[i, "model_prob"]
    st.success(f"Parlay win probability: {p:.2%}")
else:
    st.caption("Select legs then click Build Parlay")
