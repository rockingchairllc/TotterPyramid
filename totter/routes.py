from models import *
from pyramid.security import ALL_PERMISSIONS, Allow, Everyone
import logging

class ProjectFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
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
            if key is None or key == 'None': # Weird.
                raise KeyError
            project = session.query(Project)\
                .filter((Project.url_name==key) | (Project.id==key)).one()
            return project
        except NoResultFound:
            raise KeyError
        except MultipleResultsFound:
            # This is actually a problem with our database.
            logging.error('Multiple project mappings for identifier:' + key)
            raise KeyError