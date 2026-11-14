"""HTTP coverage owns JWT enforcement and GraphQL argument compatibility."""

from datetime import datetime
from unittest.mock import patch

from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.models.user_workout_week import UserWorkoutWeek
from src.models.workout import Workout
from src.tests.workout_test_db import local
from src.tests.workout_http_test import WorkoutHTTPTest
from src.utils.workout_streaks import as_utc


class WorkoutGraphQLHTTPTests(WorkoutHTTPTest):
    """Exercise workout authorization and public GraphQL responses."""

    def test_workout_mutations_require_authentication_and_ownership(self):
        """Reject missing tokens and attempts to modify another user."""
        for mutation in (
            "logWorkout(userId: %s, facilityId: 1) { id }",
            "setWorkoutGoals(userId: %s, workoutGoal: 5) { workoutGoal }",
        ):
            for authenticated, user_id in ((False, self.owner.id), (True, self.owner.id + 1)):
                with self.subTest(mutation=mutation, authenticated=authenticated):
                    result = self.execute("mutation { " + mutation % user_id + " }", authenticated=authenticated)
                    self.assertIn("errors", result)
                    if authenticated:
                        self.assertIn("own account", result["errors"][0]["message"])
        self.assertEqual(self.session.query(Workout).count(), 0)
        self.session.refresh(self.owner)
        self.assertEqual(self.owner.workout_goal, 1)

    def test_owner_checkins_accept_legacy_and_optional_time_arguments(self):
        """Ignore client dates while preserving legacy argument compatibility."""
        now = local("2026-10-28", 14)
        with patch("src.schema.datetime", wraps=datetime) as clock:
            clock.now.return_value = now
            result = self.execute(
                "mutation { setWorkoutGoals(userId: %s, workoutGoal: 5) { workoutGoal } }" % self.owner.id
            )
            self.assertEqual(result.get("data", {}).get("setWorkoutGoals"), {"workoutGoal": 5}, result)
            for declaration, argument, variables in (
                ("($time: DateTime!)", ", workoutTime: $time", {"time": "2026-09-01T12:00:00Z"}),
                ("($time: DateTime!)", ", workoutTime: $time", {"time": "2099-01-01T12:00:00Z"}),
                ("($time: DateTime)", ", workoutTime: $time", {"time": None}),
                ("", "", {}),
            ):
                with self.subTest(variables=variables, declaration=declaration):
                    query = "mutation%s { logWorkout(userId: %s, facilityId: 1%s) { workoutTime } }" % (
                        declaration,
                        self.owner.id,
                        argument,
                    )
                    result = self.execute(query, variables)
                    self.assertNotIn("errors", result, result)
                    self.assertEqual(
                        as_utc(datetime.fromisoformat(result["data"]["logWorkout"]["workoutTime"])), as_utc(now)
                    )
            # Check real API reads here instead of rebuilding a second schema.
            with patch("src.schema.Workout.get_query", side_effect=AssertionError("Unexpected workout history scan")):
                result = self.execute(
                    '{ getUserByNetId(netId: "tester") { workoutGoal currentWeekGoal '
                    "activeStreak maxStreak currentWeekActiveDays } getWeeklyWorkoutDays(id: %s) }" % self.owner.id
                )
            self.assertNotIn("errors", result, result)
            self.assertEqual(
                result["data"]["getUserByNetId"],
                [
                    {
                        "workoutGoal": 5,
                        "currentWeekGoal": 5,
                        "activeStreak": 0,
                        "maxStreak": 0,
                        "currentWeekActiveDays": 1,
                    }
                ],
            )
            self.assertEqual(result["data"]["getWeeklyWorkoutDays"], ["Wednesday"])
        self.session.refresh(self.owner)
        self.assertEqual(self.session.query(Workout).count(), 4)
        self.assertEqual(self.owner.active_streak, 0)

    def test_selected_goal_and_current_week_goal_are_distinct_after_later_change(self):
        """Expose the scheduled choice separately from the frozen weekly goal."""
        self.owner.last_goal_change = local("2026-09-01")
        self.session.commit()
        with patch("src.schema.datetime", wraps=datetime) as clock:
            clock.now.return_value = local("2026-10-28")
            result = self.execute(
                "mutation { setWorkoutGoals(userId: %s, workoutGoal: 4) { workoutGoal currentWeekGoal } }"
                % self.owner.id
            )
            self.assertEqual(
                result.get("data", {}).get("setWorkoutGoals"), {"workoutGoal": 4, "currentWeekGoal": 1}, result
            )
            clock.now.return_value = local("2026-11-02")
            result = self.execute('{ getUserByNetId(netId: "tester") { workoutGoal currentWeekGoal } }')
            self.assertEqual(
                result.get("data", {}).get("getUserByNetId"), [{"workoutGoal": 4, "currentWeekGoal": 4}], result
            )

    def test_checkin_recovers_missing_legacy_baseline_without_duplicate_credit(self):
        """Heal rollout-gap accounts through the public authenticated mutation."""
        self.session.query(UserWorkoutWeek).delete()
        self.owner.workout_goal = 3
        self.session.add_all(
            Workout(user_id=self.owner.id, facility_id=1, workout_time=local(day))
            for day in ("2026-10-23", "2026-10-24", "2026-10-25", "2026-10-26")
        )
        self.session.commit()
        with patch("src.schema.datetime", wraps=datetime) as clock:
            clock.now.return_value = local("2026-10-28")
            for _ in range(2):
                result = self.execute(
                    "mutation { logWorkout(userId: %s, facilityId: 1) { id user { "
                    "workoutGoal currentWeekGoal activeStreak maxStreak currentWeekActiveDays } } }" % self.owner.id
                )
                self.assertNotIn("errors", result, result)
                self.assertEqual(
                    result["data"]["logWorkout"]["user"],
                    dict(workoutGoal=3, currentWeekGoal=3, activeStreak=1, maxStreak=1, currentWeekActiveDays=2),
                )
        self.session.expire_all()
        row = self.session.query(UserWorkoutWeek).one()
        self.assertEqual((row.checked_in_days, row.goal_awarded, row.finalized), (5, True, False))
        self.assertEqual(self.session.query(UserWorkoutGoalHistory).count(), 1)
        self.assertEqual(self.session.query(Workout).count(), 6)
