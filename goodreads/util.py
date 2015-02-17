def oauth_required(f):
    """ Decorator for oauth setup"""

    def wrapper(self):
        if not self.oauth:
            raise GoodreadsError('Operation requires OAuth; not provided')
        else:
            f(self)

    return wrapper


def developer_required(f):
    """ Decorator for developer key setup"""

    def wrapper(self):
        if not self.developer:
            raise GoodreadsError('Operation requires developer api keys; not provided')
        else:
            f(self)

    return wrapper


def extra_permissions_required(f):
    """ Decorator for extra permissions required methods"""

    def wrapper(self):
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
