import logging
from datetime import datetime
from src.utils.constants import SERVICE_ACCOUNT_PATH, JWT_SECRET_KEY
import os
import sentry_sdk
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_graphql import GraphQLView
# from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from graphene import Schema
from graphql.utils import schema_printer
from src.database import db_session, init_db
from src.database import Base as db
from src.database import db_url, db_user, db_password, db_name, db_host, db_port
from src.models.openhours import OpenHours
from flask_migrate import Migrate
from src.schema import Query, Mutation
from flasgger import Swagger
from flask_graphql import GraphQLView

# Check if we're in migration mode with error handling
try:
    FLASK_MIGRATE = os.getenv('FLASK_MIGRATE', 'false').lower() == 'true'
except Exception as e:
    logging.warning(f"Error reading FLASK_MIGRATE environment variable: {e}. Defaulting to false.")
    FLASK_MIGRATE = False

# Only import scraping-related modules if not in migration mode
if not FLASK_MIGRATE:
    from flask_apscheduler import APScheduler
    from src.scrapers.capacities_scraper import fetch_capacities, update_hourly_capacity
    from src.scrapers.reg_hours_scraper import fetch_reg_building, fetch_reg_facility
    from src.scrapers.scraper_helpers import clean_past_hours
    from src.scrapers.sp_hours_scraper import fetch_sp_facility
    from src.scrapers.equipment_scraper import scrape_equipment
    from src.scrapers.class_scraper import fetch_classes
    from src.scrapers.activities_scraper import fetch_activity
    from src.utils.utils import create_gym_table
from src.utils.messaging import send_workout_reminders
from src.models.openhours import OpenHours
from src.models.workout_reminder import WorkoutReminder
from src.models.user import User as UserModel
from src.models.enums import DayOfWeekEnum
import firebase_admin
from firebase_admin import credentials, messaging


def initialize_firebase():
    if not firebase_admin._apps:
        if SERVICE_ACCOUNT_PATH:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_app = firebase_admin.initialize_app(cred)
        else:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_PATH environment variable not set.")
    else:
        firebase_app = firebase_admin.get_app()
    logging.info("Firebase app created...")
    return firebase_app

def send_notification():
    # Replace with your iOS device's FCM registration token
    registration_token = 'fUMWE_YmMU1IryBkt4gXdC:APA91bHlZIlLXOixsPMTu2_8F1u0FqzOzS_GxhvrcOLeNn7DFg-5qaIGEJ2zCpwrJxTk1Jo6_gaGC7LyjrBgfIB3Q6PjcrQqdB7j4rN28TkDKi9DTPneACU'

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

    print("HELLOOO!!!")
    print(reminders)

    for reminder in reminders:
        user = db_session.query(UserModel).filter_by(id=reminder.user_id).first()
        print("HELLOOO")
        print(user.id)
        if user and user.fcm_token:  # Access user directly via relationship
            # Format scheduled time to send in the payload
            scheduled_time = f"{current_date} {reminder.reminder_time}"
            payload = messaging.Message(
                data={
                    "title": "Workout Reminder",
                    "message": "Don't forget to hit the gym today!",
                    "scheduledTime": scheduled_time
                },
                token=user.fcm_token  # Use the user's FCM token directly
            )

            print("HELLOOO!!!")
            print(payload.data)

            try:
                response = messaging.send(payload)
                print(f'Successfully sent notification for reminder {reminder.id}, response: {response}')
            except Exception as e:
                print(f'Error sending notification for reminder {reminder.id}: {e}')

sentry_sdk.init(
    dsn="https://2a96f65cca45d8a7c3ffc3b878d4346b@o4507365244010496.ingest.us.sentry.io/4507850536386560",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = Flask(__name__)
app.debug = True

# Verify all required variables are present
if not all([db_user, db_password, db_name, db_host, db_port]):
    raise ValueError(
        "Missing required database configuration. "
        "Please ensure all database environment variables are set."
    )

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)
schema = Schema(query=Query, mutation=Mutation)
swagger = Swagger(app)

app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
jwt = JWTManager(app)

def should_run_initial_scrape():
    """
    Check if we should run initial scraping:
    - Not in migration mode
    - Only in the main process (Werkzeug or Gunicorn)
    """
    # If in migration mode, don't run initial scraping
    if FLASK_MIGRATE:
        return False
    # Check if we're in the main process
    werkzeug_var = os.environ.get('WERKZEUG_RUN_MAIN')
    # Logic: if in local, then werkzeug_var exists: so only run when true to prevent double running
    # If in Gunicorn, then werkzeug_var is None, so then it will also run
    return werkzeug_var is None or werkzeug_var == 'true'

# Initialize scheduler only if not in migration mode
if not FLASK_MIGRATE:
    scheduler = APScheduler()
    if should_run_initial_scrape():  # Only start scheduler in main process
        scheduler.init_app(app)
        scheduler.start()

# Logging
logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

firebase_app = initialize_firebase()
send_notification()

@app.route("/")
def index():
    return render_template("index.html")

app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Only define scheduler tasks if not in migration mode
if not FLASK_MIGRATE:
    # Scrape hours every 15 minutes
    @scheduler.task("interval", id="scrape_hours", seconds=900)
    def scrape_hours():
        try:
            logging.info("Scraping hours from sheets...")
            # Clear hours
            db_session.query(OpenHours).delete()
            fetch_reg_facility()
            fetch_reg_building()
            fetch_sp_facility()
            clean_past_hours()
        except Exception as e:
            logging.error(f"Error in scrape_hours: {e}")

    # Scrape capacities every 10 minutes
    @scheduler.task("interval", id="scrape_capacities", seconds=600)
    def scrape_capacities():
        try:
            logging.info("Scraping capacities from C2C...")
            fetch_capacities()
        except Exception as e:
            logging.error(f"Error in scrape_capacities: {e}")

# Scrape classes every hour
@scheduler.task("interval", id="scrape_classes", seconds=3600)
def scrape_classes():
    logging.info("Scraping classes from group-fitness-classes...")


    fetch_classes(10)
    
#Send workout reminders every morning at 9:00 AM
@scheduler.task('cron', id='send_reminders', hour=9, minute=0)
def scheduled_job():
    logging.info("Sending workout reminders...")
    send_workout_reminders()

#Update hourly average capacity every hour
@scheduler.task('cron', id='update_capacity', minute="*")
def scheduled_job():
    current_time = datetime.now()
    current_day = current_time.strftime("%A").upper()
    current_hour = current_time.hour
    
    logging.info(f"Updating hourly average capacity for {current_day}, hour {current_hour}...")
    update_hourly_capacity(current_day, current_hour)

# Create database
init_db()

# Run initial scraping only in main process and not in migration mode
if should_run_initial_scrape():
    logging.info("Running initial scraping...")
    try:
        create_gym_table()
        scrape_classes()
        scrape_hours()
        scrape_capacities()
        scrape_equipment()
        logging.info("Scraping activities from sheets...")
        fetch_activity()
    except Exception as e:
        logging.error(f"Error during initial scraping: {e}")

# Create schema.graphql
with open("schema.graphql", "w+") as schema_file:
    schema_file.write(schema_printer.print_schema(schema))
    schema_file.close()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
