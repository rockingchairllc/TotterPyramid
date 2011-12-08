# template.py 
# Our template helpers
from totter.cache import memoize_on
from datetime import datetime

## Stolen from flask's jinja extensions
# This is the function we use for the tojinja filter

# try to load the best simplejson implementation available.  If JSON
# is not installed, we add a failing class.
json_available = True
json = None
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        try:
            # Google Appengine offers simplejson via django
            from django.utils import simplejson as json
        except ImportError:
            json_available = False

def _assert_have_json():
    """Helper function that fails if JSON is unavailable."""
    if not json_available:
        raise RuntimeError('simplejson not installed')
        

# figure out if simplejson escapes slashes.  This behaviour was changed
# from one version to another without reason.
if not json_available or '\\/' not in json.dumps('/'):

    def _tojson_filter(*args, **kwargs):
        if __debug__:
            _assert_have_json()
        return json.dumps(*args, **kwargs).replace('/', '\\/')
else:
    _tojson_filter = json.dumps

### Date formatting ###
def timefmt(*args, **kwargs):
    # Takes strftime arguments
    if not isinstance(args[0], datetime):
        raise RuntimeError('Not instance of datetime.')
    # Prints December 02 at 09:00 PM
    return args[0].strftime('%B %d at %I:%M %p')

### Model to dict helpers ###
@memoize_on(size=100, argf=lambda req,usr: usr.id)
def user_dict(request, user):
    return  {
        'id' : str(user.id),
        'first_name' : user.first_name, 
        'last_name' : user.last_name, 
        'profile_picture' : user.profile_picture,
        'profile_url' : request.root.user_url(user)
    }
    
def idea_dict(request, idea, user_rating, total_rating, include_comments=False):
    rating_data = {
        'liked' : user_rating.liked if user_rating else False,
        'loved' : user_rating.loved if user_rating else False,
    }
    idea_data = {
        'id' : str(idea.id), 
        'data' : idea.data, 
        'author' : user_dict(request, idea.author) if not idea.anonymous else None,
        'anonymous' : idea.anonymous,
        'user_rating' : rating_data,
        'total_rating' : total_rating,
        'created' : idea.creation_time.strftime('%B %d at %I:%M %p')
    }
    if include_comments:
        idea_data['comments'] = [comment_dict(request, comment) for comment in idea.comments]
    return idea_data
    
def comment_dict(request, comment):
    return {
        'id' : str(comment.id),
        'author': user_dict(request, comment.author) if not comment.anonymous else None,
        'created' : comment.creation_time.strftime('%B %d at %I:%M %p'),
        'anonymous' : comment.anonymous,
        'data' : comment.data
    }