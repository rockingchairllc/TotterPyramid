# From http://blog.sadphaeton.com/2009/01/19/sqlalchemy-recipeuuid-column.html

from sqlalchemy import types
from sqlalchemy.types import CHAR
from sqlalchemy.schema import Column
import uuid


class UUID(types.TypeDecorator):
    impl = CHAR
    def __init__(self):
        self.impl.length = 32
        types.TypeDecorator.__init__(self,length=self.impl.length)
 
    def process_bind_param(self,value,dialect=None):
        if value and isinstance(value,uuid.UUID):
            return value.hex
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
 
 
    
