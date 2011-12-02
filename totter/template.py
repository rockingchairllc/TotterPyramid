# template.py 
# Our template helpers



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
from datetime import datetime
def timefmt(*args, **kwargs):
    # Takes strftime arguments
    if not isinstance(args[0], datetime):
        raise RuntimeError('Not instance of datetime.')
    # Prints December 02 at 09:00 PM
    return args[0].strftime('%B %d at %I:%M %p')