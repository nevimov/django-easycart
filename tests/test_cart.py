"""Tests for easycart.cart."""
import json
from copy import deepcopy
from unittest.mock import Mock, patch

from django.test import TestCase, RequestFactory

from easycart import (
    BaseItem,
    InvalidItemQuantity,
    ItemNotInCart,
    ItemNotInDatabase,
)
from tests.common import (
    DUMMY_SESSION_DATA,
    SESSION_KEY,
    Cart,
    SessionStore,
    fill_db,
    set_up_session,
)
from tests.models import Item, Book, Magazine

request_factory = RequestFactory()


class TestBaseItem(TestCase):

    def setUp(self):
        self.obj = Item(pk=1, name='dummy_item', price=100)

    def test_instance_attrs_are_ok(self):
        item = BaseItem(self.obj, 3)
        self.assertIs(item.obj, self.obj)
        self.assertEqual(item.price, 100)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.total, 300)

    def test_constructor_cleans_quantity(self):
        with patch.object(BaseItem, 'clean_quantity') as mock_clean_quantity:
            mock_clean_quantity.return_value = 'cleaned'
            item = BaseItem(self.obj, 'raw')
        mock_clean_quantity.assert_called_once_with('raw')
        self.assertEqual(item.quantity, 'cleaned')

    def test_quantity_can_be_changed_to_valid_value(self):
        item = BaseItem(self.obj, quantity=1)

        def test(new_quantity):
            item.quantity = new_quantity
            self.assertEqual(item.quantity, int(new_quantity))

        test(10)
        test('19')
        test(123.45)

    def test_quantity_cannot_be_changed_to_invalid_value(self):
        item = BaseItem(self.obj, quantity=3)

        def test(new_quantity):
            with self.assertRaises(InvalidItemQuantity):
                item.quantity = new_quantity
            self.assertEqual(item.quantity, 3)

        test('text-that-cant-be-converted-to-int')
        test(0)
        test(-1)
        item.max_quantity = 999
        test(1000)

    def test_total_changes_with_quantity(self):
        item = BaseItem(self.obj, quantity=1)
        self.assertEqual(item.total, 100)
        item.quantity = 10
        self.assertEqual(item.total, 1000)

    def test__eq__(self):
        item_1 = BaseItem(self.obj)
        item_2 = BaseItem(self.obj)
        item_3 = BaseItem(self.obj, 2)
        self.assertEqual(item_1, item_1)
        self.assertEqual(item_1, item_2)
        self.assertNotEqual(item_1, item_3)

    def test__repr__(self):
        item = BaseItem(self.obj, 1)
        self.assertEqual(repr(item), '<CartItem: obj=dummy_item, quantity=1>')


class TestBaseCart(TestCase):

    def setUp(self):
        fill_db()
        request = request_factory.post('')
        request.session = SessionStore()
        set_up_session(request.session)
        cart = Cart(request)
        mock_update = Mock(wraps=cart.update)
        patch.object(cart, 'update', mock_update).start()
        self.addCleanup(patch.stopall)
        self.mock_update = mock_update
        self.request = request
        self.cart = cart
        self.cart_session = request.session[SESSION_KEY]

    def assert_cart_is_empty(self, cart):
        self.assertEqual(cart.items, {})
        self.assertEqual(cart.item_count, 0)
        self.assertEqual(cart.total_price, 0)

    def assert_session_reflects_cart_state(self):
        cart = self.cart
        cart_session = self.cart_session
        self.assertEqual(cart_session['itemCount'], cart.item_count)
        self.assertEqual(cart_session['totalPrice'], str(cart.total_price))
        expected_items = {}
        for item in cart.items.values():
            pk = str(item.obj.pk)
            expected_items[pk] = item.quantity
        self.assertEqual(cart_session['items'], expected_items)

    def test_initial_cart_state_with_empty_session(self):
        del self.request.session[SESSION_KEY]
        cart = Cart(self.request)
        self.assert_cart_is_empty(cart)

    def test_initial_cart_state_with_dummy_session(self):
        cart = self.cart
        self.assertEqual(cart.item_count, 4)
        self.assertEqual(cart.total_price, '101.00')
        self.assertEqual(
            cart.items,
            {
                '1': BaseItem(Book.objects.get(pk=1), 10),
                '2': BaseItem(Book.objects.get(pk=2), 12),
                '3': BaseItem(Magazine.objects.get(pk=3), 6),
                '4': BaseItem(Magazine.objects.get(pk=4), 1),
            }
        )

    def test_update_does_not_corrupt_session(self):
        self.cart.update()
        self.assertEqual(self.cart_session, DUMMY_SESSION_DATA)

    def test_update_after_direct_modification_of_items(self):
        cart = self.cart
        del cart.items['1']
        cart.update()
        self.assertEqual(cart.item_count, 3)
        self.assertEqual(cart.total_price, 71)
        self.assert_session_reflects_cart_state()

    def test_add_item_that_is_not_in_cart(self):
        cart = self.cart
        new_item = Book.objects.create(name='foo', price=999)
        new_item_pk = str(new_item.pk)
        self.assertNotIn(new_item_pk, cart.items)
        cart.add(pk=new_item_pk, quantity=1)
        self.mock_update.assert_called_once_with()
        self.assertEqual(cart.items[new_item_pk], BaseItem(new_item, 1))
        self.assertEqual(cart.item_count, 5)
        self.assertEqual(cart.total_price, 1100)
        self.assert_session_reflects_cart_state()

    def test_add_item_that_is_already_in_cart(self):
        cart = self.cart
        self.assertIn('1', cart.items)
        self.assertEqual(cart.items['1'].quantity, 10)
        cart.add(pk='1', quantity=5)
        self.mock_update.assert_called_once_with()
        self.assertEqual(cart.items['1'].quantity, 15)
        self.assertEqual(cart.item_count, 4)
        self.assertEqual(cart.total_price, 116)
        self.assert_session_reflects_cart_state()

    def test_add_item_in_invalid_quantity(self):
        cart = self.cart
        max_allowed_quantity = BaseItem.max_quantity = 9999
        orig_items = deepcopy(cart.items)

        def test(pk, quantity):
            with self.assertRaises(InvalidItemQuantity):
                cart.add(pk=pk, quantity=quantity)
            self.assertEqual(cart.items, orig_items)
            self.assert_session_reflects_cart_state()

        # With an item that is already in the cart
        test('1', 0)
        test('1', -1)
        test('1', max_allowed_quantity)
        # With an item that is not in the cart
        new_item = Book.objects.create(name='foo', price=999)
        new_item_pk = str(new_item.pk)
        test(new_item_pk, 0)
        test(new_item_pk, -1)
        test(new_item_pk, max_allowed_quantity+1)

    def test_change_item_quantity_to_valid_value(self):
        cart = self.cart
        cart.change_quantity('1', 20)
        self.assertEqual(cart.items['1'].quantity, 20)
        self.assertEqual(cart.items['1'].total, 60)
        self.mock_update.assert_called_once_with()

    def test_change_item_quantity_to_invalid_value(self):
        cart = self.cart
        orig_items = deepcopy(cart.items)
        max_allowed_quantity = BaseItem.max_quantity = 9999

        def test(quantity):
            with self.assertRaises(InvalidItemQuantity):
                cart.change_quantity('1', quantity)
            self.mock_update.assert_not_called()
            self.assertEqual(cart.items, orig_items)
            self.assert_session_reflects_cart_state()

        test(0)
        test(-1)
        test(max_allowed_quantity+1)

    def test_change_item_quantity_of_item_missing_from_cart(self):
        with self.assertRaises(ItemNotInCart):
            self.cart.change_quantity('no-such-item-in-cart', 10)
        self.mock_update.assert_not_called()

    def test_remove_item_present_in_cart(self):
        cart = self.cart
        self.assertIn('1', cart.items)
        cart.remove('1')
        self.assertNotIn('1', cart.items)
        self.assertEqual(cart.item_count, 3)
        self.assertEqual(cart.total_price, 71)
        self.assert_session_reflects_cart_state()

    def test_remove_item_missing_from_cart(self):
        cart = self.cart
        orig_items = deepcopy(cart.items)
        with self.assertRaises(ItemNotInCart):
            self.cart.remove('999')
        self.mock_update.assert_not_called()
        self.assertEqual(cart.items, orig_items)

    def test_empty_cart(self):
        cart = self.cart
        cart.empty()
        self.mock_update.assert_called_once_with()
        self.assert_cart_is_empty(cart)
        self.assert_session_reflects_cart_state()

    def test_encode_cart(self):

        def get_response(formatter=None):
            response = self.cart.encode(formatter)
            return json.loads(response.content.decode('utf-8'))

        expected_response = {
            'items': {
                '1': {'price': '3.00', 'quantity': 10, 'total': '30.00'},
                '2': {'price': '5.00', 'quantity': 12, 'total': '60.00'},
                '3': {'price': '1.50', 'quantity': 6, 'total': '9.00'},
                '4': {'price': '2.00', 'quantity': 1, 'total': '2.00'},
            },
            'itemCount': 4,
            'totalPrice': '101.00',
        }
        self.assertEqual(get_response(), expected_response)

        # Test with format callback

        def format_total_price(cart_repr):
            raw_price = cart_repr['totalPrice']
            fmt_price = str(raw_price) + ' $'
            cart_repr['totalPrice'] = fmt_price
            return cart_repr

        expected_response['totalPrice'] = '101.00 $'
        self.assertEqual(get_response(format_total_price), expected_response)

    def test_stale_item_handler_is_not_called_if_cart_has_no_stale_items(self):
        with patch.object(Cart, 'handle_stale_items') as mock_handler:
            cart = Cart(self.request)  #pylint:disable=unused-variable
        mock_handler.assert_not_called()

    def test_stale_item_handler_is_called_if_cart_has_stale_items(self):
        Book.objects.get(pk=1).delete()
        with patch.object(Cart, 'handle_stale_items') as mock_handler:
            cart = Cart(self.request)  #pylint:disable=unused-variable
        mock_handler.assert_called_once_with({'1'})

    def test_stale_items_are_silently_removed(self):
        Book.objects.get(pk=1).delete()
        Book.objects.get(pk=2).delete()
        cart = Cart(self.request)
        self.assertEqual(cart.item_count, 2)
        self.assertEqual(cart.total_price, 11)

    def test_list_items(self):
        self.assertEqual(
            sorted(self.cart.list_items(), key=lambda item: item.quantity),
            [
                BaseItem(Magazine.objects.get(pk=4), 1),
                BaseItem(Magazine.objects.get(pk=3), 6),
                BaseItem(Book.objects.get(pk=1), 10),
                BaseItem(Book.objects.get(pk=2), 12),
            ]
        )

    def test_list_items_sorting(self):

        def sort_key(dummy):
            pass

        class mock_list(list):
            sort = Mock()

        list_items = self.cart.list_items
        with patch('easycart.cart.list', mock_list):
            list_items()  # By default the list shouldn't be sorted
            mock_list.sort.assert_not_called()
            list_items(sort_key=sort_key, reverse=True)
            mock_list.sort.assert_called_once_with(key=sort_key, reverse=True)

    def test_method_add_raises_if_item_not_in_database(self):
        self.assertEqual(Item.objects.filter(pk='999').count(), 0)
        with self.assertRaises(ItemNotInDatabase):
            self.cart.add(pk='999')

    def test_items_are_counted_correctly(self):
        self.assertEqual(self.cart.count_items(unique=True), 4)
        self.assertEqual(self.cart.count_items(unique=False), 29)

