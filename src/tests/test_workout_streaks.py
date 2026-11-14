"""Regression coverage for weekly workout accounting and recovery."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier
from unittest.mock import patch

import sqlalchemy as sa
from src.tests.workout_test_db import WorkoutDatabaseTest, local
from src.models.user import User
from src.models.workout import Workout
from src.models.user_workout_week import UserWorkoutWeek
from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.utils.workout_streaks import active_days, current_week, finalize_due_weeks, record_checkin, run_weekly_rollover


class WorkoutStreakTests(WorkoutDatabaseTest):
    """Check calendar-week awards, recovery, and concurrent writes."""

    def test_early_award_once_duplicate_days_and_finalization(self):
        """Award once per week and count duplicate local days only once."""
        user = self.user(local("2026-10-26"), streak=4)
        for day in ("2026-10-26", "2026-10-26", "2026-10-27"):
            timestamp = datetime(2026, 10, 27, 2, tzinfo=timezone.utc) if day == "2026-10-26" else local(day)
            record_checkin(self.session, user, timestamp, timestamp)
            self.assertEqual(user.active_streak, 4)
        row = record_checkin(self.session, user, local("2026-10-28"), local("2026-10-28"))
        self.assertEqual((user.active_streak, user.max_streak, active_days(row.checked_in_days)), (5, 5, 3))
        record_checkin(self.session, user, local("2026-10-29"), local("2026-10-29"))
        finalize_due_weeks(self.session, user, local("2026-11-02", 0))
        self.assertEqual(user.active_streak, 5)
        self.assertTrue(row.finalized)

    def test_partial_and_empty_weeks(self):
        """Preserve partial-week credit and reset streaks after empty weeks."""
        for days, expected in ((1, 4), (0, 0)):
            with self.subTest(days=days):
                user = self.user(local("2026-10-26"), streak=4)
                if days:
                    record_checkin(self.session, user, local("2026-10-27"), local("2026-10-27"))
                finalize_due_weeks(self.session, user, local("2026-11-02", 0))
                self.assertEqual((user.active_streak, user.max_streak), (expected, 4))
                if not days:
                    self.assertIsNone(user.streak_started_at)

    def test_delayed_rollover_catches_up_before_awarding_current_week(self):
        """Reset stale credit before awarding a current week after downtime."""
        user = self.user(local("2026-10-26"), goal=1, streak=4)
        now = local("2026-11-16")
        row = record_checkin(self.session, user, now, now)
        self.assertEqual((user.active_streak, row.goal_awarded), (4, False))
        self.session.commit()
        self.assertEqual(run_weekly_rollover(self.session, now), 1)
        self.assertEqual((user.active_streak, row.goal_awarded), (1, True))
        self.assertEqual(self.session.query(UserWorkoutWeek).filter_by(finalized=True).count(), 1)

    def test_inactive_accounts_remain_sparse_and_return_without_backfill(self):
        """Skip dormant years and resume tracking with one new current row."""
        user = self.user(local("2026-10-26"), goal=1, streak=4)
        self.session.commit()
        now = local("2036-11-03")
        self.assertEqual(run_weekly_rollover(self.session, now), 1)
        self.assertEqual(run_weekly_rollover(self.session, now), 0)
        self.assertEqual(self.session.query(UserWorkoutWeek).count(), 1)
        self.assertIsNone(current_week(self.session, user, now))
        self.assertEqual((user.active_streak, user.max_streak), (0, 4))
        row = record_checkin(self.session, user, now, now)
        self.assertEqual((row.goal_awarded, user.active_streak, user.max_streak), (True, 1, 4))
        self.assertEqual(self.session.query(UserWorkoutWeek).count(), 2)

    def test_missing_tracking_initializes_fresh_account(self):
        """Recover a fresh account's first check-in atomically."""
        user = self.user(local("2026-10-26"), goal=1)
        self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).delete()
        self.session.commit()
        now = local("2026-11-02")
        row = record_checkin(self.session, user, now, now)
        self.assertEqual((row.checked_in_days, row.goal_awarded, user.active_streak), (1, True, 1))

    def test_missing_legacy_baseline_preserves_display_and_cutover_credit(self):
        """Restore history once and avoid awarding overlapping cutover credit."""
        legacy = self.user(local("2026-10-26"), goal=3, streak=9)
        self.session.query(UserWorkoutWeek).filter_by(user_id=legacy.id).delete()
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        self.session.add_all(
            Workout(user_id=legacy.id, facility_id=1, workout_time=local(day))
            for day in ("2026-10-30", "2026-10-31", "2026-11-01", "2026-11-02")
        )
        self.session.commit()
        now = local("2026-11-04")
        row = record_checkin(self.session, legacy, now, now)
        # Legacy resolvers displayed 1, despite stale persisted counters of 9.
        self.assertEqual((legacy.active_streak, legacy.max_streak, legacy.streak_started_at), (1, 1, None))
        self.assertEqual((row.checked_in_days, row.goal_awarded), (5, True))
        self.assertEqual(self.session.query(UserWorkoutGoalHistory).filter_by(user_id=legacy.id).count(), 1)
        self.session.commit()
        # Ordinary writes must neither rescan history nor recompute baseline.
        with patch("src.utils.workout_streak_backfill.legacy_streaks", side_effect=AssertionError("repeat backfill")):
            record_checkin(self.session, legacy, local("2026-11-05"), local("2026-11-05"))
            finalize_due_weeks(self.session, legacy, local("2026-11-09"))
        self.assertEqual((legacy.active_streak, legacy.max_streak), (1, 1))
        self.assertTrue(row.finalized)

    def test_missing_legacy_baseline_leaves_uncredited_calendar_goal_awardable(self):
        """A goal decrease must not suppress calendar credit absent from legacy display."""
        user = self.user(local("2026-11-02"), goal=3)
        self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).delete()
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        self.session.add_all(
            [
                UserWorkoutGoalHistory(user_id=user.id, workout_goal=5, effective_at=local("2026-10-01")),
                UserWorkoutGoalHistory(user_id=user.id, workout_goal=3, effective_at=local("2026-11-02", 0)),
                Workout(user_id=user.id, facility_id=1, workout_time=local("2026-11-02")),
                Workout(user_id=user.id, facility_id=1, workout_time=local("2026-11-03")),
            ]
        )
        self.session.commit()
        now = local("2026-11-04")
        row = record_checkin(self.session, user, now, now)
        self.assertEqual((row.workout_goal, row.checked_in_days, row.goal_awarded), (3, 7, True))
        self.assertEqual((user.active_streak, user.max_streak), (1, 1))
        self.session.rollback()
        # Restoring the baseline and awarding its first check-in are atomic.
        self.assertEqual(self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).count(), 0)
        row = record_checkin(self.session, user, now, now)
        self.assertEqual((row.goal_awarded, user.active_streak), (True, 1))

    def test_missing_legacy_baseline_without_current_activity_can_earn_new_credit(self):
        """Prior-week legacy credit leaves a disjoint new calendar week eligible."""
        user = self.user(local("2026-10-26"), goal=1)
        self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).delete()
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        self.session.add_all(
            [
                UserWorkoutGoalHistory(user_id=user.id, workout_goal=1, effective_at=local("2026-10-01")),
                Workout(user_id=user.id, facility_id=1, workout_time=local("2026-11-01")),
            ]
        )
        self.session.commit()
        now = local("2026-11-04")
        row = record_checkin(self.session, user, now, now)
        self.assertEqual((row.checked_in_days, row.goal_awarded, user.active_streak), (4, True, 2))
        self.assertEqual(user.max_streak, 2)
        self.assertEqual(user.streak_started_at, local("2026-11-01", 0).astimezone(timezone.utc))

    def test_return_after_finalized_history_resets_unrecorded_empty_gap(self):
        """Reset stale credit when a returning user has no pending rows."""
        user = self.user(local("2026-10-26"), goal=1, streak=4)
        previous = current_week(self.session, user, local("2026-10-26"))
        previous.checked_in_days, previous.goal_awarded, previous.finalized = 1, True, True
        self.session.commit()
        now = local("2026-11-16")
        row = record_checkin(self.session, user, now, now)
        self.assertEqual((user.active_streak, user.max_streak, row.goal_awarded), (1, 4, True))
        self.assertEqual(self.session.query(UserWorkoutWeek).count(), 2)

    def test_rollover_processes_over_500_users_once(self):
        """Process all due users without a fixed batch limit or repeat work."""
        for index in range(501):
            user = self.user(local("2026-10-26"), goal=1, streak=4, commit=False)
            if index == 0:
                record_checkin(self.session, user, local("2026-10-26"), local("2026-10-26"))
        self.session.commit()
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 501)
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 0)
        self.assertEqual([u.active_streak for u in self.session.query(User).filter(User.active_streak != 0)], [5])

    def test_failed_user_rolls_back_others_continue_and_later_run_retries(self):
        """Isolate one failed user while preserving successful rollover work."""
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
                self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 1)
            self.assertEqual(finalize.call_count, 2)
        self.assertEqual((first.active_streak, second.active_streak), (4, 0))
        self.assertFalse(current_week(self.session, first, local("2026-10-26")).finalized)
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 1)
        self.assertEqual(first.active_streak, 0)

    def test_concurrent_duplicate_checkins_award_once(self):
        """Serialize duplicate check-ins so concurrent requests award once."""
        if not self.postgres:
            self.skipTest("PostgreSQL row-lock test")
        self.session.execute(sa.text("INSERT INTO facility (id) VALUES (1)"))
        for recover in (False, True):
            with self.subTest(recover=recover):
                user = self.user(local("2026-10-26"), goal=1, streak=2)
                if recover:
                    self.session.query(UserWorkoutWeek).filter_by(user_id=user.id).delete()
                    self.session.add(Workout(user_id=user.id, facility_id=1, workout_time=local("2026-10-26")))
                    self.session.commit()
                uid, barrier = user.id, Barrier(2)

                def checkin():
                    session = self.Session()
                    try:
                        barrier.wait(timeout=10)
                        locked = session.query(User).filter_by(id=uid).with_for_update().one()
                        record_checkin(session, locked, local("2026-10-27"), local("2026-10-27"))
                        session.commit()
                    finally:
                        session.close()

                with ThreadPoolExecutor(max_workers=2) as pool:
                    list(pool.map(lambda _: checkin(), range(2)))
                self.session.refresh(user)
                self.assertEqual(user.active_streak, 1 if recover else 3)
                self.assertEqual(
                    current_week(self.session, user, local("2026-10-27")).checked_in_days, 3 if recover else 2
                )
                if recover:
                    self.assertEqual(self.session.query(UserWorkoutWeek).filter_by(user_id=uid).count(), 1)
                    self.assertEqual(self.session.query(UserWorkoutGoalHistory).filter_by(user_id=uid).count(), 1)

    def test_concurrent_rollover_workers_finalize_once(self):
        """Let concurrent workers finalize each due user only once."""
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
