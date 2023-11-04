from flask import Flask, render_template
from flask_graphql import GraphQLView
from graphene import Schema
from graphql.utils import schema_printer
from src.database import db_session, init_db
from src.schema import Query
from src.constants import create_gym_table
from src.scrapers import c2c_scraper, class_scraper, pool_scraper
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import time



app = Flask(__name__)
SCRAPED_PAGES=10
app.debug = True

schema = Schema(query=Query)


@app.route("/")
def index():
    return render_template("index.html")


app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

def scrape():
    print('Scraping...')
    print("Capacities")
    c2c_scraper.scrape_capacity()
    print("Classes")
    class_scraper.scrape_classes(SCRAPED_PAGES)
    print("Pool hours")
    pool_scraper.scrape_pool_hours()
    print("Done scraping")

# Create database and fill it with constants
init_db()
create_gym_table()
scrape()

scheduler = BackgroundScheduler()
scheduler.add_job(func=scrape, trigger="interval", minutes=15)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Create schema.graphql
with open("schema.graphql", "w+") as schema_file:
    schema_file.write(schema_printer.print_schema(schema))
    schema_file.close()

# Should only be used for dev
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)  # For Dev Purposes only (use start_server.sh for release)
