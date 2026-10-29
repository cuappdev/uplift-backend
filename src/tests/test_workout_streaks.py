from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier
from unittest.mock import patch

from src.tests.workout_test_db import WorkoutDatabaseTest
from src.models.user import User
from src.models.user_workout_week import UserWorkoutWeek
from src.utils.workout_streaks import (
    WORKOUT_TIMEZONE, active_days, current_week, finalize_due_weeks,
    initialize_tracking, next_week_start, record_checkin,
    run_weekly_rollover,
)


def local(day, hour=12):
    return datetime.fromisoformat(day).replace(hour=hour, tzinfo=WORKOUT_TIMEZONE)


class WorkoutStreakTests(WorkoutDatabaseTest):
    def test_default_goal_one_awards_first_day(self):
        user = User(net_id="new", name="New")
        self.session.add(user)
        self.session.flush()
        self.assertEqual(user.workout_goal, 1)
        initialize_tracking(self.session, user, local("2026-10-26"))
        record_checkin(self.session, user, local("2026-10-26"), local("2026-10-26"))
        self.assertEqual(user.active_streak, 1)

    def test_early_award_once_duplicate_days_and_finalization(self):
        user = self.user(local("2026-10-26"), streak=4)
        for day in ("2026-10-26", "2026-10-26", "2026-10-27"):
            record_checkin(self.session, user, local(day), local(day))
            self.assertEqual(user.active_streak, 4)
        row = record_checkin(self.session, user, local("2026-10-28"), local("2026-10-28"))
        self.assertEqual((user.active_streak, user.max_streak, active_days(row.checked_in_days)), (5, 5, 3))
        record_checkin(self.session, user, local("2026-10-29"), local("2026-10-29"))
        finalize_due_weeks(self.session, user, local("2026-11-02", 0))
        self.assertEqual(user.active_streak, 5)
        self.assertTrue(row.finalized)

    def test_nonempty_below_goal_keeps_streak(self):
        user = self.user(local("2026-10-26"), streak=4)
        record_checkin(self.session, user, local("2026-10-27"), local("2026-10-27"))
        finalize_due_weeks(self.session, user, local("2026-11-02", 0))
        self.assertEqual(user.active_streak, 4)

    def test_empty_week_resets_without_checkin(self):
        user = self.user(local("2026-10-26"), streak=4)
        finalize_due_weeks(self.session, user, local("2026-11-02", 0))
        self.assertEqual((user.active_streak, user.max_streak), (0, 4))
        self.assertIsNone(user.streak_started_at)

    def test_job_retries_are_idempotent(self):
        user = self.user(local("2026-10-26"), goal=1, streak=2)
        record_checkin(self.session, user, local("2026-10-27"), local("2026-10-27"))
        self.session.commit()
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02", 0)), 1)
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02", 0)), 0)
        self.assertEqual(user.active_streak, 3)

    def test_checkin_never_finalizes_delayed_week(self):
        user = self.user(local("2026-10-26"), goal=1, streak=4)
        old = current_week(self.session, user, local("2026-10-26"))
        new = record_checkin(self.session, user, local("2026-11-02"), local("2026-11-02"))
        self.assertFalse(old.finalized)
        self.assertFalse(new.goal_awarded)
        self.assertEqual(user.active_streak, 4)
        finalize_due_weeks(self.session, user, local("2026-11-02", 13))
        self.assertTrue(old.finalized)
        self.assertTrue(new.goal_awarded)
        self.assertEqual(user.active_streak, 1)

    def test_job_catches_up_empty_weeks(self):
        user = self.user(local("2026-10-26"), goal=1, streak=4)
        record_checkin(self.session, user, local("2026-11-16"), local("2026-11-16"))
        finalize_due_weeks(self.session, user, local("2026-11-16", 13))
        self.assertEqual(user.active_streak, 1)
        self.assertEqual(self.session.query(UserWorkoutWeek).filter_by(finalized=True).count(), 3)

    def test_rollover_batch_limit_leaves_other_users_for_next_run(self):
        first = self.user(local("2026-10-26"), streak=4)
        second = self.user(local("2026-10-26"), streak=7)
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02"), limit=1), 1)
        self.assertEqual((first.active_streak, second.active_streak), (0, 7))
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 1)
        self.assertEqual(second.active_streak, 0)
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 0)

    def test_failed_user_rolls_back_others_continue_and_later_run_retries(self):
        first = self.user(local("2026-10-26"), streak=4)
        second = self.user(local("2026-10-26"), streak=7)
        first_id = first.id
        def fail_after_flush(session, user, now):
            finalize_due_weeks(session, user, now)
            session.flush()
            if user.id == first_id:
                raise RuntimeError("persistent user failure")
        with patch("src.utils.workout_streaks.finalize_due_weeks", side_effect=fail_after_flush) as finalize:
            with self.assertLogs("src.utils.workout_streaks", level="ERROR"):
                self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02"), limit=2), 1)
            self.assertEqual(finalize.call_count, 2)
        self.assertEqual((first.active_streak, second.active_streak), (4, 0))
        self.assertFalse(current_week(self.session, first, local("2026-10-26")).finalized)
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 1)
        self.assertEqual(first.active_streak, 0)

    def test_selection_failure_rolls_back_and_reports_outage(self):
        with patch.object(self.session, "query", side_effect=RuntimeError("database unavailable")) as query, patch.object(self.session, "rollback", wraps=self.session.rollback) as rollback:
            with self.assertRaisesRegex(RuntimeError, "database unavailable"):
                run_weekly_rollover(self.session, local("2026-11-02"))
            query.assert_called_once()
            rollback.assert_called_once()

    def test_failed_attempt_counts_towards_limit(self):
        first = self.user(local("2026-10-26"), streak=4)
        second = self.user(local("2026-10-26"), streak=7)
        with patch("src.utils.workout_streaks.finalize_due_weeks", side_effect=RuntimeError("failure")) as finalize:
            with self.assertLogs("src.utils.workout_streaks", level="ERROR"):
                self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02"), limit=1), 0)
            self.assertEqual(finalize.call_count, 1)
        self.assertEqual((first.active_streak, second.active_streak), (4, 7))

    def test_checkin_awards_after_previous_week_finalized(self):
        user = self.user(local("2026-10-26"), goal=1, streak=4)
        run_weekly_rollover(self.session, local("2026-11-02", 0))
        row = record_checkin(self.session, user, local("2026-11-02"), local("2026-11-02"))
        self.assertTrue(row.goal_awarded)
        self.assertEqual(user.active_streak, 1)

    def test_user_has_no_week_cursor_or_deadline_columns(self):
        self.assertNotIn("workout_week_start", User.__table__.columns)
        self.assertNotIn("next_workout_week_at", User.__table__.columns)

    def test_current_week_fetch_only_queries_week_table(self):
        user = self.user(local("2026-10-26"))
        with patch.object(self.session, "query", wraps=self.session.query) as query:
            current_week(self.session, user, local("2026-10-28"))
        self.assertEqual(query.call_count, 1)
        self.assertIs(query.call_args.args[0], UserWorkoutWeek)

    def test_new_york_timezone_determines_day(self):
        user = self.user(local("2026-10-26"), goal=1)
        timestamp = datetime(2026, 10, 27, 2, tzinfo=timezone.utc)
        row = record_checkin(self.session, user, timestamp, timestamp)
        self.assertEqual(row.checked_in_days, 1)  # UTC Tuesday is local Monday.
        self.assertEqual(user.active_streak, 1)

    def test_future_checkin_rejected_and_past_week_does_not_change_progress(self):
        user = self.user(local("2026-10-26"))
        with self.assertRaises(ValueError):
            record_checkin(self.session, user, local("2026-10-29"), local("2026-10-28"))
        self.assertIsNone(record_checkin(self.session, user, local("2026-10-25"), local("2026-10-28")))
        self.assertEqual(current_week(self.session, user, local("2026-10-28")).checked_in_days, 0)

    def test_new_york_monday_boundary_respects_dst(self):
        self.assertEqual(next_week_start(local("2026-10-28")), datetime(2026, 11, 2, 5, tzinfo=timezone.utc))
        self.assertEqual(next_week_start(local("2026-03-04")), datetime(2026, 3, 9, 4, tzinfo=timezone.utc))

    def test_rollback_restores_progress_and_streak(self):
        user = self.user(local("2026-10-26"), goal=1, streak=2)
        record_checkin(self.session, user, local("2026-10-26"), local("2026-10-26"))
        self.session.flush()
        self.session.rollback()
        self.assertEqual(user.active_streak, 2)
        self.assertEqual(current_week(self.session, user, local("2026-10-26")).checked_in_days, 0)

    def test_concurrent_duplicate_checkins_award_once(self):
        if not self.postgres:
            self.skipTest("PostgreSQL row-lock test")
        user = self.user(local("2026-10-26"), goal=1, streak=2)
        uid, barrier = user.id, Barrier(2)
        def checkin():
            session = self.Session()
            try:
                barrier.wait(timeout=10)
                locked = session.query(User).filter_by(id=uid).with_for_update().one()
                record_checkin(session, locked, local("2026-10-26"), local("2026-10-26"))
                session.commit()
            finally:
                session.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda _: checkin(), range(2)))
        self.session.refresh(user)
        self.assertEqual(user.active_streak, 3)
        self.assertEqual(current_week(self.session, user, local("2026-10-26")).checked_in_days, 1)

    def test_concurrent_rollover_workers_finalize_once(self):
        if not self.postgres:
            self.skipTest("PostgreSQL skip-locked test")
        user = self.user(local("2026-10-26"), streak=5)
        barrier = Barrier(2)
        def rollover():
            session = self.Session()
            try:
                barrier.wait(timeout=10)
                return run_weekly_rollover(session, local("2026-11-02", 0))
            finally:
                session.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            counts = list(pool.map(lambda _: rollover(), range(2)))
        self.assertEqual(sum(counts), 1)
        self.session.refresh(user)
        self.assertEqual(user.active_streak, 0)
