#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_goodreads
----------------------------------

Tests for `goodreads` module.
"""

import unittest

from rauth import OAuth1Session

from goodreads.api import GoodreadsAPI
from tests import local_settings


class TestGoodreadsApi(unittest.TestCase):
    def setUp(self):
        self.api = GoodreadsAPI(local_settings.DEVELOPER_KEY, local_settings.DEVELOPER_SECRET)
        self.session = OAuth1Session(
            consumer_key=local_settings.DEVELOPER_KEY,
            consumer_secret=local_settings.DEVELOPER_SECRET,
            access_token=local_settings.AUTH_USER['access_token'],
            access_token_secret=local_settings.AUTH_USER['access_token_secret']
        )

    def test_auth_user(self):
        response = self.api.auth_user(session=self.session)
        self.assertEqual(response['@id'], local_settings.AUTH_USER['id'])

    def test_author_books(self):
        # 18541, Tim O'Reilly
        response = self.api.author_books(id=18541)
        self.assertEqual(response['id'], '18541')
        self.assertEqual(response['name'], "Tim O'Reilly")
        self.assertEqual(len(response['books']['book']), 30)

    def test_author_show(self):
        # 18541, Tim O'Reilly
        response = self.api.author_show(id=18541)
        self.assertEqual(response['id'], '18541')
        self.assertEqual(response['name'], "Tim O'Reilly")

    def test_books_isbn_to_id(self):
        response = self.api.book_isbn_to_id(isbn=9780596001087)
        self.assertEqual(response['id'], '134825')

    def test_book_review_counts(self):
        response = self.api.book_review_counts()

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()