import sys
import os
import shutil
import datetime as dt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.app.dao import post_dao as pd
from src.app.dao import routine_dao as rd
from src.app.dao import social_media_dao as smd
from src.app.utils import db_utils

def setup_dbs():
  print('Setting up databases...')
  os.chdir('..')
  os.system('python manage.py db init')
  os.system('python manage.py db migrate')
  os.system('python manage.py db upgrade')
  os.chdir('scripts')
  print('Finished setting up databases...')

def delete_migrations():
  try:
    os.chdir('..')
    shutil.rmtree('migrations')
    os.system('export PGPASSWORD={}; psql --user={} --host={} {} '
              .format(os.environ['DB_PASSWORD'], os.environ['DB_USERNAME'],
                      os.environ['DB_HOST'], os.environ['DB_NAME'])
              + '-c "drop table alembic_version"')
    os.chdir('scripts')
    print('Migrations folder deleted...')

  except OSError:
    os.chdir('scripts')
    print('No migrations folder to delete...')

def init_data():
  # TODO: Set up posts
  print("Adding posts to db...")