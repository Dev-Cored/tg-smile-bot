#Импорт библиотек
from sqlalchemy.orm import registry, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_session
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

#Инициализация базы данных
engine = create_engine("sqlite:///database.db", echo=True)
Base = declarative_base()

async_engine = create_async_engine("sqlite+aiosqlite:///database.db", echo=True)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
#Структура базы данных
class User(Base):
    __tablename__ = "users"
    id = Column(Integer,Identity(), primary_key=True)
    user_id = Column(Integer, Identity(), nullable=False)
    username = Column(Text)
    user_fullname = Column(Text)
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    daily_photo_sent = Column(Integer, default=0)

class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer,Identity(), primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Text, nullable=False)
    file = Column(BLOB)
    emotion = Column(Text)
    date = Column(TIMESTAMP)

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer,Identity(), primary_key=True)
    group_id = Column(Integer, nullable=False)
    today_emoji = Column(Text)

class SentMathce(Base):
    __tablename__ = "sent_mathces"
    id = Column(Integer,Identity(), primary_key=True)
    group_id = Column(Integer, nullable=False)
    photos_ids = Column(Text, nullable=False)
    recipients_ids = Column(Text, nullable=False)
    date = Column(TIMESTAMP)


#Функции
def get_session(url='sqlite:///database.db'):
    engine = create_engine(url, echo=True)
    Session = sessionmaker(bind=engine)
    return Session()


async def get_acync_session():
    return async_session()



def init_db():
    Base.metadata.create_all(engine)



if __name__ == "__main__":
    Base.metadata.create_all(engine)