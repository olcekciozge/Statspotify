from html import escape

import streamlit as st

from src.charts import (
    listening_heatmap,
    monthly_hours_chart,
    new_artists_chart,
    skip_rate_chart,
    top_artists_chart,
)
from src.clean import clean_history, load_history
from src.stats import top_items, yearly_favorites

st.set_page_config(page_title="Spotify Listening History", layout="wide")


@st.cache_data
def load_data():
    """Load and clean the data once, then reuse it between reruns."""
    return clean_history(load_history(), keep_short=True)


# all_plays includes short listens (needed for skip rates), df is the usual view
all_plays = load_data()
df = all_plays[~all_plays["is_short"]]

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


def apply_filters(data):
    mask = (data["played_at"].dt.date >= start) & (data["played_at"].dt.date <= end)
    if selected_artists:
        mask &= data["artist"].isin(selected_artists)
    return data[mask]


filtered = apply_filters(df)
filtered_all = apply_filters(all_plays)

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

st.subheader("Track of the year")
favorites = yearly_favorites(filtered)
cards = st.columns(len(favorites))
for card, row in zip(cards, favorites.itertuples()):
    with card.container(border=True):
        st.markdown(
            f"""
<div style="font-size:0.85rem; opacity:0.7;">{row.year}</div>
<div style="font-size:1.25rem; font-weight:700; line-height:1.25; margin:0.2rem 0;">{escape(row.track)}</div>
<div>{escape(row.artist)}</div>
<div style="color:#1DB954; font-weight:600; margin-bottom:0.9rem;">{row.track_plays} plays</div>
<div style="font-size:0.85rem; opacity:0.7;">Most listened artist</div>
<div style="font-weight:600;">{escape(row.top_artist)}</div>
<div style="color:#1DB954; font-weight:600;">{row.artist_plays} plays</div>
""",
            unsafe_allow_html=True,
        )

st.plotly_chart(top_artists_chart(filtered), width="stretch")
st.plotly_chart(monthly_hours_chart(filtered), width="stretch")
st.plotly_chart(listening_heatmap(filtered), width="stretch")
st.plotly_chart(new_artists_chart(df, start, end), width="stretch")

min_plays = st.slider("Minimum plays for skip rate", 20, 300, 100, step=10)
st.plotly_chart(skip_rate_chart(filtered_all, min_plays=min_plays), width="stretch")

st.subheader("Explore rankings")
c1, c2, c3, c4 = st.columns(4)

kind = c1.selectbox("Rank", ["Tracks", "Artists", "Albums"])
years = sorted((int(y) for y in filtered["played_at"].dt.year.unique()), reverse=True)
year_choice = c2.selectbox("Year", ["All time"] + years)
sort_choice = c3.selectbox("Sort by", ["Plays", "Hours"])
top_n = c4.slider("Show top", min_value=10, max_value=100, value=25, step=5)

ranking = top_items(
    filtered,
    by={"Tracks": "track", "Artists": "artist", "Albums": "album"}[kind],
    n=top_n,
    year=None if year_choice == "All time" else year_choice,
    sort_by=sort_choice.lower(),
)
st.dataframe(
    ranking,
    width="stretch",
    height=min(35 * (len(ranking) + 1) + 3, 600),
    column_config={
        "track": "Track",
        "artist": "Artist",
        "album": "Album",
        "plays": "Plays",
        "hours": st.column_config.NumberColumn("Hours", format="%.1f"),
    },
)