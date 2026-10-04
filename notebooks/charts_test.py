import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.clean import load_history, clean_history
from src.charts import top_artists_chart, monthly_hours_chart

df = clean_history(load_history())

top_artists_chart(df).show()
monthly_hours_chart(df).show()