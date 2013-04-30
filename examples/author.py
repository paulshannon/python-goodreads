from config import DEVELOPER_KEY, DEVELOPER_SECRET, AUTHORS
from goodreads import Goodreads
import pprint

author_id = AUTHORS[0]['id']

g = Goodreads(DEVELOPER_KEY, DEVELOPER_SECRET)

g.author_show(author_id)

for book in g.author_books(author_id):
    pprint.pprint(book)
