from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound

import hashlib
from models import *

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:users', 'edit') ]
    def __init__(self, request):
        pass

def groupfinder(userid, request):
    session = DBSession()
    try:
        user = session.query(User).filter(User.email==userid).one()
        return ['group:users']
    except:
        return None

def login(request):
    login_url = request.route_url('login', request)
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        session = DBSession()        
        try:
            user = session.query(User).filter(User.email==login).one()
            salt = user.salt
            password_data = hashlib.md5(salt + hashlib.md5(password).hexdigest()).hexdigest()
            if password_data == user.salted_password_hash:
                headers = remember(request, login)
                return HTTPFound(location = came_from, headers = headers)
        except:
            pass
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )

