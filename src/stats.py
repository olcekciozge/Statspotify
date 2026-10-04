def yearly_favorites(df):
    """Most played track and most played artist (by play count) for each year."""
    year = df["played_at"].dt.year.rename("year")

    # Grouping by name + artist merges single/album versions of the same song
    tracks = (
        df.groupby([year, "track", "artist"]).size().rename("track_plays").reset_index()
    )
    top_tracks = (
        tracks.sort_values(["year", "track_plays"], ascending=[True, False])
        .groupby("year")
        .head(1)
    )

    artists = (
        df.groupby([year, "artist"])
        .size()
        .rename("artist_plays")
        .reset_index()
        .rename(columns={"artist": "top_artist"})
    )
    top_artists = (
        artists.sort_values(["year", "artist_plays"], ascending=[True, False])
        .groupby("year")
        .head(1)
    )

    return top_tracks.merge(top_artists, on="year").reset_index(drop=True)

def top_items(df, by="track", n=100, year=None, sort_by="plays"):
    """Ranking of tracks, artists or albums by play count or hours."""
    if year is not None:
        df = df[df["played_at"].dt.year == year]

    keys = {
        "track": ["track", "artist"],
        "artist": ["artist"],
        "album": ["album", "artist"],
    }[by]

    ranking = (
        df.groupby(keys)
        .agg(plays=("ms_played", "size"), minutes=("minutes_played", "sum"))
        .reset_index()
    )
    ranking["hours"] = (ranking["minutes"] / 60).round(1)
    ranking = ranking.drop(columns="minutes")

    # Ties are broken by the other metric
    other = "hours" if sort_by == "plays" else "plays"
    ranking = ranking.sort_values([sort_by, other], ascending=False).head(n)

    ranking = ranking.reset_index(drop=True)
    ranking.index += 1
    ranking.index.name = "rank"
    return ranking