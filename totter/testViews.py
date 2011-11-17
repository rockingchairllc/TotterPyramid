#from totter.models import DBSession
#from totter.models import MyModel

from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('totter')


def create(request):
    return {}
    
def enterKey(request):
    return {}
    
def ideas(request):
    user_info = {'user_name' : 'Francisco Saldana', 'user_image': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-snc4/211801_1135710554_1230207683_q.jpg'}
    ideas_data = {'project_title' : 'Grand Opening of Hotel LaRitz',
        'author_name' : 'Coca Cola',
        'author_image' : 'http://fbcdn-profile-a.akamaihd.net/hprofile-ak-snc4/276879_40796308305_1578420141_q.jpg',
        'people_count' : 32,
        'ideas_count' : 4,
        'deadline' : 'None',
        'ideas' : [{'author_name' : 'Francisco Saldana',
                    'author_image' : 'http://fbcdn-profile-a.akamaihd.net/hprofile-ak-snc4/211801_1135710554_1230207683_q.jpg',
                    'rating' : 3, 
                    'rating_count' : 120, 'creation_time' : 'December 17, 2009 at 10:20am',
                    'idea_content' : 'Let\'s have a party',
                    'comments' : [
                        {'author_name' : 'Dolores Smith', 'comment_content' : 'We should have it at my house!'},
                        {'author_name' : 'Sam Smith', 'comment_content' : 'We should make it blue themed.'},
                        {'author_name' : 'Douche Bag', 'comment_content' : 'Let\'s not.'},
                    ]},
                    {'author_name' : 'Sam Smith', 'rating' : 1, 
                    'author_image' : 'http://fbcdn-profile-a.akamaihd.net/hprofile-ak-snc4/368731_562443218_874585432_q.jpg',
                    'rating_count' : 49, 'creation_time' : 'August, 15 2009 at 12:01am',
                    'idea_content' : 'Blue Themed Party',
                    'comments' : [
                        {'author_name' : 'Dolores Smith', 'comment_content' : 'I like green better.'},
                        {'author_name' : 'Sam Smith', 'comment_content' : 'I never liked you Dolores.'},
                    ]},
                    {'author_name' : 'Shubert Samanthan', 'rating' : 2, 
                    'author_image' : 'http://fbcdn-profile-a.akamaihd.net/hprofile-ak-snc4/275165_100000084707992_354701_q.jpg',
                    'rating_count' : 2, 'creation_time' : '3 minutes ago',
                    'idea_content' : 'Whateverrr',
                    'comments' : [
                        {'author_name' : 'Dolores Smith', 'comment_content' : 'Wow youre still here?'},
                        {'author_name' : 'Tolune Tobias', 'comment_content' : 'LOL'},
                    ]},
                    ]
        }
    ideas_data.update(user_info)
    return ideas_data
def login(request):
    return {}
    
def project(request):
    user_info = {'user_name' : 'Francisco Saldana', 'user_image': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-snc4/211801_1135710554_1230207683_q.jpg'}
    project_data = {'project_title' : 'Grand Opening of Hotel LaRitz',
            'author_name' : 'Francisco Saldana',
            'idea_count' : 3,
            'description' : 'We should plan something for the grand opening.',
            'deadline' : 'None',
            'updates' : [{'type' : 'Idea Added', 'who' : 'Jaime Ortega', 'when' : 'Wed 10/21/2011 at 10pm', 'what' : 'Yoga class.'},
            {'type' : 'Comment', 'who' : 'Jeremy Smith', 'when' : 'Thurs 10/11/2011 at 2pm', 'what' : 'Tell me about it.'}]
    }
    project_data.update(user_info)
    return project_data
            
    
def register(request):
    return {}
    
def stars(request):
    return ideas(request)
