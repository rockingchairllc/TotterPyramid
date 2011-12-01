import sqlalchemy
import transaction

from sqlalchemy import Column
from sqlalchemy import Integer, Boolean
from sqlalchemy import Unicode
from sqlalchemy import DateTime
from sqlalchemy import String, Text, CHAR
from sqlalchemy import ForeignKey, Table, Enum


from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.schema import Column
import uuid

from custom_types import UUID, JSONEncodedDict
import string
import random
from datetime import datetime
import hashlib

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

salt_generator = lambda : ''.join(random.choice([chr(x) for x in range(0x20,0x7F)]) for x in range(16))

class User(Base):
    __tablename__ = 'Users'
    id = Column('UserUUID',UUID(),primary_key=True,default=uuid.uuid4)
    email = Column('Email', String(256), unique=True, nullable=False)
    first_name = Column('FirstName', String(128))
    last_name = Column('LastName', String(128))
    profile_picture = Column('ProfilePicture', String(512), nullable=True)
    facebook_id = Column('FacebookID', Integer, nullable=True)
    registration_date = Column('RegistrationDate', DateTime, default=datetime.now)
    last_login = Column('LastLogin', DateTime, nullable=True) 
    salted_password_hash = Column('SaltedPasswordHash', CHAR(32)) # MD5(Salt+MD5(Password), nullable=False)
    salt = Column('Salt', CHAR(16), default=salt_generator, nullable=False)

    def password_hash(self, password):
        return hashlib.md5(self.salt + hashlib.md5(password).hexdigest()).hexdigest()


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
    creator_id = Column('CreatorUUID',UUID(), ForeignKey('Users.UserUUID'))
    creation_time = Column('CreationTime', DateTime, default=datetime.now)
    deadline = Column('Deadline', DateTime, nullable=True)
    anonymous = Column('Anonymous', Boolean, nullable=False, default=0)
    
    creator = relationship(User, backref=backref('created_projects'))
    participants = relationship(User, secondary=participants, 
        backref=backref('projects'))
        
        
class ProjectEvent(Base):
    __tablename__ = 'ProjectEvents'
    id = Column('EventID', Integer, primary_key=True, nullable=False, autoincrement=True)
    project_id = Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID'), nullable=False, index=True)
    when = Column('When', DateTime, default=datetime.now, nullable=False, index=True)
    type = Column('EventType', String(32), nullable=False)
    data = Column('Data', JSONEncodedDict)
    
    project = relationship(Project, backref=backref('events', lazy='dynamic'))

class Idea(Base):
    __tablename__ = 'Ideas'
    id = Column('IdeaID', Integer, 
        primary_key=True, nullable=False, autoincrement = True)
    project_id = Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID'))
    author_id = Column('AuthorUUID', UUID(), ForeignKey('Users.UserUUID'))
    creation_time = Column('CreationTime', DateTime, default=datetime.now)
    anonymous = Column('Anonymous', Boolean, nullable=False, default=0)
    data = Column('IdeaData', Text)
    
    author = relationship(User, backref=backref('ideas'))
    project = relationship(Project, backref=backref('ideas'))
    


class Comment(Base):
    __tablename__ = 'Comments'
    id = Column('CommentID', Integer, 
        primary_key=True, nullable=False, autoincrement=True)
    idea_id = Column('IdeaID', Integer, ForeignKey('Ideas.IdeaID'))
    author_id = Column('AuthorUUID', UUID(), ForeignKey('Users.UserUUID'))
    creation_time = Column('CreationTime', DateTime, default=datetime.now)
    anonymous = Column('Anonymous', Boolean, nullable=False, default=0)
    data = Column('CommentData', Text)
    
    author = relationship(User, backref=backref('comments'))
    idea = relationship(Idea, backref=backref('comments'))
                
class UserRating(Base):
    __tablename__ = 'UserRatings'
    idea_id = Column('IdeaID', Integer, ForeignKey('Ideas.IdeaID'), primary_key=True)
    user_id = Column('UserUUID', UUID(), ForeignKey('Users.UserUUID'), primary_key=True)
    type = Column('Type', Enum('like/love', 'star'))
    liked = Column('Liked', Boolean, nullable=False, default='0')
    loved = Column('Loved', Boolean, nullable=False, default='0')
    stars = Column('Stars', Integer, nullable=False, default='0')
    modified = Column('LastModified', DateTime, default=datetime.now)
    creation_time = Column('CreationTime', DateTime, default=datetime.now)
    
    idea = relationship(Idea, backref=backref('user_ratings', lazy='dynamic'))
    rater = relationship(User, backref=backref('ratings'))
    

class AggregateRating(Base):
    __tablename__ = 'AggregateRatings'
    idea_id = Column('IdeaID', Integer, ForeignKey('Ideas.IdeaID'), primary_key=True)
    liked = Column('Liked', Integer, nullable=False, default='0')
    loved = Column('Loved', Integer, nullable=False, default='0')
    stars = Column('Stars', Integer, nullable=False, default='0')
    count = Column('Count', Integer, nullable=False, default='0')
    
    idea = relationship(Idea, backref=backref('aggregate_rating', uselist=False), uselist=False)
    
    def __init__(self, idea_id=None):
        self.idea_id = idea_id
        self.liked = 0
        self.loved = 0
        self.stars = 0
        self.count = 0
    
    
def populate():
    session = DBSession()
    import hashlib
    salt = salt_generator()
    password_data = hashlib.md5(salt + hashlib.md5('password1234').hexdigest()).hexdigest()
    test_user = User(first_name='Tester', last_name='McTesterton', salted_password_hash=password_data, salt=salt, email='test@rockingchairllc.com', 
    profile_picture='http://linux-engineer.net/blog/public/test.jpg')
    session.add(test_user)
    
    test_project = Project(description="This is the project description.", title="This is the project title",
        key="test_key_1234")
    test_project.creator = test_user
    test_project.participants.append(test_user)
    session.add(test_project)
    
    test_idea = Idea(data="This is a test idea")
    test_idea.author = test_user
    test_idea.project = test_project
    session.add(test_idea)
    
    test_comment = Comment(data="This is a test comment.")
    test_comment.author = test_user
    test_comment.idea = test_idea
    session.add(test_comment)
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
