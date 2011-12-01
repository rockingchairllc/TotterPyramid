#from totter.models import DBSession
#from totter.models import MyModel
import uuid
from pyramid.exceptions import NotFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config
from models import *
from pyramid.i18n import TranslationStringFactory
from datetime import datetime, timedelta
_ = TranslationStringFactory('totter')
import logging
def get_user(request):
    session = DBSession()
    uid_hex = authenticated_userid(request)
    if uid_hex is None:
        return session.query(User).filter(User.email=='test@rockingchairllc.com').one()
    user_id = uuid.UUID(hex=uid_hex)
    return session.query(User).filter(User.id==user_id).one()

def record_event(action, project_id, time, action_data):
    # TODO: Deferred processing?
    #return # weird utf8 bugs in json encoder...
    session = DBSession()
    new_event = ProjectEvent(project_id=project_id, type=action, when=time, data=action_data)
    session.add(new_event)
    
@view_config(route_name='event_collection', request_method='GET', renderer='json')
def get_event_list(request):
    # Grabs the list of events for a particular project.
    project_id = request.matchdict['project_id']
    # Last ID received by client, client can call again to get new events:
    last_id = request.params.get('last_received_id')
    
    return {}

@view_config(route_name='comment_collection', request_method='POST', renderer='json')
def add_comment(request):
    # Add comment request body is JSON-encoded with parameters:
    # 'data' : The comment text.
    session = DBSession()
    comment_text = request.json_body['data']
    idea_id = request.matchdict['idea_id']
    cur_user = get_user(request)
    new_comment = Comment(idea_id=idea_id, data=comment_text)
    new_comment.author = cur_user
    session.add(new_comment)
    session.flush()
    
    # Record event:
    idea_author = session.query(Idea).filter(Idea.id==idea_id).one().author
    record_event('add_comment', request.json_body['project_id'], datetime.now(), {
        'commenter_first' : cur_user.first_name,
        'commenter_last' : cur_user.last_name,
        'comment_uri' : request.current_route_url() + '/' + str(new_comment.id),
        'idea_first' : idea_author.first_name,
        'idea_last' : idea_author.last_name,
        })
    return {'comment_id' : new_comment.id}
    
    
@view_config(route_name='rating_collection', request_method='POST', renderer='json')
def add_rating(request):
    # Add rating request body is JSON-encoded with parameters:
    # 'like' : Boolean, True if user Liked a post, False if he unliked it.
    # 'love' : Boolean, True if user loved a post, False is she unloved it.
    
    session = DBSession()
    cur_user = get_user(request)
    idea_id = request.matchdict['idea_id']
    rating_data = request.json_body
    
    logging.warn('Rating received ' + str(rating_data))
    
    # Get the old rating, or make a new one if user never rated this post:
    old_rating = session.query(UserRating)\
        .filter(UserRating.rater==cur_user)\
        .filter(UserRating.idea_id==idea_id).first()\
        or UserRating(user_id=cur_user.id, idea_id=idea_id)
    new_rating = UserRating(user_id=cur_user.id, idea_id=idea_id)
    
    logging.warn('old rating loved: %d, liked: %d' % (old_rating.loved or 0, old_rating.liked or 0))
    
    # loves, likes track the change in the user's rating.
    loves = 0
    likes = 0
    # Handle unlikes/unloves first:
    if 'like' in rating_data and not rating_data['like']:
        # Unliked the post.
        if old_rating.liked:
            new_rating.liked = False
            likes = -1
    if 'love' in rating_data and not rating_data['love']:
        # Unloved the post.
        if old_rating.loved:
            new_rating.loved = False
            loves = -1
            
    # Handle likes/loves:
    if 'like' in rating_data and rating_data['like']:
        # Liked the post.
        if not old_rating.liked:
            new_rating.liked = True
            likes = 1
        if old_rating.loved:
            new_rating.loved = False
            loves = -1
    if 'love' in rating_data and rating_data['love']:
        # Loved the post.
        if not old_rating.loved:
            new_rating.loved = True
            loves = 1
        if old_rating.liked:
            new_rating.liked = False
            likes = -1
    
    if likes == 1 and loves == 1:
        # Client error. User shouldn't be able to like and love at the same time. 
        new_rating.liked = False
        likes = 0
    session.merge(new_rating)
    logging.warn('%s love: %d, like: %d' % (cur_user.first_name, loves, likes))
    
    # Update aggregate count:
    if likes or loves: # User did something worth tracking.
        agg_rating = session.query(AggregateRating)\
            .filter(AggregateRating.idea_id==idea_id).first() or AggregateRating(idea_id=idea_id)
            
        agg_rating.liked += likes
        agg_rating.loved += loves
        agg_rating.count += likes + loves
        # Case: User switches like for love: like=-1, love=1. count does nothing
        # Case: User likes: like=1,love=0. Count increments.
        # Case: User unlikes: like=-1,love=0. Count decrements.
        session.merge(agg_rating)
    
    session.flush()
    return {}
    
@view_config(route_name='idea_collection', request_method='POST', renderer='json')
def add_idea(request):
    # Idea request body is JSON encoded with parameters:
    # 'data' : The idea text
    session = DBSession()
    idea_text = request.json_body['data']
    project_id = uuid.UUID(hex=request.matchdict['project_id'])
    cur_user = get_user(request)
    new_idea = Idea(project_id=project_id, data=idea_text)
    new_idea.author = cur_user
    session.add(new_idea)
    session.flush()
    
    try:
        project = session.query(Project).filter(Project.id==project_id).one()
    except NoResultFound:
        raise NotFound()
        
    # Record event:
    record_event('add_idea', request.json_body['project_id'], datetime.now(), {
        'idea_uri' : request.current_route_url() + '/' + str(new_idea.id),
        'idea_first' : new_idea.author.first_name,
        'idea_last' : new_idea.author.last_name,
        })
        
    return {'idea_id' : new_idea.id, 'ideas_count' : len(project.ideas)}

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
    idea_data = session.query(Idea, UserRating)\
        .outerjoin(UserRating, (Idea.id==UserRating.idea_id) & (UserRating.user_id==user.id))\
        .join(User, (Idea.author_id==User.id))\
        .filter(Idea.project_id == project.id)
    
    sort = request.params.get('sort')
    if sort == 'user':
        idea_data = idea_data.order_by(User.first_name)
    elif sort == 'rating':
        # Use Python to sort it. 
        pass
    elif sort == 'date':
        idea_data = idea_data.order_by(Idea.creation_time.desc()) # Most recent first
    else:
        logging.warn('Unrecognized sort: ' + str(sort))
    
    idea_data = idea_data.all()
    
    # Create a new field Idea.user_rating, that stores the IdeaRating for
    # the current user. We're taking advantage of SQLAlchemy's one-instance
    # per session feature, so that all project.idea entries have a user_rating field.
    for i in range(len(idea_data)):
        idea, rating, _ = idea_data[i]
        
        # Compute total numeric rating:
        total_rating = 0
        if idea.aggregate_rating is not None:
            total_rating = idea.aggregate_rating.liked + idea.aggregate_rating.loved * 2
        
        idea_data[i] = {}
        idea_data[i]['idea'] = idea
        idea_data[i]['user_rating'] = rating or UserRating()
        idea_data[i]['total_rating'] = total_rating
        
    # Handle sort by rating:
    if sort == 'rating':
        # Descending (highest rating first)
        idea_data.sort(key=lambda el:el['total_rating'], reverse=True)
    
    # Idea.user_rating will be used to determine the initial state of the Like/Love/Stars
    return {
        'project' : project, 
        'project_id' : project_id,
        'idea_data': idea_data, 
        'user' : user, 
        'ideas_count': len(project.ideas), 
        'people_count': 1
    }
    


@view_config(route_name='project_entity', renderer='project_overview.jinja2')
def project(request):
    user = get_user(request)
    project_id = uuid.UUID(hex=request.matchdict['project_id'])
    session = DBSession()
    try:
        project = session.query(Project).filter(Project.id==project_id).one()
    except NoResultFound:
        raise NotFound()
        
    events = session.query(ProjectEvent)\
        .filter(ProjectEvent.project_id==project_id)\
        .filter(ProjectEvent.when >= datetime.today() - timedelta(days=10))\
        .order_by(ProjectEvent.when.desc()).limit(10)
    
    return {
        'project_id' : project_id,
        'project' : project, 
        'events' : events,
        'ideas': project.ideas, 
        'user' : user, 
        'ideas_count': len(project.ideas), 
        'people_count': 1
    }
@view_config(route_name='project_people', renderer='project_people.jinja2')
def display_project_people(request):
    user = get_user(request)
    project_id = uuid.UUID(hex=request.matchdict['project_id'])
    session = DBSession()
    try:
        project = session.query(Project).filter(Project.id==project_id).one()
    except NoResultFound:
        raise NotFound()
        
    people_bucket = {}
    
    for idea in project.ideas:
        people_bucket[idea.author.id] = idea.author
        for comment in idea.comments:
            people_bucket[comment.author.id] = comment.author
    
    return {
        'people' : people_bucket.values(),
        'project_id' : project_id,
        'project' : project, 
        'user' : user, 
        'ideas_count': len(project.ideas), 
        'people_count': 1,
    }

def login(request):
    return {}
    
def create(request):
    return {}
    
def enterKey(request):
    return {}
    
def register(request):
    return {}
    
def stars(request):
    return ideas(request)
