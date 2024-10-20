import logging
from datetime import datetime
from firebase_admin import messaging
from src.database import db_session
from src.models.workout_reminder import WorkoutReminder
from src.models.user import User
from src.models.user import DayOfWeekEnum  # Ensure the DayOfWeekEnum is imported

def send_capacity_reminder(topic_name, facility_id, current_percent):
    """
    Send a reminder notification to the user.

    Parameters:
        - `topic_name`: The topic to send the notification to.
        - `facility_id`: The gym facility ID.
        - `current_percent`: The current capacity percentage.
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title="Gym Capacity Update",
            body=f"The capacity for gym {facility_id} is now at {current_percent * 100:.1f}%.",
        ),
        topic=topic_name,
    )

    try:
        response = messaging.send(message)
        logging.info(f"Message sent to {topic_name}: {response}")
    except Exception as e:
        logging.error(f"Error sending message to {topic_name}: {e}")


def send_workout_reminders():
    """
    Check for scheduled workout reminders and send notifications to users
    whose reminders match the current day and time.
    """
    current_time = datetime.now().time()
    
    # Get the current weekday name
    current_day_name = datetime.now().strftime("%A")

    # Query for workout reminders that match the current day
    reminders = (
        db_session.query(WorkoutReminder)
        .join(User)  # Fetch both the reminder and the user in a single query
        .filter(
            WorkoutReminder.reminder_time == current_time,
            WorkoutReminder.days_of_week.contains([DayOfWeekEnum[current_day_name.upper()]])
        )
        .all()
    )

    for reminder in reminders:
        user = reminder.user

        if user and user.fcm_token:
            # Prepare the notification message
            message = messaging.Message(
                notification=messaging.Notification(
                    title="Workout Reminder",
                    body="It's time to workout! Don't forget to hit the gym today!"
                ),
                token=user.fcm_token  # Use the FCM token for the user
            )

            try:
                # Send the message
                response = messaging.send(message)
                logging.info(f'Successfully sent message to user ID {user.id}: {response}')
            except Exception as e:
                logging.error(f'Error sending message to user ID {user.id}: {e}')
        else:
            logging.warning(f'No FCM token found for user ID {user.id}. Reminder not sent.')
