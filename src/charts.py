from html import escape

import pandas as pd
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

def new_artists_chart(df, start, end):
    """Bar chart of artists heard for the first time each month.

    Hovering a bar shows the 3 most played artists discovered that month.
    """
    # First play is computed on the full history, then limited to the date range
    stats = df.groupby("artist").agg(
        first_play=("played_at", "min"), plays=("ms_played", "size")
    )
    stats = stats[
        (stats["first_play"].dt.date >= start) & (stats["first_play"].dt.date <= end)
    ].copy()
    stats["month"] = (
        stats["first_play"].dt.tz_localize(None).dt.to_period("M").dt.to_timestamp()
    )

    rows = []
    for month, group in stats.groupby("month"):
        top3 = group.nlargest(3, "plays")
        names = "<br>".join(
            f"{i}. {escape(artist)} ({plays} plays)"
            for i, (artist, plays) in enumerate(top3["plays"].items(), start=1)
        )
        rows.append(
            {"month": month, "new_artists": len(group), "top_artists": names}
        )
    counts = pd.DataFrame(rows, columns=["month", "new_artists", "top_artists"])

    fig = px.bar(
        counts,
        x="month",
        y="new_artists",
        custom_data=["top_artists"],
        title="New artists discovered per month",
        labels={"month": "", "new_artists": "New artists"},
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x|%B %Y}</b><br>"
            "%{y} new artists<br><br>"
            "Most played discoveries:<br>%{customdata[0]}"
            "<extra></extra>"
        )
    )
    return fig

def skip_rate_chart(df, min_plays=100, n=15):
    """Artists whose tracks are most often skipped (played under 30 seconds)."""
    stats = df.groupby("artist").agg(
        plays=("is_short", "size"), skips=("is_short", "sum")
    )
    # Ignore artists with too few plays, their rate would be noise
    stats = stats[stats["plays"] >= min_plays].copy()
    stats["skip_rate"] = stats["skips"] / stats["plays"] * 100
    top = stats.nlargest(n, "skip_rate").reset_index()

    fig = px.bar(
        top,
        x="skip_rate",
        y="artist",
        orientation="h",
        custom_data=["skips", "plays"],
        title=f"Most skipped artists (min. {min_plays} plays)",
        labels={"skip_rate": "Skip rate (%)", "artist": ""},
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>%{x:.0f}% skipped<br>"
            "%{customdata[0]} of %{customdata[1]} plays<extra></extra>"
        )
    )
    return fig