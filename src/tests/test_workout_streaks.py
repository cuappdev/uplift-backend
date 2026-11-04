from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier
from unittest.mock import patch

from src.tests.workout_test_db import WorkoutDatabaseTest, local
from src.models.user import User
from src.models.user_workout_week import UserWorkoutWeek
from src.utils.workout_streaks import (
    active_days,
    current_week,
    finalize_due_weeks,
    record_checkin,
    run_weekly_rollover,
)


class WorkoutStreakTests(WorkoutDatabaseTest):
    def test_early_award_once_duplicate_days_and_finalization(self):
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
        user = self.user(local("2026-10-26"), goal=1, streak=4)
        now = local("2026-11-16")
        row = record_checkin(self.session, user, now, now)
        self.assertEqual((user.active_streak, row.goal_awarded), (4, False))
        self.session.commit()
        self.assertEqual(run_weekly_rollover(self.session, now), 1)
        self.assertEqual((user.active_streak, row.goal_awarded), (1, True))
        self.assertEqual(self.session.query(UserWorkoutWeek).filter_by(finalized=True).count(), 3)

    def test_rollover_processes_over_500_users_once(self):
        for index in range(501):
            user = self.user(local("2026-10-26"), goal=1, streak=4, commit=False)
            if index == 0:
                record_checkin(self.session, user, local("2026-10-26"), local("2026-10-26"))
        self.session.commit()
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 501)
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 0)
        self.assertEqual([u.active_streak for u in self.session.query(User).filter(User.active_streak != 0)], [5])

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
                self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 1)
            self.assertEqual(finalize.call_count, 2)
        self.assertEqual((first.active_streak, second.active_streak), (4, 0))
        self.assertFalse(current_week(self.session, first, local("2026-10-26")).finalized)
        self.assertEqual(run_weekly_rollover(self.session, local("2026-11-02")), 1)
        self.assertEqual(first.active_streak, 0)

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
