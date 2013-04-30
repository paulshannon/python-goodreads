from config import DEVELOPER_KEY, DEVELOPER_SECRET
from goodreads import Goodreads

g = Goodreads(DEVELOPER_KEY, DEVELOPER_SECRET)

authorize_url = g.oauth_authorize_url()

print 'Please authorize at: %s' % authorize_url
accepted = 'n'
while accepted.lower() == 'n':
    # you need to access the authorize_link via a browser,
    # and proceed to manually authorize the consumer
    accepted = raw_input('Have you authorized me? (y/n) ')

token = g.oauth_retrieve_token()

print 'You need to save key: \'%s\' and secret: \'%s\'' % (token.key, token.secret)

