import csv
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "uploads" / "historical_traffic_dataset.csv"
with path.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
print("rows", len(rows))
print("first", rows[0])
print("last", rows[-1])
