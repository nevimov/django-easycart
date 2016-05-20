"""A set of views every cart needs.

On success, each view returns a JSON-response with the cart
representation. For the details on the format of the return value,
see the :meth:`~easycart.cart.BaseCart.encode` method of the
:class:`~easycart.cart.BaseCart` class.

Note
----
All of the views in this module accept only POST requests.

"""
from importlib import import_module

from django.conf import settings
from django.views.generic import View

__all__ = [
    'AddItem',
    'RemoveItem',
    'ChangeItemQuantity',
    'EmptyCart',
]

cart_module, cart_class = settings.EASYCART_CART_CLASS.rsplit('.', 1)
Cart = getattr(import_module(cart_module), cart_class)


class AddItem(View):
    """Add an item to the cart.

    This view expects `request.POST` to contain:

    +------------+----------------------------------------------------+
    | key        | value                                              |
    +============+====================================================+
    | `pk`       | the primary key of an item to add                  |
    +------+-----+----------------------------------------------------+
    | `quantity` | a quantity that should be associated with the item |
    +------------+----------------------------------------------------+

    """

    def post(self, request):
        cart = Cart(request)
        pk = request.POST['pk']
        quantity = request.POST['quantity']
        cart.add(pk, quantity)
        return cart.encode()


class ChangeItemQuantity(View):
    """Change the quantity of an item.

    This view expects `request.POST` to contain:

    +------------+----------------------------------------------------+
    | key        | value                                              |
    +============+====================================================+
    | `pk`       | the primary key of an item                         |
    +------+-----+----------------------------------------------------+
    | `quantity` | a new quantity to associate with the item          |
    +------------+----------------------------------------------------+

    """

    def post(self, request):
        cart = Cart(request)
        pk = request.POST['pk']
        quantity = request.POST['quantity']
        cart.change_quantity(pk, quantity)
        return cart.encode()


class RemoveItem(View):
    """Remove an item from the cart.

    Expects `request.POST` to contain key *pk*. The associated value
    should be the primary key of an item you wish to remove.

    """

    def post(self, request):
        cart = Cart(request)
        pk = request.POST['pk']
        cart.remove(pk)
        return cart.encode()


class EmptyCart(View):
    """Remove all items from the cart."""

    def post(self, request):
        cart = Cart(request)
        cart.empty()
        return cart.encode()
