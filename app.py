from datetime import time, datetime
import json
from flask import Flask
from flask_graphql import GraphQLView
from graphene import Schema
from schema import Query

app = Flask(__name__)

schema = Schema(query=Query)
with open('schema.json', 'w') as schema_file:
  json.dump(schema.introspect(), schema_file)

app.add_url_rule(
    '/',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=Schema(query=Query),
        graphiql=True
    )
)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
