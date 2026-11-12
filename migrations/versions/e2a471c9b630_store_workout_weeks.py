"""Store weekly progress and preserve the legacy API's displayed streaks.

Revision ID: e2a471c9b630
Revises: d8f2a614be30
"""

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from alembic import op
import sqlalchemy as sa

revision = "e2a471c9b630"
down_revision = "d8f2a614be30"
branch_labels = None
depends_on = None


def utc(value):
    """Normalize legacy timestamps under the existing UTC convention."""
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


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


def seed_current_weeks(bind, now):
    """Backfill legacy display once, then initialize the calendar-week baseline."""
    metadata = sa.MetaData()
    users = sa.Table("users", metadata, autoload_with=bind)
    workouts = sa.Table("workout", metadata, autoload_with=bind)
    history = sa.Table("user_workout_goal_history", metadata, autoload_with=bind)
    weeks = sa.Table("user_workout_week", metadata, autoload_with=bind)
    tz = ZoneInfo("America/New_York")
    today = utc(now).astimezone(tz).date()
    monday = today - timedelta(days=today.weekday())
    boundary = midnight(monday, tz)
    date_column = (
        sa.cast(workouts.c.workout_time, sa.Date()) if bind.dialect.name == "postgresql" else workouts.c.workout_time
    )
    cursor = -1
    while True:
        batch = list(
            bind.execute(sa.select(users).where(users.c.id > cursor).order_by(users.c.id).limit(250)).mappings()
        )
        if not batch:
            break
        cursor = batch[-1]["id"]
        ids = [user["id"] for user in batch]
        existing = set(bind.execute(sa.select(weeks.c.user_id).where(weeks.c.user_id.in_(ids))).scalars())
        times_by_user = {uid: [] for uid in ids}
        goals_by_user = {uid: [] for uid in ids}
        for uid, timestamp, day in bind.execute(
            sa.select(workouts.c.user_id, workouts.c.workout_time, date_column).where(workouts.c.user_id.in_(ids))
        ):
            times_by_user[uid].append((timestamp, day if bind.dialect.name == "postgresql" else utc(day).date()))
        for uid, goal, effective in bind.execute(
            sa.select(history.c.user_id, history.c.workout_goal, history.c.effective_at)
            .where(history.c.user_id.in_(ids))
            .order_by(history.c.effective_at.desc())
        ):
            goals_by_user[uid].append((goal, effective))
        updates, baselines, inserts = [], [], []
        for user in batch:
            uid = user["id"]
            if uid in existing:
                continue
            times, goals = times_by_user[uid], goals_by_user[uid]
            dates = [day for _, day in times]
            active, longest, started = legacy_streaks(dates, goals, user["workout_goal"], utc(now).date())
            updates.append(dict(uid=uid, active=active, longest=longest, started=started))
            mask = 0
            for timestamp, _ in times:
                if boundary <= utc(timestamp) <= utc(now):
                    mask |= 1 << utc(timestamp).astimezone(tz).weekday()
            goal = next((g for g, effective in goals if utc(effective) <= boundary), user["workout_goal"])
            goal = goal if goal and 1 <= goal <= 7 else 1
            if not goals:
                baselines.append(
                    dict(user_id=uid, workout_goal=goal, effective_at=datetime(1970, 1, 1, tzinfo=timezone.utc))
                )
            # Preserve the displayed baseline without awarding an overlapping week.
            # With no current-week activity, the new week can still earn credit.
            rolling_start = utc(now).date() - timedelta(days=6)
            legacy_goals = goals or ([(user["workout_goal"], datetime.min)] if user["workout_goal"] else [])
            rolling_goal = next(
                (g for g, effective in legacy_goals if effective.date() <= rolling_start),
                legacy_goals[-1][0] if legacy_goals else None,
            )
            rolling_count = len({day for day in dates if day >= rolling_start})
            overlap_awarded = bool(mask and rolling_goal and rolling_count >= rolling_goal)
            inserts.append(
                dict(
                    user_id=uid,
                    week_start=monday,
                    workout_goal=goal,
                    checked_in_days=mask,
                    goal_awarded=overlap_awarded,
                    finalized=False,
                )
            )
        if updates:
            bind.execute(
                users.update()
                .where(users.c.id == sa.bindparam("uid"))
                .values(
                    active_streak=sa.bindparam("active"),
                    max_streak=sa.bindparam("longest"),
                    streak_started_at=sa.bindparam("started"),
                ),
                updates,
            )
        if baselines:
            bind.execute(history.insert(), baselines)
        if inserts:
            bind.execute(weeks.insert(), inserts)


def upgrade():
    """Create weekly storage and preserve the legacy display at cutover."""
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    additions = [sa.Column("streak_started_at", sa.DateTime(timezone=True), nullable=True)]
    for column in additions:
        if column.name not in columns:
            op.add_column("users", column)
    if not sa.inspect(bind).has_table("user_workout_week"):
        op.create_table(
            "user_workout_week",
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("week_start", sa.Date(), primary_key=True),
            sa.Column("workout_goal", sa.Integer(), nullable=False),
            sa.Column("checked_in_days", sa.Integer(), nullable=False),
            sa.Column("goal_awarded", sa.Boolean(), nullable=False),
            sa.Column("finalized", sa.Boolean(), nullable=False),
            sa.CheckConstraint("checked_in_days BETWEEN 0 AND 127", name="ck_workout_week_days"),
            sa.CheckConstraint("workout_goal BETWEEN 1 AND 7", name="ck_workout_week_goal"),
        )
    for table, name, cols in (
        ("user_workout_week", "ix_workout_week_pending", ["finalized", "week_start", "user_id"]),
        ("user_workout_goal_history", "ix_workout_goal_user_effective", ["user_id", "effective_at"]),
        ("workout", "ix_workout_user_time", ["user_id", "workout_time"]),
    ):
        if name not in {index["name"] for index in sa.inspect(bind).get_indexes(table)}:
            op.create_index(name, table, cols)
    seed_current_weeks(bind, datetime.now(timezone.utc))
    bind.execute(
        sa.text("UPDATE users SET workout_goal = 1 WHERE workout_goal IS NULL OR workout_goal NOT BETWEEN 1 AND 7")
    )
    op.alter_column("users", "workout_goal", existing_type=sa.Integer(), nullable=False, server_default=sa.text("1"))


def downgrade():
    """Refuse a rollback that cannot restore the original streak and goal data."""
    raise RuntimeError(
        "Weekly streak migration is irreversible: restore a pre-migration backup "
        "or use a reviewed forward repair. No downgrade changes were applied."
    )
