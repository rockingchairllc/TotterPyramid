from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.exceptions import Forbidden
from pyramid.view import view_config
from datetime import datetime
import facebook as fb
import requests, urlparse
from urllib2 import URLError
from models import *
import logging 
import uuid
import pprint
from pyramid.response import Response
pp = pprint.PrettyPrinter(indent=4)

def get_user(request, allow_anon=False):
    user_id = authenticated_userid(request)
    if user_id == 'PROJECT':
        return None
    else:
        try:
            return request.root.users.fromID(user_id)
        except NoResultFound:
            logging.warn('Invalid user received: ' + str(user_id))
            return None

## We actually have three login scenarios to cover:
## If an anonymous user has project key/id, he gets view privs on that project.
## Anonymous users have no privs without having "logged in" with a key/id pair.
## Anonymous => Authenticated User?
## TODO: Anon => Auth User
## We should associate the Anonymous privs with the authed user privs.
## If an authenticated user has project key/id he gets full privs on that project.

def groupfinder(userid, request):
    # "Groups" based on projects user's allowed to post to.
    session = DBSession()
    try:
        if userid == 'PROJECT':
            logging.info('loading groups for anonymous authenticated user.')
            groups = ['group:anonymous']
            project_list = request.session.get('project_id', [])
            for project_id in project_list:
                groups += ['group:ro-' + project_id] 
            return groups
        else:
            user = session.query(User).filter(User.id==userid).one()
            groups = ['group:users']
            for project in user.projects:
                groups += ['group:rw-' + str(project.id)]
            return groups
    except NoResultFound,e:
        return None

@view_config(context=Forbidden)
def forbidden_handler(request):
    if request.referrer is not None:
        logging.info('setting referrer(1): ' + str(request.referrer))
        request.session['referrer'] = request.referrer
    elif request.context is not None:
        logging.info('setting referrer(2): ' + str(request.referrer))
        request.session['referrer'] = request.resource_url(request.context)
    if isinstance(request.context, Project):
        # User tried to access a project.
        return HTTPFound(location=request.route_url('access_project', project_id=request.context.id))
    else:
        return HTTPFound(location=request.route_url('login'))

@view_config(route_name="access_project", renderer="enter_key.jinja2")
def project_access(request):
    if 'project_id' in request.params:
        # Attempt login.
        project_id = request.params.get('project_id')
        project_key = request.params.get('project_key')
        logging.info('Attempting to authenticate user for project ' + project_id)
        session = DBSession()
        
        try: 
            project = request.root.projects[project_id]
        except KeyError,e:
            return {'not_found' : True, 'project_id' : project_id}
        
        if project.key != project_key:
            logging.info('Invalid authentication, access denied to: ' + project_id)
            return {'access_denied' : True, 'project_id' : project_id}
        
        
        # Add project to user's access list.
        headers = None
        if authenticated_userid(request):
            user_id = authenticated_userid(request)
            if user_id == 'PROJECT':
                logging.info('Authorization approved, appending to access cookie.')
                # User still anonymous, has creds for another project.
                request.session['project_id'] = request.session.get('project_id',[]) + [str(project.id)]
                headers = remember(request, 'PROJECT')
            else:
                logging.info('Authorization approved, adding project to participants.')
                request.session['project_id'] = request.session.get('project_id',[]) + [str(project.id)]
                merge_anon_user_projects(request, user_id)
        else:
            logging.info('Authorization approved, setting access cookie.')
            # Create temporary project access cookie.
            request.session['project_id'] = [str(project.id)]
            headers = remember(request, 'PROJECT')
            
            
        # Redirect to project page:
        return HTTPFound(location=request.root.project_url(project), headers=headers)
    else:
        # Just render the form.
        return {'project_id' : request.matchdict.get('project_id')}

def merge_anon_user_projects(request, user_id):
    session = DBSession()
    user = session.query(User).filter(User.id==user_id).one()
    projects = request.session.get('project_id', [])
    for project in projects:
        if project not in user.projects: # FIXME: Always runs.
            try: 
                session.merge(Participation(project_id=project, user_email=user.email, access_time=utcnow()))
            except IntegrityError:
                continue

@view_config(route_name='home', renderer="login.jinja2")
def landing(request):
    if 'referrer' in request.session:
        logging.info("Cleared referrer in landing page.")
        request.session['referrer'] = None
    if get_user(request):
        return HTTPFound(location=request.route_url('dashboard'))
    else:
        return HTTPFound(location=request.route_url('login'))
    
@view_config(route_name='login', renderer="login.jinja2")
def login(request):
    login_url = request.route_url('login', request)
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
                headers = remember(request, str(user.id))
                user.last_login = utcnow()
                session.flush()
                merge_anon_user_projects(request, user.id)
                return HTTPFound(location=referrer(request), headers=headers)
            else:
                message = 'invalid_password'
        except NoResultFound:
            message = 'unknown_user'
    
    fail_result = dict(
        app_id = request.registry.settings['facebook.app_id'],
        login = login,
        password = password,
        user = authenticated_userid(request),
        fb_redirect_url = referrer(request),
        fb_login_url = fb_login_url(request),
        )
    fail_result[message] = True
    return fail_result

@view_config(context=Forbidden, xhr=True, renderer='json')
def xhr_forbidden(request):
    return HTTPForbidden()

def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'), headers = headers)

def register(request):
    login_url = request.route_url('login')
    register_url = request.route_url('register')
    
    message = login = password = firstname = lastname = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        firstname = request.params['firstname']
        lastname = request.params['lastname']
        password = request.params['password']
        session = DBSession()
        user = User(
            id = uuid.uuid4(),
            email = login,
            first_name = firstname,
            last_name = lastname,
            salt = salt_generator(),
        )
        user.profile_picture = user.default_profile_url(request)
        user.salted_password_hash = user.password_hash(password)
        try:
            session.add(user)
            session.flush()
        except IntegrityError:
            message = "Email '%s' already taken" % login
            session.rollback()
        else:
            merge_anon_user_projects(request, user.id)
            headers = remember(request, str(user.id))
            return HTTPFound(location=referrer(request), headers=headers)


    
    return dict(
        message = message,
        login = login,
        firstname = firstname,
        lastname = lastname,
        password = password,
        user = authenticated_userid(request),
        app_id = request.registry.settings['facebook.app_id'],
        fb_redirect_url = referrer('request'),
        fb_login_url = fb_login_url(request),
        )
def fb_login_url(request):
    fb_url = "https://www.facebook.com/dialog/oauth"
    params = "&".join([
        'client_id=' + request.registry.settings['facebook.app_id'], 
        'redirect_uri='+request.route_url('fb_redirect'),
        'display=popup',
        'scope=email,publish_stream',
    ])
    return fb_url + '?' + params

def facebook(request):
    # Our handler for facebook stuff.
    logging.info('Facebook handler')
    if 'code' in request.params:
        # Facebook redirected the user back to our page with an access code
        # Request access token from facebook:
        try: 
            logging.info('Requesting access token from facebook.')
            fb_resp = requests.request('GET',
                'https://graph.facebook.com/oauth/access_token',
                params = {
                    'client_id' : request.registry.settings['facebook.app_id'],
                    'client_secret' : request.registry.settings['facebook.secret'],
                    'code' : request.params['code'],
                    'redirect_uri' : request.route_url('facebook'),
                    'type' : 'web_server'
                }
            )
            logging.info('facebook response:' + str(fb_resp.content))
            fb_params = dict(urlparse.parse_qsl(fb_resp.content))
            # If we're good, fb_params should contain keys (access_token,expires)
            if 'access_token' not in fb_params:
                raise Exception(fb_resp.content)
            request.session['access_token'] = fb_params['access_token']
        except URLError,e:
            logging.error(repr(e))
        except Exception,e:
            logging.error(repr(e))
        
        logging.info('Got facebook access token')
        graph = fb.GraphAPI(fb_params['access_token'])
        profile = graph.get_object("me")
        session = DBSession()
        try:
            logging.info('Mapped user found!')
            user = session.query(User).filter_by(email=profile['email']).one()
            merge_anon_user_projects(request, user.id)
        except NoResultFound,e:
            logging.info('Creating facebook user.')
            user = User(
                id = uuid.uuid4(),
                email = profile['email'],
                first_name = profile['first_name'],
                last_name = profile['last_name'],
                facebook_id = profile['id'],
                profile_picture = 'http://graph.facebook.com/'+str(profile['id'])+ '/picture',
                salt = salt_generator(),
            )
            session.add(user)
            session.flush()
            merge_anon_user_projects(request, user.id)
        login = user.email
        headers = remember(request, str(user.id))
        return HTTPFound(location=referrer(request), headers=headers)
    elif 'error' in request.params:
        # The user denied our request to use their fb creds.
        logging.info('Facebook credential access denied by user.')
        return {'message': request.params['error_reason'] + ' ' +
                           request.params['error'] + ' ' +
                           request.params['error_description'] }
    else:
        # The user pressed the Login With Facebook button.
        logging.info('Redirecting to facebook login screen.')
        # Call authentication dialog
        fb_url = "https://www.facebook.com/dialog/oauth"
        params = "&".join([
            'client_id=' + request.registry.settings['facebook.app_id'], 
            'redirect_uri='+request.route_url('facebook'),
            'display=popup',
            'scope=email,publish_stream',
        ])
        return HTTPFound(location = fb_url+"?"+params)
        
def referrer(request):
    url = request.referer if request.referer else request.application_url
    if request.session.get('referrer'):
        url = request.session['referrer']
        request.session['referrer'] = None
        logging.info('redirect_to_referrer read from cookie: ' + str(url))
    if  (url.startswith(request.route_url('login')) or 
               url.startswith(request.route_url('logout')) or
               url.startswith(request.route_url('register')) or
               url.startswith(request.route_url('fb_redirect'))):
        # User 
        url = '/'
        logging.info('Referrer cookie is invalid.' if 'referrer' in request.session else 'no referrer cookie!')
    logging.info('referrer: ' + url)
    return url

@view_config(route_name='fb_redirect')
def fb_redirect(request):
    document = """
    <html><head>
    <script type="text/javascript">
    window.opener.location.href = "%s";// + window.location.href.slice(window.location.href.indexOf('?') );
    window.close();
    </script>
    </head><body></body></html>
    """ % request.route_url('facebook')
    return Response(document, content_type='text/html')
    