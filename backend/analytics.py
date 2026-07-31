from datetime import datetime, timedelta, timezone
from typing import Optional

from database import get_database


COLLECTION_NAME = "traffic_logs"


def _get_collection():
    db = get_database()
    return db[COLLECTION_NAME]


def _parse_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _build_date_filter(start_date: Optional[str], end_date: Optional[str]):
    query = {}
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)

    if start_dt is not None:
        query["$gte"] = start_dt
    if end_dt is not None:
        query["$lte"] = end_dt

    if start_dt is not None or end_dt is not None:
        return {"timestamp": query}
    return {}


def get_history(start_date: Optional[str] = None, end_date: Optional[str] = None):
    collection = _get_collection()
    query = _build_date_filter(start_date, end_date)
    cursor = collection.find(query).sort("timestamp", 1)
    return list(cursor)


def get_today_summary(start_date: Optional[str] = None, end_date: Optional[str] = None):
    collection = _get_collection()
    query = _build_date_filter(start_date, end_date)

    if not query:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        query = {"timestamp": {"$gte": start_of_day, "$lt": end_of_day}}

    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": None,
            "totalVehicles": {"$sum": "$vehicle_count"},
            "records": {"$sum": 1},
            "averageVehicles": {"$avg": "$vehicle_count"},
            "averageWaitingTime": {"$avg": "$waiting_time"},
            "highestDensity": {"$max": "$density_level"},
            "lastUpdated": {"$max": "$timestamp"},
        }},
    ]

    result = list(collection.aggregate(pipeline))
    if not result:
        return None

    summary = result[0]
    records = list(collection.find(query).sort("timestamp", 1))
    if not records:
        return None

    peak_hour = _get_peak_hour(records)
    highest_traffic_road = _get_highest_traffic_road(records)
    least_busy_road = _get_least_busy_road(records)

    return {
        "status": "success",
        "summary": {
            "totalVehicles": int(summary.get("totalVehicles", 0) or 0),
            "averageVehicles": round(float(summary.get("averageVehicles", 0) or 0), 2),
            "peakTrafficHour": peak_hour,
            "highestTrafficRoad": highest_traffic_road,
            "leastBusyRoad": least_busy_road,
            "averageWaitingTime": round(float(summary.get("averageWaitingTime", 0) or 0), 2),
            "highestDensity": summary.get("highestDensity") or "LOW",
            "records": int(summary.get("records", 0) or 0),
            "lastUpdated": summary.get("lastUpdated").isoformat() if summary.get("lastUpdated") else None,
        },
    }


def get_weekly_summary(start_date: Optional[str] = None, end_date: Optional[str] = None):
    collection = _get_collection()
    query = _build_date_filter(start_date, end_date)
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": {
                "year": {"$year": "$timestamp"},
                "week": {"$isoWeek": "$timestamp"},
            },
            "totalVehicles": {"$sum": "$vehicle_count"},
            "records": {"$sum": 1},
            "averageVehicles": {"$avg": "$vehicle_count"},
            "averageWaitingTime": {"$avg": "$waiting_time"},
        }},
        {"$sort": {"_id.year": 1, "_id.week": 1}},
    ]
    return list(collection.aggregate(pipeline))


def get_monthly_summary(start_date: Optional[str] = None, end_date: Optional[str] = None):
    collection = _get_collection()
    query = _build_date_filter(start_date, end_date)
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": {
                "year": {"$year": "$timestamp"},
                "month": {"$month": "$timestamp"},
            },
            "totalVehicles": {"$sum": "$vehicle_count"},
            "records": {"$sum": 1},
            "averageVehicles": {"$avg": "$vehicle_count"},
            "averageWaitingTime": {"$avg": "$waiting_time"},
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ]
    return list(collection.aggregate(pipeline))


def _get_peak_hour(records):
    if not records:
        return "N/A"

    hour_counts = {}
    for record in records:
        timestamp = record.get("timestamp")
        if not timestamp:
            continue
        hour_key = timestamp.hour
        hour_counts[hour_key] = hour_counts.get(hour_key, 0) + int(record.get("vehicle_count", 0) or 0)

    if not hour_counts:
        return "N/A"

    peak_hour = max(hour_counts.items(), key=lambda item: item[1])[0]
    return f"{peak_hour:02d}:00-{peak_hour + 1:02d}:00"


def _get_highest_traffic_road(records):
    if not records:
        return "N/A"

    road_totals = {}
    for record in records:
        road_name = record.get("road_name") or f"Road {record.get('road_id', '')}"
        road_totals[road_name] = road_totals.get(road_name, 0) + int(record.get("vehicle_count", 0) or 0)

    if not road_totals:
        return "N/A"

    highest = max(road_totals.items(), key=lambda item: item[1])[0]
    return highest


def _get_least_busy_road(records):
    if not records:
        return "N/A"

    road_totals = {}
    for record in records:
        road_name = record.get("road_name") or f"Road {record.get('road_id', '')}"
        road_totals[road_name] = road_totals.get(road_name, 0) + int(record.get("vehicle_count", 0) or 0)

    if not road_totals:
        return "N/A"

    least = min(road_totals.items(), key=lambda item: item[1])[0]
    return least
