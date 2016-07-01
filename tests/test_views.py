"""Tests for cart.views."""
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from tests.common import fill_db, set_up_session


class TestViews(TestCase):

    def setUp(self):
        fill_db()
        set_up_session(self.client.session)

    def check_response(self, url_name, post_data, expected):
        url = reverse(url_name)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        actual = json.loads(response.content.decode('utf-8'))
        self.assertEqual(actual, expected)

    def test_add_item(self):
        self.check_response(
            'cart-add',
            {'pk': 1, 'quantity': 5},
            {'items': {'1': {'price': '3.00', 'quantity': 15, 'total': '45.00'},
                       '2': {'price': '5.00', 'quantity': 12, 'total': '60.00'},
                       '3': {'price': '1.50', 'quantity': 6, 'total': '9.00'},
                       '4': {'price': '2.00', 'quantity': 1, 'total': '2.00'}},
             'itemCount': 4,
             'totalPrice': '116.00'}
        )

    def test_add_item_without_quantity(self):
        """If post data don't contain parameter 'quantity', then one unit of a
        requested item should be added (the quantity defaults to 1).
        """
        self.check_response(
            'cart-add',
            {'pk': 1},
            {'items': {'1': {'price': '3.00', 'quantity': 11, 'total': '33.00'},
                       '2': {'price': '5.00', 'quantity': 12, 'total': '60.00'},
                       '3': {'price': '1.50', 'quantity': 6, 'total': '9.00'},
                       '4': {'price': '2.00', 'quantity': 1, 'total': '2.00'}},
             'itemCount': 4,
             'totalPrice': '104.00'}
        )

    def test_add_item_without_pk(self):
        """If post data don't contain parameter 'pk', no exception should be
        raised and the response is expected to contain the relevant error
        message.
        """
        self.check_response(
            'cart-add',
            {},
            {'error': 'MissingRequestParam', 'param': 'pk'}
        )

    def test_add_item_with_negative_quantity(self):
        """If post data contain parameter 'quantity' and the associated value
        is negative, then the corresponding exception is expected to be handled
        by the view, and the response should contain the relevant error message.
        """
        self.check_response(
            'cart-add',
            {'pk': 1, 'quantity': -1},
            {'error': 'NegativeItemQuantity', 'quantity': -1}
        )

    def test_add_item_with_zero_quantity(self):
        """If post data contain parameter 'quantity' and the associated value
        is zero, then the corresponding exception is expected to be handled by
        the view, and the response should contain the relevant error message.
        """
        self.check_response(
            'cart-add',
            {'pk': 1, 'quantity': 0},
            {'error': 'ZeroItemQuantity'}
        )

    def test_add_item_with_non_convertible_quantity(self):
        """If post data contain parameter 'quantity' and the associated value
        can't be converted to an integer, then the corresponding exception is
        expected to be handled by the view, and the response should contain the
        relevant error message.
        """
        self.check_response(
            'cart-add',
            {'pk': 1, 'quantity': 'xxx'},
            {'error': 'NonConvertibleItemQuantity', 'quantity': 'xxx'}
        )

    def test_remove_item(self):
        self.check_response(
            'cart-remove',
            {'pk': 1},
            {'items': {'2': {'price': '5.00', 'quantity': 12, 'total': '60.00'},
                       '3': {'price': '1.50', 'quantity': 6, 'total': '9.00'},
                       '4': {'price': '2.00', 'quantity': 1, 'total': '2.00'}},
             'itemCount': 3,
             'totalPrice': '71.00'}
        )

    def test_remove_item_without_pk(self):
        """If post data don't contain parameter 'pk', then the corresponding
        exception is expected to be handled by the view, and the response
        should contain the relevant error message.
        """
        self.check_response(
            'cart-remove',
            {},
            {'error': 'MissingRequestParam', 'param': 'pk'}
        )

    def test_change_item_quantity(self):
        self.check_response(
            'cart-change-quantity',
            {'pk': 1, 'quantity': 5},
            {'items': {'1': {'price': '3.00', 'quantity': 5, 'total': '15.00'},
                       '2': {'price': '5.00', 'quantity': 12, 'total': '60.00'},
                       '3': {'price': '1.50', 'quantity': 6, 'total': '9.00'},
                       '4': {'price': '2.00', 'quantity': 1, 'total': '2.00'}},
             'itemCount': 4,
             'totalPrice': '86.00'}
        )

    def test_change_item_without_pk(self):
        """If post data don't contain parameter 'pk', no exception should be
        raised and the response is expected to contain the relevant error
        message.
        """
        self.check_response(
            'cart-change-quantity',
            {},
            {'error': 'MissingRequestParam', 'param': 'pk'}
        )

    def test_change_item_with_negative_quantity(self):
        """If post data contain parameter 'quantity' and the associated value
        is negative, then the corresponding exception is expected to be handled
        by the view, and the response should contain the relevant error message.
        """
        self.check_response(
            'cart-change-quantity',
            {'pk': 1, 'quantity': -1},
            {'error': 'NegativeItemQuantity', 'quantity': -1}
        )

    def test_change_item_with_zero_quantity(self):
        """If post data contain parameter 'quantity' and the associated value
        is zero, then the corresponding exception is expected to be handled by
        the view, and the response should contain the relevant error message.
        """
        self.check_response(
            'cart-change-quantity',
            {'pk': 1, 'quantity': 0},
            {'error': 'ZeroItemQuantity'}
        )

    def test_change_item_with_non_convertible_quantity(self):
        """If post data contain parameter 'quantity' and the associated value
        can't be converted to an integer, then the corresponding exception is
        expected to be handled by the view, and the response should contain the
        relevant error message.
        """
        self.check_response(
            'cart-change-quantity',
            {'pk': 1, 'quantity': 'xxx'},
            {'error': 'NonConvertibleItemQuantity', 'quantity': 'xxx'}
        )


    def test_empty_cart(self):
        self.check_response(
            'cart-empty',
            {},
            {'items': {}, 'itemCount': 0, 'totalPrice': '0'}
        )
