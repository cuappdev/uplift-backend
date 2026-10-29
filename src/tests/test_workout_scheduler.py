from datetime import datetime, timedelta, timezone
from threading import Event
from unittest import TestCase
from unittest.mock import Mock, patch

from apscheduler.events import EVENT_JOB_ERROR
from flask import Flask
from flask_apscheduler import APScheduler

from src.utils.workout_streaks import WorkoutWeekTrigger, schedule_weekly_rollover


class WorkoutSchedulerTests(TestCase):
    def setUp(self):
        # Pause execution while exercising the real in-memory job store.
        self.scheduler = APScheduler(app=Flask(__name__))
        self.scheduler._scheduler.start(paused=True)
        self.session = Mock()
        schedule_weekly_rollover(self.scheduler, self.session)
        self.job = self.scheduler.get_job("finalize_workout_weeks")

    def tearDown(self):
        self.scheduler.shutdown()

    @patch("src.utils.workout_streaks.run_weekly_rollover")
    def test_weekly_schedule_uses_new_york_and_catches_up_at_startup(self, rollover):
        self.assertLess(abs((self.job.next_run_time - datetime.now(timezone.utc)).total_seconds()), 5)
        self.session.query.return_value.filter.return_value.first.return_value = None
        for start, expected in (
            (datetime(2026, 10, 28, tzinfo=timezone.utc), datetime(2026, 11, 2, 5, tzinfo=timezone.utc)),
            (datetime(2026, 3, 4, tzinfo=timezone.utc), datetime(2026, 3, 9, 4, tzinfo=timezone.utc)),
        ):
            self.assertEqual(self.job.trigger.get_next_fire_time(None, start), expected)
            self.assertEqual(self.job.trigger.get_next_fire_time(start, start), expected)
        self.assertIsNone(self.job.misfire_grace_time)

    @patch("src.utils.workout_streaks.run_weekly_rollover")
    def test_success_without_pending_users_does_not_schedule_retry(self, rollover):
        self.session.query.return_value.filter.return_value.first.return_value = None
        self.job.func()
        rollover.assert_called_once()
        self.assertIs(self.scheduler.get_job("finalize_workout_weeks"), self.job)
        self.assertIsNone(self.scheduler.get_job("retry_workout_weeks"))
        self.session.remove.assert_called_once()

    @patch("src.utils.workout_streaks.run_weekly_rollover")
    def test_unfinished_users_schedule_one_delayed_retry(self, rollover):
        self.session.query.return_value.filter.return_value.first.return_value = (1,)
        self.job.func()
        retry = self.scheduler.get_job("retry_workout_weeks")
        delay = (retry.trigger.run_date - datetime.now(timezone.utc)).total_seconds()
        self.assertTrue(295 <= delay <= 305)
        self.assertIs(retry.func, self.job.func)

    @patch("src.utils.workout_streaks.run_weekly_rollover", side_effect=RuntimeError("outage"))
    def test_database_failure_schedules_retry_and_cleans_up(self, rollover):
        with self.assertLogs("src.utils.workout_streaks", level="ERROR"):
            self.job.func()
        self.session.rollback.assert_called_once()
        self.session.remove.assert_called_once()
        retry = self.scheduler.get_job("retry_workout_weeks")
        self.assertTrue(295 <= (retry.trigger.run_date - datetime.now(timezone.utc)).total_seconds() <= 305)

    @patch("src.utils.workout_streaks.run_weekly_rollover")
    def test_cleanup_failure_still_schedules_retry(self, rollover):
        self.session.query.return_value.filter.return_value.first.return_value = None
        self.session.remove.side_effect = RuntimeError("cleanup failure")
        with self.assertLogs("src.utils.workout_streaks", level="ERROR"):
            self.job.func()
        retry = self.scheduler.get_job("retry_workout_weeks")
        self.assertTrue(295 <= (retry.trigger.run_date - datetime.now(timezone.utc)).total_seconds() <= 305)

    @patch("src.utils.workout_streaks.run_weekly_rollover", side_effect=RuntimeError("outage"))
    def test_rollback_failure_still_cleans_up_and_schedules_retry(self, rollover):
        self.session.rollback.side_effect = RuntimeError("rollback failure")
        with self.assertLogs("src.utils.workout_streaks", level="ERROR"):
            with self.assertRaisesRegex(RuntimeError, "rollback failure"):
                self.job.func()
        self.session.remove.assert_called_once()
        retry = self.scheduler.get_job("retry_workout_weeks")
        self.assertTrue(295 <= (retry.trigger.run_date - datetime.now(timezone.utc)).total_seconds() <= 305)

    @patch("src.utils.workout_streaks.run_weekly_rollover")
    def test_monday_crossed_during_cleanup_is_scheduled_without_skipping(self, rollover):
        # Advance the clock during cleanup, after the last due-week check.
        self.session.query.return_value.filter.return_value.first.return_value = None
        before = datetime(2026, 11, 2, 4, 59, 59, tzinfo=timezone.utc)
        boundary = datetime(2026, 11, 2, 5, 0, tzinfo=timezone.utc)
        with patch("src.utils.workout_streaks.datetime", wraps=datetime) as clock:
            clock.now.return_value = before
            self.session.remove.side_effect = lambda: setattr(clock.now, "return_value", boundary)
            self.job.func()
        next_job = self.scheduler.get_job("retry_workout_weeks")
        self.assertEqual(next_job.trigger.run_date, boundary + timedelta(minutes=5))

    def test_recurring_trigger_advances_each_monday_across_dst(self):
        # DST makes these weeks 167 and 169 hours, rather than a fixed 168.
        trigger = WorkoutWeekTrigger()
        for before, after in (
            (datetime(2026, 3, 2, 5, tzinfo=timezone.utc), datetime(2026, 3, 9, 4, tzinfo=timezone.utc)),
            (datetime(2026, 10, 26, 4, tzinfo=timezone.utc), datetime(2026, 11, 2, 5, tzinfo=timezone.utc)),
        ):
            self.assertEqual(trigger.get_next_fire_time(before, before), after)
            self.assertEqual(trigger.get_next_fire_time(None, before), before)

    @patch("src.utils.workout_streaks.run_weekly_rollover", side_effect=RuntimeError("outage"))
    def test_retry_scheduling_failure_does_not_remove_weekly_job(self, rollover):
        with patch.object(self.scheduler, "add_job", side_effect=RuntimeError("scheduling failure")):
            with self.assertLogs("src.utils.workout_streaks", level="ERROR"):
                with self.assertRaisesRegex(RuntimeError, "scheduling failure"):
                    self.job.func()
        self.assertIs(self.scheduler.get_job("finalize_workout_weeks"), self.job)
        self.assertIsNotNone(self.job.trigger.get_next_fire_time(self.job.next_run_time, datetime.now(timezone.utc)))

    @patch("src.utils.workout_streaks.run_weekly_rollover", side_effect=RuntimeError("outage"))
    def test_executing_failed_job_keeps_its_next_weekly_run(self, rollover):
        # Exercise real dispatch; an error event synchronizes completion.
        finished = Event()
        self.scheduler._scheduler.add_listener(lambda event: finished.set(), EVENT_JOB_ERROR)
        with patch.object(self.scheduler, "add_job", side_effect=RuntimeError("retry scheduling failure")):
            with self.assertLogs(level="ERROR"):
                self.scheduler.resume()
                self.assertTrue(finished.wait(timeout=5), "The real scheduler did not execute the job")
        weekly = self.scheduler.get_job("finalize_workout_weeks")
        self.assertIs(weekly, self.job)
        self.assertGreater(weekly.next_run_time, datetime.now(timezone.utc))
        self.assertEqual(weekly.next_run_time, weekly.trigger.get_next_fire_time(None, datetime.now(timezone.utc)))
