# template.py 
# Our template helpers
from totter.cache import memoize_on
from datetime import datetime
from pytz import timezone
import pytz

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
@memoize_on(size=100, argf=lambda req,usr: usr.id if usr else None)
def user_dict(request, user):
    if not user:
        return None
    return  {
        'id' : str(user.id),
        'first_name' : user.first_name, 
        'last_name' : user.last_name, 
        'profile_picture' : user.profile_picture,
        'profile_url' : request.root.user_url(user)
    }

tz = timezone('US/Eastern')
def idea_dict(request, idea, user_rating, aggregate_rating, include_comments=False):
    rating_data = {
        'liked' : user_rating.liked if user_rating else False,
        'loved' : user_rating.loved if user_rating else False,
        'stars' : user_rating.stars if user_rating else False
    }
    idea_data = {
        'id' : str(idea.id), 
        'data' : idea.data, 
        'author' : user_dict(request, idea.author) if not idea.anonymous else None,
        'anonymous' : idea.anonymous,
        'user_rating' : rating_data,
        'total_rating' : aggregate_rating.total_rating if aggregate_rating else 0,
        'total_stars' : aggregate_rating.average_stars if aggregate_rating and aggregate_rating.count else 0,
        'rating_count' : aggregate_rating.count if aggregate_rating else 0,
        'created' : idea.creation_time.astimezone(tz).strftime('%B %d at %I:%M %p %Z')
    }
    if include_comments:
        idea_data['comments'] = [comment_dict(request, comment) for comment in idea.comments]
    return idea_data
    
def comment_dict(request, comment):
    return {
        'id' : str(comment.id),
        'author': user_dict(request, comment.author) if not comment.anonymous else None,
        'created' : comment.creation_time.astimezone(tz).strftime('%B %d at %I:%M %p %Z'),
        'anonymous' : comment.anonymous,
        'data' : comment.data
    }