"""Verified Google signup starts with the default weekly baseline."""

from datetime import datetime, timezone
from unittest.mock import patch

from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.models.user_workout_week import UserWorkoutWeek
from src.schema import CreateUser
from src.tests.workout_test_db import WorkoutDatabaseTest
from src.utils.google_auth import GoogleIdentity
from src.utils.workout_streaks import week_start, WORKOUT_TIMEZONE


class WorkoutSignupTests(WorkoutDatabaseTest):
    """Check the weekly baseline for verified Google signup."""

    def test_signup_initializes_default_goal_and_empty_week(self):
        """Start Google signup with an unselected default and empty week."""
        now = datetime(2026, 10, 29, 16, tzinfo=timezone.utc)
        identity = GoogleIdentity(sub="signup-google", net_id="testgoogle", email="testgoogle@cornell.edu")
        with patch("src.schema.db_session", self.session), patch(
            "src.schema.verify_google_identity", return_value=identity
        ), patch("src.schema.datetime", wraps=datetime) as clock:
            clock.now.return_value = now
            user = CreateUser().mutate(None, name="Test", id_token="test-token")
        row = self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).one()
        self.assertEqual((user.workout_goal, row.workout_goal), (1, 1))
        self.assertEqual(row.week_start, week_start(now.astimezone(WORKOUT_TIMEZONE).date()))
        self.assertEqual((row.checked_in_days, row.goal_awarded, row.finalized), (0, False, False))
        self.assertIsNone(user.last_goal_change)
        self.assertEqual(self.session.query(UserWorkoutGoalHistory).filter_by(user_id=user.id).count(), 0)
