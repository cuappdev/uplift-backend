import logging
from flask import Flask, render_template
from graphene import Schema
from graphql.utils import schema_printer
from src.database import db_session, init_db
from src.database import Base as db
from src.database import db_url, db_user, db_password, db_name, db_host, db_port
from flask_migrate import Migrate
from src.schema import Query, Mutation
from flasgger import Swagger
from flask_graphql import GraphQLView
import sentry_sdk

# Set up logging at module level
logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s",
                    level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

def create_app(run_migrations=False):
    """
    Application factory for Flask app.

    Args:
        run_migrations: If True, configure app for migrations only (no scrapers)

    Returns:
        Configured Flask application
    """
    logger.info("Initializing application")

    # Initialize Sentry
    logger.info("Configuring Sentry")
    sentry_sdk.init(
        dsn="https://2a96f65cca45d8a7c3ffc3b878d4346b@o4507365244010496.ingest.us.sentry.io/4507850536386560",
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

    # Create and configure Flask app
    app = Flask(__name__)
    app.debug = True
    logger.info("Flask app created with debug=%s", app.debug)

    # Verify all required database variables are present
    if not all([db_user, db_password, db_name, db_host, db_port]):
        logger.error("Missing required database configuration variables")
        raise ValueError(
            "Missing required database configuration. "
            "Please ensure all database environment variables are set."
        )

    # Configure database
    logger.info("Configuring database connection to %s:%s/%s", db_host, db_port, db_name)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set up extensions
    logger.info("Setting up Flask extensions")
    migrate = Migrate(app, db)
    schema = Schema(query=Query, mutation=Mutation)
    swagger = Swagger(app)

    # Configure routes
    logger.info("Configuring routes")

    @app.route("/")
    def index():
        return render_template("index.html")

    app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # Initialize database
    logger.info("Initializing database")
    init_db()

    # Create schema.graphql
    logger.info("Generating GraphQL schema file")
    with open("schema.graphql", "w+") as schema_file:
        schema_file.write(schema_printer.print_schema(schema))
        schema_file.close()

    # Configure and run scrapers if not in migration mode
    if not run_migrations:
        logger.info("Setting up scrapers and scheduled tasks")
        setup_scrapers(app)
    else:
        logger.info("Running in migration mode - scrapers disabled")

    logger.info("Application initialization complete")
    return app

def setup_scrapers(app):
    """Set up scrapers and scheduled tasks"""
    # Import scraper-related modules only when needed
    from flask_apscheduler import APScheduler
    from src.scrapers.capacities_scraper import fetch_capacities
    from src.scrapers.reg_hours_scraper import fetch_reg_building, fetch_reg_facility
    from src.scrapers.scraper_helpers import clean_past_hours
    from src.scrapers.sp_hours_scraper import fetch_sp_facility
    from src.scrapers.equipment_scraper import scrape_equipment
    from src.scrapers.class_scraper import fetch_classes
    from src.scrapers.activities_scraper import fetch_activity
    from src.utils.utils import create_gym_table
    from src.models.openhours import OpenHours
    import os

    logger = logging.getLogger(__name__)
    logger.info("Beginning scraper configuration")

    # Initialize scheduler
    scheduler = APScheduler()
    logger.info("APScheduler initialized")

    # Scrape hours every 15 minutes
    @scheduler.task("interval", id="scrape_hours", seconds=900)
    def scrape_hours():
        job = scheduler.get_job('scrape_hours')
        next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job and job.next_run_time else "Unknown"
        logging.info("Running job \"scrape_hours (trigger: interval[0:15:00], next run at: %s EST)\"", next_run)
        try:
            logging.info("Scraping hours from sheets...")
            # Clear hours
            db_session.query(OpenHours).delete()
            fetch_reg_facility()
            fetch_reg_building()
            fetch_sp_facility()
            clean_past_hours()
            logging.info(
                "Job \"scrape_hours (trigger: interval[0:15:00], next run at: %s EST)\" executed successfully", next_run)
        except Exception as e:
            logging.error(f"Error in scrape_hours: {e}")

    # Scrape capacities every 10 minutes
    @scheduler.task("interval", id="scrape_capacities", seconds=600)
    def scrape_capacities():
        job = scheduler.get_job('scrape_capacities')
        next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job and job.next_run_time else "Unknown"
        logging.info("Running job \"scrape_capacities (trigger: interval[0:10:00], next run at: %s EST)\"", next_run)
        try:
            logging.info("Scraping capacities from C2C...")
            fetch_capacities()
            logging.info(
                "Job \"scrape_capacities (trigger: interval[0:10:00], next run at: %s EST)\" executed successfully", next_run)
        except Exception as e:
            logging.error(f"Error in scrape_capacities: {e}")

    # Scrape classes every hour
    @scheduler.task("interval", id="scrape_classes", seconds=3600)
    def scrape_classes():
        job = scheduler.get_job('scrape_classes')
        next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job and job.next_run_time else "Unknown"
        logging.info("Running job \"scrape_classes (trigger: interval[1:00:00], next run at: %s EST)\"", next_run)
        try:
            logging.info("Scraping classes from group-fitness-classes...")
            fetch_classes(10)
            logging.info(
                "Job \"scrape_classes (trigger: interval[1:00:00], next run at: %s EST)\" executed successfully", next_run)
        except Exception as e:
            logging.error(f"Error in scrape_classes: {e}")

    # We're now handling job execution logging within each task function

    # Initialize scheduler
    logger.info("Starting scheduler")
    scheduler.init_app(app)
    scheduler.start()

    # Run initial scraping
    logger.info("Running initial scraping...")
    try:
        create_gym_table()
        logger.info("Gym table created")

        logger.info("Scraping classes from group-fitness-classes...")
        fetch_classes(10)
        logger.info("Initial class scraping complete")

        logger.info("Scraping hours from sheets...")
        db_session.query(OpenHours).delete()
        fetch_reg_facility()
        fetch_reg_building()
        fetch_sp_facility()
        clean_past_hours()
        logger.info("Initial hours scraping complete")

        logger.info("Scraping capacities from C2C...")
        fetch_capacities()
        logger.info("Initial capacities scraping complete")

        logger.info("Scraping equipment...")
        scrape_equipment()
        logger.info("Initial equipment scraping complete")

        logger.info("Scraping activities from sheets...")
        fetch_activity()
        logger.info("Initial activities scraping complete")

        logger.info("All initial scraping completed successfully")
    except Exception as e:
        logger.error(f"Error during initial scraping: {e}")
