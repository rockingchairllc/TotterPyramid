import facebook as fb
from pyramid.security import authenticated_userid
from pyramid.view import view_config

from facebook import OAuth2

@view_config(route_name='fb')
def facebook2(request):
    fbuser = fb.get_user_from_cookie(request.cookies, 
                        request.registry.settings['facebook.app_id'],
                        request.registry.settings['facebook.secret']
    )
    fbuser = OAuth2.getUserFromCookie(request.cookies, 
                        request.registry.settings['facebook.app_id'],
                        request.registry.settings['facebook.secret']
    )
    return {}

@view_config(route_name='fbtest', renderer='fbtest.jinja2')
def fbtest(request):
    fbuser = fb.get_user_from_cookie(request.cookies, 
                        request.registry.settings['facebook.app_id'],
                        request.registry.settings['facebook.secret']
    )
    
    message = ''
    if fbuser:
        try:
            graph = fb.GraphAPI(fbuser["access_token"])
            profile = graph.get_object("me")
            name = profile['first_name'] + profile['last_name']
            message = 'Logged in as ' + name
            message += '<br/>Email: ' + profile['email']
        except fb.GraphAPIError:
            message = 'Logged out!'
    else:
        message = '<not logged in>'
    return {'message': message,
        'app_id' : request.registry.settings['facebook.app_id']}
    