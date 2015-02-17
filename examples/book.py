import pprint
from goodreads.models import GoodreadsBook

try:
    from examples.local_settings import DEVELOPER_KEY, DEVELOPER_SECRET
except ImportError:
    DEVELOPER_KEY = u'your-developer-key'
    DEVELOPER_SECRET = u'your-developer-secret'

from goodreads import Goodreads

Goodreads(DEVELOPER_KEY, DEVELOPER_SECRET)

results = GoodreadsBook().search('Python')
pprint.pprint(results)
