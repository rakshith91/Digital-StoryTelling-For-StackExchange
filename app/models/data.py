import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy import UniqueConstraint, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,relationship,scoped_session
from sqlalchemy.interfaces import PoolListener


Base = declarative_base()


poststags_table  = Table('poststags',Base.metadata,
							Column('PostsId', Integer(), ForeignKey('questions.id')),
							Column('TagsId', Integer(), ForeignKey('tags.id')))


class Questions(Base):
	__tablename__ = 'questions'

	id = Column(Integer, primary_key=True)
	accepted_answer_id = Column(Integer, ForeignKey('answers.id'))
	score = Column(Integer)
	author_id = Column(Integer, ForeignKey('users.id'))
	creation_date = Column(DateTime)
	modified_date = Column(DateTime)
	answer_count = Column(Integer) # TODO: To remove post-verification using joins


class Answers(Base):
	__tablename__ = 'answers'

	id = Column(Integer, primary_key=True)
	question_id = Column(Integer, ForeignKey('questions.id'))
	score = Column(Integer)
	author_id = Column(Integer, ForeignKey('users.id'))
	creation_date = Column(DateTime)
	modified_date = Column(DateTime)


class Tags(Base):
	__tablename__ = 'tags'

	id = Column(Integer, primary_key=True)
	name = Column(String,index = True, unique = True)
	questions = relationship("Questions", secondary = poststags_table)


class Location(Base):
	__tablename__ = 'locations'

	id = Column(Integer, primary_key = True, autoincrement= True)
	location = Column(String(convert_unicode=True), unique=True)
	city = Column(String(convert_unicode=True))
	state = Column(String(convert_unicode=True))
	country = Column(String(convert_unicode=True))
	timezone = Column(String)
	left = Column(Float)
	right = Column(Float)
	top = Column(Float)
	bottom = Column(Float)

class Users(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key= True)
	reputation = Column(Integer)
	location_id = Column(Integer, ForeignKey('locations.id'))
	views = Column(Integer)
	upvotes = Column(Integer)
	downvotes = Column(Integer)
	age = Column(Integer)
	questions = relationship('Questions', backref = 'users')
	answers = relationship('Answers', backref = 'users')



def get_sqlite3_session(path):
	class ForeignKeysListener(PoolListener):
		def connect(self, dbapi_con, con_record):
			db_cursor = dbapi_con.execute('pragma foreign_keys=ON')

	listeners = [ForeignKeysListener()]
	engine = create_engine('sqlite:///' + path, listeners=listeners)
	Base.metadata.create_all(engine)
	return scoped_session(sessionmaker(bind=engine))

def get_postgres_session(host, port, username, password, db):
	protocol = "postgresql"
	string = "{}://{}:{}@{}:{}/{}".format(protocol, username, password,
						host, port, db)
	engine = create_engine(string)
	Base.metadata.create_all(engine)
	return scoped_session(sessionmaker(bind=engine))

Session = get_postgres_session("db.slis.indiana.edu", 5433, 'rangira', 'iDNKrQa4', 'rangira')
