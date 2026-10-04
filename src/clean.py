from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FILE_PATTERN = "Streaming_History_Audio_*.json"

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


def using_sample_data(data_dir=ROOT / "data"):
    """True when no personal export is found and the demo data is used instead."""
    return not any(Path(data_dir).glob(FILE_PATTERN))


def load_history(data_dir=ROOT / "data", sample_dir=ROOT / "sample_data"):
    """Read and concatenate all Streaming_History_Audio_*.json files.

    Falls back to the synthetic demo data when there is no personal export.
    """
    files = sorted(Path(data_dir).glob(FILE_PATTERN))
    if not files:
        files = sorted(Path(sample_dir).glob(FILE_PATTERN))
    if not files:
        raise FileNotFoundError(
            f"No streaming history files found in '{data_dir}' or '{sample_dir}'"
        )
    return pd.concat(
        [pd.read_json(f, encoding="utf-8") for f in files], ignore_index=True
    )


def clean_history(df, min_ms=MIN_MS_PLAYED, tz="Europe/Istanbul", keep_short=False):
    """Keep music plays only and convert timestamps.

    Plays shorter than min_ms are dropped, or kept and flagged in an
    `is_short` column when keep_short=True.
    """
    df = df[list(COLUMNS)].rename(columns=COLUMNS)

    # Podcasts and unknown items have no track/artist name
    df = df.dropna(subset=["track", "artist"]).copy()

    df["is_short"] = df["ms_played"] < min_ms
    if not keep_short:
        df = df[~df["is_short"]].copy()

    # UTC string -> timezone-aware datetime in local time
    df["played_at"] = pd.to_datetime(df["played_at"], utc=True).dt.tz_convert(tz)

    df = df.drop_duplicates(subset=["played_at", "track_uri"])
    df["minutes_played"] = df["ms_played"] / 60_000

    return df.sort_values("played_at").reset_index(drop=True)