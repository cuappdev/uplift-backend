"""API reads stored fields; writes share a database transaction with progress."""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
import graphene
import sqlalchemy as sa
from graphql import GraphQLError
from src.tests.workout_test_db import WorkoutDatabaseTest
from src.tests.test_workout_streaks import local
from src.schema import Query, SetWorkoutGoals, User, logWorkout
from src.models.user import User as UserModel
from src.models.workout import Workout
from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.utils.workout_streaks import current_week, record_checkin


class WorkoutSchemaTests(WorkoutDatabaseTest):
    def setUp(self):
        super().setUp()
        self.app = Flask(__name__)
        self.app.config["JWT_SECRET_KEY"] = "workout-test-secret-at-least-32-characters"
        JWTManager(self.app)
        self.identity = patch("src.schema.get_jwt_identity", return_value="1")
        self.identity.start()
        self.addCleanup(self.identity.stop)

    def test_real_jwt_rejects_cross_user_before_query_and_preserves_all_data(self):
        caller = self.user(local("2026-10-26"), goal=1)
        target = self.user(local("2026-10-26"), goal=3, streak=8)
        tables = (UserModel.__table__, Workout.__table__, UserWorkoutGoalHistory.__table__)
        from src.models.user_workout_week import UserWorkoutWeek
        tables += (UserWorkoutWeek.__table__,)
        def snapshot():
            return [self.session.execute(table.select().order_by(*table.primary_key.columns)).fetchall() for table in tables]
        before = snapshot()
        # Restore the real identity function as well as the real JWT decorators.
        self.identity.stop()
        with self.app.app_context():
            token = create_access_token(identity=str(caller.id))
        with self.app.test_request_context(headers={"Authorization": "Bearer " + token}), patch("src.schema.db_session", self.session), patch("src.schema.User.get_query") as query:
            for mutation, args in (
                (SetWorkoutGoals, dict(workout_goal=5)),
                (logWorkout, dict(workout_time=datetime.now(timezone.utc), facility_id=1)),
            ):
                with self.assertRaisesRegex(GraphQLError, "own workout data"):
                    mutation.mutate(None, None, user_id=target.id, **args)
            query.assert_not_called()
        self.assertEqual(snapshot(), before)

    def test_real_jwt_owner_can_change_goal_and_log_workout(self):
        user = self.user(datetime.now(timezone.utc), goal=1)
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        self.session.commit()
        self.identity.stop()
        with self.app.app_context():
            token = create_access_token(identity=str(user.id))
        with self.app.test_request_context(headers={"Authorization": "Bearer " + token}), patch("src.schema.db_session", self.session), patch("src.schema.User.get_query", return_value=self.session.query(UserModel)), patch("src.schema.Facility.get_query") as facility:
            facility.return_value.filter.return_value.first.return_value.id = 1
            SetWorkoutGoals.mutate(None, None, user_id=user.id, workout_goal=5)
            logWorkout.mutate(None, None, user_id=user.id, workout_time=datetime.now(timezone.utc), facility_id=1)
        self.assertEqual(user.workout_goal, 5)
        self.assertEqual(user.active_streak, 1)
        self.assertEqual(self.session.query(Workout).count(), 1)

    def test_graphql_reads_stored_streak_and_week_count_without_history(self):
        user = self.user(local("2026-10-26"), streak=8)
        record_checkin(self.session, user, local("2026-10-26"), local("2026-10-26"))
        self.session.commit()
        class TestQuery(graphene.ObjectType):
            user = graphene.Field(User)
            def resolve_user(root, info):
                return user
        statements = []
        listener = lambda conn, cursor, statement, parameters, context, many: statements.append(statement)
        sa.event.listen(self.engine, "before_cursor_execute", listener)
        try:
            with patch("src.schema.db_session", self.session), patch("src.schema.datetime") as clock:
                clock.now.return_value = local("2026-10-28")
                result = graphene.Schema(query=TestQuery).execute(
                    "{ user { activeStreak maxStreak workoutGoal currentWeekActiveDays streakStart } }"
                )
        finally:
            sa.event.remove(self.engine, "before_cursor_execute", listener)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["user"]["activeStreak"], 8)
        self.assertEqual(result.data["user"]["currentWeekActiveDays"], 1)
        self.assertEqual(len(statements), 1)
        self.assertIn("user_workout_week", statements[0])
        self.assertNotIn("goal_history", statements[0])

    def test_weekday_query_uses_flags_in_order(self):
        user = self.user(local("2026-10-26"))
        for day in ("2026-10-26", "2026-10-28"):
            record_checkin(self.session, user, local(day), local(day))
        with patch("src.schema.db_session", self.session), patch("src.schema.User.get_query", return_value=self.session.query(UserModel)), patch("src.schema.datetime") as clock:
            clock.now.return_value = local("2026-10-28")
            self.assertEqual(Query.resolve_get_weekly_workout_days.__wrapped__(None, None, id=user.id),
                             ["Monday", "Wednesday"])

    def test_goal_change_preserves_week_snapshot_and_starts_next_monday(self):
        user = self.user(local("2026-10-26"), goal=3, streak=8)
        with patch("src.schema.db_session", self.session), patch("src.schema.User.get_query", return_value=self.session.query(UserModel)), patch("src.schema.datetime") as clock:
            clock.now.return_value = datetime(2026, 10, 28, 16, tzinfo=timezone.utc)
            clock.side_effect = datetime
            SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=5)
        history = self.session.query(UserWorkoutGoalHistory).order_by(UserWorkoutGoalHistory.effective_at).all()
        self.assertEqual([row.workout_goal for row in history], [3, 5])
        from src.utils.workout_streaks import as_utc
        self.assertEqual(as_utc(history[-1].effective_at), datetime(2026, 11, 2, 5, tzinfo=timezone.utc))
        self.assertEqual(user.last_streak, 8)
        self.assertEqual(current_week(self.session, user, local("2026-10-28")).workout_goal, 3)

    def test_goal_range_and_thirty_day_restriction(self):
        for goal in (0, -1, 8):
            with self.subTest(goal=goal), self.assertRaises(GraphQLError):
                SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=1, workout_goal=goal)
        user = self.user(local("2026-10-26"))
        user.last_goal_change = datetime.now(timezone.utc)
        self.session.commit()
        with patch("src.schema.db_session", self.session), patch("src.schema.User.get_query", return_value=self.session.query(UserModel)), self.assertRaisesRegex(GraphQLError, "30 days"):
            SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=5)

    def test_log_workout_and_progress_commit_together(self):
        user = self.user(local("2026-10-26"), goal=1)
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        self.session.commit()
        with patch("src.schema.db_session", self.session), patch("src.schema.User.get_query", return_value=self.session.query(UserModel)), patch("src.schema.Facility.get_query") as facility, patch("src.schema.datetime") as clock:
            facility.return_value.filter.return_value.first.return_value.id = 1
            clock.now.return_value = local("2026-10-28", 14)
            result = logWorkout.mutate.__wrapped__(None, None, workout_time=local("2026-10-28"), user_id=user.id, facility_id=1)
        self.assertIsNotNone(result.id)
        self.assertEqual(self.session.query(Workout).count(), 1)
        self.assertEqual(user.active_streak, 1)
        self.assertEqual(current_week(self.session, user, local("2026-10-28")).checked_in_days, 4)

    def test_commit_failure_rolls_back_workout_and_progress(self):
        user = self.user(local("2026-10-26"), goal=1, streak=2)
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        self.session.commit()
        with patch("src.schema.db_session", self.session), patch("src.schema.User.get_query", return_value=self.session.query(UserModel)), patch("src.schema.Facility.get_query") as facility, patch("src.schema.datetime") as clock, patch.object(self.session, "commit", side_effect=RuntimeError("test failure")):
            facility.return_value.filter.return_value.first.return_value.id = 1
            clock.now.return_value = local("2026-10-28", 14)
            with self.assertRaisesRegex(RuntimeError, "test failure"):
                logWorkout.mutate.__wrapped__(None, None, workout_time=local("2026-10-28"), user_id=user.id, facility_id=1)
        self.assertEqual(self.session.query(Workout).count(), 0)
        self.assertEqual(user.active_streak, 2)
        self.assertEqual(current_week(self.session, user, local("2026-10-28")).checked_in_days, 0)

    def test_server_time_used_when_legacy_time_past_future_null_or_omitted(self):
        user = self.user(local("2026-10-26"), goal=1, streak=2)
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        self.session.commit()
        now = local("2026-10-26", 14)
        with patch("src.schema.db_session", self.session), patch("src.schema.User.get_query", return_value=self.session.query(UserModel)), patch("src.schema.Facility.get_query") as facility, patch("src.schema.datetime") as clock:
            facility.return_value.filter.return_value.first.return_value.id = 1
            clock.now.return_value = now
            for arguments in ({"workout_time": local("2026-09-25")},
                              {"workout_time": local("2099-10-25")},
                              {"workout_time": None}, {}):
                with self.subTest(arguments=arguments):
                    result = logWorkout.mutate.__wrapped__(None, None, user_id=user.id, facility_id=1, **arguments)
                    from src.utils.workout_streaks import as_utc
                    self.assertEqual(as_utc(result.workout_time), as_utc(now))
        self.assertEqual(self.session.query(Workout).count(), 4)
        self.assertEqual(user.active_streak, 3)
        self.assertEqual(current_week(self.session, user, now).checked_in_days, 1)

    def test_graphql_has_no_configurable_workout_timezone(self):
        from src.schema import Mutation
        schema = graphene.Schema(query=Query, mutation=Mutation)
        self.assertNotIn("workoutTimezone", schema.get_type("User").fields)
        self.assertNotIn("setWorkoutTimezone", schema.get_type("Mutation").fields)
        self.assertNotIn("workoutTimezone", schema.get_type("Mutation").fields["createUser"].args)
