"""HTTP coverage owns JWT enforcement and GraphQL argument compatibility."""
from contextlib import ExitStack
from datetime import datetime
from unittest.mock import patch

import sqlalchemy as sa
from flask_jwt_extended import create_access_token
from sqlalchemy.orm import scoped_session

from src.database import Base
from src.models.token_blacklist import TokenBlocklist
from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.models.user_workout_week import UserWorkoutWeek
from src.models.workout import Workout
from src.tests.workout_test_db import WorkoutDatabaseTest, local
from src.utils.workout_streaks import as_utc


class WorkoutGraphQLHTTPTests(WorkoutDatabaseTest):
    """Exercise workout authorization and public GraphQL responses."""

    def setUp(self):
        """Prepare an isolated database and controlled mutation dependencies."""
        super().setUp()
        import app_factory

        self.owner = self.user(local("2026-10-26"), goal=1)
        with self.engine.begin() as conn:
            for name, kind in (("name", "VARCHAR"), ("gym_id", "INTEGER"), ("facility_type", "VARCHAR")):
                conn.execute(sa.text("ALTER TABLE facility ADD COLUMN " + name + " " + kind))
            conn.execute(sa.text("INSERT INTO facility VALUES (1, 'Test gym', 1, 'fitness')"))
        TokenBlocklist.__table__.create(self.engine, checkfirst=True)
        sessions = scoped_session(self.Session)
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.addCleanup(sessions.remove)
        # Keep the real route and JWT callback; isolate external startup services.
        for target, value in (("app_factory.db_session", sessions), ("src.schema.db_session", sessions)):
            stack.enter_context(patch(target, value))
        stack.enter_context(patch.object(Base, "query", sessions.query_property()))
        with patch.multiple(
            app_factory,
            db_user="test",
            db_password="test",
            db_name="local_streak_test",
            db_host="localhost",
            db_port="5432",
        ), patch.object(app_factory, "initialize_firebase"), patch.object(app_factory, "init_db"), patch(
            "app_factory.open", create=True
        ):
            app = app_factory.create_app(run_migrations=True)
        app.config["JWT_SECRET_KEY"] = "isolated-http-test-secret-at-least-32-characters"
        with app.app_context():
            token = create_access_token(identity=str(self.owner.id))
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer " + token}

    def execute(self, query, variables=None, authenticated=True):
        """Send a GraphQL request through the real HTTP route."""
        response = self.client.post(
            "/graphql",
            json={"query": query, "variables": variables or {}},
            headers=self.headers if authenticated else {},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        return response.get_json()

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
                        self.assertIn("own workout data", result["errors"][0]["message"])
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

