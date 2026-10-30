"""Both supported signup paths initialize persisted weekly progress."""
from datetime import datetime, timezone
from unittest.mock import patch

from src.tests.workout_test_db import WorkoutDatabaseTest
from src.models.user_workout_week import UserWorkoutWeek
from src.schema import CreateUser
from src.utils.google_auth import GoogleIdentity
from src.utils.workout_streaks import week_start, WORKOUT_TIMEZONE


class WorkoutSignupTests(WorkoutDatabaseTest):
    def assert_initialized(self, user, now):
        row = self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).one()
        self.assertEqual(user.workout_goal, 1)
        self.assertEqual(row.workout_goal, 1)
        self.assertEqual(row.week_start, week_start(now.astimezone(WORKOUT_TIMEZONE).date()))
        self.assertEqual(row.checked_in_days, 0)
        self.assertFalse(row.goal_awarded)
        self.assertFalse(row.finalized)

    def test_google_signup_initializes_week(self):
        now = datetime(2026, 10, 29, 16, tzinfo=timezone.utc)
        identity = GoogleIdentity(sub='signup-google', net_id='testgoogle', email='testgoogle@cornell.edu')
        with patch('src.schema.db_session', self.session), patch('src.schema.verify_google_identity', return_value=identity), patch('src.schema.datetime') as clock:
            clock.now.return_value = now
            user = CreateUser().mutate(None, name='Google Test', id_token='test-token')
        self.assertEqual(user.google_sub, identity.sub)
        self.assertEqual(user.net_id, identity.net_id)
        self.assert_initialized(user, now)

    def test_legacy_signup_initializes_week(self):
        now = datetime(2026, 10, 29, 16, tzinfo=timezone.utc)
        with patch('src.schema.db_session', self.session), patch('src.schema.verify_google_identity') as verify, patch('src.schema.datetime') as clock:
            clock.now.return_value = now
            user = CreateUser().mutate(None, name='Legacy Test', net_id='testlegacy', email='testlegacy@cornell.edu')
        verify.assert_not_called()
        self.assertIsNone(user.google_sub)
        self.assertEqual(user.net_id, 'testlegacy')
        self.assert_initialized(user, now)
