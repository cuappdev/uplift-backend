from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///database.sqlite3")
db_session = scoped_session(
  sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules that might define models so they will be registered properly
    # on metadata - otherwise import them first before calling init_db()
    from models.gym import Gym

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create the fixtures - i think you have to get this from the csv files or a web scraper
    gym = Gym(name="Helen Newman", description="Something",
              image_url="Not a clue")  # this could be wrong but check on that
    db_session.add(gym)
    # a bunch more info once i figure it out

    # committing the data through the session
    db_session.commit()
