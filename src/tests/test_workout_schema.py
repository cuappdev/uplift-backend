"""Goal changes and workout writes preserve transaction/week boundaries."""
from contextlib import ExitStack
from datetime import datetime
from unittest.mock import patch

import sqlalchemy as sa
from graphql import GraphQLError
from src.models.user import User as UserModel
from src.models.workout import Workout
from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.schema import SetWorkoutGoals, logWorkout
from src.tests.workout_test_db import WorkoutDatabaseTest, local
from src.utils.workout_streaks import as_utc, current_week, finalize_due_weeks


class WorkoutSchemaTests(WorkoutDatabaseTest):
    def setUp(self):
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

    def test_goal_change_keeps_this_week_and_applies_next_monday(self):
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

    def test_checkin_waiting_across_rollover_uses_time_after_user_lock(self):
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
            query.return_value.filter.return_value.populate_existing.return_value.with_for_update.return_value.first.side_effect = (
                acquire_after_rollover
            )
            workout = logWorkout.mutate.__wrapped__(None, None, user_id=user.id, facility_id=1, workout_time=sunday)
        self.assertEqual((old_week.checked_in_days, old_week.finalized, old_week.goal_awarded), (0, True, False))
        self.assertEqual(as_utc(workout.workout_time), as_utc(monday))
        self.assertEqual((user.active_streak, current_week(self.session, user, monday).goal_awarded), (1, True))

    def test_failed_commit_rolls_back_workout_and_progress(self):
        user = self.user(local("2026-10-26"), goal=1, streak=2)
        with patch.object(self.session, "commit", side_effect=RuntimeError("test failure")):
            with self.assertRaisesRegex(RuntimeError, "test failure"):
                logWorkout.mutate.__wrapped__(None, None, user_id=user.id, facility_id=1)
        self.assertEqual(self.session.query(Workout).count(), 0)
        self.assertEqual(
            (user.active_streak, current_week(self.session, user, self.clock.now()).checked_in_days), (2, 0)
        )
