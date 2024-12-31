import logging
from datetime import datetime
from firebase_admin import messaging
from src.database import db_session
from src.models.workout_reminder import WorkoutReminder
from src.models.user import User
from src.models.user import DayOfWeekEnum  # Ensure the DayOfWeekEnum is imported

def send_capacity_reminder(topic_name, facility_name, readable_name, current_percent):
    """
    Send a capacity reminder to the user.

    Parameters:
        - `topic_name`: The topic to send the notification to.
        - `facility_id`: The gym facility ID.
        - `current_percent`: The current capacity percentage.
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title="Gym Capacity Update",
            body=f"The capacity for {facility_name} is now below {current_percent}%.",
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
    whose reminders match the current day.
    """
    current_date = datetime.now().date()
    current_day_name = datetime.now().strftime("%A").upper()

    reminders = (
        db_session.query(WorkoutReminder)
        .filter(
            WorkoutReminder.is_active == True,
            WorkoutReminder.days_of_week.contains([DayOfWeekEnum[current_day_name]])
        )
        .all()
    )

    for reminder in reminders:
        if reminder.user and reminder.user.fcm_token:  # Access user directly via relationship
            # Format scheduled time to send in the payload
            scheduled_time = f"{current_date} {reminder.reminder_time}"
            payload = messaging.Message(
                data={
                    "title": "Workout Reminder",
                    "message": "Don't forget to hit the gym today!",
                    "scheduledTime": scheduled_time
                },
                token=reminder.user.fcm_token  # Use the user's FCM token directly
            )

            try:
                response = messaging.send(payload)
                print(f'Successfully sent notification for reminder {reminder.id}, response: {response}')
            except Exception as e:
                print(f'Error sending notification for reminder {reminder.id}: {e}')
        print(f'Invalid user or no FCM token.')

    # current_time = datetime.now().time()
    
    # # Get the current weekday name
    # current_day_name = datetime.now().strftime("%A")

    # # Query for workout reminders that match the current day
    # reminders = (
    #     db_session.query(WorkoutReminder)
    #     .join(User)  # Fetch both the reminder and the user in a single query
    #     .filter(
    #         WorkoutReminder.reminder_time == current_time,
    #         WorkoutReminder.days_of_week.contains([DayOfWeekEnum[current_day_name.upper()]])
    #     )
    #     .all()
    # )

    # for reminder in reminders:
    #     user = reminder.user

    #     if user and user.fcm_token:
    #         # Prepare the notification message
    #         message = messaging.Message(
    #             notification=messaging.Notification(
    #                 title="Workout Reminder",
    #                 body="It's time to workout! Don't forget to hit the gym today!"
    #             ),
    #             token=user.fcm_token  # Use the FCM token for the user
    #         )

    #         try:
    #             # Send the message
    #             response = messaging.send(message)
    #             logging.info(f'Successfully sent message to user ID {user.id}: {response}')
    #         except Exception as e:
    #             logging.error(f'Error sending message to user ID {user.id}: {e}')
    #     else:
    #         logging.warning(f'No FCM token found for user ID {user.id}. Reminder not sent.')
