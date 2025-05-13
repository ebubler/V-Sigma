from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_class import Base

def global_init(db_name):
    engine = create_engine(f"sqlite:///data/{db_name}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def create_session(session_factory):
    return session_factory()