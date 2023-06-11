from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings.base import settings

Base = declarative_base()


engine = create_engine(settings.db.as_engine)
Session = sessionmaker(bind=engine)
session = Session()


def create_all_hook():
    Base.metadata.create_all(engine)


def get_session():
    return session
