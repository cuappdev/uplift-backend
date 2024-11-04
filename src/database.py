import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database credentials with logging
db_user = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT", "25060")  # Add default port

# Verify all required variables are present
if not all([db_user, db_password, db_name, db_host, db_port]):
    raise ValueError(
        "Missing required database configuration. "
        "Please ensure all database environment variables are set."
    )

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
