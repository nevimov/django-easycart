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
            {'pk': '1', 'quantity': '5'},
            {'items': {'1': {'price': '3.00', 'quantity': 15, 'total': '45.00'},
                       '2': {'price': '5.00', 'quantity': 12, 'total': '60.00'},
                       '3': {'price': '1.50', 'quantity': 6, 'total': '9.00'},
                       '4': {'price': '2.00', 'quantity': 1, 'total': '2.00'}},
             'itemCount': 4,
             'totalPrice': '116.00'}
        )

    def test_remove_item(self):
        self.check_response(
            'cart-remove',
            {'pk': '1'},
            {'items': {'2': {'price': '5.00', 'quantity': 12, 'total': '60.00'},
                       '3': {'price': '1.50', 'quantity': 6, 'total': '9.00'},
                       '4': {'price': '2.00', 'quantity': 1, 'total': '2.00'}},
             'itemCount': 3,
             'totalPrice': '71.00'}
        )

    def test_change_item_quantity(self):
        self.check_response(
            'cart-change-quantity',
            {'pk': '1', 'quantity': '5'},
            {'items': {'1': {'price': '3.00', 'quantity': 5, 'total': '15.00'},
                       '2': {'price': '5.00', 'quantity': 12, 'total': '60.00'},
                       '3': {'price': '1.50', 'quantity': 6, 'total': '9.00'},
                       '4': {'price': '2.00', 'quantity': 1, 'total': '2.00'}},
             'itemCount': 4,
             'totalPrice': '86.00'}
        )

    def test_empty_cart(self):
        self.check_response(
            'cart-empty',
            {},
            {'items': {}, 'itemCount': 0, 'totalPrice': '0'}
        )
