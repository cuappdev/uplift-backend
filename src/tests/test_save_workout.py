import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

# src.schema reads these at import time.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_PATH", "service-account-key.json")
os.environ.setdefault("FLASK_ENV", "test")

from graphql import GraphQLError  # noqa: E402

from src.models.facility import Facility as FacilityModel  # noqa: E402
from src.models.user import User as UserModel  # noqa: E402
from src.models.workout import Workout as WorkoutModel  # noqa: E402
from src.schema import SaveWorkout  # noqa: E402

USER_ID = 7
START = datetime(2026, 11, 12, 18, 0, tzinfo=timezone.utc)
END = START + timedelta(minutes=45)

# jwt_required needs a request with a token; the tests patch get_jwt_identity instead
save_workout = SaveWorkout.mutate.__wrapped__


@patch("src.schema.get_jwt_identity", return_value=str(USER_ID))
@patch("src.schema.db_session")
class TestSaveWorkout(unittest.TestCase):
    def use_rows(self, db_session, workout=None, facility=True, user=True):
        """Make db_session queries return the given rows, by model."""
        rows = {
            WorkoutModel: workout,
            FacilityModel: MagicMock() if facility else None,
            UserModel: MagicMock() if user else None,
        }

        def query(model):
            result = MagicMock()
            result.filter.return_value.first.return_value = rows[model]
            return result

        db_session.query.side_effect = query

    def test_updates_the_check_in_workout(self, db_session, _):
        checked_in = WorkoutModel(id=3, user_id=USER_ID, facility_id=1, workout_time=START)
        self.use_rows(db_session, workout=checked_in)

        workout = save_workout(None, None, START, END, workout_id=3, title="  Leg day ", description="Squats", rating=4)

        self.assertIs(workout, checked_in)
        self.assertEqual((workout.started_at, workout.ended_at), (START, END))
        self.assertEqual((workout.title, workout.description, workout.rating), ("Leg day", "Squats", 4))
        self.assertEqual(workout.facility_id, 1)
        db_session.add.assert_not_called()
        db_session.commit.assert_called_once()

    def test_creates_a_workout_without_a_check_in(self, db_session, _):
        self.use_rows(db_session)

        workout = save_workout(None, None, START, END, facility_id=2)

        db_session.add.assert_called_once_with(workout)
        self.assertEqual((workout.user_id, workout.facility_id, workout.workout_time), (USER_ID, 2, START))
        self.assertEqual((workout.title, workout.description, workout.rating), (None, None, None))

    def test_naive_times_are_treated_as_utc(self, db_session, _):
        self.use_rows(db_session)

        workout = save_workout(None, None, START.replace(tzinfo=None), END.replace(tzinfo=None), facility_id=2)

        self.assertEqual((workout.started_at, workout.ended_at), (START, END))

    def test_cannot_save_another_users_workout(self, db_session, _):
        self.use_rows(db_session, workout=WorkoutModel(id=3, user_id=USER_ID + 1, facility_id=1))

        with self.assertRaisesRegex(GraphQLError, "does not exist"):
            save_workout(None, None, START, END, workout_id=3)
        db_session.commit.assert_not_called()

    def test_rejects_invalid_details(self, db_session, _):
        self.use_rows(db_session, workout=WorkoutModel(id=3, user_id=USER_ID, facility_id=1))
        cases = {
            "end time must be after": dict(end_time=START),
            "at most 24 hours": dict(end_time=START + timedelta(hours=25)),
            "rating must be between": dict(rating=6),
            "title must be at most": dict(title="x" * 101),
            "description must be at most": dict(description="x" * 2001),
        }
        for message, override in cases.items():
            with self.subTest(message):
                args = {"start_time": START, "end_time": END, "workout_id": 3, **override}
                with self.assertRaisesRegex(GraphQLError, message):
                    save_workout(None, None, **args)
        db_session.commit.assert_not_called()

    def test_new_workout_needs_an_existing_facility(self, db_session, _):
        self.use_rows(db_session, facility=False)

        with self.assertRaisesRegex(GraphQLError, "facility ID is required"):
            save_workout(None, None, START, END)
        with self.assertRaisesRegex(GraphQLError, "Facility with given ID does not exist"):
            save_workout(None, None, START, END, facility_id=99)
        db_session.add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
