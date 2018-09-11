from datetime import time

from flask import Flask
from flask_graphql import GraphQLView
from graphene import Schema

from schema import Query

app = Flask(__name__)

data = {
  'gyms': {
    0: {
      'id': 0,
      'name': 'Helen Newman',
      'times': [
        (0, time(hour=10), time(hour=23, minute=30)),
        (1, time(hour=6), time(hour=23, minute=30))
      ]
    }
  },
  'classes': {
    0: {
      'type': 'yoga',
      'name': 'Pilates',
      'gym_id': 0
    }
  }
}

app.add_url_rule(
  '/',
  view_func=GraphQLView.as_view(
    'graphql',
    schema=Schema(query=Query),
    graphiql=True,
    get_context=(lambda: data)
  )
)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
                 
