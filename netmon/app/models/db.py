import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_URL = os.getenv("DB_URL")

class Base(DeclarativeBase):
    pass

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_engine_and_create():
    Base.metadata.create_all(engine)