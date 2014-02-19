#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml.objectify import fromstring as object_from_string
from urllib import urlencode
import oauth2 as oauth
import requests
import time
import urlparse


class GoodreadsException(Exception):
    pass


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class GoodreadsUser(Bunch):

    def __repr__(self):
        return '<GoodreadsUser:%s:%s>' % (self.id, self.name)

    @classmethod
    def from_object(cls, o):
        u = cls(
            id=o.id.text,
            name=o.name.text,
            link=o.link.text,
        )

        u.location = o.location.text
        u.image = o.image_url.text
        u.small_image = o.small_image_url.text

        u.joined = o.joined.text
        u.last_active = o.last_active.text

        u.about = o.about.text
        u.age = o.age.text
        try:
            u.favorite_authors = [GoodreadsAuthor.from_object(a.author) for a in o.favorite_authors]
        except AttributeError:
            u.favorite_authors = None
# TODO: favorite books not working on api end?
#        u.favorite_books = [GoodreadsBook.from_object(b) for b in o.favorite_books]
        u.friends_count = o.friends_count.text
        u.gender = o.gender.text
        u.groups_count = o.groups_count.text
        u.interests = o.interests.text
        u.reviews_count = o.reviews_count.text
        u.reviews_rss_url = o.reviews_rss_url.text

        return u

    @classmethod
    def from_auth_user_object(cls, o):
        return cls(
            id=o.attrib['id'],
            name=o.name.text,
            link=o.link.text
        )


class GoodreadsAuthor(Bunch):

    def __repr__(self):
        return '<GoodreadsAuthor:%s:%s>' % (self.id, self.name)

    @classmethod
    def from_object(cls, o):
        return cls(
            id=o.id.text,
            name=o.name.text
        )


class GoodreadsSeries(Bunch):

    def __init__(self):
        raise NotImplementedError

        # <series>
        # <id>62223</id>
        # <title>
        # <![CDATA[
        #    Brian's Saga
        # ]]>
        # </title>
        # <description>
        # <![CDATA[
        # ]]>
        # </description>
        # <note>
        # <![CDATA[
        # ]]>
        # </note>
        # <series_works_count>7</series_works_count>
        # <primary_work_count>5</primary_work_count>
        # <numbered>true</numbered>
        # </series>


class GoodreadsWork(Bunch):

    @classmethod
    def from_object(cls, work):
        return cls(**{
            'id': work.id,
            'title': work.title,
            'media_type': work.media_type,
            'publication_day': work.publication_day,
            'publication_month': work.publication_month,
            'publication_year': work.publication_year,
            'language_id': work.language_id,
            'best_book_id': work.best_book_id,
            'books_count': work.books_count,
            'default_chaptering_book_id': work.default_chaptering_book_id,
            'desc_user_id': work.desc_user_id,
            'rating_dist': work.rating_dist,
            'ratings_count': work.ratings_count,
            'ratings_sum': work.ratings_sum,
            'reviews_count': work.reviews_count,
            'text_reviews_count': work.text_reviews_count,
        })


class GoodreadsBook(Bunch):

    def __repr__(self):
        return '<GoodreadsBook:%s:%s>' % (self.id, self.title)

    @classmethod
    def from_object(cls, o):
        return cls(
            id=o.id.text,
            title=o.title.text,
            link=o.url.text
        )

#    @classmethod
#    def from_element(cls, book):
#        b = cls.from_small_element(book)
#        b.publication_year = book.publication_year
#        b.publication_month = book.publication_month
#        b.publication_day = book.publication_day
#        b.language_code = book.language_code
#        b.edition_information = book.edition_information
#        b.is_ebook = book.is_ebook
#        b.small_image_url = book.small_image_url
#        b.url = book.url
#        b.link = book.link
#        b.description = book.description
#        b.average_rating = book.average_rating
#        b.ratings_count = book.ratings_count
#        b.text_reviews_count = book.text_reviews_count
#        b.reviews_widget = book.reviews_widget
#        b.popular_shelves = [(s.attrib['name'], s.attrib['count']) for s in book.popular_shelves.iterate_children()]
#        b.book_links = [{'id': l.id, 'name': l.name, 'link': l.link} for l in book.book_links.iterate_children()]
#        b.isbn13 = book.isbn13
#        b.asin = book.asin
#        b.series = [{'id': sw.id, 'position': sw.user_position, 'series': GoodreadsSeries.from_element(sw.series)} for sw in book.series_works.iterate_children()]
#        b.similar_books = [cls.from_small_element(sb) for sb in book.similar_books.iterate_children()]
#
#        return b
#
#    @classmethod
#    def from_small_element(cls, book):
#        return cls(**{
#            'id': book.id,
#            'title': book.title,
#            'authors': [GoodreadsAuthor.from_element(author) for author in book.authors.iterchildren()],
#            'format': book.format,
#            'pages': book.num_pages,
#            'date': book.published,
#            'publisher': book.publisher,
#            'image': book.image_url,
#            'isbn': book.isbn,
#            })


class GoodreadsShelf(Bunch):
    def __init__(self):
        raise NotImplementedError

    #        book_count
    #        description
    #        display_fields
    #        exclusive
    #        featured
    #        id
    #        user_id
    #        name
    #        order
    #        per_page
    #        recommend_for
    #        sort
    #        sticky


class Goodreads(object):

    base_url = 'http://www.goodreads.com'  # no slash

    def __init__(self, developer_key=None, developer_secret=None, user_token=None, user_secret=None):

        if developer_key and developer_secret:
            self.set_developer(developer_key, developer_secret)
            if not (user_token and user_secret):
                self.client = oauth.Client(self.consumer)

        else:
            self.developer = False

        if user_token and user_secret:
            self.set_oauth_user(user_token, user_secret)
        else:
            self.oauth = False

        self.last_request = time.time() - 1
        self.client.follow_redirects = False

    def set_developer(self, key, secret):
        self.developer_key = key
        self.developer_secret = secret
        self.consumer = oauth.Consumer(key=self.developer_key, secret=self.developer_secret)
        self.developer = True

    def developer_check(self):
        if not self.developer:
            raise GoodreadsException('Operation requires developer api keys; not provided')

    def set_oauth_user(self, token, secret):
        self.developer_check()
        self.user_token = token
        self.user_secret = secret
        self.token = oauth.Token(self.user_token, self.user_secret)
        self.client = oauth.Client(self.consumer, self.token)
        self.oauth = True

    def oauth_check(self):
        if not self.oauth:
            raise GoodreadsException('Operation requires OAuth; not provided')

    # HTTP helpers

    def wait(self):
        since = time.time() - self.last_request
        if since < 1:
            time.sleep(1 - since)

    def get(self, url, data):
        self.wait()
        return requests.get('%s/%s' % (self.base_url, url), params=data)  # TODO: Bad response

    def post(self, url, data):
        self.wait()
        return requests.post('%s/%s' % (self.base_url, url), data)  # TODO: Bad response

    def dev_get(self, url, data):
        self.developer_check()
        data.update(key=self.developer_key)
        return self.get(url, data)

    def dev_post(self, url, data):
        self.developer_check()
        data.update(key=self.developer_key)
        return self.post(url, data)

    def client_request(self, method, url, data={}, headers={}):
        self.oauth_check()
        self.wait()
        response, content = self.client.request(
            uri='%s/%s' % (self.base_url, url),
            method=method,
            body=urlencode(data),
            headers=headers)  # TODO: Bad response
        return content

    def client_get(self, url, data={}, headers={}):
        return self.client_request('GET', url, data, headers)

    def client_post(self, url, data={}, headers={}):
        return self.client_request('POST', url, data, headers)

    def client_put(self, url, data={}, headers={}):
        return self.client_request('PUT', url, data, headers)

    def client_delete(self, url, data={}, headers={}):
        return self.client_request('DELETE', url, data, headers)

    # OAuth

    def oauth_authorize_url(self):
        response, content = self.client.request('%s/oauth/request_token' % self.base_url, 'GET')
        if response['status'] != '200':
            raise Exception('Invalid response: %s' % response['status'])
        self.request_token = dict(urlparse.parse_qsl(content))
        return '%s?oauth_token=%s' % ('%s/oauth/authorize' % self.base_url, self.request_token['oauth_token'])

    def oauth_retrieve_token(self):
        token = oauth.Token(self.request_token['oauth_token'], self.request_token['oauth_token_secret'])
        client = oauth.Client(self.consumer, token)
        response, content = client.request('%s/oauth/access_token' % self.base_url, 'POST')
        if response['status'] != '200':
            raise Exception('Invalid response: %s' % response['status'])
        access_token = dict(urlparse.parse_qsl(content))
        self.token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
        self.client = oauth.Client(self.consumer, self.token)
        return self.token

################ API #################
# http://www.goodreads.com/api

    # User

    def user(self, user_id=None, username=None):
        '''
        Get info about a member by id or username: http://www.goodreads.com/api#user.show
        '''
        if not (user_id or username):
            raise GoodreadsException('User id or username required')
        r = self.dev_get('user/show/', {'id': user_id, 'username': username})
        return GoodreadsUser.from_object(object_from_string(r.content).user)

    def auth_user(self):
        '''
         Get id of user who authorized OAuth: http://www.goodreads.com/api#auth.user
        '''
        xml = self.client_get('api/auth_user')
        return GoodreadsUser.from_auth_user_object(object_from_string(xml).user)

    def user_notifications(self,):
        '''
        See the current user's notifications: http://www.goodreads.com/api#notifications
        '''
        xml = self.client_get('notifications?format=xml')
        # TODO: Paging:  Parameters:     page: page number (optional, default 1)
        o = object_from_string(xml)
        try:
            return [
                Bunch(**{
                    'created': n.created_at,  # TODO: Delorean doesn't understand this format
                    'new': n.new.pyval,
                    'html': n.body.html.text
                })
                for n in o.notifications.notification
            ]
        except AttributeError:
            return None

    def user_compare(self, other_user_id):
        '''
        Compare books with another member: http://www.goodreads.com/api#user.compare
        '''
        xml = self.client_get('user/compare/1.xml', {'id': other_user_id})
        o = object_from_string(xml)
        return Bunch(**{
            'common': o.compare.common_count,
            'not_common': o.compare.not_in_common,
            'my-percent': o.compare.your_library_percent,
            'my-total': o.compare.your_total_books_count,
            'their-percent': o.compare.their_library_percent,
            'their-total': o.compare.their_total_books_count,
            'books': [Bunch(**{
                'book': GoodreadsBook.from_object(r.book),
                'my-rating': r.your_review.rating,
                'my-review': r.your_review.text,
                'their-rating': r.their_review.rating,
                'their-review': r.their_review.text,
            }) for r in o.compare.reviews.review],
        })

    # User Followers
    def user_followers(self, user_id):
        '''
        Get a user's followers.

        Get an xml file with the given user's followers.
        '''

        # TODO: Paging: # Parameters:     key: Developer key (required).    id: Goodreads user_id    page: 1-N (optional, default 1)
        # 302 with OATH, 401 with dev
#         xml = self.client_get('user/%s/following' % user_id, {'id': user_id, 'format': 'xml'})
#         o = object_from_string(xml)
#         pass

    def user_following(self,):
        '''
        Get people a user is following.

        Get an xml file with people the given user is following.
        '''

        self.get('user_followings/followings.xml?id=USER_ID')
        # Parameters:     key: Developer key (required).    id: Goodreads user_id    page: 1-N (optional, default 1)
#
#    def followers_create(self,):
#        '''
#        Follow a user.
#
#        Start following a user using OAuth. You'll need to You'll need to register your app (required).
#        '''
#
#        self.POST('user/USER_ID/followers?format=xml')
#        # Parameters:     id: Goodreads user id of user to follow

    # User Friends
#    def user_friends(self,):
#        '''
#        Get a user's friends.
#
#        Get an xml file with the given user's friends using OAuth.
#        '''
#
#        self.get('friend/user.xml')
#        # Parameters:     id: Goodreads user_id (required)    page: 1-N (optional, default 1)    sort: first_name|date_added|last_online (optional)
#
#    def friends_create(self,):
#        '''
#        Add a friend.
#
#        Sends a friend request to a user using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('friend/add_as_friend.xml')
#        # Parameters:     id: Goodreads user id for friend
#
#    def updates_friends(self,):
#        '''
#        Get your friend updates.
#
#        Get your friend updates (the same data you see on your homepage) using OAuth. You'll need to register your app (required).
#        '''
#
#        self.get('updates/friends.xml')
#        # Parameters:     update: Type of update. Valid values are: books, reviews, statuses. (optional, default all)    update_filter: Which updates to show. Options are: friends (default - includes followers), following, top_friends. (optional)    max_updates: The max limit of updates. (optional)

    # User Status
#    def user_status_create(self,):
#        '''
#        Update user status.
#
#        Add status updates for members using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('user_status.xml')
#        # Parameters:     user_status[book_id]: id of the book being reviewed (optional)    user_status[page]: page of the book (optional)    user_status[percent]: percent complete (use instead of page if appropriate)    user_status[body]: status update (required, unless page or percent is present, then it is optional)
#
#    def user_status_destroy(self,):
#        '''
#        Delete user status.
#
#        Delete a status update for a member using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('user_status/destroy/USER_STATUS_ID?format=xml')
#
#    def user_status_show(self,):
#        '''
#        Get a user status.
#
#        Get information about a user status update.
#        '''
#
#        self.get('user_status/show/USER_STATUS_ID?format=xml&key=MY_KEY')
#        # Parameters:     key: Developer key (required).    id: user status id
#
#    def user_status_index(self,):
#        '''
#        View user statuses.
#
#        View most recent user statuses on the site.
#        '''
#
#        self.get('user_status.xml')

    # Author

    def author(self, author_id):
        '''
        Get info about an author by id: http://www.goodreads.com/api#author.show
        '''
        raise NotImplementedError
#         response = self.dev_get('author/show.xml', {'id': author_id})
#         author_show = objectify.fromstring(response.content)  # @UndefinedVariable
#         books = [self.book_from_element(book) for book in author_show.author.books.iterchildren()]

    def author_search(self, name):
        '''
        Find an author by name: http://www.goodreads.com/api#search.authors
        '''
        raise NotImplementedError
        self.dev_get('api/author_url/<ID>')
        # Parameters:     id: Author name    key: Developer key (required).

    def author_books(self, author_id, limit=None):
        '''
        Paginate an author's books: http://www.goodreads.com/api#author.books
        '''
        page = 1
        counter = 0
        while True:
            response = self.dev_get('author/list.xml', {'id': author_id, 'page': page})
            author_list = objectify.fromstring(response.content)  # @UndefinedVariable
            for book in author_list.author.books.iterchildren():
                yield self.book_from_element(book)
                counter += 1
                if counter <= limit:
                    return
            if author_list.author.books.attrib['total'] < author_list.author.books.attrib['end']:
                page += 1
            else:
                return

    # Fanship
#    def fanship_create(self,):
#        '''
#        Become fan of an author.
#
#        Make the signed-in user become a fan of an author using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('fanships?format=xml')
#        # Parameters:     fanship[author_id]: id of the author (required)
#
#    def fanship_destroy(self,):
#        '''
#        Stop being fan of an author.
#
#        Stop being a fan of an author using OAuth. You'll need to register your app (required).
#        '''
#
#        self.DELETE('fanships/FANSHIP_ID?format=xml')
#
#    def fanship_show(self,):
#        '''
#        Show fanship information.
#
#        Get an XML file using OAuth describing the association between a user and an author. You'll need to register your app (required).
#        '''
#
#        self.get('fanships/show/FANSHIP_ID?format=xml')

    # Book

    def book_search(self,):
        '''
        Find books by title, author, or ISBN.
        '''
        raise NotImplementedError
        self.dev_get('search.xml')
        # Parameters:     q: The query text to match against book title, author, and ISBN fields. Supports boolean operators and phrase searching.    page: Which page to return (default 1, optional)    key: Developer key (required).    search[field]: Field to search, one of 'title', 'author', or 'genre' (default is 'all')

    def book(self, book_id):
        '''
        Get the reviews for a book given a Goodreads book id: http://www.goodreads.com/api#book.show.
        XML responses also include shelves and book meta-data (title, author, et cetera).
        '''
        raise NotImplementedError
        self.dev_get('book/show?format=FORMAT')
        # Parameters:     format: xml or json    key: Developer key (required).    id: A Goodreads internal book_id    text_only: Only show reviews that have text (default false)    rating: Show only reviews with a particular rating (optional)

    def book_by_isbn(self, isbn):
        '''
        Get the reviews for a book given an ISBN: http://www.goodreads.com/api#book.show_by_isbn
        '''
        raise NotImplementedError
        self.dev_get('book/isbn?format=FORMAT&isbn=ISBN')
        # Parameters:     format: xml or json    callback: function to wrap JSON response if format=json    key: Developer key (required only for XML).    user_id: 16193727 (required only for JSON)    isbn: The ISBN of the book to lookup.    rating: Show only reviews with a particular rating (optional)

    # Shelves

    def shelve_book(self, shelf_name, book_id, remove=False):
        '''
        Add/remove a book to a shelf: http://www.goodreads.com/api#shelves.add_to_shelf
        '''
        raise NotImplementedError
        data = {
            'name': shelf_name,
            'book_id': book_id,  # Book_id (capitalization?)
            }
        if remove:
            data.update(a='remove')
        self.client_post('shelf/add_to_shelf.xml')

    def shelf_list(self, user_id=None):
        '''
        Get a user's shelves: http://www.goodreads.com/api#shelves.list
        '''
        raise NotImplementedError
        self.dev_get('shelf/list.xml', {"user_id": user_id if user_id else self.user_id})

    def shelf_create(self,):
        '''
        Add book shelf: http://www.goodreads.com/api#user_shelves.create
        '''
        raise NotImplementedError
        self.client_post('user_shelves.xml')
        # Parameters:     user_shelf[name]: Name of the new shelf    user_shelf[exclusive_flag]: 'true' or 'false' (optional, default false)    user_shelf[sortable_flag]: 'true' or 'false' (optional, default false)    user_shelf[featured]: 'true' or 'false' (optional, default false)

    def shelf_destroy(self, shelf_id):
        '''
        Delete book shelf: http://www.goodreads.com/api#user_shelves.destroy
        '''
        raise NotImplementedError
        self.client_delete('user_shelves/destroy.xml?id=USER_SHELF_ID')

    def shelf_update(self,):
        '''
        Edit book shelf: http://www.goodreads.com/api#user_shelves.update
        '''
        raise NotImplementedError
        self.client_put('user_shelves/update.xml?id=USER_SHELF_ID')
        # Parameters:     user_shelf[name]: Name of the new shelf    user_shelf[exclusive_flag]: 'true' or 'false' (optional, default false)    user_shelf[sortable_flag]: 'true' or 'false' (optional, default false)    user_shelf[featured]: 'true' or 'false' (optional, default false)

# Comments
#
#    def comment_create(self,):
#        '''
#        Create a comment.
#
#        Creates a new comment. You'll need to register your app (required).
#        '''
#
#        self.POST('comment.xml')
#        # Parameters:     type: one of 'author_blog_post', 'book_news_post', 'blog', 'chapter', 'comment', 'event_response', 'fanship', 'interview', 'librarian_note', 'list', 'owned_book', 'photo', 'poll', 'poll_vote', 'question', 'question_user_stat', 'quiz', 'quiz_score', 'rating', 'recommendation', 'recommendation_request', 'review', 'topic', 'user', 'user_challenge', 'user_list_vote', 'user_quote', 'user_list_challenge', 'user_status', 'video'    id: Id of resource given as type param    comment[body]: This review was really insightful!
#
#    def comment_list(self,):
#        '''
#        List comments on a subject.
#
#        Lists comments
#        '''
#
#        self.get('comment.xml')
#        # Parameters:     type: one of 'author_blog_post', 'book_news_post', 'blog', 'chapter', 'comment', 'event_response', 'fanship', 'interview', 'librarian_note', 'list', 'owned_book', 'photo', 'poll', 'poll_vote', 'question', 'question_user_stat', 'quiz', 'quiz_score', 'rating', 'recommendation', 'recommendation_request', 'review', 'topic', 'user', 'user_challenge', 'user_list_vote', 'user_quote', 'user_list_challenge', 'user_status', 'video'    id: Id of resource given as type param    page: 1-N (optional, default 1)

# Events
#    def events_list(self,):
#        '''
#        Events in your area.
#
#        Shows events nearby the authenticating user or you can get a list of events near a location by passing lat/lng coordinates
#        '''
#
#        self.get('event.xml')
#        # Parameters:     key: Developer key (required).    lat: Latitude (optional)    lng: Longitude (optional)

# Groups
#    def group_list(self,):
#        '''
#        List groups for a given user.
#
#        Returns xml list of groups the user specified by id belongs to
#        '''
#
#        self.get('group/list/USER_ID.xml')
#        # Parameters:     sort: One of 'my_activity', 'members', 'last_activity', 'title' ('members' will sort by number of members in the group)    key: Developer key (required).
#
#    def group_members(self,):
#        '''
#        Return members of a particular group.
#
#        Returns an XML list of members of the group
#        '''
#
#        self.get('group/members.xml?id=GROUP_ID')
#        # Parameters:     sort: One of 'last_online', 'num_comments', 'date_joined', 'num_books', 'first_name'    q: List of names to search for, separating each name with a space character. Optional, will find all members by default    page: Which page of results to show (default 1)    key: Developer key (required).
#
#    def group_show(self,):
#        '''
#        Get info about a group by id.
#
#        XML version of group/show
#        '''
#
#        self.get('group/show.xml?id=GROUP_ID')
#        # Parameters:     sort: Field to sort topics by. One of 'comments_count', 'title', 'updated_at', 'views'    order: 'a' for ascending, 'd' for descending    key: Developer key (required).

# Owned Books
#    def owned_books_create(self,):
#        '''
#        Add to books owned.
#
#        Adds a book to user's list of owned books using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('owned_books.xml')
#        # Parameters:     owned_book[book_id]: id of the book (required)    owned_book[condition_code]: one of 10 (brand new), 20 (like new), 30 (very good), 40 (good), 50 (acceptable), 60 (poor)    owned_book[condition_description]: description of book's condition    owned_book[original_purchase_date]: when book was purchased    owned_book[original_purchase_location]: where this book was purchased    owned_book[unique_code]: BookCrossing id (BCID)
#
#    def owned_books_list(self,):
#        '''
#        List books owned by a user.
#
#        Get an xml file with a list of owned books using OAuth. You'll need to register your app (required).
#        '''
#
#        self.get('owned_books/user?format=xml')
#        # Parameters:     id: Goodreads user_id    page: 1-N (optional, default 1)
#
#    def owned_books_show(self,):
#        '''
#        Show an owned book.
#
#        Get an xml file describing an owned book using OAuth, including the current owner's user id (current_owner_id), it's BookCrossing ID (bcid), number of times traded, etc. OWNED_BOOK_ID is a unique identifier for the owned book (not a book_id) You'll need to register your app (required).
#        '''
#
#        self.get('owned_books/show.xml?id=OWNED_BOOK_ID')
#
#    def owned_books_update(self,):
#        '''
#        Update an owned book.
#
#        Updates a book a user owns using OAuth. You'll need to register your app (required).
#        '''
#
#        self.PUT('owned_books/update.xml?id=ID')
#        # Parameters:     id: id of the owned book record    owned_book[book_id]: id of the book (required)    owned_book[condition_code]: one of 10 (brand new), 20 (like new), 30 (very good), 40 (good), 50 (acceptable), 60 (poor), (optional)    owned_book[condition_description]: description of book's condition (optional)    owned_book[original_purchase_date]: when book was purchased (optional)    owned_book[original_purchase_location]: where this book was purchased (optional)    owned_book[unique_code]: BookCrossing id (BCID) (optional)

# Reviews
#    def ratings_create(self,):
#        '''
#        Rate a review.
#
#        Rate a review (like or dislike) using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('rating/new_review?format=xml')
#        # Parameters:     resource_id: id of the review to rate    rating: 1 (like) or 0 (unlike)
#
#    def review_create(self,):
#        '''
#        Add review.
#
#        Add book reviews for members using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('review.xml')
#        # Parameters: (self,):
#        # Book_id: Goodreads book_id (required)    review[review]: Text of the review (optional)    review[rating]: Rating (0-5) (optional, default is 0 (No rating))    review[read_at]: Date (YYYY-MM-DD format, e.g. 2008-02-01) (optional)    shelf: read|currently-reading|to-read|<USER SHELF NAME> (optional, must exist, see: shelves.list)
#
#    def review_destroy(self,):
#        '''
#        Destroy a review.
#
#        Delete book reviews for members using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('/review/destroy.xml')
#        # Parameters: (self,): Book_id: Goodreads book_id (required)
#
#    def reviews_list(self,):
#        '''
#        Get the books on a members shelf.
#
#        Get the books on a members shelf. Customize the feed with the below variables. Viewing members with profiles who have set them as visible to members only or just their friends requires using OAuth.
#        '''
#
#        self.get('review/list?format=xml&v=2')
#        # Parameters:     v: 2    id: Goodreads id of the user    shelf: read, currently-reading, to-read, etc. (optional)    sort: title, author, cover, rating, year_pub, date_pub, date_pub_edition, date_started, date_read, date_updated, date_added, recommender, avg_rating, num_ratings, review, read_count, votes, random, comments, notes, isbn, isbn13, asin, num_pages, format, position, shelves, owned, date_purchased, purchase_location, condition (optional)    search[query]: query text to match against member's books (optional)    order: a, d (optional)    page: 1-N (optional)    per_page: 1-200 (optional)    key: Developer key (required).
#
#    def review_recent_reviews(self,):
#        '''
#        Recent reviews from all members.
#
#        Get an xml file with the most recently added reviews from all members.
#        '''
#
#        self.get('review/recent_reviews.xml')
#        # Parameters:     key: Developer key (required).
#
#    def review_show(self,):
#        '''
#        Get a review.
#
#        Get an xml file that contains the review and rating
#        '''
#
#        self.get('review/show.xml')
#        # Parameters:     key: Developer key (required).    id: id of the review    page: 1-N. The page number of comments. (default 1, optional)
#
#    def review_show_by_user_and_book(self,):
#        '''
#        Get a user's review for a given book.
#
#        Get an xml file that contains the review and rating for the specified book and user
#        '''
#
#        self.get('review/show_by_user_and_book.xml')
#        # Parameters:     key: Developer key (required).    user_id: id of the user(self,):
#        # Book_id: id of the book    include_review_on_work: 'true' or 'false' indicating whether to return a review for another book in the same work if review not found for the specified book (default 'false', optional)
#
#    def review_update(self,):
#        '''
#        Update book reviews.
#
#        Update book reviews for members using OAuth. You'll need to register your app (required). This method must be called with a PUT request and the final, numeric portion of the URL is the review ID.
#        '''
#
#        self.PUT('review/<ID>.xml')
#        # Parameters:     review[review]: Text of the review (optional)    review[rating]: Rating (0-5) (optional, 0 means no rating)    review[read_at]: Date (optional, YYYY-MM-DD format, e.g. 2008-02-01)
#
#    def book_review_counts(self,):
#        '''
#        Get review statistics given a list of ISBNs.
#
#        Get review statistics for books given a list of ISBNs. ISBNs can be specified as an array (e.g. isbns[]=0441172717&isbns[]=0141439602) or a single, comma-separated string (e.g. isbns=0441172717,0141439602). You can mix ISBN10s and ISBN13s, but you'll receive a 422 error if you don't specify any, and you'll receive a 404 if none are found.
#        '''
#
#        self.get('book/review_counts.json')
#        # Parameters:     key: Developer key (required).    isbns: Array of ISBNs or a comma seperated string of ISBNs (1000 ISBNs per request max.)    format: json    callback: function to wrap JSON response
#
#    def book_title(self,):
#        '''
#        Get the reviews for a book given a title string.
#
#        Get an xml file that contains embed code for the iframe reviews widget, which shows an excerpt (first 300 characters) of the most popular reviews of a book for a given title/author. The book shown will be the most popular book that matches all the keywords in the input string. The reviews are from all known editions of the book.
#        '''
#        self.get('book/title?format=FORMAT')
#        # format: xml or json
#        # key: Developer key (required)
#        # title
#        # author; optional
#        # rating; optional
#
#    def book_isbn_to_id(self, isbn):
#        '''
#        Get the Goodreads book ID given an ISBN: http://www.goodreads.com/api#book.isbn_to_id
#        '''
#        response = self.get('book/isbn_to_id', {'isbn': isbn})

# Series
#    def series_show(self,):
#        '''
#        See a series.
#
#        Info on a series
#        '''
#
#        self.get('series/show.xml?id=ID')
#
#    def series_list(self,):
#        '''
#        See all series by an author.
#
#        List of all series by an author
#        '''
#
#        self.get('/series/list?format=xml&id=AUTHOR_ID')
#
#    def series_work(self,):
#        '''
#        See all series a work is in.
#
#        List of all series a work is in
#        '''
#
#        self.get('series/work.xml?id=WORK_ID')

# Topics
#    def topic_create(self,):
#        '''
#        Create a new topic via OAuth.
#
#        Create a new topic using OAuth. You'll need to register your app (required).
#        '''
#
#        self.POST('topic.xml')
#        # Parameters:     topic[subject_type]: Either 'Book' or 'Group'. If 'Book', the book the topic is about. If 'Group', the group that the topic belongs to. (required)    topic[subject_id]: The id for the subject the topic belongs to, either book_id or group_id, as appropriate (required)    topic[folder_id]: If the subject is a group, you can supply a folder id to add the topic to. Be sure that the folder belongs to the group. By default, if the subject_type is 'Group', then the topic will be added to the 'general' folder    topic[title]: Title for the topic (required)    topic[question_flag]: Indicates whether the topic is a discussion question ('1') or not ('0'). Default is 0 (non-question)    comment[body_usertext]: The text of the comment that starts the topic thread. Can include Goodreads book/author tags of the form [book:Title|ID] (required)    update_feed: Indicates whether the comment for the new topic should be added to the user's update feed. To enable, set to 'on'; otherwise, default is not to add to update feed    digest: Indicates whether the user would like to receive an email when someone replies to the topic (user will get one email only). To enable, set to 'on'; otherwise, default is not to add to update feed
#
#    def topic_group_folder(self,):
#        '''
#        Get list of topics in a group's folder.
#
#        Returns a list of topics in a group's folder specified either by folder id or by group id.
#        '''
#
#        self.get('topic/group_folder/FOLDER_ID.xml')
#        # Parameters:     group_id: If supplied and id is set to 0, then will return topics from the general folder for the group indicated by group_id. If id is non-zero, this param is ignored. Note: may return 404 if there are no topics in the general folder for the specified group    page: Page in results to show, 1-N (default 1)    sort: One of 'comments_count', 'title', 'updated_at', 'views'    order: 'a' for ascending, 'd' for descending    key: Developer key (required).
#
#    def topic_show(self,):
#        '''
#        Get info about a topic by id.
#
#        XML version of topic/show
#        '''
#
#        self.get('topic/show/TOPIC_ID?format=xml')
#        # Parameters:     key: Developer key (required).
#
#    def topic_unread_group(self,):
#        '''
#        Get a list of topics with unread comments.
#
#        Get a list of topics from a specified group that have comments added since the last time the user viewed the topic using OAuth. You'll need to register your app (required).
#        '''
#
#        self.get('topic/unread_group/GROUP_ID?format=xml')
#        # Parameters:     viewed: Indicates whether to show topics user has viewed before or not. Default is to include all topics; set this param to 'true' or '1' to restrict to only topics the user has already viewed    page: Page in results to show, 1-N (default 1)    sort: One of 'comments_count', 'title', 'updated_at', 'views'    order: 'a' for ascending, 'd' for descending

# Misc
#    def quotes_create(self,):
#        '''
#        Add a quote.
#
#        Add a quote using OAuth. If you don't specify an author_id, it will try to look one up based on the author_name you provide. You'll need to register your app (required).
#        '''
#
#        self.POST('quotes.xml')
#        # Parameters:     quote[author_name]: Name of the quote author (required)    quote[author_id]: id of the author    quote[book_id]: id of the book from which the quote was taken    quote[body]: The quote! (required)    quote[tags]: Comma-separated tags    isbn: ISBN of the book from which the quote was taken. This will not override the book_id if it was provided

# Extra Permissions
    def work_editions(self):
        '''
        List of all the available editions of a particular work. This API requires extra permission
        '''
        raise NotImplementedError('Extra permissions from goodreads were denied for development.')

    def list_show(self,):
        '''
        Get the books from a listopia list. This API requires extra permission
        '''
        raise NotImplementedError('Extra permissions from goodreads were denied for development.')

    def list_tag(self,):
        '''
        Get the listopia lists for a given tag. This API requires extra permission
        '''
        raise NotImplementedError('Extra permissions from goodreads were denied for development.')

    def list_book(self,):
        '''
        Get the listopia lists for a given book. This API requires extra permission
        '''
        raise NotImplementedError('Extra permissions from goodreads were denied for development.')
