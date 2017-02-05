import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Posts(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    PostTypeId = Column(Integer)
    AcceptedAnswerId = Column(Integer)
    ParentId = Column(Integer)
    CreationDate = Column(DateTime)
    Score = Column(Integer)
    OwnerUserId = Column(Integer)
    LastActivityDate = Column(DateTime)
    Tags = Column(String)
    AnswerCount = Column(Integer)

class Users(Base):
	__tablename__ = 'users'
	

engine = create_engine('sqlite:///posts.db') 
Base.metadata.create_all(engine)

