from functools import wraps

def oauth_required(f):
    """ Decorator for oauth setup"""
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if 'session' not in kwargs:
            raise GoodreadsError('Operation requires OAuth session; not provided')
        return f(self, *args, **kwargs)

    return wrapper


def developer_required(f):
    """ Decorator for developer key setup"""
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.service.consumer_key:
            raise GoodreadsError('Operation requires developer api keys; not provided')
        else:
            kwargs.update(key=self.service.consumer_key)
            return f(self, *args, **kwargs)

    return wrapper


def extra_permissions_required(f):
    """ Decorator for extra permissions required methods"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        raise GoodreadsNotImplementedError(
            'Operation requires extra permissions; Permission were withheld for development of python-goodreads')

    return wrapper


class LazyProperty(object):
    """
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    """

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    # noinspection PyUnusedLocal
    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


class GoodreadsError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message, *args, **kwargs):
        self.message = message
        self._args = args
        self._kwargs = kwargs

    def __str__(self):
        return repr(self.message)


class InvalidResponse(GoodreadsError):
    pass


class GoodreadsNotImplementedError(GoodreadsError):
    pass
