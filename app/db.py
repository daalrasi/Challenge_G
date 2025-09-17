import os
from dotenv import load_dotenv; load_dotenv()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://app_user:app_pass@db:5432/app_db")

engine = create_engine(DATABASE_URL, poolclass=NullPool, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

class Base(DeclarativeBase):
    pass
