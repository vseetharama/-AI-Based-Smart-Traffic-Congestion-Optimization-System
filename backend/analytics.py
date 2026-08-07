from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Optional

from database import get_database


COLLECTION_NAME = "traffic_logs"


def _get_collection():
    db = get_database()
    return db[COLLECTION_NAME]


def _ensure_timestamp_index(collection):
    try:
        collection.create_index([("timestamp", 1)], name="timestamp_asc", background=True)
    except Exception:
        pass


def _parse_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _build_date_filter(start_date: Optional[str], end_date: Optional[str], default_delta=None):
    query = {}
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)

    if start_dt is not None:
        query["$gte"] = start_dt
    elif default_delta is not None:
        query["$gte"] = datetime.now(timezone.utc) - default_delta

    if end_dt is not None:
        query["$lte"] = end_dt

    if start_dt is not None or end_dt is not None or default_delta is not None:
        return {"timestamp": query}
    return {}


def _is_complete_record(record) -> bool:
    required_fields = [
        "timestamp",
        "road_name",
        "vehicle_count",
        "density_level",
        "signal_status",
        "waiting_time",
        "recommended_green_time",
        "prediction",
    ]
    for field in required_fields:
        value = record.get(field)
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
    return True


def format_timestamp_for_display(value):
    """Convert a datetime or ISO string (assumed UTC) to Asia/Kolkata formatted string DD-MM-YYYY hh:mm:ss AM/PM."""
    if value is None:
        return None
    kolkata = ZoneInfo("Asia/Kolkata")
    try:
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, str):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            return str(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone(kolkata)
        return local_dt.strftime("%d-%m-%Y %I:%M:%S %p")
    except Exception:
        try:
            return str(value)
        except Exception:
            return None


def _is_idle_record(record) -> bool:
    vehicle_count = record.get("vehicle_count")
    prediction = str(record.get("prediction") or "").strip().lower()
    density_level = str(record.get("density_level") or "").strip().upper()
    return vehicle_count == 0 and prediction in {"no video", "no_video", "unknown", ""} and density_level == "LOW"


def _filter_meaningful_records(records, include_idle: bool = False):
    meaningful_records = []
    for record in records or []:
        if not _is_complete_record(record):
            continue
        if not include_idle and _is_idle_record(record):
            continue
        meaningful_records.append(record)
    return meaningful_records


def _get_monitored_road_count(records):
    roads = {
        record.get("road_name") or f"Road {record.get('road_id', '')}"
        for record in records or []
    }
    return len(roads)


def get_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_idle: bool = False,
    limit: Optional[int] = 2000,
    default_delta: Optional[timedelta] = timedelta(days=30),
):
    collection = _get_collection()
    _ensure_timestamp_index(collection)
    query = _build_date_filter(start_date, end_date, default_delta=default_delta)
    cursor = collection.find(query).sort("timestamp", -1)
    if limit is not None:
        cursor = cursor.limit(limit)
    records = list(cursor)
    if include_idle:
        return records
    return _filter_meaningful_records(records)


def get_today_summary(start_date: Optional[str] = None, end_date: Optional[str] = None):
    collection = _get_collection()
    _ensure_timestamp_index(collection)
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    query = _build_date_filter(start_date, end_date, default_delta=timedelta(hours=24))

    if start_date is None and end_date is None:
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

    result = list(collection.aggregate(pipeline, allowDiskUse=True))
    if not result:
        return {"status": "error", "message": "No analytics records found"}

    summary = result[0]
    if start_date is None and end_date is None:
        records = get_history(start_date=start_of_day.isoformat(), end_date=end_of_day.isoformat(), include_idle=False, limit=None)
    else:
        records = get_history(start_date=start_date, end_date=end_date, include_idle=False, limit=None)
    if not records:
        return {"status": "error", "message": "No analytics records found"}

    peak_hour = _get_peak_hour(records)
    highest_traffic_road = _get_highest_traffic_road(records)
    least_busy_road = _get_least_busy_road(records)
    road_distribution = _get_road_distribution(records)
    density_distribution = _get_density_distribution(records)
    traffic_trend = _get_traffic_trend(records)
    waiting_trend = _get_waiting_trend(records)

    monitored_road_count = _get_monitored_road_count(records)
    total_vehicles = int(sum(int(record.get("vehicle_count", 0) or 0) for record in records))
    average_vehicles = round(float(total_vehicles / monitored_road_count), 2) if monitored_road_count else 0

    return {
        "status": "success",
        "summary": {
            "totalVehicles": total_vehicles,
            "averageVehicles": average_vehicles,
            "peakTrafficHour": peak_hour,
            "highestTrafficRoad": highest_traffic_road,
            "leastBusyRoad": least_busy_road,
            "averageWaitingTime": round(float(summary.get("averageWaitingTime", 0) or 0), 2),
            "highestDensity": _get_highest_density(records),
            "roadCount": monitored_road_count,
            "records": len(records),
            "lastUpdated": format_timestamp_for_display(summary.get("lastUpdated")) if summary.get("lastUpdated") else None,
        },
        "charts": {
            "roadDistribution": road_distribution,
            "trafficTrend": traffic_trend,
            "densityDistribution": density_distribution,
            "waitingTrend": waiting_trend,
        },
    }


def get_weekly_summary(start_date: Optional[str] = None, end_date: Optional[str] = None):
    collection = _get_collection()
    _ensure_timestamp_index(collection)
    query = _build_date_filter(start_date, end_date, default_delta=timedelta(days=7))
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

    weekly_groups = list(collection.aggregate(pipeline, allowDiskUse=True))
    if not weekly_groups:
        return {"status": "error", "message": "No analytics records found"}

    records = get_history(start_date=start_date, end_date=end_date, include_idle=False, limit=None)
    road_distribution = _get_road_distribution(records)
    density_distribution = _get_density_distribution(records)

    # Build weekly traffic trend and waiting trend from the filtered records
    weekly_buckets = {}
    for r in records:
        ts = r.get("timestamp")
        if not ts:
            continue
        year, week, _ = ts.isocalendar()
        key = (year, week)
        bucket = weekly_buckets.setdefault(key, {"vehicles": 0, "waiting_sum": 0.0, "count": 0})
        bucket["vehicles"] += int(r.get("vehicle_count", 0) or 0)
        bucket["waiting_sum"] += float(r.get("waiting_time", 0) or 0)
        bucket["count"] += 1

    traffic_trend = []
    waiting_trend = []
    for (year, week) in sorted(weekly_buckets.keys()):
        bucket = weekly_buckets[(year, week)]
        traffic_trend.append({"time": f"{year}-W{week:02d}", "vehicles": int(bucket["vehicles"])})
        avg_wait = round(bucket["waiting_sum"] / bucket["count"], 2) if bucket["count"] else 0
        waiting_trend.append({"time": f"{year}-W{week:02d}", "waiting": avg_wait})

    monitored_road_count = _get_monitored_road_count(records)
    total_vehicles = int(sum(int(r.get("vehicle_count", 0) or 0) for r in records))
    average_vehicles = round(float(total_vehicles / monitored_road_count), 2) if monitored_road_count else 0

    summary = {
        "totalVehicles": total_vehicles,
        "averageVehicles": average_vehicles,
        "peakTrafficHour": "N/A",
        "highestTrafficRoad": _get_highest_traffic_road(records),
        "leastBusyRoad": _get_least_busy_road(records),
        "averageWaitingTime": round(float(sum(item.get("averageWaitingTime", 0) or 0 for item in weekly_groups)) / len(weekly_groups), 2) if weekly_groups else 0,
        "highestDensity": _get_highest_density(records),
        "roadCount": monitored_road_count,
        "records": len(records),
        "lastUpdated": format_timestamp_for_display(records[-1].get("timestamp")) if records else None,
    }

    return {
        "status": "success",
        "summary": summary,
        "charts": {
            "roadDistribution": road_distribution,
            "trafficTrend": traffic_trend,
            "densityDistribution": density_distribution,
            "waitingTrend": waiting_trend,
        },
    }


def get_monthly_summary(start_date: Optional[str] = None, end_date: Optional[str] = None):
    collection = _get_collection()
    _ensure_timestamp_index(collection)
    query = _build_date_filter(start_date, end_date, default_delta=timedelta(days=30))
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

    monthly_groups = list(collection.aggregate(pipeline, allowDiskUse=True))
    if not monthly_groups:
        return {"status": "error", "message": "No analytics records found"}

    records = get_history(start_date=start_date, end_date=end_date, include_idle=False, limit=None)
    road_distribution = _get_road_distribution(records)
    density_distribution = _get_density_distribution(records)

    # Build monthly traffic trend and waiting trend from the filtered records
    monthly_buckets = {}
    for r in records:
        ts = r.get("timestamp")
        if not ts:
            continue
        year = ts.year
        month = ts.month
        key = (year, month)
        bucket = monthly_buckets.setdefault(key, {"vehicles": 0, "waiting_sum": 0.0, "count": 0})
        bucket["vehicles"] += int(r.get("vehicle_count", 0) or 0)
        bucket["waiting_sum"] += float(r.get("waiting_time", 0) or 0)
        bucket["count"] += 1

    traffic_trend = []
    waiting_trend = []
    for (year, month) in sorted(monthly_buckets.keys()):
        bucket = monthly_buckets[(year, month)]
        traffic_trend.append({"time": f"{year}-{month:02d}", "vehicles": int(bucket["vehicles"])})
        avg_wait = round(bucket["waiting_sum"] / bucket["count"], 2) if bucket["count"] else 0
        waiting_trend.append({"time": f"{year}-{month:02d}", "waiting": avg_wait})

    monitored_road_count = _get_monitored_road_count(records)
    total_vehicles = int(sum(int(r.get("vehicle_count", 0) or 0) for r in records))
    average_vehicles = round(float(total_vehicles / monitored_road_count), 2) if monitored_road_count else 0

    summary = {
        "totalVehicles": total_vehicles,
        "averageVehicles": average_vehicles,
        "peakTrafficHour": "N/A",
        "highestTrafficRoad": _get_highest_traffic_road(records),
        "leastBusyRoad": _get_least_busy_road(records),
        "averageWaitingTime": round(float(sum(item.get("averageWaitingTime", 0) or 0 for item in monthly_groups)) / len(monthly_groups), 2) if monthly_groups else 0,
        "highestDensity": _get_highest_density(records),
        "roadCount": monitored_road_count,
        "records": len(records),
        "lastUpdated": format_timestamp_for_display(records[-1].get("timestamp")) if records else None,
    }

    return {
        "status": "success",
        "summary": summary,
        "charts": {
            "roadDistribution": road_distribution,
            "trafficTrend": traffic_trend,
            "densityDistribution": density_distribution,
            "waitingTrend": waiting_trend,
        },
    }


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


def _get_road_distribution(records):
    if not records:
        return []

    road_totals = {}
    for record in records:
        road_name = record.get("road_name") or f"Road {record.get('road_id', '')}"
        road_totals[road_name] = road_totals.get(road_name, 0) + int(record.get("vehicle_count", 0) or 0)

    return [{"road": road, "vehicles": total} for road, total in sorted(road_totals.items())]


def _get_density_distribution(records):
    if not records:
        return []

    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for record in records:
        density_level = (record.get("density_level") or "LOW").upper()
        if density_level in counts:
            counts[density_level] += 1

    return [
        {"name": "LOW", "value": counts["LOW"]},
        {"name": "MEDIUM", "value": counts["MEDIUM"]},
        {"name": "HIGH", "value": counts["HIGH"]},
    ]


def _get_traffic_trend(records):
    if not records:
        return []

    grouped = {}
    for record in records:
        timestamp = record.get("timestamp")
        if not timestamp:
            continue
        label = timestamp.strftime("%I:%M %p")
        grouped[label] = grouped.get(label, 0) + int(record.get("vehicle_count", 0) or 0)

    return [{"time": time_label, "vehicles": value} for time_label, value in sorted(grouped.items())]


def _get_waiting_trend(records):
    if not records:
        return []

    grouped = {}
    for record in records:
        timestamp = record.get("timestamp")
        if not timestamp:
            continue
        label = timestamp.strftime("%I:%M %p")
        grouped[label] = grouped.get(label, 0) + float(record.get("waiting_time", 0) or 0)

    return [{"time": time_label, "waiting": round(value, 2)} for time_label, value in sorted(grouped.items())]


def _format_period_label(period_id, period_type):
    year = period_id.get("year")
    if year is None:
        year = 0

    if period_type == "week":
        week = period_id.get("week")
        if week is None:
            week = 0
        return f"W{week:02d}"

    month = period_id.get("month")
    if month is None:
        month = 0
    return f"{year}-{month:02d}"


def _get_highest_density(records):
    if not records:
        return "LOW"

    density_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    highest_density = "LOW"
    for record in records:
        density_level = (record.get("density_level") or "LOW").upper()
        if density_level in density_rank and density_rank[density_level] > density_rank[highest_density]:
            highest_density = density_level

    return highest_density
