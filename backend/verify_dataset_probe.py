import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from database import get_database


def main() -> None:
    db = get_database()
    collection = db['traffic_logs']
    docs = list(collection.find({'timestamp': {'$exists': True}}, {
        '_id': 0,
        'timestamp': 1,
        'road_id': 1,
        'vehicle_count': 1,
        'density_level': 1,
        'waiting_time': 1,
        'recommended_green_time': 1,
        'signal_status': 1,
        'current_green_road': 1,
        'current_timer': 1,
    }).sort('timestamp', 1).limit(5))
    print('traffic_docs', len(docs))
    print('sample', docs)


if __name__ == '__main__':
    main()
