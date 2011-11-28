#from totter.models import DBSession
#from totter.models import MyModel
import uuid
from pyramid.view import view_config
from models import *
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('totter')

def get_test_user():
    session = DBSession()
    return session.query(User).filter(User.email=='frank@rockingchairllc.com').one()

@view_config(route_name='post_comment', request_method='POST', xhr=True, renderer='json')
def add_comment(request):
    session = DBSession()
    new_comment = session.query(Comment).filter(Comment.id==1).one()
    return {'comment_id' : '1'}
    
@view_config(route_name='post_rating', request_method='POST', xhr=True, renderer='json')
def add_rating(request):
    session = DBSession()
    
    return {}
    
@view_config(route_name='post_idea', request_method='POST', xhr=True, renderer='json')
def add_idea(request):
    session = DBSession()
    new_idea = session.query(Idea).filter(Idea.id==1).one()
    return {'idea_id' : '1'}
    
def create(request):
    return {}
    
def enterKey(request):
    return {}


@view_config(route_name='project_ideas', renderer='ideas.jinja2')
def ideas(request):
    # Optional parameters: sort="user" | "rating" | "date"
    user = get_test_user()
    project_id = uuid.UUID(hex=request.matchdict['project_id'])
    session = DBSession()
    project = session.query(Project).filter(Project.id==project_id).one()
    
    # Create list of ideas with User's rating added:
    ideas = project.ideas
    ratings = session.query(Idea, IdeaRatings)\
        .filter(Idea.project_id == project.id)\
        .filter(IdeaRatings.user_id == user.id)
        
    # Create a new field Idea.user_rating, that stores the IdeaRating for
    # the current user. We're taking advantage of SQLAlchemy's one-instance
    # per session feature, so that all project.idea entries have a user_rating field.
    for idea in ideas:
        idea.user_rating = None # This will be the field's default value.
    for idea, rating in ratings:
        idea.user_rating = rating
    # Idea.user_rating will be used to determine the initial state of the Like/Love/Stars
    return {
        'project' : project, 
        'ideas': project.ideas, 
        'user' : user, 
        'ideas_count': len(project.ideas), 
        'people_count': 1
    }
    
def login(request):
    return {}
    
def project(request):
    user_info = {'user_name' : 'Francisco Saldana', 'user_image': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-snc4/211801_1135710554_1230207683_q.jpg'}
    project_data = {'project_title' : 'Grand Opening of Hotel LaRitz',
            'author_name' : 'Francisco Saldana',
            'idea_count' : 3,
            'description' : 'We should plan something for the grand opening.',
            'deadline' : 'None',
            'updates' : [{'type' : 'Idea Added', 'who' : 'Jaime Ortega', 'when' : 'Wed 10/21/2011 at 10pm', 'what' : 'Yoga class.'},
            {'type' : 'Comment', 'who' : 'Jeremy Smith', 'when' : 'Thurs 10/11/2011 at 2pm', 'what' : 'Tell me about it.'}]
    }
    project_data.update(user_info)
    return project_data
            
    
def register(request):
    return {}
    
def stars(request):
    return ideas(request)
