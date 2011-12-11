from user import get_user
from pyramid.httpexceptions import HTTPBadRequest

@view_config(context='totter.models.Project',  name='publish_stream', permission='invite')
def publish_stream(request):
    user = get_user(request)
    project = request.context
    profile_ids = request.json_body['selected_friends']
    if 'access_token' not in request.session:
        return HTTPBadRequest('No facebook access token for ' + user.full_name)
        
    graph = fb.GraphAPI(request.session['access_token'])
    """
    put_wall_post(self, message, attachment={}, profile_id="me"):
    
    attachment adds a structured attachment to the status message being
    posted to the Wall. It should be a dictionary of the form:

        {"name": "Link name"
         "link": "http://www.example.com/",
         "caption": "{*actor*} posted a new review",
         "description": "This is a longer description of the attachment",
         "picture": "http://www.example.com/thumbnail.jpg"}
    """
    
    message = """
    I've invited you to the Totter project, '%s'. 
    Visit http://letstotter.com and login with facebook to 
    start creating automatically. Or, check your facebook messages 
    for credentials. Totter: Where Ideas Come To Play!
    """ % project.title
    for id in profile_ids:
        graph.put_wall_post(message, {
            'name' : project.title,
            'link' : request.application_url,
            'caption' : 'Totter: Where Ideas Come To Play!',
            'description' : '',
            'picture' : request.static_url('totter:static/images/logo.png'),
        }, id)