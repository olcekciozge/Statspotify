import sys
from pathlib import Path

# Make the project root importable when running from the notebooks folder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.clean import load_history, clean_history

raw = load_history()
df = clean_history(raw)

print("Rows before cleaning:", len(raw))
print("Rows after cleaning: ", len(df))
print("Date range:", df["played_at"].min(), "->", df["played_at"].max())
print("Total hours played:", round(df["minutes_played"].sum() / 60, 1))

print("\nTop 10 artists by plays:")
print(df["artist"].value_counts().head(10))

print("\nColumns and dtypes:")
df.info()