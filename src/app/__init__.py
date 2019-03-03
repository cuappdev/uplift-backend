import os
from flask import Blueprint, Flask, render_template, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import config

# Configure Flask app
app = Flask(__name__, static_url_path='/static')
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Database
db = SQLAlchemy(app)

# Import + Register Blueprints
blueprint = Blueprint('controllers', __name__, url_prefix='/api/v1')
