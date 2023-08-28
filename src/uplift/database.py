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
  Base.metadata.create_all(bind=engine)
  def init_db():
    # import all modules that might define models so they will be registered properly
    # on metadata - otherwise import them first before calling init_db()
    from models.gym import Gym, GymTime
    from models.daytime import DayTime
    from models.activity import Activity, Amenity, ActivityPrice
    from models.price import Price
    from models.facility import Facility, FacilityTime, Equipment, FacilityPrice

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    gym_1 = Gym(name='Helen Newman', description='Something',
                location='North', image_url='something')
    db_session.add(gym_1)
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

    price_1 = Price(name="price1", cost=20, one_time=False, image_url="none")
    db_session.add(price_1)
    db_session.commit()

    price_2 = Price(name="price2", cost=40, one_time=True, image_url="n/a")
    db_session.add(price_2)
    db_session.commit()

    price_3=Price(name="price3", cost=50, one_time=False, image_url="none")
    price_4=Price(name="price4", cost=15, one_time=False, image_url="n/a")
    db_session.add(price_3)
    db_session.add(price_4)
    db_session.commit()
    
    activityprice_1 = ActivityPrice(activity_id=activity_1.id, price_id=price_1.id)
    activityprice_2=ActivityPrice(activity_id=activity_1.id, price_id=price_2.id)
    db_session.add(activityprice_1)
    db_session.add(activityprice_2)
    db_session.commit()


    amenity_1 = Amenity(name="locker", image_url="none", activity_id=activity_1.id)
    db_session.add(amenity_1)
    db_session.commit()
    activity_1.amenities.append(amenity_1)
    db_session.add(activity_1)
    db_session.commit()

    facility_1 = Facility(name="basketball court", image_url="None")
    db_session.add(facility_1)
    db_session.commit()

    facility_2 = Facility(name="beach volleyball court", image_url="N/A")
    db_session.add(facility_2)
    db_session.commit()

    facilitytime_1 = FacilityTime(facility_id=facility_1.id, daytime_id=daytime_1.id)
    db_session.add(facilitytime_1)
    db_session.commit()

    facilityprice_1 = FacilityPrice(facility_id=facility_1.id, price_id=price_3.id)
    facilityprice_2 = FacilityPrice(facility_id=facility_1.id, price_id=price_4.id)
    db_session.add(facilityprice_1)
    db_session.add(facilityprice_2)
    db_session.commit()

    equipment_1 = Equipment(equipment_type="Exercise machine", name="Squat Rack 1", quantity=2, facility_id=facility_1.id, image_url="n/a")
    db_session.add(equipment_1)
    db_session.commit()

    equipment_2 = Equipment(equipment_type="Exercise thingy", name="Dumbbell", quantity=20, facility_id=facility_1.id, image_url="none")
    db_session.add(equipment_2)
    db_session.commit()

    gym_2 = Gym(name="Morrison", description="Nicer",
                location="North", image_url="N/A")
    db_session.add(gym_2)
    daytime_2 = DayTime(day=2, start_time=datetime.datetime.utcnow(
    ), end_time=datetime.datetime.utcnow(), restrictions="A few", special_hours=False)
    db_session.add(daytime_2)
    db_session.commit()

    facilitytime_2 = FacilityTime(facility_id=facility_2.id, daytime_id=daytime_2.id)
    db_session.add(facilitytime_2)
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
    # morrison,
    teagle_up,
    teagle_down
  ]

  for gym in gyms:
    db_session.merge(gym)

def create_activities_table():
  from models.activity import Activity, Amenity
  from models.daytime import DayTime

  basketball = Activity(name = "Basketball",
    details="details",
    image_url="None"
  )

  beach_volleyball = Activity(
    name="Beach Volleyball", 
    details="details", 
    image_url="N/A"
  )

  activities = [
    basketball,
    beach_volleyball
  ]

  for act in activities:
    db_session.merge(act)




