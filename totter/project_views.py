#from totter.models import DBSession
#from totter.models import MyModel
import uuid
from pyramid.exceptions import NotFound
from pyramid.security import has_permission
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.view import view_config
from models import *
from pyramid.i18n import TranslationStringFactory
from datetime import datetime, timedelta
from template import timefmt
from urllib import urlencode
from mail import send_email
_ = TranslationStringFactory('totter')
import logging
from user import get_user

notwhite = lambda value: value is not None and len(value.strip()) > 0
notwhite.explanation = 'Value must be one or more non-whitespace characters.'
def validate_params(request, params):
    if instanceof(params, dict):
        validators = params.values()
        params = params.keys()
    else:
        validators = [None]*len(params)
    
    for i, param in enumerate(params):
        if param not in request.params:
            raise HTTPBadRequest(explanation='Expected parameter: ' + param)
        if validator[i] and not validator(request.params[param]):
            if validator[i].explanation:
                raise HTTPBadRequest(explanation=explanation)
            else:
                raise HTTPBadRequest(explanation=param + ' is not valid.')
    return True
    

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

@view_config(route_name='comment_collection', request_method='POST', renderer='json', xhr=True, permission='post')
def add_comment(request):
    # Add comment request body is JSON-encoded with parameters:
    # 'data' : The comment text.
    session = DBSession()
    comment_text = request.json_body['data']
    idea_id = request.matchdict['idea_id']
    project_id = request.matchdict['project_id']
    cur_user = get_user(request)
    new_comment = Comment(project_id=project_id, idea_id=idea_id, data=comment_text)
    new_comment.author = cur_user
    session.add(new_comment)
    session.flush()
    
    # Record event:
    idea_author = session.query(Idea).filter(Idea.id==idea_id).one().author
    record_event(u'add_comment', request.json_body['project_id'], datetime.now(), {
        'commenter_first' : cur_user.first_name,
        'commenter_last' : cur_user.last_name,
        'comment_uri' : request.current_route_url() + '/' + str(new_comment.id),
        'idea_first' : idea_author.first_name,
        'idea_last' : idea_author.last_name,
        })
    return {'comment_id' : new_comment.id}
    
@view_config(route_name='project_update', request_method='POST', renderer='json', xhr=True, permission='edit')
def add_update(request):
    # Add comment request body is JSON-encoded with parameters:
    # 'data' : The comment text.
    session = DBSession()
    project_id = request.matchdict['project_id']
    update_text = request.json_body['data']
    cur_user = get_user(request)
    new_update = ProjectUpdate(project_id=project_id, data=update_text)
    session.add(new_update)
    session.flush()
    
    # Record event:
    return {'id' : new_update.id, 'when' : timefmt(new_update.when), 'data' : new_update.data}
    
    
    
@view_config(route_name='rating_collection', request_method='POST', renderer='json', xhr=True, permission='post')
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
    agg_rating = session.query(AggregateRating)\
            .filter(AggregateRating.idea_id==idea_id).first() or AggregateRating(idea_id=idea_id)
    if likes or loves: # User did something worth tracking.
        
            
        agg_rating.liked += likes
        agg_rating.loved += loves
        agg_rating.count += likes + loves
        # Case: User switches like for love: like=-1, love=1. count does nothing
        # Case: User likes: like=1,love=0. Count increments.
        # Case: User unlikes: like=-1,love=0. Count decrements.
        session.merge(agg_rating)
    
    session.flush()
    return {
        'total_rating' : agg_rating.liked + agg_rating.loved * 2, 
        'rating' : {'loved' : new_rating.loved or 0, 'liked' : new_rating.liked or 0}
    }
    
@view_config(route_name='idea_collection', request_method='POST', renderer='json', xhr=True, permission='post')
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
    record_event(u'add_idea', request.json_body['project_id'], datetime.now(), {
        'idea_uri' : request.current_route_url() + '/' + str(new_idea.id),
        'idea_first' : new_idea.author.first_name,
        'idea_last' : new_idea.author.last_name,
        })
        
    return {'idea_id' : new_idea.id, 'ideas_count' : project.ideas.count()}

@view_config(route_name='project_ideas', renderer='ideas.jinja2', permission='view')
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
    if user:
        idea_data = session.query(Idea, UserRating)\
            .outerjoin(UserRating, (Idea.id==UserRating.idea_id) & (UserRating.user_id==user.id))\
            .join(User, (Idea.author_id==User.id))\
            .filter(Idea.project_id == project.id)
    else:
        idea_data = session.query(Idea)\
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
    
    if user is None:
        # Create the 2-tuple that we'd get with a normal user:
        idea_data = zip(idea_data, [None]*len(idea_data))
    
    # Create a new field Idea.user_rating, that stores the IdeaRating for
    # the current user. We're taking advantage of SQLAlchemy's one-instance
    # per session feature, so that all project.idea entries have a user_rating field.
    for i in range(len(idea_data)):
        idea, rating = idea_data[i]
        
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
        'ideas_count': len(idea_data), 
        'people_count': 1
    }
    


@view_config(route_name='project_entity', renderer='project_overview.jinja2', permission='view', request_method='GET')
def project(request):
    user = get_user(request)
    project_id = uuid.UUID(hex=request.matchdict['project_id'])
    session = DBSession()
    try:
        project = session.query(Project).filter(Project.id==project_id).one()
    except NoResultFound:
        raise NotFound()
        
    updates = session.query(ProjectUpdate)\
        .filter(ProjectUpdate.project_id==project_id)\
        .filter(ProjectUpdate.when >= datetime.today() - timedelta(days=10))\
        .order_by(ProjectUpdate.when.desc()).limit(10).all()
    
    # Update user access time:
    if user:
        session.merge(Participation(user_id=user.id, project_id=project.id, access_time=datetime.now()))
    
    return {
        'editable' : has_permission('edit', request.context, request),
        'project_id' : project_id,
        'project' : project, 
        'updates' : updates,
        'ideas': project.ideas.all(), 
        'user' : user, 
        'ideas_count': project.ideas.count(), 
        'people_count': 1
    }
@view_config(route_name='project_entity', renderer='string', permission='view', request_method='POST')
def edit_project(request):
    project_id = request.matchdict['project_id']
    session = DBSession()
    try:
        project = session.query(Project).filter(Project.id==project_id).one()
    except NoResultFound:
        raise NotFound()
        
    logging.info('edit_project'  + str(request.params))
    # jquery.jeditable.js passes us two parameters. 
    # id: id of the element edited
    # value: new value the user typed in
    id = request.params['id']
    value = request.params['value']
    if id == 'title':
        project.title = value
    elif id == 'description':
        project.description = value
    return value
    
@view_config(route_name='project_people', renderer='project_people.jinja2', permission='view')
def display_project_people(request):
    user = get_user(request)
    project_id = uuid.UUID(hex=request.matchdict['project_id'])
    session = DBSession()
    try:
        project = session.query(Project).filter(Project.id==project_id).one()
    except NoResultFound:
        raise NotFound()
        
    people_bucket = {}
    
    people_bucket[project.creator.id] = project.creator
    
    for idea in project.ideas.all():
        people_bucket[idea.author.id] = idea.author
        for comment in idea.comments:
            people_bucket[comment.author.id] = comment.author
    
    # Sort by first last name
    people_data = people_bucket.values()
    people_data.sort(key=lambda user: user.first_name + ' ' + user.last_name)
    
    return {
        'people' : people_data,
        'project_id' : project_id,
        'project' : project, 
        'user' : user, 
        'ideas_count': project.ideas.count(), 
        'people_count': 1,
    }

@view_config(route_name='create_project', renderer='create.jinja2', permission='create')
def create(request):
    user = get_user(request)
    
    if 'project_key' in request.params:
        # User submitted a project.
        # TODO: Validation.
        new_project = Project(
            title=request.params['project_title'],
            key=request.params['project_key'],
            description=request.params['project_description'],
            url_name=request.params['project_url'],
            creator_id=user.id)
            
        participation = Participation(user=user, project=new_project)
        try: 
            session = DBSession()
            session.add(new_project)
            session.add(participation)
            session.flush()
        except IntegrityError:
            # url_name collision.
            raise HTTPBadRequest(explanation="Sorry! That URL has already been taken!")
        return HTTPFound(location=request.route_url('project_invite', project_id=new_project.id))
    else:
        return {'user' : user}

@view_config(route_name='project_invite', renderer='invite.jinja2', permission='invite')
def invite(request):
    project_id = request.matchdict['project_id']
    session = DBSession()
    try:
        project = session.query(Project).filter(Project.id==project_id).one()
    except NoResultFound:
        raise NotFound()
    user = get_user(request)
    redirect_uri = request.route_url('project_entity', project_id=project_id)
    
    iframe_url = 'https://www.facebook.com/dialog/apprequests?access_token=%(access_token)s&api_key=%(api_key)s&app_id=%(app_id)s&display=iframe&frictionless=false&locale=en_US&message=%(message)s&next=%(next)s' % {
        'access_token' : request.session['access_token'] if 'access_token' in request.session else None,
        'api_key' : request.registry.settings['facebook.app_id'],
        'app_id' : request.registry.settings['facebook.app_id'],
        'message' : "WEE ARE THE CHAMPIONS",
        'next' : redirect_uri
    }
    
    response_params = {}
    if 'email_0' in request.params:
        emails = []
        i = 0
        while 'email_' + str(i) in request.params:
            email = request.params['email_'+str(i)]
            if email:
                emails += [email]
            i += 1
        if emails:
            logging.info('Sending invite message for project ' + str(project.id))
            message = request.params['message']
            send_email(user.email, emails, "You've been invited!", message)
            response_params['invited'] = True
            response_params['invitee_count'] = len(emails)
    else:
        if request.referrer == request.route_url('create_project'):
            response_params['created'] = True
        
    
    response_params.update({'user' : user, 
    'project' : {'key':project.key,'title':project.title, 'url': request.route_url('project_entity', project_id=project.id)},
    'creator' : {'first_name' : project.creator.first_name, 'last_name' : project.creator.last_name},
    'fb_app_id' : request.registry.settings['facebook.app_id'],
    'iframe_url' : iframe_url,
    'fb_access_token' : request.session['access_token'] if 'access_token' in request.session else None,
    })
    return response_params
    
def enterKey(request):
    return {}
    
def register(request):
    return {}
    
def stars(request):
    return ideas(request)
