import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class GeoLoc(Base):
    '''
    Definition of geographical location.
    '''
    __tablename__ = 'geoloc'
    name = Column(String, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    def __repr__(self):
        return "%s at (%f, %f)"%(self.name, self.lat, self.lon)

def __create_session():
    db_engine = create_engine(os.environ["DATABASE_URL"])
    Base.metadata.create_all(db_engine)
    Session = sessionmaker(bind=db_engine, autocommit=True)
    return Session()


Session = __create_session()