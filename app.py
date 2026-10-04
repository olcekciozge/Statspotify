import streamlit as st

from src.charts import listening_heatmap, monthly_hours_chart, top_artists_chart
from src.clean import clean_history, load_history

st.set_page_config(page_title="Spotify Listening History", layout="wide")


@st.cache_data
def load_data():
    """Load and clean the data once, then reuse it between reruns."""
    return clean_history(load_history())


df = load_data()

# ---- Sidebar filters ----
st.sidebar.header("Filters")

min_date = df["played_at"].min().date()
max_date = df["played_at"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Artists sorted by total listening time, so the favorites come first
artist_options = (
    df.groupby("artist")["minutes_played"].sum().sort_values(ascending=False).index
)
selected_artists = st.sidebar.multiselect("Artists", options=artist_options)

# date_input returns a single date while the user is still picking the end date
if len(date_range) != 2:
    st.info("Select an end date to apply the filter.")
    st.stop()

start, end = date_range
mask = (df["played_at"].dt.date >= start) & (df["played_at"].dt.date <= end)
if selected_artists:
    mask &= df["artist"].isin(selected_artists)
filtered = df[mask]

if filtered.empty:
    st.warning("No listening data for this selection.")
    st.stop()

# ---- Main page ----
st.title("Spotify Listening History")
st.caption(f"{start:%d %b %Y} - {end:%d %b %Y}")

col1, col2, col3 = st.columns(3)
col1.metric("Hours listened", f"{filtered['minutes_played'].sum() / 60:,.0f}")
col2.metric("Unique artists", f"{filtered['artist'].nunique():,}")
col3.metric("Unique tracks", f"{filtered['track_uri'].nunique():,}")

st.plotly_chart(top_artists_chart(filtered), width="stretch")
st.plotly_chart(monthly_hours_chart(filtered), width="stretch")
st.plotly_chart(listening_heatmap(filtered), width="stretch")