"""Generate a synthetic Spotify Extended Streaming History for the demo app.

The output mimics the format of the real export (same column names), but every
play is randomly generated. No real listening data is involved.

Run from the project root:
    python scripts/make_sample_data.py
"""

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

SEED = 42
START = date(2022, 3, 1)
END = date(2026, 9, 30)
OUT_DIR = Path(__file__).resolve().parent.parent / "sample_data"

# Local time = UTC + 3 (the app converts timestamps to Europe/Istanbul)
UTC_OFFSET_HOURS = 3

# Average plays per day (before the monthly random factor)
WEEKDAY_PLAYS = 9
WEEKEND_PLAYS = 12
PODCAST_SHARE = 0.015

# Relative likelihood of listening in each local hour (0-23)
WEEKDAY_HOURS = [3, 2, 1, 0.5, 0.3, 0.3, 0.5, 1, 2, 3, 3, 3.5,
                 4, 4, 4, 5, 5.5, 5, 5, 5.5, 6, 6, 6, 5]
WEEKEND_HOURS = [4, 3, 2, 1, 0.5, 0.4, 0.4, 0.8, 1.5, 2, 3, 4,
                 5, 5, 6, 7, 7, 7, 6, 6, 6, 6, 6, 5]

# (artist, popularity, first listened, skip probability, [(track, album), ...])
ARTISTS = [
    ("Billie Eilish", 10, "2022-03-01", 0.08, [
        ("bad guy", "WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?"),
        ("BIRDS OF A FEATHER", "HIT ME HARD AND SOFT"),
        ("WILDFLOWER", "HIT ME HARD AND SOFT"),
        ("ocean eyes", "dont smile at me"),
    ]),
    ("Bad Bunny", 9, "2022-03-01", 0.10, [
        ("Tití Me Preguntó", "Un Verano Sin Ti"),
        ("Me Porto Bonito", "Un Verano Sin Ti"),
        ("Ojitos Lindos", "Un Verano Sin Ti"),
        ("DtMF", "DeBÍ TiRAR MáS FOToS"),
    ]),
    ("The Weeknd", 8, "2022-03-01", 0.10, [
        ("Blinding Lights", "After Hours"),
        ("Save Your Tears", "After Hours"),
        ("Starboy", "Starboy"),
        ("Die For You", "Starboy"),
    ]),
    ("Taylor Swift", 8, "2022-03-15", 0.15, [
        ("Anti-Hero", "Midnights"),
        ("Cruel Summer", "Lover"),
        ("Blank Space", "1989"),
        ("Lavender Haze", "Midnights"),
    ]),
    ("Arctic Monkeys", 6, "2022-04-01", 0.10, [
        ("Do I Wanna Know?", "AM"),
        ("R U Mine?", "AM"),
        ("505", "Favourite Worst Nightmare"),
        ("I Wanna Be Yours", "AM"),
    ]),
    ("Coldplay", 4, "2022-03-01", 0.20, [
        ("Yellow", "Parachutes"),
        ("Viva La Vida", "Viva la Vida or Death and All His Friends"),
        ("Fix You", "X&Y"),
        ("The Scientist", "A Rush of Blood to the Head"),
    ]),
    ("Imagine Dragons", 3, "2022-05-01", 0.25, [
        ("Believer", "Evolve"),
        ("Radioactive", "Night Visions"),
        ("Thunder", "Evolve"),
        ("Demons", "Night Visions"),
    ]),
    ("Ed Sheeran", 3, "2022-03-01", 0.30, [
        ("Shape of You", "÷"),
        ("Perfect", "÷"),
        ("Thinking out Loud", "x"),
        ("Bad Habits", "="),
    ]),
    ("Queen", 3, "2022-06-01", 0.15, [
        ("Bohemian Rhapsody", "A Night at the Opera"),
        ("Don't Stop Me Now", "Jazz"),
        ("Under Pressure", "Hot Space"),
        ("Another One Bites the Dust", "The Game"),
    ]),
    ("Dua Lipa", 6, "2022-09-01", 0.12, [
        ("Levitating", "Future Nostalgia"),
        ("Don't Start Now", "Future Nostalgia"),
        ("Houdini", "Radical Optimism"),
        ("Training Season", "Radical Optimism"),
    ]),
    ("Harry Styles", 5, "2022-10-01", 0.15, [
        ("As It Was", "Harry's House"),
        ("Watermelon Sugar", "Fine Line"),
        ("Late Night Talking", "Harry's House"),
        ("Adore You", "Fine Line"),
    ]),
    ("Lana Del Rey", 5, "2022-11-01", 0.10, [
        ("Summertime Sadness", "Born to Die"),
        ("Video Games", "Born to Die"),
        ("Born to Die", "Born to Die"),
        ("Say Yes To Heaven", "Say Yes To Heaven"),
    ]),
    ("Olivia Rodrigo", 5, "2023-01-15", 0.12, [
        ("drivers license", "SOUR"),
        ("good 4 u", "SOUR"),
        ("vampire", "GUTS"),
        ("bad idea right?", "GUTS"),
    ]),
    ("Daft Punk", 3, "2023-02-01", 0.15, [
        ("Get Lucky", "Random Access Memories"),
        ("One More Time", "Discovery"),
        ("Instant Crush", "Random Access Memories"),
        ("Harder, Better, Faster, Stronger", "Discovery"),
    ]),
    ("Tame Impala", 4, "2023-03-01", 0.10, [
        ("The Less I Know The Better", "Currents"),
        ("Let It Happen", "Currents"),
        ("Borderline", "The Slow Rush"),
        ("Eventually", "Currents"),
    ]),
    ("Drake", 3, "2023-04-01", 0.30, [
        ("God's Plan", "Scorpion"),
        ("One Dance", "Views"),
        ("Hotline Bling", "Views"),
        ("Rich Flex", "Her Loss"),
    ]),
    ("Kendrick Lamar", 3, "2023-05-01", 0.20, [
        ("HUMBLE.", "DAMN."),
        ("Not Like Us", "Not Like Us"),
        ("Money Trees", "good kid, m.A.A.d city"),
        ("luther", "GNX"),
    ]),
    ("Fleetwood Mac", 3, "2023-06-01", 0.12, [
        ("Dreams", "Rumours"),
        ("Go Your Own Way", "Rumours"),
        ("The Chain", "Rumours"),
        ("Everywhere", "Tango in the Night"),
    ]),
    ("Ariana Grande", 3, "2023-08-01", 0.25, [
        ("7 rings", "thank u, next"),
        ("thank u, next", "thank u, next"),
        ("positions", "Positions"),
        ("we can't be friends (wait for your love)", "eternal sunshine"),
    ]),
    ("Rosalía", 3, "2023-10-01", 0.15, [
        ("DESPECHÁ", "MOTOMAMI"),
        ("SAOKO", "MOTOMAMI"),
        ("CUUUUuuuuuute", "MOTOMAMI"),
        ("Malamente", "El Mal Querer"),
    ]),
    ("Travis Scott", 2, "2023-11-01", 0.25, [
        ("SICKO MODE", "ASTROWORLD"),
        ("goosebumps", "Birds In The Trap Sing McKnight"),
        ("FE!N", "UTOPIA"),
        ("HIGHEST IN THE ROOM", "HIGHEST IN THE ROOM"),
    ]),
    ("Radiohead", 3, "2024-01-15", 0.10, [
        ("Creep", "Pablo Honey"),
        ("Karma Police", "OK Computer"),
        ("No Surprises", "OK Computer"),
        ("Weird Fishes/Arpeggi", "In Rainbows"),
    ]),
    ("Doja Cat", 2, "2024-03-01", 0.30, [
        ("Say So", "Hot Pink"),
        ("Kiss Me More", "Planet Her"),
        ("Woman", "Planet Her"),
        ("Paint The Town Red", "Scarlet"),
    ]),
    ("SZA", 4, "2024-05-01", 0.10, [
        ("Kill Bill", "SOS"),
        ("Snooze", "SOS"),
        ("Good Days", "Good Days"),
        ("Shirt", "SOS"),
    ]),
    ("Frank Ocean", 3, "2024-07-01", 0.12, [
        ("Pink + White", "Blonde"),
        ("Nights", "Blonde"),
        ("Thinkin Bout You", "channel ORANGE"),
        ("Ivy", "Blonde"),
    ]),
    ("Gorillaz", 2, "2024-09-01", 0.15, [
        ("Feel Good Inc.", "Demon Days"),
        ("Clint Eastwood", "Gorillaz"),
        ("On Melancholy Hill", "Plastic Beach"),
        ("DARE", "Demon Days"),
    ]),
    ("Post Malone", 2, "2024-11-01", 0.30, [
        ("Circles", "Hollywood's Bleeding"),
        ("rockstar", "beerbongs & bentleys"),
        ("Congratulations", "Stoney"),
        ("Sunflower", "Spider-Man: Into the Spider-Verse"),
    ]),
    ("Sabrina Carpenter", 5, "2025-02-01", 0.15, [
        ("Espresso", "Short n' Sweet"),
        ("Please Please Please", "Short n' Sweet"),
        ("Taste", "Short n' Sweet"),
        ("Feather", "Short n' Sweet"),
    ]),
    ("Tyler, The Creator", 3, "2025-06-01", 0.15, [
        ("EARFQUAKE", "IGOR"),
        ("See You Again", "Flower Boy"),
        ("NEW MAGIC WAND", "IGOR"),
        ("SUGAR ON MY TONGUE", "CHROMAKOPIA"),
    ]),
    ("Bruno Mars", 2, "2025-09-01", 0.20, [
        ("Locked Out Of Heaven", "Unorthodox Jukebox"),
        ("That's What I Like", "24K Magic"),
        ("24K Magic", "24K Magic"),
        ("Die With A Smile", "Die With A Smile"),
    ]),
]


def main():
    rng = np.random.default_rng(SEED)

    # --- Fixed properties of every artist and track ---
    start_days = [date.fromisoformat(a[2]) for a in ARTISTS]
    base = np.array([a[1] for a in ARTISTS], dtype=float)
    # Each artist gets a "discovery binge" that fades over time
    burst = rng.uniform(2, 6, len(ARTISTS))
    tau = rng.uniform(40, 150, len(ARTISTS))

    track_info = []  # per artist: list of (track, album, uri, duration_ms)
    track_probs = []
    for artist_idx, (_, _, _, _, tracks) in enumerate(ARTISTS):
        info = []
        for track_idx, (track, album) in enumerate(tracks):
            uri = f"spotify:track:sample{artist_idx:02d}{track_idx:02d}"
            duration_ms = int(rng.integers(150, 260)) * 1000
            info.append((track, album, uri, duration_ms))
        track_info.append(info)
        # A few favourite tracks per artist get most of the plays
        probs = 1 / (rng.permutation(len(info)) + 1) ** 0.9
        track_probs.append(probs / probs.sum())

    # Taste drifts: every artist is more or less popular in different years
    year_factor = {
        (i, year): rng.lognormal(0, 0.7)
        for i in range(len(ARTISTS))
        for year in range(START.year, END.year + 1)
    }

    hour_probs = {
        "weekday": np.array(WEEKDAY_HOURS) / sum(WEEKDAY_HOURS),
        "weekend": np.array(WEEKEND_HOURS) / sum(WEEKEND_HOURS),
    }
    month_factor = {}

    records = []
    day = START
    while day <= END:
        key = (day.year, day.month)
        if key not in month_factor:
            month_factor[key] = rng.lognormal(0, 0.25)

        is_weekend = day.weekday() >= 5
        mean = (WEEKEND_PLAYS if is_weekend else WEEKDAY_PLAYS) * month_factor[key]
        n_plays = rng.poisson(mean)

        # Artist weights for this day (0 before the artist was discovered)
        weights = np.zeros(len(ARTISTS))
        for i, first_day in enumerate(start_days):
            if day >= first_day:
                age = (day - first_day).days
                weights[i] = (
                    base[i]
                    * year_factor[(i, day.year)]
                    * (1 + burst[i] * np.exp(-age / tau[i]))
                )
        weights /= weights.sum()

        artists = rng.choice(len(ARTISTS), size=n_plays, p=weights)
        hours = rng.choice(
            24, size=n_plays, p=hour_probs["weekend" if is_weekend else "weekday"]
        )

        for artist_idx, hour in zip(artists, hours):
            local = datetime(day.year, day.month, day.day, int(hour)) + timedelta(
                minutes=int(rng.integers(0, 60)), seconds=int(rng.integers(0, 60))
            )
            ts = (local - timedelta(hours=UTC_OFFSET_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")

            if rng.random() < PODCAST_SHARE:
                records.append({
                    "ts": ts,
                    "ms_played": int(rng.integers(600_000, 1_800_000)),
                    "master_metadata_track_name": None,
                    "master_metadata_album_artist_name": None,
                    "master_metadata_album_album_name": None,
                    "spotify_track_uri": None,
                    "episode_name": "Sample Episode",
                })
                continue

            track_idx = rng.choice(len(track_info[artist_idx]), p=track_probs[artist_idx])
            track, album, uri, duration_ms = track_info[artist_idx][track_idx]
            if rng.random() < ARTISTS[artist_idx][3]:
                ms_played = int(rng.integers(2_000, 28_000))  # skipped
            else:
                ms_played = int(duration_ms * rng.uniform(0.97, 1.0))

            records.append({
                "ts": ts,
                "ms_played": ms_played,
                "master_metadata_track_name": track,
                "master_metadata_album_artist_name": ARTISTS[artist_idx][0],
                "master_metadata_album_album_name": album,
                "spotify_track_uri": uri,
                "episode_name": None,
            })

        day += timedelta(days=1)

    # --- Write one file per year, like the real export ---
    OUT_DIR.mkdir(exist_ok=True)
    for old in OUT_DIR.glob("Streaming_History_Audio_*.json"):
        old.unlink()

    by_year = {}
    for record in records:
        by_year.setdefault(record["ts"][:4], []).append(record)

    for year, rows in sorted(by_year.items()):
        rows.sort(key=lambda r: r["ts"])
        path = OUT_DIR / f"Streaming_History_Audio_sample_{year}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)
        print(f"{path.name}: {len(rows)} plays")

    print(f"Total: {len(records)} plays")


if __name__ == "__main__":
    main()