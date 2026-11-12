"""Weekly GraphQL reads stay batched and fresh across serial mutations."""

from datetime import datetime, timezone
from unittest.mock import patch

import graphene
from sqlalchemy import event

from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.models.user_workout_week import UserWorkoutWeek
from src.schema import User
from src.tests.workout_test_db import WorkoutDatabaseTest, local
from src.utils.workout_streaks import current_week


class WorkoutProgressLoaderTests(WorkoutDatabaseTest):
    """Exercise batching through GraphQL execution rather than loader internals."""

    def execute(self, users, document, now=None, mutation=None):
        """Run a small schema and collect only weekly-progress SELECTs."""

        class Query(graphene.ObjectType):
            people = graphene.List(User)

            def resolve_people(root, info):
                return users

        statements = []

        def count_progress_queries(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith("SELECT") and any(
                name in statement for name in ("user_workout_week", "user_workout_goal_history")
            ):
                statements.append(statement)

        event.listen(self.engine, "before_cursor_execute", count_progress_queries)
        try:
            with patch("src.schema.db_session", self.session), patch("src.schema.datetime", wraps=datetime) as clock:
                clock.now.return_value = now or local("2026-10-28")
                result = graphene.Schema(query=Query, mutation=mutation).execute(document, context_value={})
        finally:
            event.remove(self.engine, "before_cursor_execute", count_progress_queries)
        self.assertIsNone(result.errors, result.errors)
        return result.data, statements

    def test_user_list_batches_both_fields_and_dormant_goal_history(self):
        """Keep query count constant for stored and unmaterialized weekly rows."""
        now = local("2026-10-28")
        users = [self.user(now, goal=5) for _ in range(12)]
        for index, user in enumerate(users):
            row = current_week(self.session, user, now)
            if index % 2:
                self.session.delete(row)
                self.session.add_all(
                    [
                        UserWorkoutGoalHistory(user_id=user.id, workout_goal=2, effective_at=local("2026-10-19", 0)),
                        UserWorkoutGoalHistory(user_id=user.id, workout_goal=3, effective_at=local("2026-10-26", 0)),
                        UserWorkoutGoalHistory(user_id=user.id, workout_goal=5, effective_at=local("2026-11-02", 0)),
                    ]
                )
            else:
                row.checked_in_days = 5
        self.session.commit()
        data, statements = self.execute(users, "{ people { currentWeekActiveDays currentWeekGoal } }")
        self.assertEqual(
            data["people"],
            [
                {"currentWeekActiveDays": 0 if index % 2 else 2, "currentWeekGoal": 3 if index % 2 else 5}
                for index in range(12)
            ],
        )
        self.assertEqual(len(statements), 2, statements)
        self.assertEqual(self.session.query(UserWorkoutWeek).count(), 6)

    def test_serial_mutation_responses_do_not_reuse_progress(self):
        """Read fresh scalar values even when loaded ORM rows remain stale."""
        now = local("2026-10-28")
        user = self.user(now)
        row = current_week(self.session, user, now)
        session = self.session

        class Mutation(graphene.ObjectType):
            checkin = graphene.Field(User, mask=graphene.Int(required=True))

            def resolve_checkin(root, info, mask):
                session.execute(
                    UserWorkoutWeek.__table__.update()
                    .where(UserWorkoutWeek.user_id == user.id)
                    .values(checked_in_days=mask)
                )
                return user

        data, statements = self.execute(
            [user],
            """mutation {
            first: checkin(mask: 1) { currentWeekActiveDays currentWeekGoal }
            second: checkin(mask: 3) { currentWeekActiveDays currentWeekGoal }
        }""",
            mutation=Mutation,
        )
        self.assertEqual(
            data,
            {
                "first": {"currentWeekActiveDays": 1, "currentWeekGoal": 3},
                "second": {"currentWeekActiveDays": 2, "currentWeekGoal": 3},
            },
        )
        self.assertEqual(len(statements), 2, statements)
        self.assertEqual(row.checked_in_days, 0)

    def test_new_york_week_boundary_and_default_goal_without_rows(self):
        """Use local calendar weeks across the end of daylight saving time."""
        user = self.user(local("2026-11-01"), goal=2)
        row = current_week(self.session, user, local("2026-11-01"))
        row.checked_in_days = 64
        self.session.commit()
        document = "{ people { currentWeekActiveDays currentWeekGoal } }"
        sunday, _ = self.execute([user], document, datetime(2026, 11, 2, 4, 59, tzinfo=timezone.utc))
        monday, statements = self.execute([user], document, datetime(2026, 11, 2, 5, 0, tzinfo=timezone.utc))
        self.assertEqual(sunday["people"], [{"currentWeekActiveDays": 1, "currentWeekGoal": 2}])
        self.assertEqual(monday["people"], [{"currentWeekActiveDays": 0, "currentWeekGoal": 2}])
        self.assertEqual(len(statements), 2)
