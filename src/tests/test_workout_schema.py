"""Goal changes and workout writes preserve transaction/week boundaries."""
from contextlib import ExitStack
from datetime import datetime, timedelta
from pathlib import Path
import re
from unittest.mock import patch

import sqlalchemy as sa
from graphql import GraphQLError, build_ast_schema, parse
from src.models.user import User as UserModel
from src.models.workout import Workout
from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.schema import SetWorkoutGoals, User as UserType, logWorkout, schema
from src.tests.workout_test_db import WorkoutDatabaseTest, local
from src.utils.workout_streaks import as_utc, current_week, finalize_due_weeks


class WorkoutSchemaTests(WorkoutDatabaseTest):
    """Check goal transitions and atomic workout mutations."""

    def setUp(self):
        """Prepare an isolated database and controlled mutation dependencies."""
        super().setUp()
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch("src.schema.db_session", self.session))
        stack.enter_context(patch("src.schema.get_jwt_identity", return_value="1"))
        stack.enter_context(patch("src.schema.User.get_query", return_value=self.session.query(UserModel)))
        self.clock = stack.enter_context(patch("src.schema.datetime", wraps=datetime))
        self.clock.now.return_value = local("2026-10-28")
        facility = stack.enter_context(patch("src.schema.Facility.get_query"))
        facility.return_value.filter.return_value.first.return_value.id = 1
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        self.session.commit()

    def test_legacy_workout_contract_in_runtime_and_published_schema(self):
        """Freeze the workout surface from auth base 6be8f2b and PR HEAD 09cff5b."""
        # The only intentional changes from base are additive weekly fields,
        # non-null workoutGoal output, and accepting omitted/null workoutTime.
        user_fields = dict(
            item.split(":", 1)
            for item in (
                "id:ID! email:String netId:String! name:String! activeStreak:Int! maxStreak:Int! "
                "workoutGoal:Int! lastGoalChange:DateTime lastStreak:Int! encodedImage:String "
                "giveaways:[Giveaway] goalHistory:[WorkoutGoalHistory] friendRequestsSent:[Friendship] "
                "friendRequestsReceived:[Friendship] workouts:[Workout] friendships:[Friendship] friends:[User] "
                "totalGymDays:Int! streakStart:DateTime workoutHistory:[Workout] "
                "currentWeekActiveDays:Int! currentWeekGoal:Int!"
            ).split()
        )
        signatures = {
            "Query": {
                "getUserByNetId": ("[User]", {"netId": "String"}),
                "getWeeklyWorkoutDays": ("[String]", {"id": "Int"}),
                "getWorkoutsById": ("[Workout]", {"id": "Int"}),
            },
            "Mutation": {
                "createUser": (
                    "User",
                    dict(email="String", encodedImage="String", idToken="String", name="String!", netId="String"),
                ),
                "setWorkoutGoals": ("User", dict(userId="Int!", workoutGoal="Int!")),
                "logWorkout": ("Workout", dict(facilityId="Int!", userId="Int!", workoutTime="DateTime")),
            },
            "User": {name: (kind, {}) for name, kind in user_fields.items()},
            "Workout": {
                name: (kind, {})
                for name, kind in dict(
                    id="ID!", workoutTime="DateTime!", userId="Int!", facilityId="Int!", user="User", gymName="String!"
                ).items()
            },
        }
        snapshot = (Path(__file__).resolve().parents[2] / "schema.graphql").read_text()
        # graphql-core 2's SDL parser predates description strings, although its
        # schema printer emits them. Descriptions do not affect this contract.
        published = build_ast_schema(parse(re.sub(r'""".*?"""', "", snapshot, flags=re.DOTALL)))
        for source in (schema, published):
            for type_name, fields in signatures.items():
                for name, signature in fields.items():
                    with self.subTest(source=type(source).__name__, type=type_name, field=name):
                        field = source.get_type(type_name).fields[name]
                        self.assertEqual(
                            (str(field.type), {key: str(arg.type) for key, arg in field.args.items()}), signature
                        )

    def test_goal_change_keeps_this_week_and_applies_next_monday(self):
        """Keep an established target fixed until the next Monday."""
        user = self.user(local("2026-10-26"), goal=3, streak=8)
        for goal in (0, -1, 8):
            with self.subTest(goal=goal), self.assertRaises(GraphQLError):
                SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=goal)
        SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=5)
        history = self.session.query(UserWorkoutGoalHistory).order_by(UserWorkoutGoalHistory.effective_at).all()
        self.assertEqual([row.workout_goal for row in history], [3, 5])
        self.assertEqual(as_utc(history[-1].effective_at), as_utc(local("2026-11-02", 0)))
        self.assertEqual((user.last_streak, current_week(self.session, user, self.clock.now()).workout_goal), (8, 3))
        with self.assertRaisesRegex(GraphQLError, "30 days"):
            SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=4)

    def test_first_selection_applies_now_for_fresh_and_epoch_baselines(self):
        """Apply explicit onboarding choices now without treating fallback history as a choice."""
        for goal, epoch_baseline in ((4, False), (1, False), (4, True)):
            with self.subTest(goal=goal, epoch_baseline=epoch_baseline):
                user = self.user(local("2026-10-26"), goal=1)
                if epoch_baseline:
                    self.session.add(
                        UserWorkoutGoalHistory(
                            user_id=user.id, workout_goal=1, effective_at=as_utc(datetime(1970, 1, 1))
                        )
                    )
                    self.session.commit()
                with patch("src.schema.get_jwt_identity", return_value=str(user.id)):
                    SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=goal)
                    row = current_week(self.session, user, self.clock.now())
                    history = (
                        self.session.query(UserWorkoutGoalHistory)
                        .filter_by(user_id=user.id)
                        .order_by(UserWorkoutGoalHistory.effective_at)
                        .all()
                    )
                    self.assertEqual([entry.workout_goal for entry in history], [1, goal] if epoch_baseline else [goal])
                    self.assertEqual(
                        (user.workout_goal, row.workout_goal, UserType.resolve_current_week_goal(user, None)),
                        (goal, goal, goal),
                    )
                    self.assertEqual(as_utc(history[-1].effective_at), as_utc(local("2026-10-26", 0)))
                    self.assertEqual(as_utc(user.last_goal_change), as_utc(self.clock.now()))
                    logWorkout.mutate.__wrapped__(None, None, user_id=user.id, facility_id=1)
                    self.assertEqual((row.goal_awarded, user.active_streak), (goal == 1, int(goal == 1)))
                    with self.assertRaisesRegex(GraphQLError, "30 days"):
                        SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=2)

    def test_goal_change_allowed_at_exact_thirty_day_boundary(self):
        """Enforce the cooldown through its last microsecond across DST."""
        user = self.user(local("2026-10-26"), goal=1)
        selected_at = as_utc(self.clock.now())
        self.clock.now.return_value = selected_at
        SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=4)
        boundary = as_utc(selected_at) + timedelta(days=30)
        self.clock.now.return_value = boundary - timedelta(microseconds=1)
        with self.assertRaisesRegex(GraphQLError, "30 days"):
            SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=2)
        self.clock.now.return_value = boundary
        SetWorkoutGoals.mutate.__wrapped__(None, None, user_id=user.id, workout_goal=2)
        history = self.session.query(UserWorkoutGoalHistory).order_by(UserWorkoutGoalHistory.effective_at).all()
        self.assertEqual([entry.workout_goal for entry in history], [4, 2])
        self.assertEqual(as_utc(history[-1].effective_at), as_utc(local("2026-11-30", 0)))
        self.assertEqual(current_week(self.session, user, selected_at).workout_goal, 4)

    def test_legacy_timestamp_across_monday_uses_server_week_and_warns(self):
        """Credit the server week and diagnose a conflicting legacy timestamp."""
        user = self.user(local("2026-11-02", 0), goal=1)
        self.clock.now.return_value = local("2026-11-02", 0)
        with self.assertLogs("src.schema", level="WARNING") as logs:
            workout = logWorkout.mutate.__wrapped__(
                None, None, user_id=user.id, facility_id=1, workout_time=local("2026-11-01", 23)
            )
        self.assertEqual(len(logs.records), 1)
        self.assertIn("over five minutes", logs.output[0])
        self.assertEqual(as_utc(workout.workout_time), as_utc(self.clock.now()))
        self.assertEqual(current_week(self.session, user, self.clock.now()).checked_in_days, 1)
        self.assertIsNone(current_week(self.session, user, local("2026-11-01")))

    def test_checkin_waiting_across_rollover_uses_time_after_user_lock(self):
        """Use the new week when a check-in waits through rollover."""
        sunday, monday = local("2026-11-01", 23), local("2026-11-02", 0)
        user = self.user(sunday, goal=1, streak=2)
        old_week = current_week(self.session, user, sunday)
        self.clock.now.return_value = sunday

        def acquire_after_rollover():
            # Model rollover completing while the request waits for its lock.
            finalize_due_weeks(self.session, user, monday)
            self.session.commit()
            self.clock.now.return_value = monday
            return user

        with patch("src.schema.User.get_query") as query:
            locked_query = query.return_value.filter.return_value.populate_existing.return_value.with_for_update
            locked_query.return_value.first.side_effect = acquire_after_rollover
            workout = logWorkout.mutate.__wrapped__(None, None, user_id=user.id, facility_id=1, workout_time=sunday)
        self.assertEqual((old_week.checked_in_days, old_week.finalized, old_week.goal_awarded), (0, True, False))
        self.assertEqual(as_utc(workout.workout_time), as_utc(monday))
        self.assertEqual((user.active_streak, current_week(self.session, user, monday).goal_awarded), (1, True))

    def test_failed_commit_rolls_back_workout_and_progress(self):
        """Roll back both the workout and its weekly credit on failure."""
        user = self.user(local("2026-10-26"), goal=1, streak=2)
        with patch.object(self.session, "commit", side_effect=RuntimeError("test failure")):
            with self.assertRaisesRegex(RuntimeError, "test failure"):
                logWorkout.mutate.__wrapped__(None, None, user_id=user.id, facility_id=1)
        self.assertEqual(self.session.query(Workout).count(), 0)
        self.assertEqual(
            (user.active_streak, current_week(self.session, user, self.clock.now()).checked_in_days), (2, 0)
        )
