import facebook as fb
from pyramid.security import authenticated_userid
from pyramid.view import view_config

@view_config(route_name='fb')
def facebook2(request):
    fbuser = fb.get_user_from_cookie(request.cookies, 
                        request.registry.settings['facebook.app_id'],
                        request.registry.settings['facebook.secret']
    )
    return {}
    
def fbtest(request):
    return {'app_id' : request.registry.settings['facebook.app_id']}
    