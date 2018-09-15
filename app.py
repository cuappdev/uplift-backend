from datetime import time, datetime
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
      'description': 'helen newman description',
      'times': [
        (0, time(hour=10), time(hour=23, minute=30)),
        (1, time(hour=6), time(hour=23, minute=30))
      ],
      'popular': [
        [0,0,0,0,0,0,0,0,0,0,19,31,32,23,26,43,59,57,51,51,47,34,17,3],
        [0,0,0,0,0,0,15,25,27,22,21,31,47,53,45,34,36,52,70,75,60,35,14,0]
      ]
    }
  },
  'class_details': {
    0: {
      'tags': ['yoga'],
      'name': 'Pilates',
      'description': 'pilates description'
    }
  },
  'classes': {
    0: {
      'instructor': 'person A',
      'gym_id': 0,
      'class_description_id': 0,
      'start_time': datetime(year=2018, month=9, day=10, hour=23, minute=30),
      'end_time': datetime(year=2018, month=9, day=11)
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
                 
