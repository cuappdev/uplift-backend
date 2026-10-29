"""Store weekly progress without recalculating existing streak counters.

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


def seed_current_weeks(bind, now):
    """Initialize only this week. Never recompute or overwrite old streaks."""
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
        if bind.execute(sa.select(weeks.c.user_id).where(
            weeks.c.user_id == user["id"],
        ).limit(1)).first() is not None:
            continue
        boundary = midnight(monday, tz)
        times = bind.execute(sa.select(workouts.c.workout_time).where(
            workouts.c.user_id == user["id"], workouts.c.workout_time >= boundary,
            workouts.c.workout_time <= utc(now),
        ))
        mask = 0
        for row in times:
            mask |= 1 << utc(row[0]).astimezone(tz).weekday()
        entry = bind.execute(sa.select(history.c.workout_goal).where(
            history.c.user_id == user["id"], history.c.effective_at <= boundary,
        ).order_by(history.c.effective_at.desc()).limit(1)).first()
        goal = entry[0] if entry and entry[0] and 1 <= entry[0] <= 7 else user["workout_goal"]
        if bind.execute(sa.select(history.c.id).where(history.c.user_id == user["id"]).limit(1)).first() is None:
            bind.execute(history.insert().values(user_id=user["id"], workout_goal=goal,
                         effective_at=datetime(1970, 1, 1, tzinfo=timezone.utc)))
        # Treat an already-met current week as accounted for in the preserved
        # legacy streak, avoiding an extra award at cutover. Old logic did not
        # record per-week awards, so its exact provenance cannot be recovered.
        bind.execute(weeks.insert().values(
            user_id=user["id"], week_start=monday,
            workout_goal=goal, checked_in_days=mask,
            goal_awarded=bin(mask).count("1") >= goal, finalized=False,
        ))


def upgrade():
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    additions = [
        sa.Column("streak_started_at", sa.DateTime(timezone=True), nullable=True),
    ]
    for column in additions:
        if column.name not in columns:
            op.add_column("users", column)
    bind.execute(sa.text("UPDATE users SET workout_goal = 1 WHERE workout_goal IS NULL OR workout_goal NOT BETWEEN 1 AND 7"))
    op.alter_column("users", "workout_goal", existing_type=sa.Integer(), nullable=False, server_default=sa.text("1"))
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


def downgrade():
    # Retain the weekly audit records and existing counters: dropping them
    # would discard data and cannot recover unknown original NULL goal values.
    pass
