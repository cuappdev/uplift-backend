from flask import Flask
from flask_graphql import GraphQLView
from graphene import Schema
from graphql.utils import schema_printer
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

# Create schema.graphql
with open("schema.graphql", "w+") as schema_file:
    schema_file.write(schema_printer.print_schema(schema))
    schema_file.close()

# Should only be used for dev
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000) # For Dev Purposes only (use start_server.sh for release)

