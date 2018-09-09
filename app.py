from flask import Flask
from flask_graphql import GraphQLView
from graphene import Schema

from schema import Query

app = Flask(__name__)
app.add_url_rule(
  '/graphql',
  view_func=GraphQLView.as_view(
    'graphql',
    schema=Schema(query=Query),
    graphiql=True
  )
)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
                 
