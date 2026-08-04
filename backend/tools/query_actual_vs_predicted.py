"""Query MongoDB for actual versus predicted traffic samples."""
from __future__ import annotations

from pathlib import Path
import sys
import json

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from prediction.data_loader import load_traffic_sample
from database import get_database


def main() -> None:
    sample_df = load_traffic_sample(
        collection_name="traffic_logs",
        limit=10,
        projection={
            "timestamp": 1,
            "road_id": 1,
            "road_name": 1,
            "vehicle_count": 1,
            "prediction": 1,
            "density_level": 1,
            "signal_status": 1,
        },
    )
    print(sample_df.to_json(orient="records", date_format="iso", force_ascii=False, indent=2))


if __name__ == "__main__":
    main()
