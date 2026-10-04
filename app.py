import streamlit as st

from src.charts import monthly_hours_chart, top_artists_chart
from src.clean import clean_history, load_history

st.set_page_config(page_title="Spotify Listening History", layout="wide")


@st.cache_data
def load_data():
    """Load and clean the data once, then reuse it between reruns."""
    return clean_history(load_history())


df = load_data()

st.title("Spotify Listening History")
st.caption(
    f"{df['played_at'].min():%d %b %Y} - {df['played_at'].max():%d %b %Y}"
)

col1, col2, col3 = st.columns(3)
col1.metric("Hours listened", f"{df['minutes_played'].sum() / 60:,.0f}")
col2.metric("Unique artists", f"{df['artist'].nunique():,}")
col3.metric("Unique tracks", f"{df['track_uri'].nunique():,}")

st.plotly_chart(top_artists_chart(df), width="stretch")
st.plotly_chart(monthly_hours_chart(df), width="stretch")