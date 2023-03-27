from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime

engine = create_engine("sqlite:///database.sqlite3")
db_session = scoped_session(
  sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules that might define models so they will be registered properly
    # on metadata - otherwise import them first before calling init_db()
    from models.gym import Gym, GymTime
    from models.daytime import DayTime

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create the fixtures - i think you have to get this from the csv files or a web scraper
    gym = Gym(name="Helen Newman", description="Something", location = "somewhere on that road", image_url="Not a clue")  # this could be wrong but check on that
    db_session.add(gym)
    gym_2 = Gym(name="Morrison", description="Kinda small", location = "Toni", image_url = "Again, no clue")
    db_session.add(gym_2)
    db_session.commit()
    # a bunch more info once i figure it out
    daytime = DayTime(day=1, start_time=datetime.datetime.utcnow(), end_time=datetime.datetime.utcnow(), restrictions="Hello", special_hours=False)
    db_session.add(daytime)
    daytime_2 = DayTime(day = 1, start_time=datetime.datetime.utcnow(), end_time=datetime.datetime.utcnow(), restrictions="Nope", special_hours=True)
    db_session.add(daytime_2)
    daytime_3 = DayTime(day=2, start_time=datetime.datetime.utcnow(), end_time=datetime.datetime.utcnow(), restrictions="MAny", special_hours=True)
    db_session.add(daytime_3)
    db_session.commit()

    gymtime = GymTime(daytime_id=daytime.id, gym_id=gym.id)
    gymtime_2 = GymTime(daytime_id=daytime_2.id, gym_id=gym_2.id)
    db_session.add(gymtime)
    db_session.add(gymtime_2)
    gymtime_3 = GymTime(daytime_id=daytime_3.id, gym_id=gym_2.id)
    db_session.add(gymtime_3)

    # committing the data through the session
    db_session.commit()
