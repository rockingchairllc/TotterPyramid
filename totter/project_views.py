#from totter.models import DBSession
#from totter.models import MyModel
import uuid
import socket
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
from template import user_dict, idea_dict, comment_dict


def record_event(action, project_id, time, action_data):
    # TODO: Deferred processing?
    #return # weird utf8 bugs in json encoder...
    session = DBSession()
    new_event = ProjectEvent(project_id=project_id, type=action, when=time, data=action_data)
    session.add(new_event)


@view_config(context='totter.models.CommentContainer', name='', request_method='POST', renderer='json', xhr=True, permission='post')
def add_comment(request):
    # Add comment request body is JSON-encoded with parameters:
    # 'data' : The comment text.
    comment_text = request.json_body['data']
    anonymous = request.json_body['anonymous']
    cur_user = get_user(request)
    session = DBSession()
    
    new_comment = request.context.newComment(data=comment_text, anonymous=anonymous, author=cur_user)
    
    # Record event:
    idea_author = session.query(Idea).filter(Idea.id==request.context.idea.id).one().author
    record_event(u'add_comment', request.json_body['project_id'], utcnow(), {
        'commenter_first' : cur_user.first_name,
        'commenter_last' : cur_user.last_name,
        'comment_uri' : request.resource_url(new_comment),
        'idea_first' : idea_author.first_name,
        'idea_last' : idea_author.last_name,
        })
    return {'comment_id' : new_comment.id}
    
@view_config(context='totter.models.Project', name='updates', request_method='POST', renderer='json', xhr=True, permission='edit')
def add_update(request):
    # Add comment request body is JSON-encoded with parameters:
    # 'data' : The comment text.
    session = DBSession()
    project_id = request.context.id
    update_text = request.json_body['data']
    cur_user = get_user(request)
    new_update = ProjectUpdate(project_id=project_id, data=update_text)
    session.add(new_update)
    session.flush()
    
    # Record event:
    return {'id' : new_update.id, 'when' : timefmt(new_update.when), 'data' : new_update.data}
    
    

@view_config(context='totter.models.Idea', name='rating', request_method='POST', renderer='json', xhr=True, permission='post')
def add_rating(request):
    # Add rating request body is JSON-encoded with parameters:
    # 'like' : Boolean, True if user Liked a post, False if he unliked it.
    # 'love' : Boolean, True if user loved a post, False is she unloved it.
    
    
    cur_user = get_user(request)
    idea_id = request.context.id
    rating_data = request.json_body
    
    if not ('like' in rating_data or 'love' in rating_data or 'stars' in rating_data):
        raise HTTPBadRequest
    
    logging.warn('Rating received ' + str(rating_data))
    
    if 'stars' in rating_data:
        return star_rating(idea_id, cur_user, rating_data)
    else:
        return like_love_rating(idea_id, cur_user, rating_data)
        
def star_rating(idea_id, cur_user, rating_data):
    session = DBSession()
    stars = rating_data['stars']
    old_rating = session.query(UserRating)\
        .filter(UserRating.rater==cur_user)\
        .filter(UserRating.idea_id==idea_id).first()
        
    new_rating = UserRating(user_id=cur_user.id, idea_id=idea_id, stars=stars)
    
    # Compute change in aggregate
    star_delta = stars
    if old_rating:
        star_delta = stars - (old_rating.stars if old_rating.stars else 0)
    
    # Stars is simpler then like_love. If the user has starred something
    # He can never unstar it.
    agg_rating = session.query(AggregateRating)\
            .filter(AggregateRating.idea_id==idea_id).first() or AggregateRating(idea_id=idea_id)
    if star_delta != 0: 
        if not old_rating or not old_rating.stars and star_delta > 0:
            agg_rating.count += 1 # This user hasn't rated this project before.
        elif old_rating and old_rating.stars + star_delta == 0:
            agg_rating.count -= 1 # Don't count it toward the total.
        
    agg_rating.stars += star_delta
    
    session.merge(agg_rating)
    session.merge(new_rating)
    session.flush()
    
    return {'rating' : {'stars' : new_rating.stars}, 'total_stars' : agg_rating.average_stars, 'rating_count' : agg_rating.count}
    
def like_love_rating(idea_id, cur_user, rating_data):
    session = DBSession()
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
        'total_rating' : agg_rating.total_rating, 
        'rating' : {'loved' : new_rating.loved or 0, 'liked' : new_rating.liked or 0}
    }

@view_config(context='totter.models.IdeaContainer', name='', request_method='POST', renderer='json', xhr=True, permission='post')
def add_idea(request):
    # Idea request body is JSON encoded with parameters:
    # 'data' : The idea text
    session = DBSession()
    idea_text = request.json_body['data']
    anonymous = request.json_body['anonymous']
    cur_user = get_user(request)
    
    new_idea = request.context.newIdea(data=idea_text, anonymous=anonymous, author=cur_user)
    
    # Record event:
    record_event(u'add_idea', request.json_body['project_id'], utcnow(), {
        'idea_uri' : request.resource_url(new_idea),
        'idea_first' : new_idea.author.first_name,
        'idea_last' : new_idea.author.last_name,
        })
        
    return {'idea_id' : new_idea.id, 'ideas_count' : request.context.project.ideas.count()}

@view_config(context='totter.models.Project', name='ideas', renderer='ideas.jinja2', permission='view')
def ideas(request):
    # Optional parameters: sort="user" | "rating" | "date"
    user = get_user(request)
    session = DBSession()
    project = request.context
    # Create list of ideas with User's rating added:
    if user:
        idea_query = session.query(Idea, AggregateRating, UserRating)\
            .outerjoin(AggregateRating, (AggregateRating.idea_id==Idea.id))\
            .outerjoin(UserRating, (Idea.id==UserRating.idea_id) & (UserRating.user_id==user.id))\
            .join(User, (Idea.author_id==User.id))\
            .filter(Idea.project_id == project.id)
    else:
         # Just fill third column with Nones.
        idea_query = session.query(Idea, AggregateRating, UserRating)\
            .outerjoin(AggregateRating, (AggregateRating.idea_id==Idea.id))\
            .outerjoin(UserRating, (UserRating.idea_id==0))\
            .join(User, (Idea.author_id==User.id))\
            .filter(Idea.project_id == project.id)
            
    
    sort = request.params.get('sort', 'rating') 
    if sort == 'user':
        # Use Python to sort, so we sort Anonymous posts properly.
        pass
    elif sort == 'rating':
        # Use Python to sort, so we can use our total_rating algorithm..
        pass
    elif sort == 'date':
        idea_query = idea_query.order_by(Idea.creation_time.desc()) # Most recent first
    else:
        logging.warn('Unrecognized sort: ' + str(sort))
    
    idea_data = idea_query.all()
    # Do python sorting.
    if sort == 'user':
        idea_data.sort(key=lambda el:el[0].author.first_name + ' ' + el[0].author.last_name if not el[0].anonymous else 'Anonymous')
    elif sort == 'rating':
        if project.rating_type == 'like/love':
            idea_data.sort(key=lambda el: el[0].aggregate_rating.total_rating if el[0].aggregate_rating else 0, reverse=True)
        else:
            idea_data.sort(key=lambda el: el[0].aggregate_rating.average_stars if el[0].aggregate_rating else 0, reverse=True)
    
    # Turn it all into dicts for our templating engine.
    for i in range(len(idea_data)):
        idea, aggregate_rating, rating = idea_data[i]
        idea_data[i] = idea_dict(request, idea, rating, aggregate_rating, include_comments=True)
        
    
    # Idea.user_rating will be used to determine the initial state of the Like/Love/Stars
    return template_permissions(request, {
        'project' : project, 
        'creator' : user_dict(request, project.creator),
        'project_id' : project.id,
        'idea_data': idea_data, 
        'user' : user_dict(request, user), 
        'ideas_count': len(idea_data), 
        'people_count': 1
    })
    
def template_permissions(request, template_params):
    template_params.update({
        'editable' : has_permission('edit', request.context, request),
        'show_invite' : has_permission('invite', request.context, request),
    })
    return template_params

@view_config(context='totter.models.Project', name='', renderer='project_overview.jinja2', permission='view', request_method='GET')
def project(request):
    user = get_user(request)
    session = DBSession()
    project = request.context
        
    updates = session.query(ProjectUpdate)\
        .filter(ProjectUpdate.project_id==project.id)\
        .filter(ProjectUpdate.when >= utcnow() - timedelta(days=10))\
        .order_by(ProjectUpdate.when.desc()).limit(10).all()
    
    # Update user access time:
    if user:
        session.merge(Participation(user_email=user.email, project_id=project.id, access_time=utcnow()))
    
    return template_permissions(request, {
        'project_id' : project.id,
        'project' : project, 
        'creator' : user_dict(request, project.creator),
        'updates' : updates,
        'ideas': project.ideas.all(), 
        'user' : user_dict(request, user), 
        'ideas_count': project.ideas.count(), 
        'people_count': 1
    })
    
@view_config(context='totter.models.Project', name='', renderer='string', permission='edit', request_method='POST')
def edit_project(request):
    session = DBSession()
    project = request.context
        
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
    
@view_config(context='totter.models.Project', name='people', renderer='project_people.jinja2', permission='view')
def display_project_people(request):
    cur_user = get_user(request)
    session = DBSession()
        
    project = request.context
    
    participants = session.query(Participation, User).outerjoin(User).filter(Participation.project == project).all()
    people_data = []
    email_data = []
    for participant, user in participants:
        person_data = {}
        if user:
            person_data['first_name'] = user.first_name
            person_data['last_name'] = user.last_name
            person_data['profile_url'] = request.root.user_url(user)
            person_data['invite_accepted'] = participant.access_time is not None
            person_data['profile_picture'] = user.profile_picture
            people_data += [person_data]
        else:
            email_data += [participant.user_email]
    
    # Sort by first last name
    people_data.sort(key=lambda user: user['first_name'] + u' ' + user['last_name'])
    
    
    return template_permissions(request, {
        'people' : people_data,
        'invited_emails' : email_data,
        'project_id' : project.id,
        'project' : project, 
        'creator' : user_dict(request, project.creator),
        'user' : user_dict(request, cur_user), 
        'ideas_count': project.ideas.count(), 
        'people_count': len(active_users(project)),
    })

# Returns a list of users that have commented or posted an idea on the project.
def active_users(project):
    people_bucket = {}
    people_bucket[project.creator.id] = project.creator
    for idea in project.ideas.all():
        people_bucket[idea.author.id] = idea.author
        for comment in idea.comments:
            people_bucket[comment.author.id] = comment.author
    return people_bucket.values()

@view_config(context='totter.models.ProjectLongname',  name='new', renderer='create.jinja2', permission='create')
def create(request):
    user = get_user(request)
    
    if 'project_key' in request.params:
        # User submitted a project.
        # TODO: Validation.
        try: 
            new_project = request.context.newProject(
                title=request.params['project_title'],
                key=request.params['project_key'],
                description=request.params['project_description'],
                url_name=request.params['project_url'],
                creator_id=user.id)
                
            participation = Participation(user=user, project=new_project)
            session = DBSession()
            session.add(participation)
            session.flush()
        except IntegrityError:
            # url_name collision.
            raise HTTPBadRequest(explanation="Sorry! That URL has already been taken!")
        return HTTPFound(location=request.root.project_url(new_project)+'/invite')
    else:
        return {'user' : user_dict(request, user)}

@view_config(context='totter.models.Project', name='invite', renderer='invite.jinja2', permission='invite')
def invite(request):
    project = request.context
    session = DBSession()
    user = get_user(request)
    redirect_uri = request.resource_url(project)
    
    iframe_url = 'https://www.facebook.com/dialog/apprequests?access_token=%(access_token)s&api_key=%(api_key)s&app_id=%(app_id)s&display=iframe&frictionless=false&locale=en_US&message=%(message)s&next=%(next)s' % {
        'access_token' : request.session['access_token'] if 'access_token' in request.session else None,
        'api_key' : request.registry.settings['facebook.app_id'],
        'app_id' : request.registry.settings['facebook.app_id'],
        'message' : "WEE ARE THE CHAMPIONS",
        'next' : redirect_uri
    }
    
    # Parse the request params:
    emails = []
    message = None
    response_params = {}
    if 'email_0' in request.params:
        i = 0
        while 'email_' + str(i) in request.params:
            email = request.params['email_'+str(i)]
            if email:
                emails += [email]
            i += 1
        message = request.params['message']
        try: 
            logging.info('Sending invite message for project ' + str(project.id))
            send_email(user.email, emails, "You've been invited!", message)
            response_params['invited'] = True
            response_params['invitee_count'] = len(emails)
        except socket.error:
            pass
    else:
        if request.referrer == request.resource_url(project, 'new'):
            response_params['created'] = True
    
    if emails:
        # Add the emails to the participants list for that project.
        existing = session.query(Participation).filter(Participation.user_email.in_(emails)).filter(Participation.project==project).all()
        existing = [participation.user_email for participation in existing]
        for email in emails:
            if email in existing:
                continue
            session.add(Participation(project_id=project.id, user_email=email))
        
        
    response_params.update({'user' : user_dict(request, user), 
    'project' : {'key':project.key,'title':project.title, 'url': request.resource_url(project)},
    'creator' : user_dict(request, project.creator),
    'fb_app_id' : request.registry.settings['facebook.app_id'],
    'iframe_url' : iframe_url,
    'fb_access_token' : request.session['access_token'] if 'access_token' in request.session else None,
    })
    return template_permissions(request, response_params)
    
def enterKey(request):
    return {}
    
def register(request):
    return {}
    
def stars(request):
    return ideas(request)
