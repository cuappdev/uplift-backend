import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import dotenv
dotenv.load_dotenv()

# Get database credentials with logging
db_user = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT", "5432")  # Add default port
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine = create_engine(db_url)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    """
    Initialize database for Uplift.
    """
    logging.info("Initializing database")
    Base.metadata.create_all(bind=engine)
    db_session.commit()
