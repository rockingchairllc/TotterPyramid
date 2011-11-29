from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from totter.models import initialize_sql
from totter.user import groupfinder

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    authn_policy = AuthTktAuthenticationPolicy('#%DSDsad2', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          root_factory='totter.user.RootFactory',
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'totter:static', cache_max_age=3600)
    config.scan()
    config.add_route('home', '/')
    config.add_view('totter.views.my_view',
                    route_name='home',
                    renderer='mytemplate.jinja2')

    config.add_route('create_project', '/project/new')
    config.add_view('totter.testViews.create',
                    route_name='create_project',
                    renderer='create.jinja2',
                    permission='edit')
                    
    config.add_route('access', '/access')
    config.add_view('totter.testViews.enterKey',
                    route_name='access',
                    renderer='enterKey.jinja2')
                                        
    config.add_route('login', '/login')
    config.add_view('totter.user.login',
                    route_name='login',
                    renderer='login.jinja2')
    config.add_view('totter.user.login',
                    context='pyramid.httpexceptions.HTTPForbidden',
                    renderer='login.jinja2')

    config.add_route('facebook', '/facebook')
    config.add_view('totter.user.facebook',
                    route_name='facebook',
                    renderer='message.jinja2')

    config.add_route('logout', '/logout')
    config.add_view('totter.user.logout', route_name='logout')

    config.add_route('project_entity', '/project/{project_id}')
                    
    config.add_route('project_ideas', '/project/{project_id}/ideas')
    
                    
    config.add_route('register', '/register')
    config.add_view('totter.user.register',
                    route_name='register',
                    renderer='register.jinja2')
                    
    config.add_route('stars', '/project/{project_id}/stars')
    config.add_view('totter.testViews.stars',
                    route_name='stars',
                    renderer='stars.jinja2')
                    
    # For XMLHttpRequest
    config.add_route('comment_collection', '/project/{project_id}/idea/{idea_id}/comment')
    config.add_route('comment_entity', '/project/{project_id}/idea/{idea_id}/comment/{comment_id}')
    config.add_route('idea_collection', '/project/{project_id}/idea')
    config.add_route('idea_entity', '/project/{project_id}/idea/{idea_id}')
    config.add_route('rating_collection', '/project/{project_id}/idea/{idea_id}/rating')
    config.add_route('event_collection', '/project/{project_id}/event')
                    
    return config.make_wsgi_app()

