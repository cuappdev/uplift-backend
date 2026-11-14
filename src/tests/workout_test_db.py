"""Isolated DB fixtures. PostgreSQL requires an explicit *_streak_test DB."""

import os
import unittest
from datetime import datetime

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("FLASK_ENV", "test")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_PATH", "service-account-key.json")

# Configure test defaults before application imports read their environment.
import sqlalchemy as sa  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from src import schema  # noqa: E402,F401 - Register ORM models without starting the app.
from src.models.user import User  # noqa: E402
from src.models.workout import Workout  # noqa: E402
from src.models.user_workout_week import UserWorkoutWeek  # noqa: E402
from src.models.user_workout_goal_history import UserWorkoutGoalHistory  # noqa: E402
from src.utils.workout_streaks import WORKOUT_TIMEZONE, initialize_tracking  # noqa: E402


def local(day, hour=12):
    """Build a New York timestamp for a calendar date in a test."""
    return datetime.fromisoformat(day).replace(hour=hour, tzinfo=WORKOUT_TIMEZONE)


class WorkoutDatabaseTest(unittest.TestCase):
    """Provide isolated workout tables and a session for each test."""

    def setUp(self):
        """Create only the fixture tables in an explicitly safe database."""
        url = os.getenv("WORKOUT_TEST_DATABASE_URL", "sqlite:///:memory:")
        if url != "sqlite:///:memory:" and not sa.engine.make_url(url).database.endswith("_streak_test"):
            raise ValueError("Refusing tests against a database without the _streak_test suffix")
        self.engine = sa.create_engine(url)
        self.postgres = self.engine.dialect.name == "postgresql"
        with self.engine.begin() as conn:
            for name in ("user_workout_week", "user_workout_goal_history", "workout", "users", "facility"):
                conn.execute(sa.text("DROP TABLE IF EXISTS " + name))
            conn.execute(sa.text("CREATE TABLE facility (id INTEGER PRIMARY KEY)"))
        for table in (User.__table__, UserWorkoutGoalHistory.__table__, UserWorkoutWeek.__table__, Workout.__table__):
            table.create(self.engine)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.Session()

    def tearDown(self):
        """Release the session and its database connections."""
        self.session.close()
        self.engine.dispose()

    def user(self, now, goal=3, streak=0, commit=True):
        """Create a synthetic user with initialized weekly tracking."""
        user = User(net_id="tester", name="Test", workout_goal=goal, active_streak=streak, max_streak=streak)
        self.session.add(user)
        initialize_tracking(self.session, user, now)
        if commit:
            self.session.commit()
        return user
