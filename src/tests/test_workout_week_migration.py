"""Legacy display survives cutover; weekly state is seeded only once."""
import importlib.util
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa

from src.models.user_workout_week import UserWorkoutWeek
from src.models.workout import Workout
from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.tests.workout_test_db import WorkoutDatabaseTest, local
from src.utils.workout_streaks import as_utc, finalize_due_weeks


class WorkoutWeekMigrationTests(WorkoutDatabaseTest):
    def migration(self, filename="e2a471c9b630_store_workout_weeks.py"):
        path = Path(__file__).resolve().parents[2] / "migrations/versions" / filename
        spec = importlib.util.spec_from_file_location("workout_migration", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def legacy_user(self, goal=1):
        user = self.user(local("2026-10-26"), goal=goal, streak=17)
        user.max_streak, user.last_streak = 29, 12
        self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).delete()
        self.session.execute(
            sa.text("INSERT INTO facility (id) SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM facility WHERE id = 1)")
        )
        for day, hour in (("2020-01-01", 12), ("2026-10-26", 12), ("2026-10-26", 14), ("2099-01-01", 12)):
            self.session.add(Workout(user_id=user.id, facility_id=1, workout_time=local(day, hour)))
        self.session.commit()
        return user

    def test_chained_cutover_preserves_display_workouts_and_prevents_duplicate_awards(self):
        module = self.migration()
        for goal, expected in ((1, 1), (3, 0)):
            with self.subTest(goal=goal):
                user = self.legacy_user(goal)
                with self.engine.begin() as connection:
                    # No-history users must keep their unknown streak start.
                    connection.execute(sa.text("DROP TABLE user_workout_goal_history"))
                    prerequisite = self.migration("d8f2a614be30_ensure_workout_goal_history.py")
                    prerequisite.op = Operations(MigrationContext.configure(connection))
                    prerequisite.upgrade()
                    prerequisite.upgrade()
                    self.assertEqual(
                        connection.execute(sa.text("SELECT COUNT(*) FROM user_workout_goal_history")).scalar(), 0
                    )
                    for when in ("2026-10-28", "2026-10-28", "2026-11-02"):
                        module.seed_current_weeks(connection, local(when))
                self.session.refresh(user)
                self.assertEqual((user.active_streak, user.max_streak, user.last_streak), (expected, expected, 12))
                self.assertIsNone(user.streak_started_at)
                row = self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).one()
                self.assertEqual(
                    (row.week_start.isoformat(), row.checked_in_days, row.goal_awarded), ("2026-10-26", 1, goal == 1)
                )
                self.assertEqual(self.session.query(Workout).filter_by(user_id=user.id).count(), 4)
                finalize_due_weeks(self.session, user, local("2026-11-02", 0))
                self.assertEqual(user.active_streak, expected)
                self.session.commit()

    def test_upgrade_old_schema_defaults_goals_and_is_repeatable(self):
        if not self.postgres:
            self.skipTest("PostgreSQL ALTER COLUMN migration test")
        self.legacy_user(goal=3)
        self.session.close()
        module = self.migration()
        with self.engine.begin() as connection:
            for sql in (
                "DROP TABLE user_workout_week",
                "ALTER TABLE users DROP COLUMN streak_started_at",
                "ALTER TABLE users ALTER COLUMN workout_goal DROP NOT NULL",
                "UPDATE users SET workout_goal = NULL",
            ):
                connection.execute(sa.text(sql))
            module.op = Operations(MigrationContext.configure(connection))
            with patch.object(module, "datetime", wraps=datetime) as clock:
                clock.now.return_value = local("2026-10-28")
                module.upgrade()
                module.upgrade()
            self.assertEqual(
                tuple(
                    connection.execute(
                        sa.text("SELECT active_streak, max_streak, last_streak, workout_goal FROM users")
                    ).one()
                ),
                (0, 0, 12, 1),
            )
            column = next(c for c in sa.inspect(connection).get_columns("users") if c["name"] == "workout_goal")
            self.assertFalse(column["nullable"])
            self.assertIn("1", column["default"])
            self.assertEqual(connection.execute(sa.text("SELECT COUNT(*) FROM user_workout_week")).scalar(), 1)
            self.assertEqual(connection.execute(sa.text("SELECT COUNT(*) FROM workout")).scalar(), 4)

    def test_rolling_display_and_real_history_survive_cutover_and_rerun(self):
        user = self.legacy_user()
        self.session.query(Workout).delete()
        for goal, day in ((1, "2020-01-01"), (3, "2026-10-15")):
            self.session.add(UserWorkoutGoalHistory(user_id=user.id, workout_goal=goal, effective_at=local(day)))
        # Sundays count in old rolling windows but precede this calendar week.
        for day in ("2026-10-25", "2026-10-24", "2026-10-23", "2026-10-18", "2026-10-17", "2026-10-16", "2026-10-11"):
            self.session.add(Workout(user_id=user.id, facility_id=1, workout_time=local(day)))
        self.session.commit()
        module = self.migration()
        with self.engine.begin() as connection:
            prerequisite = self.migration("d8f2a614be30_ensure_workout_goal_history.py")
            prerequisite.op = Operations(MigrationContext.configure(connection))
            prerequisite.upgrade()
            module.seed_current_weeks(connection, local("2026-10-28"))
        self.session.refresh(user)
        self.assertEqual(
            (user.active_streak, user.max_streak, as_utc(user.streak_started_at)),
            (3, 3, as_utc(local("2026-10-11", 0))),
        )
        self.assertEqual(self.session.query(UserWorkoutGoalHistory).count(), 2)
        row = self.session.query(UserWorkoutWeek).one()
        self.assertEqual((row.checked_in_days, row.goal_awarded), (0, False))
        user.active_streak, user.max_streak = 4, 4
        self.session.commit()
        with self.engine.begin() as connection:
            module.seed_current_weeks(connection, local("2026-11-02"))
        self.session.refresh(user)
        self.assertEqual((user.active_streak, user.max_streak), (4, 4))
