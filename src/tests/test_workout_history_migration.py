"""Exercise migration data preservation against a disposable in-memory DB."""
import importlib.util
from pathlib import Path
import unittest

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa


class WorkoutHistoryMigrationTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[2] / "migrations/versions/d8f2a614be30_ensure_workout_goal_history.py"
        spec = importlib.util.spec_from_file_location("workout_history_migration", path)
        self.migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.migration)
        self.engine = sa.create_engine("sqlite:///:memory:")
        self.connection = self.engine.connect()
        self.migration.op = Operations(MigrationContext.configure(self.connection))
        self.connection.execute(sa.text("CREATE TABLE users (id INTEGER PRIMARY KEY, workout_goal INTEGER)"))
        self.connection.execute(sa.text("INSERT INTO users VALUES (1, 3), (2, NULL), (3, 8)"))

    def tearDown(self):
        self.connection.close()
        self.engine.dispose()

    def rows(self):
        return self.connection.execute(sa.text(
            "SELECT user_id, workout_goal, effective_at FROM user_workout_goal_history ORDER BY id"
        )).fetchall()

    def test_creates_table_and_seeds_only_valid_legacy_goals(self):
        self.migration.upgrade()
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(tuple(rows[0])[:2], (1, 3))
        self.migration.upgrade()
        self.assertEqual(self.rows(), rows)

    def test_preserves_existing_history_and_downgrade_keeps_data(self):
        self.connection.execute(sa.text("""CREATE TABLE user_workout_goal_history (
            id INTEGER PRIMARY KEY, user_id INTEGER, workout_goal INTEGER, effective_at TIMESTAMP)"""))
        self.connection.execute(sa.text("""INSERT INTO user_workout_goal_history
            VALUES (1, 1, 5, '2026-10-01 00:00:00+00')"""))
        before = self.rows()
        self.migration.upgrade()
        self.assertEqual(self.rows(), before)
        self.migration.downgrade()
        self.assertEqual(self.rows(), before)
