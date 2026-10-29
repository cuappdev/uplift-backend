"""Persist weekly progress on writes; reads never scan workout history.

Call write functions while holding the user's SELECT FOR UPDATE lock. They
flush as needed but never commit, so a workout and its progress are atomic.
"""
import logging
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from src.models.user_workout_week import UserWorkoutWeek
from src.models.user_workout_goal_history import UserWorkoutGoalHistory

WORKOUT_TIMEZONE = ZoneInfo("America/New_York")
DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def as_utc(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def week_start(day):
    return day - timedelta(days=day.weekday())


def week_midnight(monday):
    return datetime.combine(monday, time.min, WORKOUT_TIMEZONE).astimezone(timezone.utc)


def next_week_start(now):
    monday = week_start(as_utc(now).astimezone(WORKOUT_TIMEZONE).date())
    return week_midnight(monday + timedelta(days=7))


def active_days(mask):
    return bin(mask or 0).count("1")


def current_week(session, user, now):
    """One lookup by composite primary key, with no history or writes."""
    monday = week_start(as_utc(now).astimezone(WORKOUT_TIMEZONE).date())
    return session.query(UserWorkoutWeek).filter_by(user_id=user.id, week_start=monday).first()


def goal_for_week(session, user, monday):
    history = (session.query(UserWorkoutGoalHistory)
               .filter(UserWorkoutGoalHistory.user_id == user.id,
                       UserWorkoutGoalHistory.effective_at <= week_midnight(monday))
               .order_by(UserWorkoutGoalHistory.effective_at.desc()).first())
    if history is not None:
        return history.workout_goal if 1 <= history.workout_goal <= 7 else 1
    # First-time goals apply immediately; legacy users are seeded by migration.
    return user.workout_goal if user.workout_goal and 1 <= user.workout_goal <= 7 else 1


def get_or_create_week(session, user, monday):
    row = session.query(UserWorkoutWeek).filter_by(user_id=user.id, week_start=monday).first()
    if row is None:
        row = UserWorkoutWeek(
            user_id=user.id, week_start=monday,
            workout_goal=goal_for_week(session, user, monday),
            checked_in_days=0, goal_awarded=False, finalized=False,
        )
        session.add(row)
        session.flush()
    return row


def initialize_tracking(session, user, now):
    """For new accounts only. Existing accounts must be migrated/backfilled."""
    monday = week_start(as_utc(now).astimezone(WORKOUT_TIMEZONE).date())
    user.active_streak = user.active_streak or 0
    user.max_streak = user.max_streak or 0
    session.flush()
    return get_or_create_week(session, user, monday)


def award_goal(user, row):
    """Award once, whether called by check-in or the weekly job."""
    if not row.goal_awarded and row.workout_goal > 0 and active_days(row.checked_in_days) >= row.workout_goal:
        if not user.active_streak:
            first_day = next(i for i in range(7) if row.checked_in_days & (1 << i))
            user.streak_started_at = week_midnight(row.week_start + timedelta(days=first_day))
        user.active_streak = (user.active_streak or 0) + 1
        user.max_streak = max(user.max_streak or 0, user.active_streak)
        row.goal_awarded = True


def record_checkin(session, user, workout_time, now):
    """Update current-week progress; historical uploads leave closed weeks alone.

    The caller still saves the workout when this returns None, preserving the
    existing API's acceptance of past timestamps without finalizing on writes.
    """
    now, workout_time = as_utc(now), as_utc(workout_time)
    if workout_time > now:
        raise ValueError("Workout time cannot be in the future.")
    tz = WORKOUT_TIMEZONE
    day = workout_time.astimezone(tz).date()
    monday = week_start(day)
    if monday != week_start(now.astimezone(tz).date()):
        return None
    pending = (session.query(UserWorkoutWeek)
               .filter_by(user_id=user.id, finalized=False)
               .order_by(UserWorkoutWeek.week_start).first())
    if pending is None:
        raise ValueError("Workout tracking needs its one-time migration before check-in.")
    row = get_or_create_week(session, user, monday)
    bit = 1 << day.weekday()
    if not row.checked_in_days & bit:
        row.checked_in_days |= bit
    # If the scheduled job is behind, defer awarding until it catches up.
    # Otherwise an empty past week could reset a newly awarded current week.
    if pending.week_start == monday:
        award_goal(user, row)
    return row


def finalize_due_weeks(session, user, now):
    """Scheduled worker only: catch up in order, including empty/missed weeks."""
    monday = week_start(as_utc(now).astimezone(WORKOUT_TIMEZONE).date())
    row = (session.query(UserWorkoutWeek).filter_by(user_id=user.id, finalized=False)
           .order_by(UserWorkoutWeek.week_start).first())
    while row is not None and row.week_start < monday:
        if row.checked_in_days == 0:
            user.active_streak = 0
            user.streak_started_at = None
        else:
            award_goal(user, row)
        row.finalized = True
        row = get_or_create_week(session, user, row.week_start + timedelta(days=7))
        session.flush()
    # Award any current-week progress deferred during job downtime.
    if row is not None and row.week_start == monday:
        award_goal(user, row)


def run_weekly_rollover(session, now=None, limit=500):
    """Bounded indexed batches; row locks make multiple scheduler workers safe."""
    from src.models.user import User
    now = as_utc(now or datetime.now(timezone.utc))
    monday = week_start(now.astimezone(WORKOUT_TIMEZONE).date())
    processed = 0
    attempted = set()
    try:
        while len(attempted) < limit:
            # Selection failures (e.g. an outage) abort rather than spin.
            user = (session.query(User).join(UserWorkoutWeek, UserWorkoutWeek.user_id == User.id)
                    .filter(UserWorkoutWeek.finalized.is_(False), UserWorkoutWeek.week_start < monday,
                            ~User.id.in_(attempted))
                    .order_by(UserWorkoutWeek.week_start, User.id)
                    .populate_existing().with_for_update(of=User, skip_locked=True).first())
            if user is None:
                break
            user_id = user.id
            attempted.add(user_id)
            try:
                finalize_due_weeks(session, user, now)
                session.commit()
                processed += 1
            except Exception:
                session.rollback()
                logging.getLogger(__name__).exception("Could not finalize workout weeks for user %s", user_id)
    except Exception:
        session.rollback()
        raise
    return processed
