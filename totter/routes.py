from models import *
from pyramid.security import ALL_PERMISSIONS, Allow, Everyone
import logging

class RootFactory(object):
    __name__ = None
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:users', 'create'),
                (Allow, 'group:users', 'post') ]
    def __init__(self, request):
        self.request = request
    def __getitem__(self, key):
        route_factories = {'project' : ProjectFactory, 'user' : UserFactory}
        if key in route_factories:
            logging.info("RootFactory routing to " + str(route_factories[key]))
            factory_instance = route_factories[key](self.request)
            factory_instance.__parent__ = self
            return factory_instance
        else:
            raise KeyError
    
class ProjectFactory(object):
    __name__ = 'project'
    __acl__ = [
        (Allow, 'group:users', 'create'),
        (Allow, 'group:admin', ALL_PERMISSIONS),
    ]
    def __init__(self, request):
        self.request = request
    
    def __getitem__(self, key):
        # Get Project from database
        session = DBSession()
        try: 
            logging.info('ProjectFactory key: ' + str(key))
            logging.info('ProjectFactory key type: ' + str(type(key)))
            project = session.query(Project)\
                .filter((Project.url_name==key) | (Project.id==key)).one()
            project.__parent__ = self
            return project
        except NoResultFound:
            raise KeyError
        except MultipleResultsFound:
            # This is actually a problem with our database.
            logging.error('Multiple project mappings for identifier:' + key)
            raise KeyError
        except StatementError:
            raise KeyError
            
class UserFactory(object):
    __name__ = 'user'
    __acl__ = [
        (Allow, 'group:admin', ALL_PERMISSIONS),
    ]
    def __init__(self, request):
        self.request = request
    
    def __getitem__(self, key):
        # Get User from database
        session = DBSession()
        try: 
            logging.info('User key: ' + str(key))
            logging.info('User key type: ' + str(type(key)))
            user = session.query(User)\
                .filter(User.id==key).one()
            user.__parent__ = self
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