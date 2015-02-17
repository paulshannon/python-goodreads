try:
    from local_settings import DEVELOPER_KEY, DEVELOPER_SECRET
except ImportError:
    DEVELOPER_KEY = u'your-developer-key'
    DEVELOPER_SECRET = u'your-developer-secret'

import pprint

from builtins import input

from goodreads.models import GoodreadsUser
from goodreads import Goodreads

Goodreads(DEVELOPER_KEY, DEVELOPER_SECRET)

user = GoodreadsUser()

print('Visit this URL in your browser: ' + user.authorize_url)
accepted = 'n'
while accepted.lower() == 'n':
    accepted = input('Have you authorized me? (y/n) ')

print(u'Save user.session.access_token and user.session.access_token_secret:')
pprint.pprint({'access_token': user.session.access_token, 'access_token_secret': user.session.access_token_secret})