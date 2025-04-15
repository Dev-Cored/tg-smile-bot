
from sqlalchemy.orm import registry, declarative_base
from sqlalchemy import (
create_engine,
Column,
Integer,
Text,
ForeignKey,
TIMESTAMP,
BLOB,
Identity
)


engine = create_engine("sqlite:///database.db", echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,Identity(), primary_key=True)
    username = Column(Text)
    daily_photo_sent = Column(Integer, default=0)

class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer,Identity(), primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)