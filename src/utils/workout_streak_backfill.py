"""One-time recovery of pre-weekly workout display values.

Keep the legacy calculation aligned with the frozen weekly migration. Runtime
recovery is used only while holding the user lock and only without any weekly
baseline; ordinary check-ins never scan workout history.
"""

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def midnight(day, tz):
    """Convert a local calendar boundary to UTC."""
    return datetime.combine(day, time.min, tz).astimezone(timezone.utc)


def legacy_streaks(days, history, goal, today):
    """Freeze the old resolvers' rolling UTC-date windows at cutover.

    Active/max fall back to the oldest goal before recorded history; start
    dates instead stop there and require actual goal history. Preserve these
    differences, including active's legacy treatment of future workout dates.
    """
    days = sorted(set(days), reverse=True)
    goals = history or ([(goal, datetime.min)] if goal else [])
    active = 0
    if goals:
        pointer, end = 0, today
        while pointer < len(days):
            start = end - timedelta(days=6)
            after = pointer
            while after < len(days) and days[after] >= start:
                after += 1
            target = next((g for g, effective in goals if effective.date() <= start), goals[-1][0])
            if after == pointer:
                break
            if after - pointer >= target:
                active += 1
            pointer, end = after, end - timedelta(days=7)

    past_days = [day for day in days if day <= today]
    longest = run = 0
    started = None
    start_open = bool(history)
    pointer, end = 0, today
    while pointer < len(past_days):
        start = end - timedelta(days=6)
        after = pointer
        while after < len(past_days) and past_days[after] >= start:
            after += 1
        count = after - pointer
        if goals:
            target = next((g for g, effective in goals if effective.date() <= start), goals[-1][0])
            if not count:
                longest, run = max(longest, run), 0
            elif target and count >= target:
                run += 1
        if start_open:
            target = next((g for g, effective in history if effective.date() <= start), None)
            if target is None or not count:
                start_open = False
            elif count >= target:
                started = midnight(past_days[after - 1], ZoneInfo("America/New_York"))
        pointer, end = after, end - timedelta(days=7)
    return active, max(longest, run), started
