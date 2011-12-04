from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from totter.models import initialize_sql
from totter.user import groupfinder
from totter.routes import RootFactory

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    authn_policy = AuthTktAuthenticationPolicy('#%DSDsad2', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    session_factory = UnencryptedCookieSessionFactoryConfig('89az9*l&uw')
    config = Configurator(settings=settings,
                          root_factory=RootFactory,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory=session_factory)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'totter:static', cache_max_age=3600)
    config.scan()
    config.add_route('home', '/')

    config.add_route('create_project', '/project/new')
    config.add_view('totter.project_views.create',
                    route_name='create_project',
                    renderer='create.jinja2',
                    permission='edit')
                                        
    config.add_route('login', '/login')

    config.add_route('facebook', '/facebook')
    config.add_view('totter.user.facebook',
                    route_name='facebook',
                    renderer='message.jinja2')
    
    # Facebook client-side testing:
    config.add_route('fb', '/fb')
    config.add_route('fbtest', '/fbtest')
    config.add_view('totter.fb.fbtest',
                    route_name='fbtest',
                    renderer='fbtest.jinja2')

    config.add_route('logout', '/logout')
    config.add_view('totter.user.logout', route_name='logout')

    config.add_route('project_entity', '/project/{project_id}/', factory=RootFactory, traverse='/project/{project_id}')
                    
    config.add_route('project_ideas', '/project/{project_id}/ideas', factory=RootFactory, traverse='/project/{project_id}')
    config.add_route('project_people', '/project/{project_id}/people', factory=RootFactory, traverse='/project/{project_id}')
    config.add_route('project_update', '/project/{project_id}/updates', factory=RootFactory, traverse='/project/{project_id}')
    
    # "Magical" append slash not found view. Appends a slash when there's a route that matches the slash-ended url.
    config.add_view('pyramid.view.append_slash_notfound_view',
                context='pyramid.httpexceptions.HTTPNotFound')
                
    config.add_route('register', '/register')
    config.add_view('totter.user.register',
                    route_name='register',
                    renderer='register.jinja2')
                    
    config.add_route('stars', '/project/{project_id}/stars')
    config.add_view('totter.project_views.stars',
                    route_name='stars',
                    renderer='stars.jinja2')
                    
    # For XMLHttpRequest
    config.add_route('comment_collection', '/project/{project_id}/idea/{idea_id}/comment')
    config.add_route('comment_entity', '/project/{project_id}/idea/{idea_id}/comment/{comment_id}')
    config.add_route('idea_collection', '/project/{project_id}/idea')
    config.add_route('idea_entity', '/project/{project_id}/idea/{idea_id}')
    config.add_route('rating_collection', '/project/{project_id}/idea/{idea_id}/rating')
    config.add_route('event_collection', '/project/{project_id}/event')
    
    config.add_route('user_entity', '/user/{user_id}/', factory=RootFactory, traverse='/user/{user_id}')
    
    return config.make_wsgi_app()

