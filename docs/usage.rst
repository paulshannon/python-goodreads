========
Usage
========

To use Goodreads in a project::

	import goodreads

========
Examples
========

User Authorization
--------
::
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


Author::
--------
	from config import DEVELOPER_KEY, DEVELOPER_SECRET, AUTHORS
	from goodreads import Goodreads
	import pprint

	author_id = AUTHORS[0]['id']

	g = Goodreads(DEVELOPER_KEY, DEVELOPER_SECRET)

	g.author_show(author_id)

	for book in g.author_books(author_id):
	    pprint.pprint(book)

User
---------
::
	from config import DEVELOPER_KEY, DEVELOPER_SECRET, AUTH_USER, NON_AUTH_USER, SECONDARY_AUTH_USER
	from goodreads import Goodreads

	g = Goodreads(DEVELOPER_KEY, DEVELOPER_SECRET, SECONDARY_AUTH_USER['token'], SECONDARY_AUTH_USER['token_secret'])
	c = g.user_followers(SECONDARY_AUTH_USER['id'])
