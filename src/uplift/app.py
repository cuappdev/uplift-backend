from database import db_session, init_db
from flask import Flask
from flask_graphql import GraphQLView
from graphene import Schema
from schema import schema, Query
from flask_graphql import GraphQLView

app = Flask(__name__)
app.debug = True

schema = Schema(query=Query)

app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Init gym tables and populate them with basic gym information
init_db()
db_session.commit()

# scrape C2C website for latest capacity
from c2c_scraper import scrape_capacity
scrape_capacity()
db_session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
