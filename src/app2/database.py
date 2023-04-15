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
    from models.activity import Activity

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

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

    gym_2 = Gym(name="Morrison", description="Nicer",
                location="North", image_url="N/A")
    db_session.add(gym_2)
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

    # adding a few capacities
    # capacity_1 = Capacity(gym_id=gym_1.id, current=10,
    #                       maximum=70, last_updated=datetime.datetime.utcnow())
    # capacity_2 = Capacity(gym_id=gym_2.id, current=20,
    #                       maximum=100, last_updated=datetime.datetime.utcnow())
    # db_session.add(capacity_1)
    # db_session.add(capacity_2)
    # db_session.commit()
