"""Isolated DB fixtures. PostgreSQL requires an explicit *_streak_test DB."""
import os
import unittest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("FLASK_ENV", "test")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_PATH", "service-account-key.json")

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from src import schema  # Register ORM models without starting the app.
from src.models.user import User
from src.models.workout import Workout
from src.models.user_workout_week import UserWorkoutWeek
from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.utils.workout_streaks import initialize_tracking


class WorkoutDatabaseTest(unittest.TestCase):
    def setUp(self):
        url = os.getenv("WORKOUT_TEST_DATABASE_URL", "sqlite:///:memory:")
        if url != "sqlite:///:memory:" and not sa.engine.make_url(url).database.endswith("_streak_test"):
            raise ValueError("Refusing tests against a database without the _streak_test suffix")
        self.engine = sa.create_engine(url)
        self.postgres = self.engine.dialect.name == "postgresql"
        with self.engine.begin() as conn:
            for name in ("user_workout_week", "user_workout_goal_history", "workout", "users", "facility"):
                conn.execute(sa.text('DROP TABLE IF EXISTS ' + name))
            conn.execute(sa.text("CREATE TABLE facility (id INTEGER PRIMARY KEY)"))
        for table in (User.__table__, UserWorkoutGoalHistory.__table__, UserWorkoutWeek.__table__, Workout.__table__):
            table.create(self.engine)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def user(self, now, goal=3, streak=0):
        user = User(net_id="tester", name="Test", workout_goal=goal,
                    active_streak=streak, max_streak=streak)
        self.session.add(user)
        initialize_tracking(self.session, user, now)
        self.session.commit()
        return user
