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
import local_settings


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
        assertEqual(response['@id'], local_settings.AUTH_USER['id'])

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()