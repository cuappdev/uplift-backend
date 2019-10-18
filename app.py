from datetime import time, datetime
import json
from flask import Flask
from flask_graphql import GraphQLView
from graphene import Schema
import src.data
from src.app import app
from src.schema import Query

schema = Schema(query=Query)

app.add_url_rule("/", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
