from flask import Flask
from flask_graphql import GraphQLView
from graphene import Schema
from src.database import db_session, init_db
from src.schema import Query
from src.constants import create_gym_table

app = Flask(__name__)
app.debug = True

schema = Schema(query=Query)

app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Create database and fill it with constants
init_db()
create_gym_table()


# Should only be used for dev
if __name__ == "__main__":
<<<<<<< HEAD
    app.run(host="127.0.0.1", port=5000) # For Dev Purposes only (use start_server.sh for release)
=======
    app.run(host="127.0.0.1", port=5000)
>>>>>>> 1c9216f (Update capacity scraper)
