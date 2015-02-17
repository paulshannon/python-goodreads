#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_goodreads
----------------------------------

Tests for `goodreads` module.
"""

import unittest

from goodreads.api import GoodreadsAPI


class TestGoodreadsApi(unittest.TestCase):
    def setUp(self):
        self.api = GoodreadsAPI(DEVELOPER_KEY, DEVELOPER_SECRET)

    def test_auth_user(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()