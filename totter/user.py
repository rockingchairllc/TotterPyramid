from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
import facebook as fb

from models import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

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
            if user.password_hash(password) == user.salted_password_hash:
                headers = remember(request, login)
                return HTTPFound(location = came_from, headers = headers)
        except:
            pass
        message = 'Failed login'

    return dict(
        facebook_app_id = request.registry.settings['facebook.app_id'],
        message = message,
        came_from = came_from,
        login = login,
        password = password,
        user = authenticated_userid(request),
        )

def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'), headers = headers)

def register(request):
    login_url = request.route_url('login')
    register_url = request.route_url('register')
    referrer = request.url
    if referrer == login_url or referrer == register_url:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)
    message = login = password = firstname = lastname = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        firstname = request.params['firstname']
        lastname = request.params['lastname']
        password = request.params['password']
        session = DBSession()
        user = User(
            email = login,
            first_name = firstname,
            last_name = lastname,
            salt = salt_generator(),
        )
        user.salted_password_hash = user.password_hash(password)
        try:
            session.add(user)
            session.flush()
        except IntegrityError:
            message = "Email '%s' already taken" % login
        else:
            headers = remember(request, login)
            return HTTPFound(location = came_from, headers = headers)            

    return dict(
        message = message,
        login = login,
        firstname = firstname,
        lastname = lastname,
        password = password,
        came_from = came_from,
        user = authenticated_userid(request),
        )

def facebook(request):
    # Authenticated
    if 'code' in request.params:
        fbuser = fb.get_user_from_cookie(request.cookies, 
                            request.registry.settings['facebook.app_id'],
                            request.registry.settings['facebook.secret']
        )
        if fbuser:
            graph = fb.GraphAPI(fbuser["access_token"])
            profile = graph.get_object("me")
            session = DBSession()
            try:
                user = session.query(User).filter_by(email=profile['email']).one()
            except NoResultFound:
                user = User(
                    email = profile['email'],
                    first_name = profile['first_name'],
                    last_name = profile['last_name'],
                    facebook_id = fbuser['uid'],
                    salt = salt_generator(),
                )
                session.add(user)
            login = user.email
            headers = remember(request, login)
            url = request.referer if request.referer else request.application_url
            return HTTPFound(location = url, headers = headers) 
        else:
            return HTTPFound(location = request.route_url('login'))

    # Access denied by user
    elif 'error' in request.params:
        return {'message': request.params['error_reason'] + ' ' +
                           request.params['error'] + ' ' +
                           request.params['error_description'] }

    # Call authentication dialog
    fb_url = "https://www.facebook.com/dialog/oauth"
    params = "&".join([
        'client_id=' + request.registry.settings['facebook.app_id'], 
        'redirect_uri='+request.route_url('facebook'),
        'display=popup',
        'scope=email',
    ])
    return HTTPFound(location = fb_url+"?"+params)

