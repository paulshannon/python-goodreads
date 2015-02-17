from collections import defaultdict

from rauth import OAuth1Session

from api import GoodreadsAPI
from util import LazyProperty


class Goodreads(object):
    def __init__(self, consumer_key, consumer_secret):
        """The main entry point for interacting with the Goodreads API.

        Sets up the API singleton. Allows direct access to some site wide info.

        Args:
            consumer_key (str): The Goodreads API developer key; required for almost everything
            consumer_secret (str): The Goodreads API developer secret; required for almost everything
        """
        self._api = GoodreadsAPI(consumer_key, consumer_secret)

    def __repr__(self):
        return '<Goodreads:%s>' % self._api.service.consumer_key


class GoodreadsObject(object):
    def __init__(self, pk=None):
        self.pk = pk
        self.api = GoodreadsAPI()

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.pk)


class GoodreadsUser(GoodreadsObject):
    def __init__(self, access_token=None, access_token_secret=None, pk=None, name=None, url=None):
        super(GoodreadsUser, self).__init__(pk)
        self.api_called = defaultdict(lambda: None)

        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.logged_in = False

        if access_token and access_token_secret:
            # noinspection PyStatementEffect
            self.session

        self.pk = pk
        self.name = name
        self.url = url

    def __getattribute__(self, attr):
        api_called = super(GoodreadsUser, self).__getattribute__('api_called')
        if attr in ['pk', 'name', 'url'] and not api_called['auth_user']:
            self.auth_user()
        return super(GoodreadsUser, self).__getattribute__(attr)

    # OAuth

    @LazyProperty
    def request_token(self):
        # noinspection PyAttributeOutsideInit
        request_token, self.request_secret = self.api.get_request_token()
        return request_token

    @LazyProperty
    def request_secret(self):
        self.request_token()

    @LazyProperty
    def authorize_url(self):
        return self.api.get_authorize_url(self.request_token)

    @LazyProperty
    def session(self):
        if self.access_token and self.access_token_secret:
            session = OAuth1Session(self.api.service.consumer_key,
                                    self.api.service.consumer_secret,
                                    access_token=self.access_token,
                                    access_token_secret=self.access_token_secret)
        else:
            session = self.api.get_session(self.request_token, self.request_secret)
        self.logged_in = True
        return session

    # Api

    def auth_user(self):
        r = self.api.auth_user(self.session)
        self.pk = r['@id']
        self.name = r['name']
        self.url = r['link']
        self.api_called['auth_user'] = True


class GoodreadsAuthor(GoodreadsObject):
    pass


class GoodreadsSeries(GoodreadsObject):
    pass


class GoodreadsWork(GoodreadsObject):
    def __init__(self,
                 pk=None,
                 title=None,
                 year=None,
                 average_rating=None,
                 ratings_count=None,
                 reviews_count=None,
                 books_count=None,
                 best_book=None):
        super(GoodreadsWork, self).__init__(pk)
        self.pk = pk
        self.title = title,
        self.year = year
        self.average_rating = average_rating
        self.ratings_count = ratings_count
        self.reviews_count = reviews_count
        self.books_count = books_count
        self.best_book = best_book

    @staticmethod
    def from_object(object_):
        return GoodreadsWork(
            pk=object_['id']['#text'],
            title=object_['best_book']['title'],
            year=object_['original_publication_year']['#text'],
            average_rating=object_['average_rating'],
            ratings_count=object_['ratings_count']['#text'],
            reviews_count=object_['text_reviews_count']['#text'],
            books_count=object_['books_count']['#text'],
            best_book=GoodreadsBook.from_object(object_['best_book'])
        )


class GoodreadsBook(GoodreadsObject):
    def search(self, query, field='all', page=1):
        """
        Find books by title, author, or ISBN

        This will search all books in the title/author/ISBN fields and show matches, sorted by popularity on Goodreads.
        There will be cases where a result is shown on the Goodreads site, but not through the API. This happens when
        the result is an Amazon-only edition and we have to honor Amazon's terms of service.

        :param query:
        :param field:
        :param page:
        :return: List of GoodreadsBook
        """

        result = self.api.search(**{'q': query, 'page': page, 'search[field]': field})
        result['results'] = [GoodreadsWork.from_object(work) for work in result['results']['work']]
        return result

    @staticmethod
    def from_object(object_):
        return GoodreadsBook(
            pk=object_['id']['#text'],
        )


class GoodreadsShelf(GoodreadsObject):
    pass


