import plotly.express as px

SPOTIFY_GREEN = "#1DB954"

def top_artists_chart(df, n=10):
    """Horizontal bar chart of the artists with the most listening hours."""
    top = (
        df.groupby("artist")["minutes_played"].sum().div(60).nlargest(n).reset_index()
    )
    top.columns = ["artist", "hours"]

    fig = px.bar(
        top,
        x="hours",
        y="artist",
        orientation="h",
        title=f"Top {n} artists by listening time",
        labels={"hours": "Hours listened", "artist": ""},
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    # Biggest bar on top
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def monthly_hours_chart(df):
    """Bar chart of total listening hours per month."""
    # Drop the timezone first so to_period doesn't warn about it
    month = df["played_at"].dt.tz_localize(None).dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby(month)["minutes_played"].sum().div(60).reset_index()
    monthly.columns = ["month", "hours"]

    return px.bar(
        monthly,
        x="month",
        y="hours",
        title="Listening time per month",
        labels={"month": "", "hours": "Hours listened"},
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def listening_heatmap(df):
    """Heatmap of listening hours by day of week and hour of day."""
    day = df["played_at"].dt.dayofweek.rename("day")
    hour = df["played_at"].dt.hour.rename("hour")

    grid = (
        df.groupby([day, hour])["minutes_played"]
        .sum()
        .div(60)
        .unstack(fill_value=0)
        # Make sure all 7 days and 24 hours exist, even with filtered data
        .reindex(index=range(7), columns=range(24), fill_value=0)
    )

    fig = px.imshow(
        grid.values,
        x=[f"{h:02d}" for h in range(24)],
        y=DAYS,
        aspect="auto",
        color_continuous_scale=[
            [0.0, "#121212"],  # almost black
            [0.5, "#0B3D1E"],  # very dark green
            [0.8, "#17803D"],  # medium green
            [1.0, "#1DB954"],  # Spotify green, only for the peak hours
        ],
        labels={"x": "Hour of day", "y": "", "color": "Hours"},
        title="When I listen: day of week vs. hour of day",
    )
    return fig