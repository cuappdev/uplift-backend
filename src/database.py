from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


# engine = create_engine("sqlite:///database.sqlite3")
engine = create_engine("sqlite:///test.sqlite3")  # Soley for temp dev testing
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """
    Initialize database for uplift.
    """
    Base.metadata.create_all(bind=engine)
    db_session.commit()
