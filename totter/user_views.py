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
    
@view_config(route_name="dashboard", renderer="dashboard.jinja2")
def show_dashboard(request):
    user = get_user(request)
    if not user:
        return HTTPFound(location=request.route_url('login'))
    
    # Get the projects the user participates in, and data about that participation.
    session = DBSession()
    participations = session.query(Participation).filter(Participation.user_id==user.id)
    
    invited_projects = []
    other_projects = []
    for participation in participations:
        project = participation.project
        project_data = {
            'title' : project.title, 
            'url' : request.route_url('project_entity', project_id=project.id)
        }
        if project.creator_id == user.id: # We add these to created_projects below.
            continue
        if participation.access_time: 
            other_projects += [project_data]
        else:
            invited_projects += [project_data]
    
    # Get information about projects user has created.
    created_projects = session.query(Project).filter(Project.creator_id==user.id)
    created_projects = [
        {'title' : project.title, 'url' : request.route_url('project_entity', project_id=project.id)}
        for project in created_projects
    ]
    
        
    
    return {
        'user' : user,
        'learn_more_link' : request.route_url('home'),
        'created_projects' : created_projects,
        'invited_projects' : invited_projects,
        'other_projects' : other_projects
    }

