from pyramid.view import view_config
from models import *
from pyramid.exceptions import NotFound
from user import get_user
import logging

@view_config(route_name='user_entity', renderer="other_user.jinja2", permission='friends') 
def show_userpage(request):
    user_id = request.matchdict['user_id']
    session = DBSession()
    try:
        other_user = session.query(User).filter(User.id==user_id).one()
    except NoResultFound:
        logging.warning("User view model not found!")
        raise NotFound()
        
    current_user = get_user(request)
    shared_projects = []
    for project in current_user.projects:
        if project in other_user.projects:
            shared_projects += [project]
    
    project_data = []
    for project in shared_projects:
        data = {}
        data['title'] = project.title
        # How many ideas and comments other_user has posted to this project.
        data['idea_count'] = project.ideas.filter(Idea.author==other_user).count()
        data['comment_count'] = project.comments.filter(Comment.author==other_user).count()
        project_data += [data]

    return {
        'first_name' : other_user.first_name, 
        'last_name' : other_user.last_name, 
        'profile_picture' : other_user.profile_picture,
        'user' : current_user,
        'shared_project_count' : len(project_data),
        'projects' : project_data
    }