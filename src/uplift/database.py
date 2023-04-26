from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime

ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"

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
  Base.metadata.drop_all(bind=engine)
  Base.metadata.create_all(bind=engine)
  create_gym_table()
  create_activities()
  from classes_scraper import scrape_classes
  scrape_classes(10)


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

def create_gym_hours():
  pass 

def create_activities():
  from models.gym import Gym, GymTime
  from models.daytime import DayTime
  from models.capacity import Capacity
  from models.activity import Activity, Amenity, Price
  
  # THESE DATETIMES ARE PURELY FOR TESTING PURPOSES AND ARE NOT ACCURATE
  gym_1 = Gym.query.filter(Gym.id==1).first()
  daytime_1 = DayTime(day=1, start_time=datetime.datetime.utcnow(
  ), end_time=datetime.datetime.utcnow(), restrictions='None', special_hours=True)
  db_session.add(daytime_1)
  db_session.commit()

  gymtime_1 = GymTime(daytime_id=daytime_1.id, gym_id=gym_1.id)
  db_session.add(gymtime_1)
  db_session.commit()

  activity_1 = Activity(
      name='Volleyball', details='It fun', image_url='None')
  db_session.add(activity_1)
  db_session.commit()

  # adding the gym Helen Newman to the activity Volleyball
  activity_1.gyms.append(gym_1)
  db_session.add(activity_1)
  db_session.commit()

  price_1 = Price(name="price1", cost=20, one_time=False, image_url="none", activity_id=activity_1.id)
  db_session.add(price_1)
  db_session.commit()
  activity_1.prices.append(price_1)
  db_session.add(activity_1)
  db_session.commit()

  price_2 = Price(name="price2", cost=40, one_time=True, image_url="n/a", activity_id = activity_1.id)
  db_session.add(price_2)
  db_session.commit()
  activity_1.prices.append(price_2)
  db_session.add(activity_1)
  db_session.commit()

  amenity_1 = Amenity(name="locker", image_url="none", activity_id=activity_1.id)
  db_session.add(amenity_1)
  db_session.commit()
  activity_1.amenities.append(amenity_1)
  db_session.add(activity_1)
  db_session.commit()

  gym_2 = Gym.query.filter(Gym.id == 2).first()
  daytime_2 = DayTime(day=2, start_time=datetime.datetime.utcnow(
  ), end_time=datetime.datetime.utcnow(), restrictions="A few", special_hours=False)
  db_session.add(daytime_2)
  db_session.commit()

  gymtime_2 = GymTime(daytime_id=daytime_2.id, gym_id=gym_2.id)
  db_session.add(gymtime_2)
  db_session.commit()

  activity_2 = Activity(name="Dancing", details="more fun", image_url="No")
  db_session.add(activity_2)
  db_session.commit()

  activity_2.gyms.append(gym_1)
  activity_2.gyms.append(gym_2)
  db_session.add(activity_2)
  db_session.commit()