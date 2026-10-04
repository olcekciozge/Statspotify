import pandas as pd

from src.clean import clean_history
from src.stats import top_items, yearly_favorites

RAW_COLUMNS = [
    "ts",
    "ms_played",
    "master_metadata_track_name",
    "master_metadata_album_artist_name",
    "master_metadata_album_album_name",
    "spotify_track_uri",
]


def make_df():
    def play(ts, track, artist):
        return (ts, 200_000, track, artist, f"{artist} album", f"uri:{track}")

    rows = [
        play("2023-01-01T10:00:00Z", "Song X", "Artist 1"),
        play("2023-01-01T10:10:00Z", "Song X", "Artist 1"),
        play("2023-01-01T10:20:00Z", "Song X", "Artist 1"),
        play("2023-01-02T10:00:00Z", "Song Y", "Artist 2"),
        play("2024-01-01T10:00:00Z", "Song Y", "Artist 2"),
        play("2024-01-01T10:10:00Z", "Song Y", "Artist 2"),
    ]
    return clean_history(pd.DataFrame(rows, columns=RAW_COLUMNS))


def test_yearly_favorites_picks_most_played_track_and_artist():
    fav = yearly_favorites(make_df()).set_index("year")

    assert fav.loc[2023, "track"] == "Song X"
    assert fav.loc[2023, "track_plays"] == 3
    assert fav.loc[2023, "top_artist"] == "Artist 1"
    assert fav.loc[2023, "artist_plays"] == 3

    assert fav.loc[2024, "track"] == "Song Y"
    assert fav.loc[2024, "track_plays"] == 2


def test_top_items_ranks_tracks_by_plays():
    ranking = top_items(make_df(), by="track", n=2)
    assert list(ranking["track"]) == ["Song X", "Song Y"]
    assert ranking.loc[1, "plays"] == 3


def test_top_items_can_be_limited_to_a_year():
    ranking = top_items(make_df(), by="track", n=5, year=2024)
    assert list(ranking["track"]) == ["Song Y"]
    assert ranking.loc[1, "plays"] == 2