from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base

from config import DATABASE_URL
from config import DEBUG

engine = create_engine(DATABASE_URL, echo=DEBUG)

def init_db():
    Base.metadata.create_all(engine)
    print("✅ База данных инициализирована")

def get_session() -> Session:
    return Session(engine)
