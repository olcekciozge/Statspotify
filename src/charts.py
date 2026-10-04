import plotly.express as px


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
    )