import collections
import json
from builtins import str

from rauth import OAuth1Service
import requests
import xmltodict
import six

from .util import oauth_required, developer_required, extra_permissions_required, InvalidResponse


class GoodreadsApi(object):
    "A simple wrapper for the Goodreads.com Web API."""

    __instance = None

    def __new__(cls, *args, **kwargs):
        """Implements a 'singleton' pattern so the GoodreadsObjects can access the API via Goodreads"""
        if GoodreadsApi.__instance is None:
            GoodreadsApi.__instance = object.__new__(cls)
        return GoodreadsApi.__instance

    def __init__(self, consumer_key=None, consumer_secret=None):
        """ Initialize the API with goodreads.com keys

        See <https://www.goodreads.com/api/keys> to register your app and to get your keys

        :param consumer_key:  The goodreads.com developer 'key'
        :type consumer_key: str
        :param consumer_secret: The goodreads.com developer 'secret'
        :type consumer_secret: str
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

        Example::

            >> pprint.pprint(api.auth_user())
            {'@id': '551681',
             'name': 'Johnny Appleseed',
             'link': 'https://www.goodreads.com/user/show/551681-johnny?utm_medium=api'}

        .. seealso:: https://www.goodreads.com/api/index#auth.user
        """
        return self._api_call(self._get, 'api/auth_user', container='user', **kwargs)

    @developer_required
    def author_books(self, pk, page=1, **kwargs):
        """Get a response with a paginated list of an authors books.

        Example::

            >> pprint.pprint(api.author_books(pk=18541))
            {'id': '18541',
             'name': "Tim O'Reilly",
             'link': 'https://www.goodreads.com/author/show/18541.Tim_O_Reilly',
             'books': {'@start': '1',
                       '@end': '30',
                       '@total': '47',
                       'book': [{'id': {'@type': 'integer',
                                        '#text': '104744'},
                                 'isbn': '1565927249',
                                 'isbn13': '9781565927247',
                                 'text_reviews_count': {'@type': 'integer',
                                                        '#text': '5'},
                                 'title': 'The Cathedral & the Bazaar: Musings on '
                                          'Linux and Open Source by an Accidental '
                                          'Revolutionary',
                                 'image_url': 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png',
                                 'small_image_url': 'https://s.gr-assets.com/assets/nophoto/book/50x75-a91bf249278a81aabab721ef782c4a74.png',
                                 'large_image_url': None,
                                 'link': 'https://www.goodreads.com/book/show/104744.The_Cathedral_the_Bazaar',
                                 'num_pages': '279',
                                 'format': 'Hardcover',
                                 'edition_information': None,
                                 'publisher': "O'Reilly Media",
                                 'publication_day': '8',
                                 'publication_year': '1999',
                                 'publication_month': '10',
                                 'average_rating': '3.88',
                                 'ratings_count': '1782',
                                 'description': '"This is how we did it." --Linus '
                                                'Torvalds, creator of the Linux '
                                                ...
                                                'book. Its conclusions will be '
                                                'studied, debated, and implemented '
                                                'for years to come.',
                                 'authors': {'author': {'id': '18542',
                                                        'name': 'Eric S. Raymond',
                                                        'role': None,
                                                        'image_url': 'https://d.gr-assets.com/authors/1265508525p5/18542.jpg',
                                                        'small_image_url': 'https://d.gr-assets.com/authors/1265508525p2/18542.jpg',
                                                        'link': 'https://www.goodreads.com/author/show/18542.Eric_S_Raymond',
                                                        'average_rating': '3.91',
                                                        'ratings_count': '2717',
                                                        'text_reviews_count': '144'}},
                                 'published': '1999'},
                                 ...
                                {'id': {'@type': 'integer',
                                        '#text': '13214293'},
                                 'isbn': '0596003331',
                                 'isbn13': '9780596003333',
                                 'text_reviews_count': {'@type': 'integer',
                                                        '#text': '0'},
                                 'title': 'The .Net CD Bookshelf',
                                 'image_url': 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png',
                                 'small_image_url': 'https://s.gr-assets.com/assets/nophoto/book/50x75-a91bf249278a81aabab721ef782c4a74.png',
                                 'large_image_url': None,
                                 'link': 'https://www.goodreads.com/book/show/13214293-the-net-cd-bookshelf',
                                 'num_pages': '336',
                                 'format': 'Paperback',
                                 'edition_information': None,
                                 'publisher': "O'Reilly Media",
                                 'publication_day': None,
                                 'publication_year': None,
                                 'publication_month': None,
                                 'average_rating': '0.0',
                                 'ratings_count': '0',
                                 'description': 'Packed with seven key Microsoft .NET '
                                                'books, this CD-ROM delivers '
                                                'thousands ofpages of accessible and '
                                                'searchable information.',
                                 'authors': {'author': {'id': '18541',
                                                        'name': "Tim O'Reilly",
                                                        'role': None,
                                                        'image_url': 'https://d.gr-assets.com/authors/1199698411p5/18541.jpg',
                                                        'small_image_url': 'https://d.gr-assets.com/authors/1199698411p2/18541.jpg',
                                                        'link': 'https://www.goodreads.com/author/show/18541.Tim_O_Reilly',
                                                        'average_rating': '3.92',
                                                        'ratings_count': '1052',
                                                        'text_reviews_count': '111'}},
                                 'published': None}]}}


        .. seealso:: https://www.goodreads.com/api/index#author.books
        """
        return self._api_call(self._get, 'author/list.xml', container='author', id=pk, page=page, **kwargs)

    @developer_required
    def author_show(self, pk, **kwargs):
        """Get a response with info about an author.

        Example::

            >> pprint.pprint(api.author_show(pk=18541))
            {'id': '18541',
             'name': "Tim O'Reilly",
             'link': 'https://www.goodreads.com/author/show/18541.Tim_O_Reilly',
             'fans_count': OrderedDict([('@type', 'integer'), ('#text', '248')]),
             'image_url': 'https://d.gr-assets.com/authors/1199698411p5/18541.jpg',
             'small_image_url': 'https://d.gr-assets.com/authors/1199698411p2/18541.jpg',
             'about': None,
             'influences': None,
             'works_count': '47',
             'gender': 'male',
             'hometown': 'Cork',
             'born_at': None,
             'died_at': None,
             'user': {'id': OrderedDict([('@type', 'integer'), ('#text', '549570')])},
             'books': {'book': [{'id': {'@type': 'integer',
                                        '#text': '6356381'},
                                 'isbn': '0596802811',
                                 'isbn13': '9780596802813',
                                 'text_reviews_count': {'@type': 'integer',
                                                        '#text': '51'},
                                 'title': 'The Twitter Book',
                                 'image_url': 'https://d.gr-assets.com/books/1328834986m/6356381.jpg',
                                 'small_image_url': 'https://d.gr-assets.com/books/1328834986s/6356381.jpg',
                                 'large_image_url': None,
                                 'link': 'https://www.goodreads.com/book/show/6356381-the-twitter-book',
                                 'num_pages': '240',
                                 'format': 'Paperback',
                                 'edition_information': None,
                                 'publisher': "O'Reilly Media",
                                 'publication_day': '20',
                                 'publication_year': '2009',
                                 'publication_month': '5',
                                 'average_rating': '3.63',
                                 'ratings_count': '270',
                                 'description': '"Media organizations should take '
                                                "note of Twitter's power to quickly "
                                                ...
                                                'Twitter; she was the 21st user of '
                                                'Twitter.',
                                 'authors': {'author': {'id': '18541',
                                                        'name': "Tim O'Reilly",
                                                        'role': None,
                                                        'image_url': 'https://d.gr-assets.com/authors/1199698411p5/18541.jpg',
                                                        'small_image_url': 'https://d.gr-assets.com/authors/1199698411p2/18541.jpg',
                                                        'link': 'https://www.goodreads.com/author/show/18541.Tim_O_Reilly',
                                                        'average_rating': '3.92',
                                                        'ratings_count': '1052',
                                                        'text_reviews_count': '111'}},
                                 'published': '2009'},
                                 ...
                                {'id': {'@type': 'integer',
                                        '#text': '19282395'},
                                 'isbn': OrderedDict([('@nil', 'true')]),
                                 'isbn13': OrderedDict([('@nil', 'true')]),
                                 'text_reviews_count': {'@type': 'integer',
                                                        '#text': '0'},
                                 'title': 'Web Squared: Web 2.0 Five Years On',
                                 'image_url': 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png',
                                 'small_image_url': 'https://s.gr-assets.com/assets/nophoto/book/50x75-a91bf249278a81aabab721ef782c4a74.png',
                                 'large_image_url': None,
                                 'link': 'https://www.goodreads.com/book/show/19282395-web-squared',
                                 'num_pages': None,
                                 'format': None,
                                 'edition_information': None,
                                 'publisher': None,
                                 'publication_day': None,
                                 'publication_year': None,
                                 'publication_month': None,
                                 'average_rating': '4.00',
                                 'ratings_count': '2',
                                 'description': '<p>Ever since we first introduced '
                                                'the term Web 2.0, people have been '
                                                ...
                                                'of exploring this phenomenon and '
                                                'giving it a name.</p>',
                                 'authors': {'author': {'id': '18541',
                                                        'name': "Tim O'Reilly",
                                                        'role': None,
                                                        'image_url': 'https://d.gr-assets.com/authors/1199698411p5/18541.jpg',
                                                        'small_image_url': 'https://d.gr-assets.com/authors/1199698411p2/18541.jpg',
                                                        'link': 'https://www.goodreads.com/author/show/18541.Tim_O_Reilly',
                                                        'average_rating': '3.92',
                                                        'ratings_count': '1052',
                                                        'text_reviews_count': '111'}},
                                 'published': None}]}}


        .. seealso:: https://www.goodreads.com/api/index#author.show
        """
        return self._api_call(self._get, 'author/show.xml', container='author', id=pk, **kwargs)

    @developer_required
    def book_isbn_to_id(self, isbn, **kwargs):
        """Get the Goodreads book ID given an ISBN

        Example::

            >> pprint.pprint(api.book_isbn_to_id(pk='9780596001087'))
            '134825'

        .. seealso:: https://www.goodreads.com/api/index#book.isbn_to_id
        """
        return self._api_call(self._get, 'book/isbn_to_id', raw=True, isbn=isbn, **kwargs)

    @developer_required
    def book_review_counts(self, isbns, **kwargs):
        """Get review statistics given a list of ISBNs

        :param isbns: List of isbns
        :type isbns: iterable
        :return: List of dicts
        :rtype: list

        Example::

            >> pprint.pprint(api.book_review_counts(isbns=['9780954161781', '9781441412706',
                '9780954161767']))
            [{'average_rating': '4.00',
              'id': 475671,
              'isbn': '0954161785',
              'isbn13': '9780954161781',
              'ratings_count': 2,
              'reviews_count': 8,
              'text_reviews_count': 0,
              'work_ratings_count': 4,
              'work_reviews_count': 11,
              'work_text_reviews_count': 0},
              ...
             {'average_rating': '3.60',
              'id': 475667,
              'isbn': '0954161769',
              'isbn13': '9780954161767',
              'ratings_count': 5,
              'reviews_count': 19,
              'text_reviews_count': 0,
              'work_ratings_count': 5,
              'work_reviews_count': 22,
              'work_text_reviews_count': 0}]

        .. seealso:: https://www.goodreads.com/api/index#book.review_counts
        """
        json_string = self._api_call(self._get, 'book/review_counts.json', raw=True,
                                     isbns=','.join([str(i) for i in isbns]), **kwargs)
        return json.loads(json_string)['books']


    @developer_required
    def book_show(self, pk, **kwargs):
        """
        Get the reviews for a book given a Goodreads book id

        :param pk:
        :return:

        Example::

            >> pprint.pprint(api.book_show(pk=134825))
            {'id': '134825',
             'title': 'The Cathedral & the Bazaar: Musings on Linux and Open Source by '
                      'an Accidental Revolutionary',
             'isbn': '0596001088',
             'isbn13': '9780596001087',
             'asin': None,
             'image_url': 'https://d.gr-assets.com/books/1328835964m/134825.jpg',
             'small_image_url': 'https://d.gr-assets.com/books/1328835964s/134825.jpg',
             'publication_year': '2001',
             'publication_month': '2',
             'publication_day': '8',
             'publisher': "O'Reilly Media",
             'language_code': None,
             'is_ebook': 'false',
             'description': 'Open source provides the competitive advantage in the '
                            ...
                            'become the open source story in 2001.',
             'work': {'best_book_id': {'@type': 'integer',
                                       '#text': '134825'},
                      'books_count': OrderedDict([('@type', 'integer'), ('#text', '13')]),
                      'default_chaptering_book_id': {'@type': 'integer',
                                                     '@nil': 'true'},
                      'default_description_language_code': {'@nil': 'true'},
                      'desc_user_id': {'@type': 'integer',
                                       '#text': '-9'},
                      'id': OrderedDict([('@type', 'integer'), ('#text', '100993')]),
                      'media_type': 'book',
                      'original_language_id': {'@type': 'integer',
                                               '@nil': 'true'},
                      'original_publication_day': {'@type': 'integer',
                                                   '@nil': 'true'},
                      'original_publication_month': {'@type': 'integer',
                                                     '@nil': 'true'},
                      'original_publication_year': {'@type': 'integer',
                                                    '#text': '1999'},
                      'original_title': 'Cathedral and the Bazaar: Musings on Linux and '
                                        'Open Source by an Accidental Revolutionary',
                      'rating_dist': '5:477|4:736|3:456|2:97|1:16|total:1782',
                      'ratings_count': {'@type': 'integer',
                                        '#text': '1782'},
                      'ratings_sum': {'@type': 'integer',
                                      '#text': '6907'},
                      'reviews_count': {'@type': 'integer',
                                        '#text': '3627'},
                      'text_reviews_count': {'@type': 'integer',
                                             '#text': '93'}},
             'average_rating': '3.88',
             'num_pages': '258',
             'format': 'Paperback',
             'edition_information': None,
             'ratings_count': '1638',
             'text_reviews_count': '83',
             'url': 'https://www.goodreads.com/book/show/134825.The_Cathedral_the_Bazaar',
             'link': 'https://www.goodreads.com/book/show/134825.The_Cathedral_the_Bazaar',
             'authors': {'author': [{'id': '18542',
                                     'name': 'Eric S. Raymond',
                                     'role': None,
                                     'image_url': 'https://d.gr-assets.com/authors/1265508525p5/18542.jpg',
                                     'small_image_url': 'https://d.gr-assets.com/authors/1265508525p2/18542.jpg',
                                     'link': 'https://www.goodreads.com/author/show/18542.Eric_S_Raymond',
                                     'average_rating': '3.91',
                                     'ratings_count': '2717',
                                     'text_reviews_count': '144'},
                                    {'id': '303269',
                                     'name': 'Bob Young',
                                     'role': 'Foreword by',
                                     'image_url': 'https://s.gr-assets.com/assets/nophoto/user/u_200x266-e183445fd1a1b5cc7075bb1cf7043306.png',
                                     'small_image_url': 'https://s.gr-assets.com/assets/nophoto/user/u_50x66-632230dc9882b4352d753eedf9396530.png',
                                     'link': 'https://www.goodreads.com/author/show/303269.Bob_Young',
                                     'average_rating': '3.88',
                                     'ratings_count': '1688',
                                     'text_reviews_count': '90'}]},
             'reviews_widget': '<style>'
             ...
                               '</div>',
             'popular_shelves': {'shelf': [{'@name': 'to-read',
                                            '@count': '1357'},
                                           ...
                                           {'@name': 'open-source',
                                            '@count': '20'}]},
             'book_links': {'book_link': {'id': '8',
                                          'name': 'Libraries',
                                          'link': 'https://www.goodreads.com/book_link/follow/8'}},
             'series_works': None,
             'public_document': {'id': '5161',
                                 'document_url': 'http://feedbooks.com/book/4285.epub'},
             'similar_books': {'book': [{'id': '658332',
                                         'title': 'Free as in Freedom: Richard '
                                                  "Stallman's Crusade for Free "
                                                  'Software',
                                         'isbn': '0596002874',
                                         'isbn13': '9780596002879',
                                         'small_image_url': 'https://d.gr-assets.com/books/1344675393s/658332.jpg',
                                         'image_url': 'https://d.gr-assets.com/books/1344675393m/658332.jpg',
                                         'average_rating': '3.81',
                                         'ratings_count': '470',
                                         'authors': {'author': {'id': '36802',
                                                                'name': 'Sam '
                                                                        'Williams'}}},
                                        ...
                                        {'id': '41786',
                                         'title': 'Joel on Software',
                                         'isbn': '1590593898',
                                         'isbn13': '9781590593899',
                                         'small_image_url': 'https://d.gr-assets.com/books/1419283213s/41786.jpg',
                                         'image_url': 'https://d.gr-assets.com/books/1419283213m/41786.jpg',
                                         'average_rating': '4.09',
                                         'ratings_count': '1698',
                                         'authors': {'author': {'id': '23546',
                                                                'name': 'Joel '
                                                                        'Spolsky'}}}]}}

        .. seealso:: https://www.goodreads.com/api/index#book.show
        """
        return self._api_call(self._get, 'book/show.xml', container='book', id=pk, **kwargs)


    @developer_required
    def book_show_by_isbn(self, isbn, **kwargs):
        """Get the reviews for a book given an ISBN

        Example::

            >> pprint.pprint(api.book_show_by_isbn(isbn='0441172717'))
            {'id': '53732',
             'title': 'Dune (Dune Chronicles, #1)',
             'isbn': '0441172717',
             'isbn13': '9780441172719',
             'asin': None,
             'image_url': 'https://d.gr-assets.com/books/1419919087m/53732.jpg',
             'small_image_url': 'https://d.gr-assets.com/books/1419919087s/53732.jpg',
             'publication_year': '1990',
             'publication_month': '9',
             'publication_day': '1',
             'publisher': 'Ace/Berkley Books',
             'language_code': 'eng',
             'is_ebook': 'false',
             'description': 'Here is the novel that will be forever considered a triumph '
                            'of the imagination. Set on the desert planet Arrakis, '
                            ...
                            'in science fiction.',
             'work': {'best_book_id': {'@type': 'integer',
                                       '#text': '234225'},
                      'books_count': {'@type': 'integer',
                                      '#text': '204'},
                      'default_chaptering_book_id': {'@type': 'integer',
                                                     '@nil': 'true'},
                      'default_description_language_code': {'@nil': 'true'},
                      'desc_user_id': {'@type': 'integer',
                                       '#text': '7798697'},
                      'id': OrderedDict([('@type', 'integer'), ('#text', '3634639')]),
                      'media_type': 'book',
                      'original_language_id': {'@type': 'integer',
                                               '@nil': 'true'},
                      'original_publication_day': {'@type': 'integer',
                                                   '@nil': 'true'},
                      'original_publication_month': {'@type': 'integer',
                                                     '@nil': 'true'},
                      'original_publication_year': {'@type': 'integer',
                                                    '#text': '1965'},
                      'original_title': 'Dune',
                      'rating_dist': '5:181583|4:113528|3:58386|2:18687|1:11702|total:383886',
                      'ratings_count': {'@type': 'integer',
                                        '#text': '383886'},
                      'ratings_sum': {'@type': 'integer',
                                      '#text': '1586261'},
                      'reviews_count': {'@type': 'integer',
                                        '#text': '543562'},
                      'text_reviews_count': {'@type': 'integer',
                                             '#text': '8890'}},
             'average_rating': '4.13',
             'num_pages': '535',
             'format': 'Paperback',
             'edition_information': 'Special 25th Anniversary Edition',
             'ratings_count': '7213',
             'text_reviews_count': '662',
             'url': 'https://www.goodreads.com/book/show/53732.Dune',
             'link': 'https://www.goodreads.com/book/show/53732.Dune',
             'authors': {'author': {'id': '58',
                                    'name': 'Frank Herbert',
                                    'role': None,
                                    'image_url': 'https://d.gr-assets.com/authors/1168661521p5/58.jpg',
                                    'small_image_url': 'https://d.gr-assets.com/authors/1168661521p2/58.jpg',
                                    'link': 'https://www.goodreads.com/author/show/58.Frank_Herbert',
                                    'average_rating': '4.02',
                                    'ratings_count': '686640',
                                    'text_reviews_count': '14504'}},
             'reviews_widget': '<style>'
             ...
                               '</div>',
             'popular_shelves': {'shelf': [{'@name': 'to-read',
                                            '@count': '135248'},
                                          ...
                                           {'@name': 'sci-fi-fantasy',
                                            '@count': '858'}]},
             'book_links': {'book_link': {'id': '8',
                                          'name': 'Libraries',
                                          'link': 'https://www.goodreads.com/book_link/follow/8'}},
             'series_works': {'series_work': [{'id': '166801',
                                               'user_position': '1',
                                               'series': {'id': '45935',
                                                          'title': 'Dune Chronicles',
                                                          'description': 'Also known '
                                                                         ...
                                                                         'href="http://www.goodreads.com/series/49402-heroes-of-dune">Heroes '
                                                                         'of Dune</a>',
                                                          'note': None,
                                                          'series_works_count': '23',
                                                          'primary_work_count': '6',
                                                          'numbered': 'true'}},
                                              {'id': '563755',
                                               'user_position': '1',
                                               'series': {'id': '116548',
                                                          'title': 'Kopa',
                                                          'description': None,
                                                          'note': None,
                                                          'series_works_count': '2',
                                                          'primary_work_count': '2',
                                                          'numbered': 'true'}},
                                              {'id': '514666',
                                               'user_position': '10',
                                               'series': {'id': '106170',
                                                          'title': 'Dune Universe',
                                                          'description': None,
                                                          'note': None,
                                                          'series_works_count': '24',
                                                          'primary_work_count': '21',
                                                          'numbered': 'true'}}]},
             'similar_books': {'book': [{'id': '761575',
                                         'title': 'House Atreides (Prelude to Dune, '
                                                  '#1)',
                                         'isbn': '0553580272',
                                         'isbn13': '9780553580273',
                                         'small_image_url': 'https://d.gr-assets.com/books/1403181106s/761575.jpg',
                                         'image_url': 'https://d.gr-assets.com/books/1403181106m/761575.jpg',
                                         'average_rating': '3.59',
                                         'ratings_count': '12605',
                                         'authors': {'author': {'id': '56',
                                                                'name': 'Brian '
                                                                        'Herbert'}}},
                                        ...
                                        {'id': '546454',
                                         'title': 'The Voyage of the Space Beagle',
                                         'isbn': '0532601467',
                                         'isbn13': '9780532601463',
                                         'small_image_url': 'https://s.gr-assets.com/assets/nophoto/book/50x75-a91bf249278a81aabab721ef782c4a74.png',
                                         'image_url': 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png',
                                         'average_rating': '3.84',
                                         'ratings_count': '1763',
                                         'authors': {'author': {'id': '1293688',
                                                                'name': 'A.E. van '
                                                                        'Vogt'}}}]}}

        .. seealso:: https://www.goodreads.com/api/index#book.show_by_isbn
        """
        return self._api_call(self._get, 'book/isbn', container='book', isbn=isbn, **kwargs)

    @developer_required
    def book_title(self, title, author=None, **kwargs):
        """Get the reviews for a book given a title string

        Example::

            >> pprint.pprint(api.book_title(title='The Order of the Phoenix'))
            {'id': '2',
             'title': 'Harry Potter and the Order of the Phoenix (Harry Potter, #5)',
             'isbn': '0439358078',
             'isbn13': '9780439358071',
             'asin': None,
             'image_url': 'https://d.gr-assets.com/books/1387141547m/2.jpg',
             'small_image_url': 'https://d.gr-assets.com/books/1387141547s/2.jpg',
             'publication_year': '2004',
             'publication_month': '8',
             'publication_day': '10',
             'publisher': 'Scholastic',
             'language_code': 'eng',
             'is_ebook': 'false',
             'description': 'Harry Potter is due to start his fifth year at Hogwarts '
                            ...
                            'adventure that is impossible to put down.',
             'work': {'best_book_id': OrderedDict([('@type', 'integer'), ('#text', '2')]),
                      'books_count': {'@type': 'integer',
                                      '#text': '206'},
                      'default_chaptering_book_id': {'@type': 'integer',
                                                     '#text': '2'},
                      'default_description_language_code': {'@nil': 'true'},
                      'desc_user_id': {'@type': 'integer',
                                       '#text': '1019021'},
                      'id': OrderedDict([('@type', 'integer'), ('#text', '2809203')]),
                      'media_type': 'book',
                      'original_language_id': {'@type': 'integer',
                                               '@nil': 'true'},
                      'original_publication_day': {'@type': 'integer',
                                                   '#text': '21'},
                      'original_publication_month': {'@type': 'integer',
                                                     '#text': '6'},
                      'original_publication_year': {'@type': 'integer',
                                                    '#text': '2003'},
                      'original_title': 'Harry Potter and the Order of the Phoenix',
                      'rating_dist': '5:794277|4:384992|3:148377|2:26779|1:7911|total:1362336',
                      'ratings_count': {'@type': 'integer',
                                        '#text': '1362336'},
                      'ratings_sum': {'@type': 'integer',
                                      '#text': '6017953'},
                      'reviews_count': {'@type': 'integer',
                                        '#text': '1595582'},
                      'text_reviews_count': {'@type': 'integer',
                                             '#text': '17644'}},
             'average_rating': '4.42',
             'num_pages': '870',
             'format': 'Paperback',
             'edition_information': None,
             'ratings_count': '1306494',
             'text_reviews_count': '15214',
             'url': 'https://www.goodreads.com/book/show/2.Harry_Potter_and_the_Order_of_the_Phoenix',
             'link': 'https://www.goodreads.com/book/show/2.Harry_Potter_and_the_Order_of_the_Phoenix',
             'authors': {'author': [{'id': '1077326',
                                     'name': 'J.K. Rowling',
                                     'role': None,
                                     'image_url': 'https://d.gr-assets.com/authors/1415945171p5/1077326.jpg',
                                     'small_image_url': 'https://d.gr-assets.com/authors/1415945171p2/1077326.jpg',
                                     'link': 'https://www.goodreads.com/author/show/1077326.J_K_Rowling',
                                     'average_rating': '4.40',
                                     'ratings_count': '12090247',
                                     'text_reviews_count': '246245'},
                                    {'id': '2927',
                                     'name': 'Mary GrandPré',
                                     'role': 'Illustrator',
                                     'image_url': 'https://d.gr-assets.com/authors/1395344820p5/2927.jpg',
                                     'small_image_url': 'https://d.gr-assets.com/authors/1395344820p2/2927.jpg',
                                     'link': 'https://www.goodreads.com/author/show/2927.Mary_GrandPr_',
                                     'average_rating': '4.44',
                                     'ratings_count': '10740359',
                                     'text_reviews_count': '159511'}]},
             'reviews_widget': '<style>'
                               ...
                               '</div>',
             'popular_shelves': {'shelf': [{'@name': 'to-read',
                                            '@count': '75005'},
                                            ...
                                           {'@name': 'childrens',
                                            '@count': '1899'}]},
             'book_links': {'book_link': {'id': '8',
                                          'name': 'Libraries',
                                          'link': 'https://www.goodreads.com/book_link/follow/8'}},
             'series_works': {'series_work': {'id': '163765',
                                              'user_position': '5',
                                              'series': {'id': '45175',
                                                         'title': 'Harry Potter',
                                                         'description': 'All seven '
                                                                        'books and '
                                                                        ...
                                                                        'Boxsets too!',
                                                         'note': 'Boxsets ARE part of '
                                                                 'the series. '
                                                                 'However, the '
                                                                 ...
                                                                 'database.',
                                                         'series_works_count': '15',
                                                         'primary_work_count': '7',
                                                         'numbered': 'true'}}},
             'similar_books': {'book': [{'id': '227865',
                                         'title': 'The Eternity Code (Artemis Fowl, '
                                                  '#3)',
                                         'isbn': '0141321318',
                                         'isbn13': '9780141321318',
                                         'small_image_url': 'https://d.gr-assets.com/books/1327945417s/227865.jpg',
                                         'image_url': 'https://d.gr-assets.com/books/1327945417m/227865.jpg',
                                         'average_rating': '4.04',
                                         'ratings_count': '66863',
                                         'authors': {'author': {'id': '10896',
                                                                'name': 'Eoin Colfer'}}},
                                        ...
                                        {'id': '213105',
                                         'title': 'Dreams Made Flesh (The Black '
                                                  'Jewels, #5)',
                                         'isbn': '0451460707',
                                         'isbn13': '9780451460707',
                                         'small_image_url': 'https://d.gr-assets.com/books/1327838630s/213105.jpg',
                                         'image_url': 'https://d.gr-assets.com/books/1327838630m/213105.jpg',
                                         'average_rating': '4.29',
                                         'ratings_count': '9866',
                                         'authors': {'author': {'id': '26897',
                                                                'name': 'Anne Bishop'}}}]}}

        .. seealso:: https://www.goodreads.com/api/index#book.title
        """
        try:
            return self._api_call(self._get, 'book/title.xml', container='book', title=title, author=author, **kwargs)
        except requests.exceptions.HTTPError as ex:
            if ex.response.status_code == 404 and ex.response.text.startswith('<error>book not found</error>'):
                return None
            else:
                raise


    @oauth_required
    def comment_create(self, type_, pk, comment_body, **kwargs):
        """Create a comment

        Example::

            >> pprint.pprint(api.comment_create(type='recommendation_request', pk=129593,comment[body]="This is a sample comment"))
            {'id': '516515165151',
             'body': 'This is a sample comment',
             'user': {'id': '56151651',
                      'name': 'Johnny',
                      'location': None,
                      'link': 'https://www.goodreads.com/user/show/56151651-johnny',
                      'image_url': 'https://s.gr-assets.com/assets/nophoto/user/u_.png',
                      'small_image_url': 'https://s.gr-assets.com/assets/nophoto/user/u_.png'},
             'created_at': 'Thu Feb 19 21:31:11 +0000 2015',
             'updated_at': 'Thu Feb 19 21:31:11 +0000 2015'}

        .. seealso:: https://www.goodreads.com/api/index#comment.create
        """
        kwargs.update({
            'type': type_,
            'id': pk,
            'comment[body]': comment_body,
        })
        return self._api_call(self._post, 'comment.xml', container='comment' **kwargs)

    @developer_required
    def comment_list(self, **kwargs):
        """List comments on a subject

        Example::

            >> pprint.pprint(api.comment_create(pk=))

        https://www.goodreads.com/api/index#comment.list
        """

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
        """
        Utility method for GET-ting from the Goodreads API

        :param path: Url to GET to
        :param session: An OAuth session (optional)
        :param kwargs: Data to GET (optional)
        :return: Content of response
        :raises: HTTPError
        """
        if not session:
            session = requests
        url = self.service.base_url + path
        response = session.get(url, data=kwargs)
        response.raise_for_status()
        return response.text

    def _post(self, path, session=None, **kwargs):
        """
        Utility method for POST-ing to the Goodreads API

        :param path: Url to POST to
        :param session: An Oauth session (optional)
        :param kwargs: Data to POST (optional)
        :return: Content of response
        :raises: HTTPError
        """
        if not session:
            session = self.service
        url = self.service.base_url + path
        response = session.post(url, data=kwargs)
        response.raise_for_status()
        return response.text

    @staticmethod
    def _prepare_call(**kwargs):
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
        # elif raw:
        # result = str(result).split('\n')[0]
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
            oauth_callback (str, optional):The URL which you wish Goodreads to redirect the user to when the user finishes authorizing your application. Defaults to None.
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