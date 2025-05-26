"""
Streamlit front end for value bets — stub
"""
import streamlit as st, pandas as pd, pathlib

st.set_page_config(page_title="MLB Value Bets", layout="wide")
st.title("MLB Value Bet Finder – Stub")

path = pathlib.Path('edges.csv')
if not path.exists():
    st.warning('Run edges.py first')
    st.stop()

df = pd.read_csv(path)
st.dataframe(df)