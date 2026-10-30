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
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def midnight(day, tz):
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
    for user in bind.execute(sa.select(users)).mappings():
        tz = ZoneInfo("America/New_York")
        today = utc(now).astimezone(tz).date()
        monday = today - timedelta(days=today.weekday())
        # Existing weekly records are the tracking baseline; reruns preserve it.
        if (
            bind.execute(
                sa.select(weeks.c.user_id)
                .where(
                    weeks.c.user_id == user["id"],
                )
                .limit(1)
            ).first()
            is not None
        ):
            continue
        # Match the old database DATE cast (and its connection timezone), not
        # the New York dates used for the new calendar-week progress below.
        date_column = (
            sa.cast(workouts.c.workout_time, sa.Date())
            if bind.dialect.name == "postgresql"
            else workouts.c.workout_time
        )
        dates = [row[0] for row in bind.execute(sa.select(date_column).where(workouts.c.user_id == user["id"]))]
        if bind.dialect.name != "postgresql":
            dates = [utc(value).date() for value in dates]
        goals = list(
            bind.execute(
                sa.select(history.c.workout_goal, history.c.effective_at)
                .where(
                    history.c.user_id == user["id"],
                )
                .order_by(history.c.effective_at.desc())
            )
        )
        active, longest, started = legacy_streaks(dates, goals, user["workout_goal"], utc(now).date())
        bind.execute(
            users.update()
            .where(users.c.id == user["id"])
            .values(
                active_streak=active,
                max_streak=longest,
                streak_started_at=started,
            )
        )
        boundary = midnight(monday, tz)
        times = bind.execute(
            sa.select(workouts.c.workout_time).where(
                workouts.c.user_id == user["id"],
                workouts.c.workout_time >= boundary,
                workouts.c.workout_time <= utc(now),
            )
        )
        mask = 0
        for row in times:
            mask |= 1 << utc(row[0]).astimezone(tz).weekday()
        entry = bind.execute(
            sa.select(history.c.workout_goal)
            .where(
                history.c.user_id == user["id"],
                history.c.effective_at <= boundary,
            )
            .order_by(history.c.effective_at.desc())
            .limit(1)
        ).first()
        goal = entry[0] if entry and entry[0] and 1 <= entry[0] <= 7 else user["workout_goal"]
        goal = goal if goal and 1 <= goal <= 7 else 1
        if bind.execute(sa.select(history.c.id).where(history.c.user_id == user["id"]).limit(1)).first() is None:
            bind.execute(
                history.insert().values(
                    user_id=user["id"], workout_goal=goal, effective_at=datetime(1970, 1, 1, tzinfo=timezone.utc)
                )
            )
        # An already-met current week is included in the cutover baseline;
        # neither later check-ins nor rollover should award that week again.
        bind.execute(
            weeks.insert().values(
                user_id=user["id"],
                week_start=monday,
                workout_goal=goal,
                checked_in_days=mask,
                goal_awarded=bin(mask).count("1") >= goal,
                finalized=False,
            )
        )


def upgrade():
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    additions = [
        sa.Column("streak_started_at", sa.DateTime(timezone=True), nullable=True),
    ]
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
    # Retain the weekly audit records and existing counters: dropping them
    # would discard data and cannot recover unknown original NULL goal values.
    pass
