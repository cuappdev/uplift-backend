import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

# src.schema reads these at import time.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_PATH", "service-account-key.json")
os.environ.setdefault("FLASK_ENV", "test")

from graphql import GraphQLError  # noqa: E402

from src.models.enums import MuscleGroupEnum  # noqa: E402
from src.models.facility import Facility as FacilityModel  # noqa: E402
from src.models.user import User as UserModel  # noqa: E402
from src.models.workout import Workout as WorkoutModel  # noqa: E402
from src.schema import SaveWorkout  # noqa: E402
from src.utils.constants import (  # noqa: E402
    WORKOUT_DESCRIPTION_MAX_LENGTH,
    WORKOUT_MAX_DURATION_HOURS,
    WORKOUT_RATING_MAX,
    WORKOUT_TITLE_MAX_LENGTH,
)

USER_ID = 7
WORKOUT_ID = 3
START = datetime(2026, 11, 12, 18, 0, tzinfo=timezone.utc)
END = START + timedelta(minutes=45)


def save_workout(**arguments):
    """Call saveWorkout as the test user, with START and END unless given."""
    # jwt_required needs a request with a token, so call the undecorated mutate
    return SaveWorkout.mutate.__wrapped__(None, None, **{"start_time": START, "end_time": END, **arguments})


def own_workout(**fields):
    return WorkoutModel(id=WORKOUT_ID, user_id=USER_ID, facility_id=1, workout_time=START, **fields)


@patch("src.schema.get_jwt_identity", return_value=str(USER_ID))
@patch("src.schema.db_session")
class TestSaveWorkout(unittest.TestCase):
    def use_rows(self, db_session, workout=None, facility=True, user=True):
        """Make db_session lookups by ID return the given rows, by model."""
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
        checked_in = own_workout()
        self.use_rows(db_session, workout=checked_in)

        workout = save_workout(
            workout_id=WORKOUT_ID,
            title="  Leg day ",
            description="Squats",
            rating=4,
            muscle_groups=["LEG", "ARM", "LEG"],
        )

        self.assertIs(workout, checked_in)
        self.assertEqual((workout.started_at, workout.ended_at), (START, END))
        self.assertEqual((workout.title, workout.description, workout.rating), ("Leg day", "Squats", 4))
        # Duplicates are dropped and groups are kept in a fixed order
        self.assertEqual(workout.muscle_groups, [MuscleGroupEnum.ARM, MuscleGroupEnum.LEG])
        self.assertEqual(workout.facility_id, 1)
        db_session.add.assert_not_called()
        db_session.commit.assert_called_once()

    def test_saving_again_replaces_details(self, db_session, _):
        workout = own_workout(title="Leg day", rating=4, muscle_groups=[MuscleGroupEnum.LEG])
        self.use_rows(db_session, workout=workout)

        save_workout(workout_id=WORKOUT_ID, description="Easy day")

        self.assertEqual((workout.title, workout.description, workout.rating), (None, "Easy day", None))
        self.assertEqual(workout.muscle_groups, [])

    def test_creates_a_workout_without_a_check_in(self, db_session, _):
        self.use_rows(db_session)

        workout = save_workout(facility_id=2, start_time=START.replace(tzinfo=None), end_time=END.replace(tzinfo=None))

        db_session.add.assert_called_once_with(workout)
        self.assertEqual((workout.user_id, workout.facility_id), (USER_ID, 2))
        # Times without a time zone are treated as UTC
        self.assertEqual((workout.workout_time, workout.started_at, workout.ended_at), (START, START, END))

    def test_cannot_save_another_users_workout(self, db_session, _):
        self.use_rows(db_session, workout=WorkoutModel(id=WORKOUT_ID, user_id=USER_ID + 1, facility_id=1))

        with self.assertRaisesRegex(GraphQLError, "Workout with given ID does not exist"):
            save_workout(workout_id=WORKOUT_ID)
        db_session.commit.assert_not_called()

    def test_rejects_invalid_details(self, db_session, _):
        self.use_rows(db_session, workout=own_workout())
        cases = {
            "end time must be after": {"end_time": START},
            "hours long": {"end_time": START + timedelta(hours=WORKOUT_MAX_DURATION_HOURS, minutes=1)},
            "rating must be between": {"rating": WORKOUT_RATING_MAX + 1},
            "title must be at most": {"title": "x" * (WORKOUT_TITLE_MAX_LENGTH + 1)},
            "description must be at most": {"description": "x" * (WORKOUT_DESCRIPTION_MAX_LENGTH + 1)},
        }
        for message, arguments in cases.items():
            with self.subTest(message), self.assertRaisesRegex(GraphQLError, message):
                save_workout(workout_id=WORKOUT_ID, **arguments)
        db_session.commit.assert_not_called()

    def test_new_workout_needs_an_existing_facility(self, db_session, _):
        self.use_rows(db_session, facility=False)

        with self.assertRaisesRegex(GraphQLError, "facility ID is required"):
            save_workout()
        with self.assertRaisesRegex(GraphQLError, "Facility with given ID does not exist"):
            save_workout(facility_id=99)
        db_session.add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
