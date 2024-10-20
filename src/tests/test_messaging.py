import unittest
from datetime import datetime, time
from unittest.mock import patch, MagicMock
from firebase_admin import messaging
from src.utils.messaging import send_capacity_reminder
from src.utils.messaging import send_workout_reminders


class TestCapacityReminderService(unittest.TestCase):
    """
    Test suite for the messaging service functions.
    """

    @patch("firebase_admin.messaging.send")
    def test_send_capacity_reminder(self, mock_send):
        """
        Test procedure for `send_capacity_reminder()`.
        """

        # Mocking the messaging send function
        mock_send.return_value = "mock_message_id"

        # Test data
        facility_id = "Teagle Up"
        current_percent = 0.45  # 45% capacity
        topic_name = f"{facility_id}_50"  # Expected topic

        # Call the send_reminder function
        send_capacity_reminder(topic_name, facility_id, current_percent)

        # Check that the messaging.send function was called with correct parameters
        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]  # Extracting the first positional argument

        # Check message content
        self.assertEqual(
            message.notification.title,
            "Gym Capacity Update"
        )
        self.assertIn(
            f"capacity for gym {facility_id} is now at {current_percent * 100:.1f}%",
            message.notification.body
        )
        self.assertEqual(message.topic, topic_name)


class TestWorkoutReminderService(unittest.TestCase):
    """
    Test suite for the workout reminder sending functionality.
    """

    @patch("src.utils.messaging.db_session")
    @patch("firebase_admin.messaging.send")
    def test_send_workout_reminders(self, mock_send, mock_db_session):
        """
        Test procedure for `send_workout_reminders()`.
        """
        
        # Mocking the current time to match the reminder time
        reminder_time = time(10, 0)  # 10:00 AM
        current_time = reminder_time  # Simulate current time equals reminder time
        current_day = datetime.now().strftime("%A")

        # Mock reminder data
        mock_reminder = MagicMock()
        mock_reminder.user.fcm_token = "mock_fcm_token"
        mock_reminder.reminder_time = reminder_time
        mock_reminder.days_of_week = [current_day]

        # Setup mock query return value
        mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = [mock_reminder]

        # Call the function
        send_workout_reminders()

        # Check that the messaging.send function was called
        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]  # Extracting the first positional argument

        # Check message content
        self.assertEqual(
            message.notification.title,
            "Workout Reminder"
        )
        self.assertEqual(
            message.notification.body,
            "It's time to workout! Don't forget to hit the gym today!"
        )
        self.assertEqual(message.token, "mock_fcm_token")

    @patch("src.utils.messaging.db_session")
    @patch("firebase_admin.messaging.send")
    def test_no_reminders_sent_when_no_reminders(self, mock_send, mock_db_session):
        """
        Test procedure to ensure no reminders are sent if there are no matching reminders.
        """

        # Setup mock query to return an empty list
        mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = []

        # Call the function
        send_workout_reminders()

        # Check that the messaging.send function was not called
        mock_send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
