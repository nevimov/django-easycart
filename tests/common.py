"""Code used by multiple test modules."""
from copy import deepcopy
from importlib import import_module

from django.conf import settings

from easycart import BaseCart, BaseItem
from tests.models import Item, Book, Magazine

SESSION_KEY = 'easycart'

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

DUMMY_SESSION_DATA = {
    'items': {'1': 10, '2': 12, '3': 6, '4': 1},
    'itemCount': 4,
    'totalPrice': '101.00',
}


def set_up_session(session):
    """Augment the given instance of SessionStore with dummy data."""
    session.set_test_cookie()
    session[SESSION_KEY] = deepcopy(DUMMY_SESSION_DATA)
    session.save()
    return session


def fill_db():
    """Fill the test db with dummy items."""
    Book.objects.create(name='Moby-Dick', price=3, author='Melville')
    Book.objects.create(name='The Idiot', price=5, author='Dostoyevsky')
    Magazine.objects.create(name='Cosmos', price=1.5, issue='8 April 2016')
    Magazine.objects.create(name='Discover', price=2, issue='May 2016')


class CartItem(BaseItem):
    MAX_QUANTITY = 999


class Cart(BaseCart):
    ITEM_CLASS = CartItem

    def get_queryset(self, pks):
        return Item.objects.filter(pk__in=pks)

    def process_object(self, obj):
        return getattr(obj, obj.category)

