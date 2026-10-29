"""Migration cutover preserves counters instead of replaying old streaks."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa

from src.tests.workout_test_db import WorkoutDatabaseTest
from src.tests.test_workout_streaks import local
from src.models.user_workout_week import UserWorkoutWeek
from src.models.workout import Workout
from src.utils.workout_streaks import finalize_due_weeks


class WorkoutWeekMigrationTests(WorkoutDatabaseTest):
    def migration(self):
        path = Path(__file__).resolve().parents[2] / "migrations/versions/e2a471c9b630_store_workout_weeks.py"
        spec = importlib.util.spec_from_file_location("workout_week_migration", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def legacy_user(self, goal=1):
        user = self.user(local("2026-10-26"), goal=goal, streak=17)
        user.max_streak = 29
        user.last_streak = 12
        self.session.query(UserWorkoutWeek).delete()
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        for when in (datetime(2020, 1, 1, tzinfo=timezone.utc),
                     datetime(2026, 10, 26, 16, tzinfo=timezone.utc),
                     datetime(2026, 10, 26, 18, tzinfo=timezone.utc),
                     datetime(2099, 1, 1, tzinfo=timezone.utc)):
            self.session.add(Workout(user_id=user.id, facility_id=1, workout_time=when))
        self.session.commit()
        return user

    def test_seeds_only_current_days_and_preserves_all_streak_counters(self):
        user = self.legacy_user()
        module = self.migration()
        with self.engine.begin() as connection:
            module.seed_current_weeks(connection, local("2026-10-28"))
            module.seed_current_weeks(connection, local("2026-10-28"))
            module.seed_current_weeks(connection, local("2026-11-02"))
        self.session.refresh(user)
        self.assertEqual((user.active_streak, user.max_streak, user.last_streak), (17, 29, 12))
        rows = self.session.query(UserWorkoutWeek).all()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].week_start.isoformat(), "2026-10-26")
        self.assertEqual(rows[0].checked_in_days, 1)
        self.assertTrue(rows[0].goal_awarded)
        self.assertEqual(self.session.query(Workout).count(), 4)
        finalize_due_weeks(self.session, user, local("2026-11-02", 0))
        self.assertEqual(user.active_streak, 17)  # No duplicate cutover award.

    def test_below_goal_cutover_does_not_change_preserved_streak(self):
        user = self.legacy_user(goal=3)
        module = self.migration()
        with self.engine.begin() as connection:
            module.seed_current_weeks(connection, local("2026-10-28"))
        self.session.refresh(user)
        self.assertEqual(user.active_streak, 17)
        self.assertFalse(self.session.query(UserWorkoutWeek).one().goal_awarded)

    def test_full_upgrade_defaults_missing_goals_and_is_repeatable(self):
        if not self.postgres:
            self.skipTest("PostgreSQL ALTER COLUMN migration test")
        user = self.legacy_user(goal=3)
        self.session.close()
        module = self.migration()
        with self.engine.begin() as connection:
            connection.execute(sa.text("ALTER TABLE users ALTER COLUMN workout_goal DROP NOT NULL"))
            connection.execute(sa.text("UPDATE users SET workout_goal = NULL"))
            module.op = Operations(MigrationContext.configure(connection))
            class FrozenDateTime(datetime):
                @classmethod
                def now(cls, tz=None):
                    return datetime(2026, 10, 28, 16, tzinfo=timezone.utc)
            with patch.object(module, "datetime", FrozenDateTime):
                module.upgrade()
                module.upgrade()
            row = connection.execute(sa.text("SELECT active_streak, max_streak, last_streak, workout_goal FROM users")).one()
            self.assertEqual(tuple(row), (17, 29, 12, 1))
            column = next(c for c in sa.inspect(connection).get_columns("users") if c["name"] == "workout_goal")
            self.assertFalse(column["nullable"])
            self.assertIn("1", column["default"])
            self.assertEqual(connection.execute(sa.text("SELECT COUNT(*) FROM user_workout_week")).scalar(), 1)
            self.assertEqual(connection.execute(sa.text("SELECT COUNT(*) FROM workout")).scalar(), 4)

    def test_upgrade_from_older_schema_creates_columns_and_week_table(self):
        if not self.postgres:
            self.skipTest("PostgreSQL ALTER COLUMN migration test")
        self.legacy_user(goal=3)
        self.session.close()
        module = self.migration()
        with self.engine.begin() as connection:
            connection.execute(sa.text("DROP TABLE user_workout_week"))
            for column in ("streak_started_at",):
                connection.execute(sa.text("ALTER TABLE users DROP COLUMN " + column))
            module.op = Operations(MigrationContext.configure(connection))
            module.upgrade()
            self.assertEqual(connection.execute(sa.text("SELECT active_streak, max_streak FROM users")).one(), (17, 29))
            self.assertEqual(connection.execute(sa.text("SELECT COUNT(*) FROM user_workout_week")).scalar(), 1)
            columns = {column["name"] for column in sa.inspect(connection).get_columns("users")}
            self.assertIn("streak_started_at", columns)
            self.assertFalse({"workout_week_start", "next_workout_week_at"} & columns)
