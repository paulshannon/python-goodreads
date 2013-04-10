from lxml import objectify
from urllib import urlencode
import oauth2 as oauth
import requests
import time
import urlparse


class Goodreads(object):
    base_url = 'http://www.goodreads.com'

    def __init__(self, developer_key=None, developer_secret=None, user_token=None, user_secret=None):
        self.developer_key = developer_key
        self.developer_secret = developer_secret
        self.user_token = user_token
        self.user_secret = user_secret

        if self.developer_key and self.developer_secret:
            self.consumer = oauth.Consumer(key=self.developer_key, secret=self.developer_secret)

        if self.user_token and self.user_secret:
            self.token = oauth.Token(self.user_token, self.user_secret)
            self.client = oauth.Client(self.consumer, self.token)

        self.last_request = time.time()

    # HTTP helpers

    def wait(self):
        since = time.time() - self.last_request
        if since < 1:
            time.sleep(1 - since)

    def get(self, url, data):
        data.update(key=self.developer_key)
        self.wait()
        return requests.get('%s/%s' % (self.base_url, url), params=data)

    def post(self, url, data):
        data.update(key=self.developer_key)
        self.wait()
        return requests.post('%s/%s' % (self.base_url, url), data)

    def client_get(self, url, data={}, headers={}):
        self.wait()
        response, content = self.client.request('%s/%s' % (self.base_url, url), 'GET', urlencode(data), headers)
        return content

    def client_post(self, url, data={}, headers={}):
        self.wait()
        response, content = self.client.request('%s/%s' % (self.base_url, url), 'POST', urlencode(data), headers)
        return content

    # OAuth

    def oauth_authorize_url(self):
        response, content = self.client.request('%s/oauth/request_token' % self.base_url, 'GET')
        if response['status'] != '200':
            raise Exception('Invalid response: %s' % response['status'])
        self.request_token = dict(urlparse.parse_qsl(content))
        return '%s?oauth_token=%s' % ('%s/oauth/authorize' % self.base_url, self.request_token['oauth_token'])

    def oauth_retrieve_token(self):
        token = oauth.Token(self.request_token['oauth_token'], self.request_token['oauth_token_secret'])
        client = oauth.Client(self.oauth_consumer, token)
        response, content = client.request('%s/oauth/access_token' % self.base_url, 'POST')
        if response['status'] != '200':
            raise Exception('Invalid response: %s' % response['status'])
        access_token = dict(urlparse.parse_qsl(content))
        self.token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
        self.client = oauth.Client(self.consumer, self.token)

    ################ API #################

    # User

    def auth_user(self,):
        '''
        Current OAuth User info
        '''
        xml = self.client_get('api/auth_user')
        u = objectify.fromstring(xml)  # @UndefinedVariable
        return {'id': u.user.attrib['id'], 'name': u.user.name, 'link': u.user.link}

    # Author

    def author_books(self, author_id):
        '''
        List of author's books
        '''
        page = 1
        while True:
            response = self.get('author/list.xml', {'id': author_id, 'page': page})
            author_list = objectify.fromstring(response.content)  # @UndefinedVariable
            for book in author_list.author.books.iterchildren():
                yield self.book_from_element(book)
            if author_list.author.books.attrib['total'] < author_list.author.books.attrib['end']:
                page += 1
            else:
                break

    def author_show(self, author_id):
        '''
        Author Info
        '''
        response = self.get('author/show.xml', {'id': author_id})
        author_show = objectify.fromstring(response.content)  # @UndefinedVariable
        books = [self.book_from_element(book) for book in author_show.author.books.iterchildren()]

    def book_isbn_to_id(self,):
        '''
        Get the Goodreads book ID given an ISBN.

        Get the Goodreads book ID given an ISBN. Response contains the ID without any markup.
        '''

        self.get('book/isbn_to_id')
        # Parameters:     key: Developer key (required).    isbn: The ISBN of the book to lookup.

    def book_review_counts(self,):
        '''
        Get review statistics given a list of ISBNs.

        Get review statistics for books given a list of ISBNs. ISBNs can be specified as an array (e.g. isbns[]=0441172717&isbns[]=0141439602) or a single, comma-separated string (e.g. isbns=0441172717,0141439602). You can mix ISBN10s and ISBN13s, but you'll receive a 422 error if you don't specify any, and you'll receive a 404 if none are found.
        '''

        self.get('book/review_counts.json')
        # Parameters:     key: Developer key (required).    isbns: Array of ISBNs or a comma seperated string of ISBNs (1000 ISBNs per request max.)    format: json    callback: function to wrap JSON response

    def book_show(self,):
        '''
        Get the reviews for a book given a Goodreads book id. XML responses also include shelves and book meta-data (title, author, et cetera). The Goodreads API gives you full access to Goodreads-owned meta-data, but it does not give you full access to book meta-data supplied by third parties such as Ingram. Book cover images, descriptions, and other data from third party sources might be excluded, because we do not have a license to distribute these data via our API. If you need book meta-data beyond what our API provides, consider signing up for an Amazon developer key.
        '''

        self.get('book/show?format=FORMAT')
        # Parameters:     format: xml or json    key: Developer key (required).    id: A Goodreads internal book_id    text_only: Only show reviews that have text (default false)    rating: Show only reviews with a particular rating (optional)

    def book_show_by_isbn(self,):
        '''
        Get the reviews for a book given an ISBN.

        Get an xml or json file that contains embed code for the iframe reviews widget that shows excerpts (first 300 characters) of the most popular reviews of a book for a given ISBN. The reviews are from all known editions of the book.
        '''

        self.get('book/isbn?format=FORMAT&isbn=ISBN')
        # Parameters:     format: xml or json    callback: function to wrap JSON response if format=json    key: Developer key (required only for XML).    user_id: 16193727 (required only for JSON)    isbn: The ISBN of the book to lookup.    rating: Show only reviews with a particular rating (optional)

    def book_title(self,):
        '''
        Get the reviews for a book given a title string.

        Get an xml file that contains embed code for the iframe reviews widget, which shows an excerpt (first 300 characters) of the most popular reviews of a book for a given title/author. The book shown will be the most popular book that matches all the keywords in the input string. The reviews are from all known editions of the book.
        '''
        self.get('book/title?format=FORMAT')
        # format: xml or json
        # key: Developer key (required)
        # title
        # author; optional
        # rating; optional

    def comment_create(self,):
        '''
        Create a comment.

        Creates a new comment. You'll need to register your app (required).
        '''

        self.POST('comment.xml')
        # Parameters:     type: one of 'author_blog_post', 'book_news_post', 'blog', 'chapter', 'comment', 'event_response', 'fanship', 'interview', 'librarian_note', 'list', 'owned_book', 'photo', 'poll', 'poll_vote', 'question', 'question_user_stat', 'quiz', 'quiz_score', 'rating', 'recommendation', 'recommendation_request', 'review', 'topic', 'user', 'user_challenge', 'user_list_vote', 'user_quote', 'user_list_challenge', 'user_status', 'video'    id: Id of resource given as type param    comment[body]: This review was really insightful!

    def comment_list(self,):
        '''
        List comments on a subject.

        Lists comments
        '''

        self.get('comment.xml')
        # Parameters:     type: one of 'author_blog_post', 'book_news_post', 'blog', 'chapter', 'comment', 'event_response', 'fanship', 'interview', 'librarian_note', 'list', 'owned_book', 'photo', 'poll', 'poll_vote', 'question', 'question_user_stat', 'quiz', 'quiz_score', 'rating', 'recommendation', 'recommendation_request', 'review', 'topic', 'user', 'user_challenge', 'user_list_vote', 'user_quote', 'user_list_challenge', 'user_status', 'video'    id: Id of resource given as type param    page: 1-N (optional, default 1)

    def events_list(self,):
        '''
        Events in your area.

        Shows events nearby the authenticating user or you can get a list of events near a location by passing lat/lng coordinates
        '''

        self.get('event.xml')
        # Parameters:     key: Developer key (required).    lat: Latitude (optional)    lng: Longitude (optional)

    def fanship_create(self,):
        '''
        Become fan of an author.

        Make the signed-in user become a fan of an author using OAuth. You'll need to register your app (required).
        '''

        self.POST('fanships?format=xml')
        # Parameters:     fanship[author_id]: id of the author (required)

    def fanship_destroy(self,):
        '''
        Stop being fan of an author.

        Stop being a fan of an author using OAuth. You'll need to register your app (required).
        '''

        self.DELETE('fanships/FANSHIP_ID?format=xml')

    def fanship_show(self,):
        '''
        Show fanship information.

        Get an XML file using OAuth describing the association between a user and an author. You'll need to register your app (required).
        '''

        self.get('fanships/show/FANSHIP_ID?format=xml')

    def followers_create(self,):
        '''
        Follow a user.

        Start following a user using OAuth. You'll need to You'll need to register your app (required).
        '''

        self.POST('user/USER_ID/followers?format=xml')
        # Parameters:     id: Goodreads user id of user to follow

    def friends_create(self,):
        '''
        Add a friend.

        Sends a friend request to a user using OAuth. You'll need to register your app (required).
        '''

        self.POST('friend/add_as_friend.xml')
        # Parameters:     id: Goodreads user id for friend

    def group_list(self,):
        '''
        List groups for a given user.

        Returns xml list of groups the user specified by id belongs to
        '''

        self.get('group/list/USER_ID.xml')
        # Parameters:     sort: One of 'my_activity', 'members', 'last_activity', 'title' ('members' will sort by number of members in the group)    key: Developer key (required).

    def group_members(self,):
        '''
        Return members of a particular group.

        Returns an XML list of members of the group
        '''

        self.get('group/members.xml?id=GROUP_ID')
        # Parameters:     sort: One of 'last_online', 'num_comments', 'date_joined', 'num_books', 'first_name'    q: List of names to search for, separating each name with a space character. Optional, will find all members by default    page: Which page of results to show (default 1)    key: Developer key (required).

    def group_show(self,):
        '''
        Get info about a group by id.

        XML version of group/show
        '''

        self.get('group/show.xml?id=GROUP_ID')
        # Parameters:     sort: Field to sort topics by. One of 'comments_count', 'title', 'updated_at', 'views'    order: 'a' for ascending, 'd' for descending    key: Developer key (required).

    def list_book(self,):
        '''
        Get the listopia lists for a given book.

        XML version of list/book. This API requires extra permission please contact us
        '''

        self.get('list/book.xml?id=BOOK_ID')
        # Parameters:     key: Developer key (required).

    def list_show(self,):
        '''
        Get the books from a listopia list. This API requires extra permission please contact us.

        XML version of list/show
        '''

        self.get('list/show.xml?id=LIST_ID')
        # Parameters:     key: Developer key (required).

    def list_tag(self,):
        '''
        Get the listopia lists for a given tag. This API requires extra permission please contact us.

        XML version of list/tag
        '''

        self.get('list/tag.xml?id=tag_name')
        # Parameters:     key: Developer key (required).

    def notifications(self,):
        '''
        See the current user's notifications.

        Viewing any new notifications here will mark them as 'viewed'. using OAuth
        '''

        self.get('/notifications?format=xml')
        # Parameters:     page: page number (optional, default 1)

    def owned_books_create(self,):
        '''
        Add to books owned.

        Adds a book to user's list of owned books using OAuth. You'll need to register your app (required).
        '''

        self.POST('owned_books.xml')
        # Parameters:     owned_book[book_id]: id of the book (required)    owned_book[condition_code]: one of 10 (brand new), 20 (like new), 30 (very good), 40 (good), 50 (acceptable), 60 (poor)    owned_book[condition_description]: description of book's condition    owned_book[original_purchase_date]: when book was purchased    owned_book[original_purchase_location]: where this book was purchased    owned_book[unique_code]: BookCrossing id (BCID)

    def owned_books_list(self,):
        '''
        List books owned by a user.

        Get an xml file with a list of owned books using OAuth. You'll need to register your app (required).
        '''

        self.get('owned_books/user?format=xml')
        # Parameters:     id: Goodreads user_id    page: 1-N (optional, default 1)

    def owned_books_show(self,):
        '''
        Show an owned book.

        Get an xml file describing an owned book using OAuth, including the current owner's user id (current_owner_id), it's BookCrossing ID (bcid), number of times traded, etc. OWNED_BOOK_ID is a unique identifier for the owned book (not a book_id) You'll need to register your app (required).
        '''

        self.get('owned_books/show.xml?id=OWNED_BOOK_ID')

    def owned_books_update(self,):
        '''
        Update an owned book.

        Updates a book a user owns using OAuth. You'll need to register your app (required).
        '''

        self.PUT('owned_books/update.xml?id=ID')
        # Parameters:     id: id of the owned book record    owned_book[book_id]: id of the book (required)    owned_book[condition_code]: one of 10 (brand new), 20 (like new), 30 (very good), 40 (good), 50 (acceptable), 60 (poor), (optional)    owned_book[condition_description]: description of book's condition (optional)    owned_book[original_purchase_date]: when book was purchased (optional)    owned_book[original_purchase_location]: where this book was purchased (optional)    owned_book[unique_code]: BookCrossing id (BCID) (optional)

    def quotes_create(self,):
        '''
        Add a quote.

        Add a quote using OAuth. If you don't specify an author_id, it will try to look one up based on the author_name you provide. You'll need to register your app (required).
        '''

        self.POST('quotes.xml')
        # Parameters:     quote[author_name]: Name of the quote author (required)    quote[author_id]: id of the author    quote[book_id]: id of the book from which the quote was taken    quote[body]: The quote! (required)    quote[tags]: Comma-separated tags    isbn: ISBN of the book from which the quote was taken. This will not override the book_id if it was provided

    def ratings_create(self,):
        '''
        Rate a review.

        Rate a review (like or dislike) using OAuth. You'll need to register your app (required).
        '''

        self.POST('rating/new_review?format=xml')
        # Parameters:     resource_id: id of the review to rate    rating: 1 (like) or 0 (unlike)

    def review_create(self,):
        '''
        Add review.

        Add book reviews for members using OAuth. You'll need to register your app (required).
        '''

        self.POST('review.xml')
        # Parameters: (self,):
        # Book_id: Goodreads book_id (required)    review[review]: Text of the review (optional)    review[rating]: Rating (0-5) (optional, default is 0 (No rating))    review[read_at]: Date (YYYY-MM-DD format, e.g. 2008-02-01) (optional)    shelf: read|currently-reading|to-read|<USER SHELF NAME> (optional, must exist, see: shelves.list)

    def review_destroy(self,):
        '''
        Destroy a review.

        Delete book reviews for members using OAuth. You'll need to register your app (required).
        '''

        self.POST('/review/destroy.xml')
        # Parameters: (self,): Book_id: Goodreads book_id (required)

    def reviews_list(self,):
        '''
        Get the books on a members shelf.

        Get the books on a members shelf. Customize the feed with the below variables. Viewing members with profiles who have set them as visible to members only or just their friends requires using OAuth.
        '''

        self.get('review/list?format=xml&v=2')
        # Parameters:     v: 2    id: Goodreads id of the user    shelf: read, currently-reading, to-read, etc. (optional)    sort: title, author, cover, rating, year_pub, date_pub, date_pub_edition, date_started, date_read, date_updated, date_added, recommender, avg_rating, num_ratings, review, read_count, votes, random, comments, notes, isbn, isbn13, asin, num_pages, format, position, shelves, owned, date_purchased, purchase_location, condition (optional)    search[query]: query text to match against member's books (optional)    order: a, d (optional)    page: 1-N (optional)    per_page: 1-200 (optional)    key: Developer key (required).

    def review_recent_reviews(self,):
        '''
        Recent reviews from all members.

        Get an xml file with the most recently added reviews from all members.
        '''

        self.get('review/recent_reviews.xml')
        # Parameters:     key: Developer key (required).

    def review_show(self,):
        '''
        Get a review.

        Get an xml file that contains the review and rating
        '''

        self.get('review/show.xml')
        # Parameters:     key: Developer key (required).    id: id of the review    page: 1-N. The page number of comments. (default 1, optional)

    def review_show_by_user_and_book(self,):
        '''
        Get a user's review for a given book.

        Get an xml file that contains the review and rating for the specified book and user
        '''

        self.get('review/show_by_user_and_book.xml')
        # Parameters:     key: Developer key (required).    user_id: id of the user(self,):
        # Book_id: id of the book    include_review_on_work: 'true' or 'false' indicating whether to return a review for another book in the same work if review not found for the specified book (default 'false', optional)

    def review_update(self,):
        '''
        Update book reviews.

        Update book reviews for members using OAuth. You'll need to register your app (required). This method must be called with a PUT request and the final, numeric portion of the URL is the review ID.
        '''

        self.PUT('review/<ID>.xml')
        # Parameters:     review[review]: Text of the review (optional)    review[rating]: Rating (0-5) (optional, 0 means no rating)    review[read_at]: Date (optional, YYYY-MM-DD format, e.g. 2008-02-01)

    def search_authors(self,):
        '''
        Find an author by name.

        Get an xml file with the Goodreads url for the given author name.
        '''

        self.get('api/author_url/<ID>')
        # Parameters:     id: Author name    key: Developer key (required).

    def search_books(self,):
        '''
        Find books by title, author, or ISBN.

        Get an xml file with the most popular books for the given query. This will search all books in the title/author/ISBN fields and show matches, sorted by popularity on Goodreads. There will be cases where a result is shown on the Goodreads site, but not through the API. This happens when the result is an Amazon-only edition and we have to honor Amazon's terms of service.
        '''

        self.get('search.xml')
        # Parameters:     q: The query text to match against book title, author, and ISBN fields. Supports boolean operators and phrase searching.    page: Which page to return (default 1, optional)    key: Developer key (required).    search[field]: Field to search, one of 'title', 'author', or 'genre' (default is 'all')

    def series_show(self,):
        '''
        See a series.

        Info on a series
        '''

        self.get('series/show.xml?id=ID')

    def series_list(self,):
        '''
        See all series by an author.

        List of all series by an author
        '''

        self.get('/series/list?format=xml&id=AUTHOR_ID')

    def series_work(self,):
        '''
        See all series a work is in.

        List of all series a work is in
        '''

        self.get('series/work.xml?id=WORK_ID')

    def shelves_add_to_shelf(self,):
        '''
        Add a book to a shelf.

        Add a book to a shelf using OAuth. This method can also be used to remove from shelf. You'll need to register your app (required).
        '''

        self.POST('shelf/add_to_shelf.xml')
        # Parameters:     name: Name of the shelf (see: shelves.list)(self,):
        # Book_id: id of the book to add to the shelf    a: Leave this blank unless you're removing from a shelf. If removing, set this to 'remove'. (optional)

    def shelves_list(self):
        '''
        Get a user's shelves.

        Lists shelves for a user
        '''
        url_handler = self.unauthorized_request('shelf/list.xml', {"user_id": self.user_id})
        return self.parser.parse_shelfs(url_handler)

    def topic_create(self,):
        '''
        Create a new topic via OAuth.

        Create a new topic using OAuth. You'll need to register your app (required).
        '''

        self.POST('topic.xml')
        # Parameters:     topic[subject_type]: Either 'Book' or 'Group'. If 'Book', the book the topic is about. If 'Group', the group that the topic belongs to. (required)    topic[subject_id]: The id for the subject the topic belongs to, either book_id or group_id, as appropriate (required)    topic[folder_id]: If the subject is a group, you can supply a folder id to add the topic to. Be sure that the folder belongs to the group. By default, if the subject_type is 'Group', then the topic will be added to the 'general' folder    topic[title]: Title for the topic (required)    topic[question_flag]: Indicates whether the topic is a discussion question ('1') or not ('0'). Default is 0 (non-question)    comment[body_usertext]: The text of the comment that starts the topic thread. Can include Goodreads book/author tags of the form [book:Title|ID] (required)    update_feed: Indicates whether the comment for the new topic should be added to the user's update feed. To enable, set to 'on'; otherwise, default is not to add to update feed    digest: Indicates whether the user would like to receive an email when someone replies to the topic (user will get one email only). To enable, set to 'on'; otherwise, default is not to add to update feed

    def topic_group_folder(self,):
        '''
        Get list of topics in a group's folder.

        Returns a list of topics in a group's folder specified either by folder id or by group id.
        '''

        self.get('topic/group_folder/FOLDER_ID.xml')
        # Parameters:     group_id: If supplied and id is set to 0, then will return topics from the general folder for the group indicated by group_id. If id is non-zero, this param is ignored. Note: may return 404 if there are no topics in the general folder for the specified group    page: Page in results to show, 1-N (default 1)    sort: One of 'comments_count', 'title', 'updated_at', 'views'    order: 'a' for ascending, 'd' for descending    key: Developer key (required).

    def topic_show(self,):
        '''
        Get info about a topic by id.

        XML version of topic/show
        '''

        self.get('topic/show/TOPIC_ID?format=xml')
        # Parameters:     key: Developer key (required).

    def topic_unread_group(self,):
        '''
        Get a list of topics with unread comments.

        Get a list of topics from a specified group that have comments added since the last time the user viewed the topic using OAuth. You'll need to register your app (required).
        '''

        self.get('topic/unread_group/GROUP_ID?format=xml')
        # Parameters:     viewed: Indicates whether to show topics user has viewed before or not. Default is to include all topics; set this param to 'true' or '1' to restrict to only topics the user has already viewed    page: Page in results to show, 1-N (default 1)    sort: One of 'comments_count', 'title', 'updated_at', 'views'    order: 'a' for ascending, 'd' for descending

    def updates_friends(self,):
        '''
        Get your friend updates.

        Get your friend updates (the same data you see on your homepage) using OAuth. You'll need to register your app (required).
        '''

        self.get('updates/friends.xml')
        # Parameters:     update: Type of update. Valid values are: books, reviews, statuses. (optional, default all)    update_filter: Which updates to show. Options are: friends (default - includes followers), following, top_friends. (optional)    max_updates: The max limit of updates. (optional)

    def user_shelves_create(self,):
        '''
        Add book shelf.

        Add book shelves for members using OAuth. You'll need to register your app (required).
        '''

        self.POST('user_shelves.xml')
        # Parameters:     user_shelf[name]: Name of the new shelf    user_shelf[exclusive_flag]: 'true' or 'false' (optional, default false)    user_shelf[sortable_flag]: 'true' or 'false' (optional, default false)    user_shelf[featured]: 'true' or 'false' (optional, default false)

    def user_shelves_destroy(self,):
        '''
        Delete book shelf.

        Delete a shelf using OAuth. You'll need to register your app (required).
        '''

        self.DELETE('user_shelves/destroy.xml?id=USER_SHELF_ID')

    def user_shelves_update(self,):
        '''
        Edit book shelf.

        Edit a shelf using OAuth. You'll need to register your app (required).
        '''

        self.PUT('user_shelves/update.xml?id=USER_SHELF_ID')
        # Parameters:     user_shelf[name]: Name of the new shelf    user_shelf[exclusive_flag]: 'true' or 'false' (optional, default false)    user_shelf[sortable_flag]: 'true' or 'false' (optional, default false)    user_shelf[featured]: 'true' or 'false' (optional, default false)

    def user_show(self,):
        '''
        Get info about a member by id or username.

        Get an xml file with the public information about the given Goodreads user.
        '''

        self.get('user/show/16193727.xml')
        # Parameters:     key: Developer key (required).    id: Goodreads user id.    username: Goodreads user name (not first name). Usernames are optional on Goodreads.

    def user_compare(self,):
        '''
        Compare books with another member.

        Get an xml file with stats comparing your books to another member's using OAuth. You'll need to register your app (required).
        '''

        self.get('user/compare/1.xml')
        # Parameters:     id: Goodreads user_id you want to compare books to

    def user_followers(self,):
        '''
        Get a user's followers.

        Get an xml file with the given user's followers.
        '''

        self.get('user_followings.xml?id=USER_ID')
        # Parameters:     key: Developer key (required).    id: Goodreads user_id    page: 1-N (optional, default 1)

    def user_following(self,):
        '''
        Get people a user is following.

        Get an xml file with people the given user is following.
        '''

        self.get('user_followings/followings.xml?id=USER_ID')
        # Parameters:     key: Developer key (required).    id: Goodreads user_id    page: 1-N (optional, default 1)

    def user_friends(self,):
        '''
        Get a user's friends.

        Get an xml file with the given user's friends using OAuth.
        '''

        self.get('friend/user.xml')
        # Parameters:     id: Goodreads user_id (required)    page: 1-N (optional, default 1)    sort: first_name|date_added|last_online (optional)

    def user_status_create(self,):
        '''
        Update user status.

        Add status updates for members using OAuth. You'll need to register your app (required).
        '''

        self.POST('user_status.xml')
        # Parameters:     user_status[book_id]: id of the book being reviewed (optional)    user_status[page]: page of the book (optional)    user_status[percent]: percent complete (use instead of page if appropriate)    user_status[body]: status update (required, unless page or percent is present, then it is optional)

    def user_status_destroy(self,):
        '''
        Delete user status.

        Delete a status update for a member using OAuth. You'll need to register your app (required).
        '''

        self.POST('user_status/destroy/USER_STATUS_ID?format=xml')

    def user_status_show(self,):
        '''
        Get a user status.

        Get information about a user status update.
        '''

        self.get('user_status/show/USER_STATUS_ID?format=xml&key=MY_KEY')
        # Parameters:     key: Developer key (required).    id: user status id

    def user_status_index(self,):
        '''
        View user statuses.

        View most recent user statuses on the site.
        '''

        self.get('user_status.xml')

    def work_editions(self,):
        '''
        See all editions by work.

        List of all the available editions of a particular work. This API requires extra permission please contact us
        '''

        self.get('/work/editions.xml?id=WORK_ID')
        # Parameters:     key: Developer key (required)

    @classmethod
    def book_from_element(cls, book):
        return {
            'id': book.id,
            'title': book.title,
            'authors': [cls.author_from_element(author) for author in book.authors.iterchildren()],
            'format': book.format,
            'pages': book.num_pages,
            'date': book.published,
            'publisher': book.publisher,
            'image': book.image_url,
            'isbn': book.isbn,
            }

    @classmethod
    def author_from_element(cls, author):
        return {
            'id': author.id,
            'name': author.name,
            'image': author.image_url,
            'link': author.link
            }
