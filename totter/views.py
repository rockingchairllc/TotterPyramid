#from totter.models import DBSession
#from totter.models import MyModel

from pyramid.security import authenticated_userid
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('totter')

def my_view(request):
    #dbsession = DBSession()
    #root = dbsession.query(MyModel).filter(MyModel.name==u'root').first()
    return {'project':'totter', 'user' : authenticated_userid(request)}
