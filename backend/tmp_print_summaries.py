import sys
sys.path.insert(0, '.')
import analytics
res_today = analytics.get_today_summary()
print('today raw response:', res_today)
res_week = analytics.get_weekly_summary()
print('weekly raw response:', res_week)
res_month = analytics.get_monthly_summary()
print('monthly raw response:', res_month)
