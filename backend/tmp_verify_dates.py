from datetime import datetime, timedelta, timezone
from database import get_database
from analytics import _parse_date, _build_date_filter

db = get_database()
col = db['traffic_logs']
now = datetime.now(timezone.utc)
start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_today = start_today + timedelta(days=1)
start_week = now - timedelta(days=7)
start_month = now - timedelta(days=30)

query_aware_today = {'timestamp': {'$gte': start_today, '$lt': end_today}}
query_naive_today = {'timestamp': {'$gte': datetime(start_today.year, start_today.month, start_today.day), '$lt': datetime(start_today.year, start_today.month, start_today.day) + timedelta(days=1)}}

print('now', now)
print('start_today aware', start_today, type(start_today), start_today.tzinfo)
print('end_today aware', end_today, type(end_today), end_today.tzinfo)
print('start_today naive', query_naive_today['timestamp']['$gte'], type(query_naive_today['timestamp']['$gte']), query_naive_today['timestamp']['$gte'].tzinfo)
print('end_today naive', query_naive_today['timestamp']['$lt'], type(query_naive_today['timestamp']['$lt']), query_naive_today['timestamp']['$lt'].tzinfo)
print('count today aware doc', col.count_documents(query_aware_today))
print('count today naive doc', col.count_documents(query_naive_today))
print('count week aware doc', col.count_documents({'timestamp': {'$gte': start_week, '$lt': end_today}}))
print('count week naive doc', col.count_documents({'timestamp': {'$gte': datetime(start_week.year, start_week.month, start_week.day), '$lt': query_naive_today['timestamp']['$lt']}}))
print('count month aware doc', col.count_documents({'timestamp': {'$gte': start_month, '$lt': end_today}}))
print('count month naive doc', col.count_documents({'timestamp': {'$gte': datetime(start_month.year, start_month.month, start_month.day), '$lt': query_naive_today['timestamp']['$lt']}}))
print('parse iso start', _parse_date(start_today.isoformat()), _parse_date(start_today.isoformat()).tzinfo)
print('parse iso end', _parse_date(end_today.isoformat()), _parse_date(end_today.isoformat()).tzinfo)
print('query2', _build_date_filter(start_today.isoformat(), end_today.isoformat()))
print('count query2', col.count_documents(_build_date_filter(start_today.isoformat(), end_today.isoformat())))
print('today get_history filtered count', len(__import__('analytics').get_history(start_date=start_today.isoformat(), end_date=end_today.isoformat(), include_idle=False, limit=None)))
print('today get_history raw count', len(__import__('analytics').get_history(start_date=start_today.isoformat(), end_date=end_today.isoformat(), include_idle=True, limit=None)))
print('today get_history default limit count', len(__import__('analytics').get_history(start_date=start_today.isoformat(), end_date=end_today.isoformat(), include_idle=False)))
