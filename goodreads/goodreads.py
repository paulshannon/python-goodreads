from urllib import urlencode
import time
import urlparse

from lxml import objectify
import oauth2 as oauth
import requests

def _oauth(f):
    """ Decorator to check for oauth setup"""

    def wrapper(self):
        if not self.oauth:
            raise GoodreadsException('Operation requires OAuth; not provided')
        else:
            f(self)

    return wrapper

def _developer(f):
    """ Decorator to check for developer key setup"""

    def wrapper(self):
        if not self.developer:
            raise GoodreadsException('Operation requires developer api keys; not provided')
        else:
            f(self)

    return wrapper

class GoodreadsError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message, *args, **kwargs):
        self.message = message
        self._args = args
        self._kwargs = kwargs

    def __str__(self):
        return repr(self.message)


class GoodreadsUser(object):
    def __repr__(self):
        return '<GoodreadsUser:%s:%s>' % (self.id, self.name)


class GoodreadsAuthor(object):
    def __repr__(self):
        return '<GoodreadsAuthor:%s:%s>' % (self.id, self.name)


class GoodreadsSeries(object):
    def __repr__(self):
        return '<GoodreadsBook:%s:%s>' % (self.id, self.title)


class GoodreadsWork(object):
    def __repr__(self):
        return '<GoodreadsBook:%s:%s>' % (self.id, self.title)


class GoodreadsBook(object):
    def __repr__(self):
        return '<GoodreadsBook:%s:%s>' % (self.id, self.title)


class GoodreadsShelf(object):
    def __repr__(self):
        return '<GoodreadsShelf:%s:%s>' % (self.id, self.title)


class Goodreads(object):
    base_url = 'http://www.goodreads.com'  # no slash

    def __init__(self, developer_key=None, developer_secret=None, user_token=None, user_secret=None, base_url=False):
        """The main entry point for interacting with the Goodreads API.

        Sets up the developer and user keys and allows for some configuration.

        Args:
            developer_key (str): The Goodreads API developer key; required for almost everything
            developer_secret (str): The Goodreads API developer secret; required for almost everything
            user_token (str): The Goodreads OAuth user token; required for user specific api calls
            user_secret (str): The Goodreads OAuth user token; required for user specific api calls
            base_url (str): The Goodreads url; you probably don't need to change this

        """
        self.developer_key = developer_key
        self.developer_secret = developer_secret

        self.user_token = user_token
        self.user_secret = user_secret

        if developer_key and developer_secret:
            self.developer = True
            self.consumer = oauth.Consumer(key=self.developer_key, secret=self.developer_secret)

            if user_token and user_secret:
                self.oauth = True
                self.token = oauth.Token(self.user_token, self.user_secret)
                self.client = oauth.Client(self.consumer, self.token)
            else:
                self.oauth = False
                self.token = None
                self.client = oauth.Client(self.consumer)
        else:
            self.developer = False
            self.consumer = None

        self.last_request = time.time() - 1
        self.client.follow_redirects = False

        if base_url:
            self.base_url = base_url

    def __repr__(self):
        return '<Goodreads:%s>' % self.developer_key

    # HTTP helpers

    def wait(self):
        since = time.time() - self.last_request
        if since < 1:
            time.sleep(1 - since)

    def get(self, url, data=None):
        if not data:
            data = {}
        self.wait()
        return (
            requests.get(
                '%s/%s' %
                (self.base_url, url), params=data)  # TODO: Bad response
        )

    def post(self, url, data=None):
        if not data:
            data = {}
        self.wait()
        return (
            requests.post(
                '%s/%s' %
                (self.base_url, url), data)  # TODO: Bad response
        )

    @_developer
    def dev_get(self, url, data):
        data.update(key=self.developer_key)
        return self.get(url, data)

    @_developer
    def dev_post(self, url, data):
        data.update(key=self.developer_key)
        return self.post(url, data)

    def client_request(self, method, url, data=None, headers=None):
        if not headers:
            headers = {}
        if not data:
            data = {}
        self.oauth_check()
        self.wait()
        response, content = self.client.request(
            uri='%s/%s' % (self.base_url, url),
            method=method,
            body=urlencode(data),
            headers=headers)  # TODO: Bad response
        return content

    def client_get(self, url, data=None, headers=None):
        if not headers:
            headers = {}
        if not data:
            data = {}
        return self.client_request('GET', url, data, headers)

    def client_post(self, url, data=None, headers=None):
        if not headers:
            headers = {}
        if not data:
            data = {}
        return self.client_request('POST', url, data, headers)

    def client_put(self, url, data=None, headers=None):
        if not headers:
            headers = {}
        if not data:
            data = {}
        return self.client_request('PUT', url, data, headers)

    def client_delete(self, url, data=None, headers=None):
        if not headers:
            headers = {}
        if not data:
            data = {}
        return self.client_request('DELETE', url, data, headers)

    # OAuth

    def oauth_authorize_url(self):
        response, content = self.client.request(
            '%s/oauth/request_token' %
            self.base_url, 'GET')
        if response['status'] != '200':
            raise Exception('Invalid response: %s' % response['status'])
        request_token = dict(urlparse.parse_qsl(content))
        return (
            '%s?oauth_token=%s' % (
                '%s/oauth/authorize' % self.base_url,
                request_token['oauth_token'])
        )

    def oauth_retrieve_token(self):
        token = oauth.Token(
            self.request_token['oauth_token'],
            self.request_token['oauth_token_secret'])
        client = oauth.Client(self.consumer, token)
        response, content = client.request(
            '%s/oauth/access_token' %
            self.base_url, 'POST')
        if response['status'] != '200':
            raise Exception('Invalid response: %s' % response['status'])
        access_token = dict(urlparse.parse_qsl(content))
        self.token = oauth.Token(
            access_token['oauth_token'],
            access_token['oauth_token_secret'])
        self.client = oauth.Client(self.consumer, self.token)
        return self.token
