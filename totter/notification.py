## notifications.py ##
## Interface to the notifications server ##
# Settings:
# notification.root_url
import requests
from models import utcnow
import logging
def root_url(request):
    return request.registry.settings['notification.root_url']
    
def handle_response(response):
    logging.info("Response received for notification request:" + str(response))
    pass

def post_event(request, subscription, subject, message, time=None, after=handle_response):
    if not time:
        time = utcnow()
    requests.post(root_url(request) + '/event',
        data = {'subscription':subscription, 'subject':subject, 'message':message},
        hooks = {'response' : handle_response})
    
def subscribe(request, email, subscription, frequency='immediate', after=handle_response):
    requests.post(root_url(request, ) + '/subscribe',
        data = {'subscription':subscription, 'email':email, 'frequency':frequency},
        hooks = {'response' : handle_response})

def create_subscription(request, subscription, parent=None, after=handle_response):
    if not parent:
        parent = 'root'
    requests.post(root_url(request) + '/subscription',
        data = {'name':subscription, 'parent':parent},
        hooks = {'response' : handle_response})
    
def unroll_subscription_tree(request, root, tree):
    for parent, child in tree.items():
        create_subscription(request, parent, root)
        if isinstance(child, list):
            for el in child:
                create_subscription(request, el, parent)
        elif isinstance(child, dict):
            unroll_subscription_tree(request, parent, child)
        elif isinstance(child, str):
            create_subscription(request, child, parent)
                
def new_project(request, project, author):
    root = 'root'
    tree = {'project' :
        {str(project.id) : [
            str(project.id) + ':ideas-new',
            str(project.id) + ':ideas-comments',
            str(project.id) + ':ideas-votes',
            str(project.id) + ':participation'
            ]
        }
    }
    unroll_subscription_tree(request, root, tree)
    
def new_idea(request, project, idea, author):
    parent_sub = str(project.id) + ":ideas-new"
    subscription = str(project.id) + ':' + str(idea.id) + ":new"
    create_subscription(request, subscription, parent_sub)
    subject = "New idea posted to %s" % project.title
    message = """
%(who)s posted a new idea to the %(title)s:
%(data)s
""" % {'who' : idea.author.full_name + ' ' , 'title' : project.title, 'data' : idea.data}
    post_event(request, subscription, subject, message)
    
def new_comment(request, project, idea, comment, author):
    parent_sub = str(project.id) + ':ideas-comments'
    subscription = str(project.id) + ':' + str(idea.id) + ":comment"  
    create_subscription(request, subscription, parent_sub)
    subject = "New comment posted to %s" % project.title
    message = """
%(who)s posted a new comment to %(idea_who)s's idea on %(title)s
%(data)s
""" % {'who' : comment.author.full_name, 'idea_who' : idea.author.full_name,
    'title' : project.title, 'data' : comment.data}
    post_event(request, subscription, subject, message)
    
def new_rating(request, project, idea, rater):
    parent_sub = str(project.id) + ':ideas-votest'
    subscription = str(project.id) + ':' + str(idea.id) + ":votes"  
    create_subscription(request, subscription, parent_sub)
    subject = "%s rated %s's idea" % (rater.full_name, idea.author.full_name)
    message = subject
    post_event(request, subscription, subject, message)
    
def new_participant(request, project, participant):
    parent_sub = str(project.id)
    subscription = str(project.id) + ':participation'
    create_subscription(request, subscription, parent_sub)
    subject = "%s participated in %s" % (participant.full_name, project.title)
    message = subject
    post_event(request, subscription, subject, message)

