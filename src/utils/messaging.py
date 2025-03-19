import logging
from datetime import datetime
from firebase_admin import messaging
from src.database import db_session
from src.models.user import User
from src.models.enums import DayOfWeekEnum  # Ensure the DayOfWeekEnum is imported


def send_capacity_reminder(topic_name, facility_name, current_percent):
    """
    Send a capacity reminder to the user.
    Parameters:
        - `topic_name`: The topic to send the notification to.
        - `facility_name`: The gym facility's name.
        - `current_percent`: The current capacity percentage.
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title="Gym Capacity Update", body=f"The capacity for {facility_name} is now below {current_percent}%."
        ),
        topic=topic_name,
    )

    try:
        response = messaging.send(message)
        logging.info(f"Message sent to {topic_name}: {response}")
    except Exception as e:
        logging.error(f"Error sending message to {topic_name}: {e}")