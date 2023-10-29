from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Chat(Base):
    __tablename__ = 'Talks'
    id = Column(String(255), primary_key=True)
    chat = Column(String(255))
    reply = Column(String(255))
    datetime = Column(DateTime, server_default=func.now())

class TChats(Base):
    __tablename__ = 'TChats'
    user_no = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(255))
    name = Column(String(255))
    password = Column(String(255))
    regdate = Column(DateTime, server_default=func.now())