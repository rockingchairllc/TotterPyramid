#from totter.models import DBSession
#from totter.models import MyModel
import uuid
from pyramid.exceptions import NotFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config
from models import *
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('totter')

def get_user(request):
    session = DBSession()
    uid_hex = authenticated_userid(request)
    if uid_hex is None:
        return session.query(User).filter(User.email=='test@rockingchairllc.com').one()
    user_id = uuid.UUID(hex=uid_hex)
    return session.query(User).filter(User.id==user_id).one()
    
@view_config(route_name='post_comment', request_method='POST', renderer='json')
def add_comment(request):
    session = DBSession()
    comment_text = request.json_body['data']
    idea_id = request.matchdict['idea_id']
    cur_user = get_user(request)
    new_comment = Comment(idea_id=idea_id, data=comment_text)
    new_comment.author = cur_user
    session.add(new_comment)
    session.flush()
    return {'comment_id' : new_comment.id}
    
@view_config(route_name='post_rating', request_method='POST', renderer='json')
def add_rating(request):
    session = DBSession()
    cur_user = get_user(request)
    idea_id = request.matchdict['idea_id']
    rating_data = request.json_body
    
    old_rating = session.query(UserRating)\
        .filter(UserRating.rater==cur_user)\
        .filter(UserRating.idea_id==idea_id).first() or UserRating(rater=cur_user, idea_id=idea_id)
    changed = False
    loves = 0
    likes = 0
    # Handle unlikes/unloves first:
    if 'like' in rating_data and not rating_data['like']:
        # Unliked the post.
        if old_rating.liked:
            old_rating.liked = False
            likes = -1
    if 'love' in rating_data and not rating_data['love']:
        # Unloved the post.
        if old_rating.loved:
            old_rating.loved = False
            loves = -1
            
    # Handle likes/loves:
    if 'like' in rating_data and rating_data['like']:
        # Liked the post.
        if not old_rating.liked:
            old_rating.liked = True
            likes = 1
    if 'love' in rating_data and rating_data['love']:
        # Loved the post.
        if not old_rating.loved:
            old_rating.loved = True
            loves = 1
    if likes == 1 and loves == 1:
        # Client error.
        pass
    session.merge(old_rating)
    # Update aggregate count:
    if likes or loves:
        agg_rating = session.query(AggregateRating)\
            .filter(AggregateRating.idea_id==idea_id).first() or AggregateRating(idea_id=idea_id)
            
        agg_rating.liked += likes
        agg_rating.loved += loves
        agg_rating.count += 1
        session.merge(agg_rating)
    
    session.flush()
    return {}
    
@view_config(route_name='post_idea', request_method='POST', renderer='json')
def add_idea(request):
    session = DBSession()
    idea_text = request.json_body['data']
    project_id = uuid.UUID(hex=request.matchdict['project_id'])
    cur_user = get_user(request)
    new_idea = Idea(project_id=project_id, data=idea_text)
    new_idea.author = cur_user
    session.add(new_idea)
    session.flush()
    return {'idea_id' : new_idea.id}
    
def create(request):
    return {}
    
def enterKey(request):
    return {}


@view_config(route_name='project_ideas', renderer='ideas.jinja2')
def ideas(request):
    # Optional parameters: sort="user" | "rating" | "date"
    user = get_user(request)
    project_id = uuid.UUID(hex=request.matchdict['project_id'])
    session = DBSession()
    try:
        project = session.query(Project).filter(Project.id==project_id).one()
    except NoResultFound:
        raise NotFound()
        
    # Create list of ideas with User's rating added:
    ideas = project.ideas
    ratings = session.query(Idea, UserRating)\
        .filter(Idea.project_id == project.id)\
        .filter(UserRating.user_id == user.id)
        
    # Create a new field Idea.user_rating, that stores the IdeaRating for
    # the current user. We're taking advantage of SQLAlchemy's one-instance
    # per session feature, so that all project.idea entries have a user_rating field.
    for idea in ideas:
        idea.user_rating = None # This will be the field's default value.
        idea.total_rating = 0
        if idea.aggregate_rating is not None:
            idea.total_rating = idea.aggregate_rating.likes + idea.aggregate_rating.loves * 2
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
