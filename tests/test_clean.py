import pandas as pd

from src.clean import clean_history

RAW_COLUMNS = [
    "ts",
    "ms_played",
    "master_metadata_track_name",
    "master_metadata_album_artist_name",
    "master_metadata_album_album_name",
    "spotify_track_uri",
]


def make_raw():
    rows = [
        ("2022-02-03T19:04:24Z", 200_000, "Song A", "Artist 1", "Album 1", "uri:a"),
        ("2022-02-03T19:10:00Z", 10_000, "Song B", "Artist 1", "Album 1", "uri:b"),  # short listen
        ("2022-02-03T19:20:00Z", 150_000, None, None, None, None),  # podcast
        ("2022-02-03T19:04:24Z", 200_000, "Song A", "Artist 1", "Album 1", "uri:a"),  # duplicate
        ("2022-02-04T10:00:00Z", 180_000, "Song C", "Artist 2", "Album 2", "uri:c"),
    ]
    return pd.DataFrame(rows, columns=RAW_COLUMNS)


def test_drops_podcasts_short_listens_and_duplicates():
    df = clean_history(make_raw())
    assert list(df["track"]) == ["Song A", "Song C"]


def test_keep_short_flags_instead_of_dropping():
    df = clean_history(make_raw(), keep_short=True)
    assert len(df) == 3
    assert df["is_short"].sum() == 1
    assert df.loc[df["track"] == "Song B", "is_short"].item()


def test_timestamps_are_converted_to_local_time():
    df = clean_history(make_raw())
    # 19:04 UTC is 22:04 in Istanbul (UTC+3)
    assert df["played_at"].iloc[0].hour == 22
    assert str(df["played_at"].dt.tz) == "Europe/Istanbul"


def test_minutes_played_is_computed():
    df = clean_history(make_raw())
    assert df["minutes_played"].iloc[0] == 200_000 / 60_000