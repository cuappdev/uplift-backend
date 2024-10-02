import logging
import sentry_sdk
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_graphql import GraphQLView
from graphene import Schema
from graphql.utils import schema_printer
from src.database import db_session, init_db
from src.schema import Query, Mutation
from src.scrapers.capacities_scraper import fetch_capacities
from src.scrapers.reg_hours_scraper import fetch_reg_building, fetch_reg_facility
from src.scrapers.scraper_helpers import clean_past_hours
from src.scrapers.sp_hours_scraper import fetch_sp_facility
from src.scrapers.equipment_scraper import scrape_equipment
from src.scrapers.class_scraper import fetch_classes
from src.scrapers.activities_scraper import fetch_activity
from src.utils.utils import create_gym_table
from src.models.openhours import OpenHours
from flasgger import Swagger


sentry_sdk.init(
    dsn="https://2a96f65cca45d8a7c3ffc3b878d4346b@o4507365244010496.ingest.us.sentry.io/4507850536386560",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = Flask(__name__)
app.debug = True
schema = Schema(query=Query, mutation=Mutation)
swagger = Swagger(app)

# Scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Logging
logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")


@app.route("/")
def index():
    return render_template("index.html")


app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# Scrape hours every 15 minutes
@scheduler.task("interval", id="scrape_hours", seconds=900)
def scrape_hours():
    logging.info("Scraping hours from sheets...")

    # Clear hours
    db_session.query(OpenHours).delete()

    fetch_reg_facility()
    fetch_reg_building()
    fetch_sp_facility()
    clean_past_hours()


# Scrape capacities every 10 minutes
@scheduler.task("interval", id="scrape_capacities", seconds=600)
def scrape_capacities():
    logging.info("Scraping capacities from C2C...")

    fetch_capacities()


# Scrape classes every hour
@scheduler.task("interval", id="scrape_classes", seconds=3600)
def scrape_classes():
    logging.info("Scraping classes from group-fitness-classes...")

    fetch_classes(10)


# Create database and fill it with data
init_db()
create_gym_table()
scrape_classes()
scrape_hours()
scrape_capacities()
scrape_equipment()

logging.info("Scraping activities from sheets...")
fetch_activity()
# Create schema.graphql
with open("schema.graphql", "w+") as schema_file:
    schema_file.write(schema_printer.print_schema(schema))
    schema_file.close()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)