import collections

from rauth import OAuth1Service
import requests
import xmltodict
import six


class GoodreadsAPI(object):
    "A simple wrapper for the Goodreads.com Web API."""

    __instance = None

    def __new__(cls, *args, **kwargs):
        """Implements a 'singleton' pattern so the GoodreadsObjects can access the API via Goodreads"""
        if GoodreadsAPI.__instance is None:
            GoodreadsAPI.__instance = object.__new__(cls)
        return GoodreadsAPI.__instance

    def __init__(self, consumer_key=None, consumer_secret=None):
        """ Initialize the API with goodreads.com keys

        See <https://www.goodreads.com/api/keys> to register your app and to get your keys

        Args:
            consumer_key (str): The goodreads.com developer 'key'
            consumer_secret (str): The goodreads.com developer 'secret'
        """
        if consumer_key and consumer_secret:
            self.service = OAuth1Service(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                name='goodreads',
                request_token_url='https://www.goodreads.com/oauth/request_token',
                authorize_url='https://www.goodreads.com/oauth/authorize',
                access_token_url='https://www.goodreads.com/oauth/access_token',
                base_url='https://www.goodreads.com/',
            )
            self.request_token = None
            self.request_secret = None

    def get_request_token(self):
        """Get a request token from goodreads.com to use in the authorization url"""

        return self.service.get_request_token(header_auth=True)

    def get_authorize_url(self, request_token, oauth_callback=None, mobile=False):
        """Retrieve the URL to redirect the user to so that they may authorize your app.

        Args:
            request_token (str)
            oauth_callback (str, optional):The URL which you wish Goodreads to redirect the user to when the user
                finishes authorizing your application. Defaults to None.
            mobile (bool, optional): defaults to False

        Returns:
            str: The url to give to the user.
        """
        url = self.service.get_authorize_url(request_token)
        if oauth_callback is not None:
            url = '%s&oauth_callback=%s' % (url, oauth_callback)
        if mobile:
            url = '%s&mobile=1' % url
        return url

    def get_session(self, request_token, request_secret):
        """Retrieve the oauth session based on a (presumably) successful authorization

        Args:
            request_token (str): The request token from GoodreadsAPI.get_request_token
            request_secret (str): The request secret from GoodreadsAPI.get_request_token

        Returns:
            OAuth1Session: A session to use to communicate with goodreads.com for a user or None on error
        """
        return self.service.get_auth_session(request_token, request_secret)

    # API methods

    # OAuth Session

    def auth_user(self, session, **kwargs):
        """Get a response with the Goodreads user_id for the user who authorized access using OAuth."""
        return self._api_call(self._get, 'api/auth_user', session=session, container='user', **kwargs)

    def author_books(self, **kwargs):
        """Get a response with a paginated list of an authors books."""
        return self._api_call(self._get, 'author/list.xml', container='author', **kwargs)

    def author_show(self, **kwargs):
        """Get a response with info about an author."""
        return self._api_call(self._get, 'author/show.xml', container='author', **kwargs)

    def isbn_to_id(self, **kwargs):
        """Get the Goodreads book ID given an ISBN."""
        return self._api_call(self._get, 'book/isbn_to_id', raw=True, **kwargs)

    def create_user_status(self, **kwargs):
        """Add status updates for members"""
        return self._api_call(self._post, 'user_status.xml', container='user-status', **kwargs)

    def search(self, **kwargs):
        """
        Get a response with the most popular books for the given query.

        This will search all books in the title/author/ISBN fields and show matches, sorted by popularity on Goodreads.
        There will be cases where a result is shown on the Goodreads site, but not through the API. This happens when
        the result is an Amazon-only edition and we have to honor Amazon's terms of service.
        """
        return self._api_call(self._get, 'search/index.xml', container='search', **kwargs)

    def get_friend_requests(self, **kwargs):
        """Returns the current user's friend requests"""
        return self._api_call(self._get, 'friend/requests.xml', container='requests', **kwargs)

    def add_to_shelf(self, **kwargs):
        """Add a book to a shelf"""
        return self._api_call(self._post, 'shelf/add_to_shelf.xml', **kwargs)

    def list_shelves(self, **kwargs):
        """Lists shelves for a user"""
        return self._api_call(self._get, 'shelf/list.xml', container='shelves', **kwargs)

    def list_books(self, **kwargs):
        """Get the books on a members shelf."""
        return self._api_call(self._get, 'review/list.xml', container='books', **kwargs)

    # Helper Methods

    def _api_call(self, method, path, session=None, container=None, raw=False, **kwargs):
        return self._parse_response(
            method(path, session=session, **self._prepare_call(**kwargs)),
            container=container,
            raw=raw
        )

    def _get(self, path, session=None, **kwargs):
        """Utility method for GET-ting from the Goodreads API"""
        if not session:
            session = requests
        url = self.service.base_url + path
        response = session.get(url, data=kwargs)
        response.raise_for_status()
        return response.content

    def _post(self, path, session=None, **kwargs):
        """Utility method for POST-ing to the Goodreads API"""
        if not session:
            session = self.service
        url = self.service.base_url + path
        response = session.post(url, data=kwargs)
        response.raise_for_status()
        return response.content

    def _prepare_call(self, **kwargs):
        data = {'key': self.service.consumer_key}
        for key, val in six.iteritems(kwargs):
            if isinstance(val, collections.MutableMapping):
                for subkey, subval in val.iteritems():
                    new_key = '%s[%s]' % (key, subkey)
                    data[new_key] = subval
            else:
                data[key] = val
        return data

    @staticmethod
    def _parse_response(result, container=None, raw=False):
        if not raw:
            result = xmltodict.parse(result)
            result = result.get('GoodreadsResponse', result)
        elif raw:
            result = result.split('\n')[0]
        if container is not None:
            try:
                result = result[container]
            except KeyError:
                raise InvalidResponse("The response %r did not contain an item called %r" % (result, container))
        return result
