# From http://blog.sadphaeton.com/2009/01/19/sqlalchemy-recipeuuid-column.html

from sqlalchemy import types, Text
from sqlalchemy.types import CHAR, VARCHAR
from sqlalchemy.schema import Column
import uuid
import string
import json
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
 
 
    
