
from sqlalchemy import types, Text, String
from sqlalchemy.types import CHAR, VARCHAR
from sqlalchemy.schema import Column

import uuid
import string
import json

## UUID:
# From http://blog.sadphaeton.com/2009/01/19/sqlalchemy-recipeuuid-column.html
# With modification: Accept reasonable hex strings.
class UUID(types.TypeDecorator):
    impl = CHAR
    def __init__(self):
        self.impl.length = 32
        types.TypeDecorator.__init__(self,length=self.impl.length)
 
    def process_bind_param(self,value,dialect=None):
        if value and isinstance(value,uuid.UUID):
            return value.hex
        elif value and (isinstance(value, str) or isinstance(value, unicode))\
                and (len(value) == 32 or len(value) == 36):
            # NOTE: Doesn't validate hyphen positions.
            temp = value.replace('-', '', 4).lower() 
            if all(c in 'abcdef0123456789' for c in temp):
                return temp
            else:
                raise ValueError,'value %s is not a valid uuid.UUID' % value
        elif value and not isinstance(value,uuid.UUID):
            raise ValueError,'value %s is not a valid uuid.UUID' % value
        else:
            return None
 
    def process_result_value(self,value,dialect=None):
        if value:
            return uuid.UUID(hex=value)
        else:
            return None
 
    def is_mutable(self):
        return False
        

# From http://www.sqlalchemy.org/docs/core/types.html#marshal-json-strings
# With modifications: VARCHAR => Text
class JSONEncodedDict(types.TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    Usage::
        JSONEncodedDict()
    """
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

import cgi, re
def encode_for_xml(unicode_data, encoding='ascii'):
    """
    Encode unicode_data for use as XML or HTML, with characters outside
    of the encoding converted to XML numeric character references.
    """
    try:
        return unicode_data.encode(encoding, 'xmlcharrefreplace')
    except ValueError:
        # ValueError is raised if there are unencodable chars in the
        # data and the 'xmlcharrefreplace' error handler is not found.
        # Pre-2.3 Python doesn't support the 'xmlcharrefreplace' error
        # handler, so we'll emulate it.
        return _xmlcharref_encode(unicode_data, encoding)

def _xmlcharref_encode(unicode_data, encoding):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    chars = []
    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            chars.append(char.encode(encoding, 'strict'))
        except UnicodeError:
            chars.append('&#%i;' % ord(char))
    return ''.join(chars)

def lenient_deccharref(m):
   return unichr(int(m.group(1)))
   
class HTMLUnicode(types.TypeDecorator):
    impl=String
    def process_bind_param(self, value, dialect):
        # From our code to the DB
        if isinstance(value, str):
            raise ValueError, 'Value must be unicode!'
        # Replaces < with &lt; > with &gt and & with &amp;
        value = cgi.escape(value)
        value = encode_for_xml(value, 'ascii')
        return value
        
 
    def process_result_value(self, value, dialect):
        # From the DB to our code.
        if value:
            value = value.decode('ascii')
            value = re.sub('&#(\d+);', lenient_deccharref, value)
            value = value.replace(u'&gt;', u'>')
            value = value.replace(u'&lt;', u'<')
            value = value.replace(u'&amp;', u'&')
            return value
        else:
            return None
        
class HTMLUnicodeText(types.TypeDecorator):
    impl=Text
    def process_bind_param(self, value, dialect):
        # From our code to the DB
        if isinstance(value, str):
            raise ValueError, 'Value must be unicode!'
        # Replaces < with &lt; > with &gt and & with &amp;
        value = cgi.encode(value)
        value = encode_for_xml(value, 'ascii')
        return value
        
 
    def process_result_value(self, value, dialect):
        if value:
            # From the DB to our code.
            value = value.decode('ascii')
            value = re.sub('&#(\d+);', lenient_deccharref, value)
            value = value.replace(u'&gt;', u'>')
            value = value.replace(u'&lt;', u'<')
            value = value.replace(u'&amp;', u'&')
            return value
        else:
            return None