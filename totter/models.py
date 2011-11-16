import sqlalchemy
import transaction

from sqlalchemy import Column
from sqlalchemy import Integer, Boolean
from sqlalchemy import Unicode
from sqlalchemy import DateTime
from sqlalchemy import String, Text, CHAR
from sqlalchemy import ForeignKey, Table, Enum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.schema import Column
import uuid

from sqlalchemy_uuid import UUID
import string
import random
from datetime import datetime

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

salt_generator = lambda : ''.join(random.choice([chr(x) for x in range(0x20,0x7F)]) for x in range(128))
class User(Base):
    __tablename__ = 'Users'
    id = Column('UserUUID',UUID(),primary_key=True,default=uuid.uuid4)
    email = Column('Email', String(256), unique=True, nullable=False)
    first_name = Column('FirstName', String(128))
    last_name = Column('LastName', String(128))
    profile_picture = Column('ProfilePicture', String(512), nullable=True)
    facebook_id = Column('FacebookID', Integer, nullable=True)
    registration_date = Column('RegistrationDate', DateTime, default=datetime.now)
    salted_password_hash = Column('SaltedPasswordHash', CHAR(32)) # MD5(Salt+MD5(Password), nullable=False)
    salt = Column('Salt', CHAR(128), default=salt_generator, nullable=False)

participants = Table('Participants', Base.metadata,
    Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID')),
    Column('UserUUID', UUID(), ForeignKey('Users.UserUUID'))
)
class Project(Base):
    __tablename__ = 'Projects'
    id = Column('ProjectUUID', UUID(),primary_key=True,default=uuid.uuid4)
    description = Column('ProjectDescription', Text)
    urlName = Column('URLName', String(128), unique=True)
    title = Column('ProjectTitle', String(128))
    key = Column('ProjectKey', String(128))
    creator_id = Column('CreatorUUID',UUID())
    creation_time = Column('CreationTime', DateTime, default=datetime.now)
    anonymous = Column('Anonymous', Boolean)
    
    participants = relationship('User', secondary=participants, 
        backref=backref('projects', lazy='dynamic'))

class Idea(Base):
    __tablename__ = 'Ideas'
    id = Column('IdeaID', Integer, 
        primary_key=True, nullable=False, autoincrement = True)
    project_id = Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID'))
    author_id = Column('AuthorUUID', UUID(), ForeignKey('Users.UserUUID'))
    creation_time = Column('CreationTime', DateTime, default=datetime.now)
    anonymous = Column('Anonymous', Boolean)
    
    data = Column('IdeaData', Text)
    project = relationship('Project', backref=backref('ideas'))
    

class Comment(Base):
    __tablename__ = 'Comments'
    id = Column('CommentID', Integer, 
        primary_key=True, nullable=False, autoincrement=True)
    idea_id = Column('IdeaID', Integer, ForeignKey('Ideas.IdeaID'))
    author_id = Column('AuthorUUID', UUID(), ForeignKey('Users.UserUUID'))
    creation_time = Column('CreationTime', DateTime, default=datetime.now)
    anonymous = Column('Anonymous', Boolean)
    data = Column('CommentData', Text)
    idea = relationship('Idea', backref=backref('comments'))
    
class IdeaRatings(Base):
    __tablename__ = 'IdeaRatings'
    idea_id = Column('IdeaID', Integer, ForeignKey('Ideas.IdeaID'), primary_key=True)
    user_id = Column('UserUUID', UUID(), ForeignKey('Users.UserUUID'), primary_key=True)
    type = Column('Type', Enum('like/love', 'star'))
    liked = Column('Liked', Boolean)
    loved = Column('Loved', Boolean)
    stars = Column('Stars', Integer)
    modified = Column('LastModified', DateTime, default=datetime.now)
    creation_time = Column('CreationTime', DateTime, default=datetime.now)
    
    
def populate():
    session = DBSession()
    import hashlib
    salt = salt_generator()
    password_data = hashlib.md5(salt + hashlib.md5('password1234').hexdigest()).hexdigest()
    model = User(first_name='Francisco', last_name='Saldana', salted_password_hash=password_data, salt=salt, email='frank@rockingchairllc.com')
    session.add(model)
    session.flush()
    transaction.commit()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        transaction.abort()
