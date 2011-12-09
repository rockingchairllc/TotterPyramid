import sqlalchemy
import transaction

from sqlalchemy import Column
from sqlalchemy import Integer, Boolean
from sqlalchemy import Unicode
from sqlalchemy import DateTime
from sqlalchemy import String, Text, CHAR
from sqlalchemy import ForeignKey, Table, Enum
from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.schema import Column
import uuid
from sets import ImmutableSet
from custom_types import UUID, JSONEncodedDict, HTMLUnicode, HTMLUnicodeText, URLEncodedUnicode, UTCDateTime
import string
import random
from datetime import datetime
import hashlib
import pytz
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

utcnow = lambda : pytz.utc.localize(datetime.utcnow())
salt_generator = lambda : ''.join(random.choice([chr(x) for x in range(0x20,0x7F)]) for x in range(16))

class User(Base):
    __tablename__ = 'Users'
    id = Column('UserUUID',UUID(),primary_key=True,default=uuid.uuid4)
    email = Column('Email', URLEncodedUnicode(256), unique=True, nullable=False)
    first_name = Column('FirstName', HTMLUnicode(128))
    last_name = Column('LastName', HTMLUnicode(128))
    profile_picture = Column('ProfilePicture', URLEncodedUnicode(512), nullable=True)
    facebook_id = Column('FacebookID', Integer, nullable=True)
    registration_date = Column('RegistrationDate', UTCDateTime, default=utcnow)
    last_login = Column('LastLogin', UTCDateTime, nullable=True) 
    salted_password_hash = Column('SaltedPasswordHash', CHAR(32)) # MD5(Salt+MD5(Password), nullable=False)
    salt = Column('Salt', CHAR(16), default=salt_generator, nullable=False)

    projects = relationship('Project', backref=backref('participants', collection_class=set), secondary='Participants', collection_class=set)
    
    def password_hash(self, password):
        return hashlib.md5(self.salt + hashlib.md5(password).hexdigest()).hexdigest()

    def default_profile_url(self, request):
        return request.static_url('totter:static/images/default_profile.jpg')
    
    # These should be set by totter.routes.UserContainer
    __name__ = None
    __parent__ = None
        
    @property
    def __acl__(self):
        return [
            (Allow, str(self.id), 'personal'),
            (Allow, 'group:users', 'friends'),
            ('Deny', 'system.Everyone', 'view'),
        ]

class Participation(Base):
    __tablename__ = 'Participants'
    project_id = Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID'), primary_key=True)
    user_email = Column('UserEmail', URLEncodedUnicode(256), ForeignKey('Users.Email'), primary_key=True)
    access_time = Column('AccessTime', UTCDateTime, nullable=True)
    
    user = relationship(User, uselist=False)
    project = relationship('Project', uselist=False)
    
def project_exists(*filter_params):
    from sqlalchemy.sql.expression import select, exists
    session = DBSession()
    project_query = session.query(Project).filter_by(*filter_params)
    project_exists_select = select((exists(project_query.statement),))
    engine = Base.metadata.bind
    return engine.execute(project_exists_select).scalar()

class Project(Base):
    __tablename__ = 'Projects'
    id = Column('ProjectUUID', UUID(),primary_key=True,default=uuid.uuid4)
    description = Column('ProjectDescription', Text)
    url_name = Column('URLName', URLEncodedUnicode(128), unique=True)
    title = Column('ProjectTitle', HTMLUnicode(128), nullable=False)
    key = Column('ProjectKey', URLEncodedUnicode(128))
    creator_id = Column('CreatorUUID',UUID(), ForeignKey('Users.UserUUID'), nullable=False)
    creation_time = Column('CreationTime', UTCDateTime, default=utcnow, nullable=False)
    deadline = Column('Deadline', UTCDateTime, nullable=True)
    anonymous = Column('Anonymous', Boolean, nullable=False, default=0)
    rating_type = Column('RatingType', Enum('like/love', 'star'), default='like/love', nullable=False)
    
    creator = relationship(User, backref=backref('created_projects'))
    
    # These should be set by totter.routes.ProjectContainer
    __name__ = None
    __parent__ = None
    
    @property
    def __acl__(self):
        return [
            (Allow, str(self.creator_id), ['edit', 'invite', 'view']),
            (Allow, 'group:ro-'+str(self.id), 'view'),
            (Allow, 'group:rw-'+str(self.id), ['post', 'view']),
            ('Deny', 'system.Everyone', 'view'),
        ]
    
    def __getitem__(self, key):
        if key != 'idea':
            raise KeyError # Perform view lookup.
        return IdeaContainer(self, 'idea')
            
class ProjectUpdate(Base):
    __tablename__ = 'ProjectUpdates'
    id = Column('UpdateID', Integer, primary_key=True, nullable=False, autoincrement=True)
    project_id = Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID'), nullable=False, index=True)
    when = Column('When', UTCDateTime, default=utcnow, nullable=False, index=True)
    data = Column('Data', JSONEncodedDict)
    project = relationship(Project, backref=backref('updates', lazy='dynamic'))
        
class ProjectEvent(Base):
    __tablename__ = 'ProjectEvents'
    id = Column('EventID', Integer, primary_key=True, nullable=False, autoincrement=True)
    project_id = Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID'), nullable=False, index=True)
    when = Column('When', UTCDateTime, default=utcnow, nullable=False, index=True)
    type = Column('EventType', HTMLUnicode(32), nullable=False)
    data = Column('Data', JSONEncodedDict)
    
    project = relationship(Project, backref=backref('events', lazy='dynamic'))

class Idea(Base):
    __tablename__ = 'Ideas'
    id = Column('IdeaID', Integer, 
        primary_key=True, nullable=False, autoincrement = True)
    project_id = Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID'))
    author_id = Column('AuthorUUID', UUID(), ForeignKey('Users.UserUUID'))
    creation_time = Column('CreationTime', UTCDateTime, default=utcnow)
    anonymous = Column('Anonymous', Boolean, nullable=False, default=0)
    data = Column('IdeaData', HTMLUnicodeText)
    
    author = relationship(User, backref=backref('ideas', lazy='dynamic'))
    project = relationship(Project, backref=backref('ideas', lazy='dynamic'))
    
    # These should be set by totter.routes.IdeaContainer
    @property
    def __name__(self):
        return self.id
        
    @property
    def __parent__(self):
        return self.project['idea']
    
    def __getitem__(self, key):
        if key != 'comment':
            raise KeyError # Perform view lookup.
        return CommentContainer(self, 'comment')
        
    @hybrid_property
    def total_rating(self):
        return self.aggregate_rating.total_rating
    
    @hybrid_property
    def stars(self):
        return self.aggregate_rating.stars / self.aggregate_rating.count
    
class Comment(Base):
    __tablename__ = 'Comments'
    id = Column('CommentID', Integer, 
        primary_key=True, nullable=False, autoincrement=True)
    idea_id = Column('IdeaID', Integer, ForeignKey('Ideas.IdeaID'))
    project_id = Column('ProjectUUID', UUID(), ForeignKey('Projects.ProjectUUID'))
    author_id = Column('AuthorUUID', UUID(), ForeignKey('Users.UserUUID'))
    creation_time = Column('CreationTime', UTCDateTime, default=utcnow)
    anonymous = Column('Anonymous', Boolean, nullable=False, default=0)
    data = Column('CommentData', HTMLUnicodeText)
    
    author = relationship(User, backref=backref('comments'))
    idea = relationship(Idea, backref=backref('comments'))
    project = relationship(Project, backref=backref('comments', lazy='dynamic'))
    
    # These should be set by totter.routes.CommentContainer
    @property
    def __name__(self):
        return self.id
        
    @property
    def __parent__(self):
        return self.idea['comment']
                
class UserRating(Base):
    __tablename__ = 'UserRatings'
    idea_id = Column('IdeaID', Integer, ForeignKey('Ideas.IdeaID'), primary_key=True)
    user_id = Column('UserUUID', UUID(), ForeignKey('Users.UserUUID'), primary_key=True)
    type = Column('Type', Enum('like/love', 'star'))
    liked = Column('Liked', Boolean, nullable=False, default='0')
    loved = Column('Loved', Boolean, nullable=False, default='0')
    stars = Column('Stars', Integer, nullable=False, default='0')
    modified = Column('LastModified', UTCDateTime, default=utcnow)
    creation_time = Column('CreationTime', UTCDateTime, default=utcnow)
    
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
    
    @hybrid_property
    def total_rating(self):
        return self.liked + self.loved * 2
        
    @hybrid_property
    def average_stars(self):
        # Every user can give at most 3 stars.
        return self.stars / (self.count) if self.count else 0
        
#### Containers ####
from pyramid.security import ALL_PERMISSIONS, Allow, Everyone
import logging
from zope.interface import implements, Interface
# FIXME: ProjectLongname and ProjectShortname both derive from ProjectContainer
# For pyramid views to be able to specify "either" as their context by just specifying
# ProjectContainer, the subclasses need to be wired up to the zope.interface 
# stuff. I wonder if ABCMeta is supported as an alternative...

class RootFactory(dict):
    __name__ = None
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:users', 'create'),
                (Allow, 'group:users', 'post') ]
    def __init__(self, request):
        self.request = request
        self['project'] = ProjectLongname(self, 'project')
        self['p'] = ProjectShortname(self, 'p')
        self['user'] =  UserContainer(self, 'user')
        self.projects = self['project']
        
        self.users = self['user']
        
    def project_url(self, project):
        return self.request.resource_url(self['p'][project.url_name])
        
    def user_url(self, user):
        return self.request.resource_url(self['user'][user.id])
        
        
class ProjectContainer():
    __acl__ = [
        (Allow, 'group:users', 'create'),
        (Allow, 'group:admin', ALL_PERMISSIONS),
    ]
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        
    def name_from_project(self, project):
        raise NotImplementedError
    def lookup_field(self):
        raise NotImplementedError
        
    def __getitem__(self, key):
        # Get Project from database
        session = DBSession()
        try: 
            logging.info('ProjectContainer key: ' + str(key))
            logging.info('ProjectContainer key type: ' + str(type(key)))
            project = session.query(Project)\
                .filter((self.lookup_field()==key)).one()
            name = self.name_from_project(project)
            project.__parent__ = self
            project.__name__ = name
            return project
        except NoResultFound:
            logging.info('ProjectContainer KeyError: ' + str(key))
            raise KeyError
        except MultipleResultsFound:
            # This is actually a problem with our database.
            logging.error('Multiple project mappings for identifier:' + key)
            raise KeyError
        except StatementError:
            raise KeyError
            
    def newProject(self, *args, **kwargs):
        session = DBSession()
        project = Project(*args, **kwargs)
        session.add(project)
        session.flush()
        project.__name__ = self.name_from_project(project)
        project.__parent__ = self
        return project
        
    def fromID(self, id):
        session = DBSession()
        project = session.query(Project).filter(Project.id==id).one()
        project.__name__ = self.name_from_project(project)
        project.__parent__ = self
        return project
        
class ProjectShortname(ProjectContainer):
    def name_from_project(self, project):
        return project.url_name
    def lookup_field(self):
        return Project.url_name
        
class ProjectLongname(ProjectContainer):
    def name_from_project(self, project):
        return project.id
    def lookup_field(self):
        return Project.id
        
class UserContainer(object):
    __acl__ = [
        (Allow, 'group:admin', ALL_PERMISSIONS),
    ]
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
    
    def __getitem__(self, key):
        # Get User from database
        session = DBSession()
        try: 
            logging.info('User key: ' + str(key))
            logging.info('User key type: ' + str(type(key)))
            user = session.query(User)\
                .filter(User.id==key).one()
            user.__parent__ = self
            user.__name__ = str(user.id)
            logging.info('User model found!')
            return user
        except NoResultFound:
            logging.info('User model not found.')
            raise KeyError
        except MultipleResultsFound:
            # This is actually a problem with our database.
            logging.error('Multiple user mappings for identifier:' + key)
            raise KeyError
        except StatementError:
            raise KeyError
            
    def newUser(self, *args, **kwargs):
        session = DBSession()
        user = User(*args, **kwargs)
        user.__name__ = str(user.id)
        user.__parent__ = self
        session.add(user)
        session.flush()
        return user
        
    def fakeUser(self):
        session = DBSession()
        return session.query(User).filter(User.email=='test@rockingchairllc.com').one()
        
    def fromID(self, id):
        session = DBSession()
        return session.query(User).filter(User.id==id).one()

class IdeaContainer(object):
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        assert isinstance(parent, Project)
        self.project = parent
        
    def __getitem__(self, key):
        # Get Idea from database
        session = DBSession()
        try: 
            idea = session.query(Idea)\
                .filter(Project.id==self.project.id)\
                .filter(Idea.id==key).one()
                
            return idea
        except NoResultFound:
            logging.info('Idea model not found:' + key)
            raise KeyError
            
    def newIdea(self, *args, **kwargs):
        session = DBSession()
        idea = Idea(*args, **kwargs)
        idea.project = self.project
        session.add(idea)
        session.flush()
        return idea
            
class CommentContainer(object):
    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        assert isinstance(parent, Idea)
        self.idea = parent
        
    def __getitem__(self, key):
        # Get Comment from database
        session = DBSession()
        try: 
            comment = session.query(Comment)\
                .filter(Idea.id==self.idea.id)\
                .filter(Comment.id==key).one()
            return comment
        except NoResultFound:
            logging.info('Idea model not found:' + key)
            raise KeyError
            
    def newComment(self, *args, **kwargs):
        session = DBSession()
        comment = Comment(*args, **kwargs)
        comment.idea = self.idea
        comment.project = self.idea.project
        session.add(comment)
        session.flush()
        return comment
    
    
def populate():
    session = DBSession()
    import hashlib
    salt = salt_generator()
    password_data = hashlib.md5(salt + hashlib.md5('password1234').hexdigest()).hexdigest()
    test_user = User(first_name=u'Tester', last_name=u'McTesterton', salted_password_hash=password_data, salt=salt, email=u'test@rockingchairllc.com', 
    profile_picture=u'http://linux-engineer.net/blog/public/test.jpg')
    session.add(test_user)
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
