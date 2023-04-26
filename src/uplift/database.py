from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime
from constants import ASSET_BASE_URL, PAGE_LIMIT

engine = create_engine("sqlite:///database.sqlite3")
db_session = scoped_session(
  sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
  """
  Initialize database for uplift.
  """
  # import all modules that might define models so they will be registered properly
  # on metadata - otherwise import them first before calling init_db()
  Base.metadata.create_all(bind=engine)
  create_gym_table()
  from classes_scraper import scrape_classes
  scrape_classes(PAGE_LIMIT)


"""
Initialize basic information for all five fitness centers
(Helen Newman...Teagle Down) with location, hours, images. 
"""
def create_gym_table():
  # import all modules that might define models so they will be registered properly
  # on metadata - otherwise import them first before calling init_db()
  from models.gym import Gym, GymTime
  from models.daytime import DayTime
  from models.capacity import Capacity

  helen_newman = Gym(
    id=1,
    name='Helen Newman',
    description='description',
    location='123 Cradit Farm Road',
    latitude=42.454342,
    longitude=-76.473618,
    image_url=ASSET_BASE_URL + 'gyms/helen-newman.jpg'
  )

  toni_morrison = Gym(
    id=2,
    name = 'Toni Morrison',
    description='description',
    location='18 Sisson Place',
    latitude=0.00,
    longitude=0.00,
    image_url = ASSET_BASE_URL + 'gyms/toni-morrison-outside-min.jpeg'
  )

  noyes = Gym(
    id=3,
    name='Noyes',
    description='description',
    location='306 West Avenue',
    latitude=0.0,
    longitude=0.0,
    image_url=ASSET_BASE_URL + 'gyms/noyes.jpg'
  )

  teagle_up = Gym(
    id=4,
    name='Teagle Up',
    description='description',
    location='512 Campus Road',
    latitude=0.0,
    longitude=0.0,
    image_url=ASSET_BASE_URL + 'gyms/teagle.jpg'
  )

  teagle_down = Gym(
    id=5,
    name='Teagle Down',
    description='description',
    location='512 Campus Road',
    latitude=0.0,
    longitude=0.0,
    image_url=ASSET_BASE_URL + 'gyms/teagle.jpg'
  )

  gyms = [
    helen_newman, 
    noyes, 
    toni_morrison,
    teagle_up,
    teagle_down
  ]

  for gym in gyms:
    if Gym.query.filter_by(id = gym.id):
      db_session.merge(gym)
    else: 
      db_session.add(gym)
  
  db_session.commit()
