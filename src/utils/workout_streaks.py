"""Persist weekly progress on writes; reads never scan workout history.

Call write functions while holding the user's SELECT FOR UPDATE lock. They
flush as needed but never commit, so a workout and its progress are atomic.
"""
import logging
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from apscheduler.triggers.base import BaseTrigger

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


class WorkoutWeekTrigger(BaseTrigger):
    """Recurring New York Mondays, calculated as calendar dates across DST."""

    def get_next_fire_time(self, previous_fire_time, now):
        if previous_fire_time is not None:
            return next_week_start(previous_fire_time)
        now = as_utc(now)
        boundary = week_midnight(week_start(now.astimezone(WORKOUT_TIMEZONE).date()))
        return boundary if now == boundary else next_week_start(now)


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
    # Accounts start with a default goal; later selections have dated history.
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
    """Update current-week progress without finalizing ended weeks.

    The public mutation passes server time for both timestamps. Other callers
    supplying an older week leave its progress and streak counters unchanged.
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
    # One bit per local weekday (Monday=1, Sunday=64); repeats keep the same bit.
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


def run_weekly_rollover(session, now=None):
    """Process all due users; lock/commit one user at a time."""
    from src.models.user import User
    now = as_utc(now or datetime.now(timezone.utc))
    monday = week_start(now.astimezone(WORKOUT_TIMEZONE).date())
    processed = 0
    failed = set()
    try:
        while True:
            # Selection failures (e.g. an outage) abort rather than spin.
            user = (session.query(User).join(UserWorkoutWeek, UserWorkoutWeek.user_id == User.id)
                    .filter(UserWorkoutWeek.finalized.is_(False), UserWorkoutWeek.week_start < monday,
                            ~User.id.in_(failed))
                    .order_by(UserWorkoutWeek.week_start, User.id)
                    .populate_existing().with_for_update(of=User, skip_locked=True).first())
            if user is None:
                break
            user_id = user.id
            # Successful users no longer match the due-week query. Only retain
            # failed IDs, so a large successful run does not grow an IN clause.
            try:
                finalize_due_weeks(session, user, now)
                session.commit()
                processed += 1
            except Exception:
                session.rollback()
                failed.add(user_id)
                logging.getLogger(__name__).exception("Could not finalize workout weeks for user %s", user_id)
    except Exception:
        session.rollback()
        raise
    return processed


def schedule_weekly_rollover(scheduler, session):
    """Run at local Monday midnight/startup; retry only unfinished work."""
    def finalize_workout_weeks():
        retry = True
        checked_at = datetime.now(timezone.utc)
        # Cleanup and retry registration must survive a failed rollback.
        try:
            try:
                run_weekly_rollover(session, checked_at)
                # A long catch-up can cross another Monday boundary.
                checked_at = datetime.now(timezone.utc)
                monday = week_start(checked_at.astimezone(WORKOUT_TIMEZONE).date())
                retry = session.query(UserWorkoutWeek.user_id).filter(
                    UserWorkoutWeek.finalized.is_(False),
                    UserWorkoutWeek.week_start < monday,
                ).first() is not None
            except Exception:
                logging.getLogger(__name__).exception("Could not finalize workout weeks")
                session.rollback()
        finally:
            try:
                session.remove()
            except Exception:
                retry = True
                logging.getLogger(__name__).exception("Could not clean up workout rollover session")
            finally:
                # The recurring job owns the weekly schedule independently.
                # Also retry if Monday passed after the final due-week check.
                now = datetime.now(timezone.utc)
                if retry or next_week_start(checked_at) <= now:
                    scheduler.add_job(
                        id="retry_workout_weeks", func=finalize_workout_weeks,
                        trigger="date", run_date=now + timedelta(minutes=5),
                        replace_existing=True, max_instances=1, misfire_grace_time=None,
                    )

    scheduler.add_job(
        id="finalize_workout_weeks", func=finalize_workout_weeks,
        trigger=WorkoutWeekTrigger(), next_run_time=datetime.now(timezone.utc),
        max_instances=1, coalesce=True, misfire_grace_time=None,
    )
