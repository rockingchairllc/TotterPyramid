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
    logging.info("Response content: " + response.content)
    pass

def post_event(request, subscription, subject, message, time=None, after=handle_response, from_email=None):
    if not time:
        time = utcnow()
    data = {'subscription':subscription, 'subject':subject, 'message':message}
    if from_email:
        data['from'] = from_email
    requests.post(root_url(request) + '/event',
        data,
        hooks = {'response' : handle_response})
    
def subscribe(request, email, subscription, frequency='immediate', after=handle_response):
    requests.post(root_url(request, ) + '/subscribe',
        data = {'subscription':subscription, 'email':email, 'frequency':frequency},
        hooks = {'response' : handle_response})

def create_subscription(request, subscription, parent=None, after=handle_response):
    if not parent:
        parent = 'root'
    logging.info("Creating subscription %s => %s" % (subscription, str(parent)))
    requests.post(root_url(request) + '/subscription',
        data = {'name':subscription, 'parent':parent},
        hooks = {'response' : handle_response})
    
def unroll_subscription_tree(request, root, tree):
    for parent, child in tree.items():
        create_subscription(request, parent, root)
        if isinstance(child, list):
            for el in child:
                if isinstance(el, str):
                    create_subscription(request, el, parent)
                elif isinstance(el, dict):
                    unroll_subscription_tree(request, parent, el)
        elif isinstance(child, dict):
            unroll_subscription_tree(request, parent, child)
        elif isinstance(child, str):
            create_subscription(request, child, parent)

                
def new_project(request, project, author):
    root = 'root'
    tree = {'project' :
        {str(project.id) : [
                {str(project.id) + ":owner" : [
                        str(project.id) + ':ideas-new',
                        str(project.id) + ':participation',
                        str(project.id) + ':ideas-comments',
                    ]
                },
                str(project.id) + ':ideas-votes',
            ]
        }
    }
    unroll_subscription_tree(request, root, tree)
    subscribe(request, author.email, str(project.id) + ":owner")
    
    create_subscription(request, str(project.id) + ":created", root)
    subscribe(request, author.email, str(project.id) + ":created")
    
    
    subject = "You Created a Totter"
    message = """
    Congratulations! Your Totter project %s is located at
    <%s>
    Your project access key is: %s
    """ % (project.title, request.resource_url(project), project.key)
    post_event(request, str(project.id) + ":created", subject, message)
    
def new_idea(request, project, idea, author):
    parent_sub = str(project.id) + ":ideas-new"
    subscription = str(project.id) + ':' + str(idea.id) + ":new"
    create_subscription(request, subscription, parent_sub)
    parent_sub = str(project.id) + ':ideas-comments'
    subscription = str(project.id) + ':' + str(idea.id) + ":comments" 
    create_subscription(request, subscription, parent_sub)
    parent_sub = str(project.id) + ':ideas-votes'
    subscription = str(project.id) + ':' + str(idea.id) + ":votes"  
    create_subscription(request, subscription, parent_sub)
    
    subject = "New idea posted to %s" % project.title
    message = """
%(who)s posted a new idea to the %(title)s:
%(data)s
""" % {'who' : idea.author.full_name + ' ' , 'title' : project.title, 'data' : idea.data}
    post_event(request, subscription, subject, message, from_email=idea.author.email)
    
    subscribe(request, idea.author.email, str(project.id) + ':' + str(idea.id) + ":comments", frequency='immediate')
    
def new_comment(request, project, idea, comment, author):
    subscription = str(project.id) + ':' + str(idea.id) + ":comments" 
    subject = "New comment posted to %s" % project.title
    message = """
%(who)s posted a new comment to %(idea_who)s's idea on %(title)s
%(data)s
""" % {'who' : comment.author.full_name, 'idea_who' : idea.author.full_name,
    'title' : project.title, 'data' : comment.data}
    post_event(request, subscription, subject, message, from_email=comment.author.email)
    
    subscribe(request, comment.author.email, subscription, frequency='immediate')
    
def new_rating(request, project, idea, rater):
    subscription = str(project.id) + ':' + str(idea.id) + ":votes"
    subject = "%s rated %s's idea" % (rater.full_name, idea.author.full_name)
    message = subject
    post_event(request, subscription, subject, message, from_email=rater.email)
    
def new_participant(request, project, participant):
    subscription = str(project.id) + ':participation'
    subject = "%s participated in %s" % (participant.full_name, project.title)
    message = subject
    post_event(request, subscription, subject, message, from_email=participant.email)
    subscribe(request, participant.email, str(project.id), frequency='daily')

