import collections

from rauth import OAuth1Service
import requests
import xmltodict
import six

from .util import oauth_required, developer_required, extra_permissions_required


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

    # API methods

    @oauth_required
    def auth_user(self, **kwargs):
        """Get id of user who authorized OAuth

        https://www.goodreads.com/api/index#auth.user
        """
        return self._api_call(self._get, 'api/auth_user', container='user', **kwargs)

    @developer_required
    def author_books(self, **kwargs):
        """Get a response with a paginated list of an authors books.

        https://www.goodreads.com/api/index#author.books
        """
        return self._api_call(self._get, 'author/list.xml', container='author', **kwargs)

    @developer_required
    def author_show(self, **kwargs):
        """Get a response with info about an author.

        https://www.goodreads.com/api/index#author.show
        """
        return self._api_call(self._get, 'author/show.xml', container='author', **kwargs)

    @developer_required
    def book_isbn_to_id(self, **kwargs):
        """Get the Goodreads book ID given an ISBN

        https://www.goodreads.com/api/index#book.isbn_to_id
        """
        return self._api_call(self._get, 'book/isbn_to_id', raw=True, **kwargs)

    @developer_required
    def book_review_counts(self, **kwargs):
        """Get review statistics given a list of ISBNs

        https://www.goodreads.com/api/index#book.review_counts
        """
        return self._api_call(self._get, 'book/review_counts.json', raw=True, **kwargs)

    @developer_required
    def book_show(self, **kwargs):
        """Get the reviews for a book given a Goodreads book id"""

    @developer_required
    def book_show_by_isbn(self, **kwargs):
        """Get the reviews for a book given an ISBN"""

    @developer_required
    def book_title(self, **kwargs):
        """Get the reviews for a book given a title string"""

    @oauth_required
    def comment_create(self, **kwargs):
        """Create a comment"""

    @developer_required
    def comment_list(self, **kwargs):
        """List comments on a subject"""

    @developer_required
    def events_list(self, **kwargs):
        """Events in your area"""

    @oauth_required
    def fanship_create(self, **kwargs):
        """Become fan of an author"""

    @oauth_required
    def fanship_destroy(self, **kwargs):
        """Stop being fan of an author"""

    @oauth_required
    def fanship_show(self, **kwargs):
        """Show fanship information"""

    @oauth_required
    def followers_create(self, **kwargs):
        """Follow a user"""

    @oauth_required
    def followers_destroy(self, **kwargs):
        """Unfollow a user"""

    @oauth_required
    def friend_confirm_recommendation(self, **kwargs):
        """Confirm or decline a friend recommendation"""

    @oauth_required
    def friend_confirm_request(self, **kwargs):
        """Confirm or decline a friend request"""

    @oauth_required
    def friend_requests(self, **kwargs):
        """Get friend requests"""
        return self._api_call(self._get, 'friend/requests.xml', container='requests', **kwargs)

    @oauth_required
    def friends_create(self, **kwargs):
        """Add a friend"""

    @oauth_required
    def group_join(self, **kwargs):
        """Join a group"""

    @developer_required
    def group_list(self, **kwargs):
        """List groups for a given user"""

    @developer_required
    def group_members(self, **kwargs):
        """Return members of a particular group"""

    @developer_required
    def group_search(self, **kwargs):
        """Find a group"""

    @developer_required
    def group_show(self, **kwargs):
        """Get info about a group by id"""

    @extra_permissions_required
    def list_book(self, **kwargs):
        """Get the listopia lists for a given book"""

    @oauth_required
    def notifications(self, **kwargs):
        """See the current user's notifications"""

    @oauth_required
    def owned_books_create(self, **kwargs):
        """Add to books owned"""

    @oauth_required
    def owned_books_list(self, **kwargs):
        """List books owned by a user"""

    @oauth_required
    def owned_books_show(self, **kwargs):
        """Show an owned book"""

    @oauth_required
    def owned_books_update(self, **kwargs):
        """Update an owned book"""

    @oauth_required
    def quotes_create(self, **kwargs):
        """Add a quote"""

    @oauth_required
    def rating_create(self, **kwargs):
        """Like a resource"""

    @oauth_required
    def rating_destroy(self, **kwargs):
        """Unlike a resource"""

    @developer_required
    def read_statuses_show(self, **kwargs):
        """Get a user's read status"""

    @oauth_required
    def recommendations_show(self, **kwargs):
        """Get a recommendation from a user to another user"""

    @oauth_required
    def review_create(self, **kwargs):
        """Add review"""

    @oauth_required
    def review_edit(self, **kwargs):
        """Edit a review"""

    @oauth_required
    def reviews_list(self, **kwargs):
        """Get the books on a members shelf"""
        return self._api_call(self._get, 'review/list.xml', container='books', **kwargs)

    @developer_required
    def review_recent_reviews(self, **kwargs):
        """Recent reviews from all members_"""

    @developer_required
    def review_show(self, **kwargs):
        """Get a review"""

    @developer_required
    def review_show_by_user_and_book(self, **kwargs):
        """Get a user's review for a given book"""

    @developer_required
    def search_authors(self, **kwargs):
        """Find an author by name"""

    @developer_required
    def search_books(self, **kwargs):
        """
        Get a response with the most popular books for the given query.

        This will search all books in the title/author/ISBN fields and show matches, sorted by popularity on Goodreads.
        There will be cases where a result is shown on the Goodreads site, but not through the API. This happens when
        the result is an Amazon-only edition and we have to honor Amazon's terms of service.
        """
        return self._api_call(self._get, 'search/index.xml', container='search', **kwargs)

    @developer_required
    def series_show(self, **kwargs):
        """See a series"""

    @developer_required
    def series_list(self, **kwargs):
        """See all series by an author"""

    @developer_required
    def series_work(self, **kwargs):
        """See all series a work is in"""

    @oauth_required
    def shelves_add_to_shelf(self, **kwargs):
        """Add a book to a shelf"""
        return self._api_call(self._post, 'shelf/add_to_shelf.xml', **kwargs)

    @oauth_required
    def shelves_add_books_to_shelves(self, **kwargs):
        """Add books to many shelves"""

    @oauth_required
    def shelves_list(self, **kwargs):
        """Get a user's shelves"""
        return self._api_call(self._get, 'shelf/list.xml', container='shelves', **kwargs)

    @oauth_required
    def topic_create(self, **kwargs):
        """Create a new topic via OAuth"""

    @developer_required
    def topic_group_folder(self, **kwargs):
        """Get list of topics in a group's folder"""

    @developer_required
    def topic_show(self, **kwargs):
        """Get info about a topic by id"""

    @oauth_required
    def topic_unread_group(self, **kwargs):
        """Get a list of topics with unread comments"""

    @oauth_required
    def updates_friends(self, **kwargs):
        """Get your friend updates"""

    @oauth_required
    def user_shelves_create(self, **kwargs):
        """Add book shelf"""

    @oauth_required
    def user_shelves_update(self, **kwargs):
        """Edit book shelf"""

    @developer_required
    def user_show(self, **kwargs):
        """Get info about a member by id or username"""

    @oauth_required
    def user_compare(self, **kwargs):
        """Compare books with another member"""

    @oauth_required
    def user_followers(self, **kwargs):
        """Get a user's followers"""  # TODO: Don't understand this

    @oauth_required
    def user_following(self, **kwargs):
        """Get people a user is following"""

    @oauth_required
    def user_friends(self, **kwargs):
        """Get a user's friends"""

    @oauth_required
    def user_status_create(self, **kwargs):
        """Update user status"""
        return self._api_call(self._post, 'user_status.xml', container='user-status', **kwargs)

    @oauth_required
    def user_status_destroy(self, **kwargs):
        """Delete user status"""

    @developer_required
    def user_status_show(self, **kwargs):
        """Get a user status"""

    def user_status_index(self, **kwargs):
        """View user statuses (Developer key NOT required)"""

    @extra_permissions_required
    def work_editions(self, **kwargs):
        """See all editions by work"""

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
        data = {}
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

    # OAuth Methods

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