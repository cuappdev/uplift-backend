import os
from flask import Blueprint, Flask, render_template, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from src import config

# Configure Flask app
app = Flask(__name__, static_url_path='/static')
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Database
db = SQLAlchemy(app)

# Import + Register Blueprints
blueprint = Blueprint('controllers', __name__, url_prefix='/api/v1')

from src.app.controllers._all import controllers
for controller in controllers:
  blueprint.add_url_rule(
      controller.get_path(),
      controller.get_name(),
      controller.response,
      methods=controller.get_methods()
  )

app.register_blueprint(blueprint)