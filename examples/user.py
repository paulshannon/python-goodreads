try:
    from local_settings import DEVELOPER_KEY, DEVELOPER_SECRET, AUTH_USER
except ImportError:
    DEVELOPER_KEY = u'your-developer-key'
    DEVELOPER_SECRET = u'your-developer-secret'
    AUTH_USER = {'access_token': 'user-access-token',
                 'access_token_secret': 'user-access-token-secret'}

from goodreads.models import Goodreads, GoodreadsUser

Goodreads(DEVELOPER_KEY, DEVELOPER_SECRET)

user = GoodreadsUser(access_token=AUTH_USER['access_token'], access_token_secret=AUTH_USER['access_token_secret'])
print(user.pk, user.name, user.url)