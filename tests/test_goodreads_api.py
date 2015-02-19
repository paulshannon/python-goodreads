import unittest

from rauth import OAuth1Session
import requests

from goodreads.api import GoodreadsApi
from tests import local_settings


class TestGoodreadsApi(unittest.TestCase):
    def setUp(self):
        self.api = GoodreadsApi(local_settings.DEVELOPER_KEY, local_settings.DEVELOPER_SECRET)
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
        response = self.api.author_books(pk=18541)
        self.assertEqual(response['id'], '18541')
        self.assertEqual(response['name'], "Tim O'Reilly")
        self.assertEqual(len(response['books']['book']), 30)

    def test_author_show(self):
        # 18541, Tim O'Reilly
        response = self.api.author_show(pk=18541)
        self.assertEqual(response['id'], '18541')
        self.assertEqual(response['name'], "Tim O'Reilly")

    def test_books_isbn_to_id(self):
        response = self.api.book_isbn_to_id(isbn=9780596001087)
        self.assertEqual(response, '134825')

    def test_book_review_counts(self):
        response = self.api.book_review_counts(isbns=['9780954161781', '9781441412706', '9780954161767'])
        self.assertEqual(len(response), 3)
        self.assertGreaterEqual(response[0]['reviews_count'], 8)
        self.assertGreaterEqual(response[0]['work_reviews_count'], 11)

    def test_book_show(self):
        response = self.api.book_show(pk=134825)
        self.assertEqual(response['title'],
                         "The Cathedral & the Bazaar: Musings on Linux and Open Source by an Accidental Revolutionary")

    def test_book_title(self):
        response = self.api.book_title(title='The Order of the Phoenix')
        self.assertEqual(response['title'], "Harry Potter and the Order of the Phoenix (Harry Potter, #5)")

        response = self.api.book_title(title='The Order of the Phoenix', author='Tom Clancy')
        self.assertEqual(response, None)

    def test_comment_create(self):
        response = self.api.comment_create(**{
            'session': self.session,
            'type_': 'recommendation_request',
            'pk': 129593,
            'comment_body': "This is a sample comment",
        })
        self.assertEqual(response['body'], "This is a sample comment")

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()