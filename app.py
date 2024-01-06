import logging, schedule, time
from flask import Flask, render_template
from flask_graphql import GraphQLView
from graphene import Schema
from graphql.utils import schema_printer
from src.database import db_session, init_db
from src.models.capacity import Capacity
from src.models.openhours import OpenHours
from src.schema import Query
from src.scrapers.capacities_scraper import fetch_capacities
from src.scrapers.reg_hours_scraper import fetch_reg_building, fetch_reg_facility
from src.scrapers.sp_hours_scraper import fetch_sp_facility
from src.utils.utils import create_gym_table


app = Flask(__name__)
app.debug = True

schema = Schema(query=Query)


@app.route("/")
def index():
    return render_template("index.html")


app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def scrape_sheets():
    logging.info("Scraping from sheets...")

    # Fetch Hours
    fetch_reg_facility()
    fetch_reg_building()
    fetch_sp_facility()

    # Fetch Capacities
    fetch_capacities()


# Create database and fill it with data
init_db()
create_gym_table()
scrape_sheets()

# Create schema.graphql
with open("schema.graphql", "w+") as schema_file:
    schema_file.write(schema_printer.print_schema(schema))
    schema_file.close()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

# Schedule the scraping to run every 10 minutes
schedule.every(10).minutes.do(scrape_sheets)
while True:
    schedule.run_pending()
    time.sleep(60)
