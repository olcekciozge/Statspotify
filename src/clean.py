from pathlib import Path

import pandas as pd

# Spotify counts a stream only after 30 seconds of playback
MIN_MS_PLAYED = 30_000

COLUMNS = {
    "ts": "played_at",
    "ms_played": "ms_played",
    "master_metadata_track_name": "track",
    "master_metadata_album_artist_name": "artist",
    "master_metadata_album_album_name": "album",
    "spotify_track_uri": "track_uri",
}


def load_history(data_dir="data"):
    """Read and concatenate all Streaming_History_Audio_*.json files."""
    files = sorted(Path(data_dir).glob("Streaming_History_Audio_*.json"))
    if not files:
        raise FileNotFoundError(f"No streaming history files found in '{data_dir}'")
    return pd.concat(
        [pd.read_json(f, encoding="utf-8") for f in files], ignore_index=True
    )


def clean_history(df, min_ms=MIN_MS_PLAYED, tz="Europe/Istanbul"):
    """Keep music plays only, drop short listens, convert timestamps."""
    df = df[list(COLUMNS)].rename(columns=COLUMNS)

    # Podcasts and unknown items have no track/artist name
    df = df.dropna(subset=["track", "artist"])

    # Drop very short listens (skips)
    df = df[df["ms_played"] >= min_ms].copy()

    # UTC string -> timezone-aware datetime in local time
    df["played_at"] = pd.to_datetime(df["played_at"], utc=True).dt.tz_convert(tz)

    df = df.drop_duplicates(subset=["played_at", "track_uri"])
    df["minutes_played"] = df["ms_played"] / 60_000

    return df.sort_values("played_at").reset_index(drop=True)