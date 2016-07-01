"""A set of views every cart needs.

On success, each view returns a JSON-response with the cart
representation. For the details on the format of the return value,
see the :meth:`~easycart.cart.BaseCart.encode` method of the
:class:`~easycart.cart.BaseCart` class.

If a parameter required by a view is not present in the request's POST
data, then the JSON-response will have the format::

   {'error': 'MissingRequestParam', 'param': parameter_name}

Almost the same thing happens, if a parameter is invalid and results in
an exception, which is a subclass of :class:`~easycart.cart.CartException`.
In this case, the error value will be the name of the concrete exception
class (e.g. ``'ItemNotInCart'`` or ``'NegativeItemQuantity'``).
And instead of ``param`` there may be one or more items providing
additional info on the error, for example, the primary key of an item
you was trying to change or an invalid quantity passed in the request.


Note
----
All of the views in this module accept only POST requests.

"""
from importlib import import_module

from django.conf import settings
from django.http import JsonResponse
from django.views.generic import View

from easycart.cart import CartException

__all__ = [
    'AddItem',
    'RemoveItem',
    'ChangeItemQuantity',
    'EmptyCart',
]

cart_module, cart_class = settings.EASYCART_CART_CLASS.rsplit('.', 1)
Cart = getattr(import_module(cart_module), cart_class)


class CartView(View):
    """Base class for views operating the cart."""
    action = None
    """Attribute of the cart object, which will be called to perform
    some action on the cart.
    """
    required_params = ()
    """Iterable of parameters, which MUST be present in the post data."""
    optional_params = {}
    """Dictionary of parameters, which MAY be present in the post data.

    Parameters serve as keys. Associated values will be used as fallbacks
    in case the parameter is not in the post data.
    """

    def post(self, request):
        # Extract parameters from the post data
        params = {}
        for param in self.required_params:
            try:
                params[param] = request.POST[param]
            except KeyError:
                return JsonResponse({
                    'error': 'MissingRequestParam',
                    'param': param,
                })
        for param, fallback in self.optional_params.items():
            params[param] = request.POST.get(param, fallback)
        # Perform an action on the cart using these parameters
        cart = Cart(request)
        action = getattr(cart, self.action)
        try:
            action(**params)
        except CartException as exc:
            return JsonResponse(dict({'error': exc.__class__.__name__},
                                     **exc.kwargs))
        return cart.encode()


class AddItem(CartView):
    """Add an item to the cart.

    This view expects `request.POST` to contain:

    +------------+----------------------------------------------------+
    | key        | value                                              |
    +============+====================================================+
    | `pk`       | the primary key of an item to add                  |
    +------------+----------------------------------------------------+
    | `quantity` | a quantity that should be associated with the item |
    +------------+----------------------------------------------------+

    The `quantity` parameter is optional (defaults to 1).

    """
    action = 'add'
    required_params = ('pk',)
    optional_params = {'quantity': 1}


class ChangeItemQuantity(CartView):
    """Change the quantity associated with an item.

    This view expects `request.POST` to contain:

    +------------+----------------------------------------------------+
    | key        | value                                              |
    +============+====================================================+
    | `pk`       | the primary key of an item                         |
    +------------+----------------------------------------------------+
    | `quantity` | a new quantity to associate with the item          |
    +------------+----------------------------------------------------+

    """
    action = 'change_quantity'
    required_params = ('pk', 'quantity')


class RemoveItem(CartView):
    """Remove an item from the cart.

    Expects `request.POST` to contain key *pk*. The associated value
    should be the primary key of an item you wish to remove.

    """
    action = 'remove'
    required_params = ('pk',)


class EmptyCart(CartView):
    """Remove all items from the cart."""
    action = 'empty'
