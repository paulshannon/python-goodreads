from config import DEVELOPER_KEY, DEVELOPER_SECRET, AUTH_USER, NON_AUTH_USER, SECONDARY_AUTH_USER
from goodreads import Goodreads

g = Goodreads(DEVELOPER_KEY, DEVELOPER_SECRET, SECONDARY_AUTH_USER['token'], SECONDARY_AUTH_USER['token_secret'])

# auth_user = g.auth_user()
#
# user = g.user(auth_user.id)
#
# n = g.user_notifications()
c = g.user_followers(SECONDARY_AUTH_USER['id'])

pass
