"""Core classes to represent the user cart and items in it."""
from django.conf import settings
from django.http import JsonResponse

__all__ = [
    'BaseCart',
    'BaseItem',
    'InvalidItemQuantity',
    'ItemNotInCart',
    'ItemNotInDatabase',
    'NegativeItemQuantity',
    'NonConvertibleItemQuantity',
    'TooLargeItemQuantity',
    'ZeroItemQuantity',
]

# Key in request.session under which to store the cart data.
session_key = getattr(settings, 'EASYCART_SESSION_KEY', 'easycart')


class BaseItem(object):
    """Base class representing the cart item.

    Parameters
    ----------
    obj : subclass of django.db.models.Model
        A model instance holding database information about the item.
        The instance is required to have an attribute containing the
        item's price.
    quantity : int, optional
        A quantity to associate with the item.

    Attributes
    ----------
    obj
        A reference to the `obj` argument.
    price : same as `obj.price`
        The price of the item (a reference to the corresponding
        attribute on the `obj`).

    Raises
    ------
    NegativeItemQuantity
    NonConvertibleItemQuantity
    TooLargeItemQuantity
    ZeroItemQuantity

    """
    PRICE_ATTR = 'price'
    """str: The name of the `obj` attribute containing the item's price."""

    max_quantity = None
    """The maximum quantity allowed per item.

    Used by the :meth:`clean_quantity` method. Should be either a
    positive integer or a falsy value. The latter case disables the
    check. Note that you can make it a property to provide dynamic
    values.

    Examples
    --------
    If you want to ensure that the user can't put more items in his
    cart than you have in stock, you may write something like this::

        class CartItem(BaseItem):
            @property
            def max_quantity(self):
                return self.obj.stock

    """

    def __init__(self, obj, quantity=1, **kwargs):
        self._quantity = self.clean_quantity(quantity)
        self.price = getattr(obj, self.PRICE_ATTR)
        self.obj = obj
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._kwargs = kwargs

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        main_args = 'obj={}, quantity={}'.format(self.obj, self.quantity)
        extra_args = ['{}={}'.format(k, getattr(self, k)) for k in self._kwargs]
        args_repr = ', '.join([main_args] + extra_args)
        return  '<CartItem: ' + args_repr + '>'

    @property
    def quantity(self):
        """int: The quantity associated with the item.

        A read/write property.

        New values are checked and normalized to
        integers by the :meth:`clean_quantity` method.

        """
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        self._quantity = self.clean_quantity(value)

    @property
    def total(self):
        """same as obj.price: Total price of the item.

        A read-only property.

        The default implementation simply returns the product of the
        item's price and quantity. Override to adjust for things like
        an individual item discount or taxes.

        """
        return self.quantity * self.price

    def clean_quantity(self, quantity):
        """Check and normalize the quantity.

        The following checks are performed:

            * the quantity can be converted to an integer
            * it's positive
            * it's doesn't exceed the value of :attr:`max_quantity`

        Parameters
        ----------
        quantity : int-convertible

        Returns
        -------
        int
            The normalized quanity.

        Raises
        ------
        NegativeItemQuantity
        NonConvertibleItemQuantity
        TooLargeItemQuantity
        ZeroItemQuantity

        """
        return _clean_quantity(quantity, self.max_quantity)


class BaseCart(object):
    """Base class representing the user cart.

    In the simplest case, you just subclass it in your views and
    override the :meth:`get_queryset` method.

    If multi-table inheritance is used to store information about
    items, then you may also want to override :meth:`process_object`
    as well.

    Parameters
    ----------
    request : django.http.HttpRequest

    Attributes
    ----------
    items : dict
        A map between item primary keys (converted to strings) and
        corresponding instances of :attr:`item_class`.
        If, for some reason, you need to modify `items` directly,
        don't forget to call :meth:`update` afterwards.
    item_count : int
        The total number of items in the cart. By default, only unique
        items are counted.
    total_price : same as the type of item prices
        The total value of all items in the cart.
    request
        A reference to the `request` used to instantiate the cart.

    """
    item_class = BaseItem
    """Class to use to represent cart items."""
    _stale_pks = None

    def __init__(self, request):
        self.request = request
        session_data = request.session.setdefault(session_key, {})
        session_items = session_data.setdefault('items', {})
        self.items = self.create_items(session_items)
        self.item_count = session_data.get('itemCount', 0)
        self.total_price = session_data.get('totalPrice', 0)
        if self._stale_pks:
            self.handle_stale_items(self._stale_pks)

    def add(self, pk, quantity=1, **kwargs):
        """Add an item to the cart.

        If the item is already in the cart, then its quantity will be
        increased by `quantity` units.

        Parameters
        ----------
        pk : str or int
            The primary key of the item.
        quantity : int-convertible
            A number of units of to add.
        **kwargs
            Extra keyword arguments to pass to the item class
            constructor.

        Raises
        ------
        ItemNotInDatabase
        NegativeItemQuantity
        NonConvertibleItemQuantity
        TooLargeItemQuantity
        ZeroItemQuantity

        """
        pk = str(pk)
        if pk in self.items:
            existing_item = self.items[pk]
            existing_item.quantity += _clean_quantity(quantity)
        else:
            queryset = self.get_queryset([pk])
            try:
                obj = queryset[0]
            except IndexError:
                raise ItemNotInDatabase(pk=pk)
            obj = self.process_object(obj)
            self.items[pk] = self.item_class(obj, quantity, **kwargs)
        self.update()

    def change_quantity(self, pk, quantity):
        """Change the quantity of an item.

        Parameters
        ----------
        pk : str or int
            The primary key of the item.
        quantity : int-convertible
            A new quantity.

        Raises
        ------
        ItemNotInCart
        NegativeItemQuantity
        NonConvertibleItemQuantity
        TooLargeItemQuantity
        ZeroItemQuantity

        """
        pk = str(pk)
        try:
            item = self.items[pk]
        except KeyError:
            raise ItemNotInCart(pk=pk)
        item.quantity = quantity
        self.update()

    def remove(self, pk):
        """Remove an item from the cart.

        Parameters
        ----------
        pk : str or int
            The primary key of the item.

        Raises
        ------
        ItemNotInCart

        """
        pk = str(pk)
        try:
            del self.items[pk]
        except KeyError:
            raise ItemNotInCart(pk=pk)
        self.update()

    def empty(self):
        """Remove all items from the cart."""
        self.items.clear()
        self.update()

    def list_items(self, sort_key=None, reverse=False):
        """Return a list of cart items.

        Parameters
        ----------
        sort_key : func
            A function to customize the list order, same as the 'key'
            argument to the built-in :func:`sorted`.
        reverse: bool
            If set to True, the sort order will be reversed.

        Returns
        -------
        list
            List of :attr:`item_class` instances.

        Examples
        --------
        >>> cart = Cart(request)
        >>> cart.list_items(lambda item: item.obj.name)
        [<CartItem: obj=bar, quantity=3>,
         <CartItem: obj=foo, quantity=1>,
         <CartItem: obj=nox, quantity=5>]
        >>> cart.list_items(lambda item: item.quantity, reverse=True)
        [<CartItem: obj=nox, quantity=5>,
         <CartItem: obj=bar, quantity=3>,
         <CartItem: obj=foo, quantity=1>]

        """
        items = list(self.items.values())
        if sort_key:
            items.sort(key=sort_key, reverse=reverse)
        return items

    def encode(self, formatter=None):
        """Return a representation of the cart as a JSON-response.

        Parameters
        ----------
        formatter : func, optional
            A function that accepts the cart representation and returns
            its formatted version.

        Returns
        -------
        django.http.JsonResponse

        Examples
        --------
        Assume that items with primary keys "1" and "4" are already in
        the cart.

        >>> cart = Cart(request)
        >>> def format_total_price(cart_repr):
        ...     return intcomma(cart_repr['totalPrice'])
        ...
        >>> json_response = cart.encode(format_total_price)
        >>> json_response.content
        b'{
            "items": {
                '1': {"price": 100, "quantity": 10, "total": 1000},
                '4': {"price": 50, "quantity": 20, "total": 1000},
            },
            "itemCount": 2,
            "totalPrice": "2,000",
        }'

        """
        items = {}
        # The prices are converted to strings, because they may have a
        # type that can't be serialized to JSON (e.g. Decimal).
        for item in self.items.values():
            pk = str(item.obj.pk)
            items[pk] = {
                'price': str(item.price),
                'quantity': item.quantity,
                'total': item.total,
            }
        cart_repr = {
            'items': items,
            'itemCount': self.item_count,
            'totalPrice': str(self.total_price),
        }
        if formatter:
            cart_repr = formatter(cart_repr)
        return JsonResponse(cart_repr)

    def get_queryset(self, pks):
        """Construct a queryset using given primary keys.

        The cart is pretty much useless until this method is overriden.
        The default implementation just raises ``NotImplementedError``.

        Parameters
        ----------
        pks : list of str

        Returns
        -------
        django.db.models.query.QuerySet

        Examples
        --------
        In the most basic case this method may look like the one
        below::

            def get_queryset(self, pks):
                return Item.objects.filter(pk__in=pks)

        """

        raise NotImplementedError('override the get_queryset() method')

    def process_object(self, obj):
        """Process an object before it will be used to create a cart item.

        This method provides a hook to perform arbitrary actions on
        the item's model instance, before it gets associated with the
        cart item. However, it's usually used just to replace the
        passed model instance with its related object. The default
        implementation simply returns the passed object.

        Parameters
        ----------
        obj : item model
            An item's model instance.

        Returns
        -------
        item model
            A model instance that will be used as the `obj` argument to
            :attr:`item_class`.

        """
        return obj

    def handle_stale_items(self, pks):  #pylint:disable=unused-argument
        """Handle cart items that are no longer present in the database.

        The default implementation results in silent removal of stale
        items from the cart.

        Parameters
        ----------
        pks : set of str
            Primary keys of stale items.

        """
        # Primary keys missing from the database won't be included in
        # the queryset returned by the get_queryset() method, which means
        # that they won't appear in the cart.
        self.update()

    def create_items(self, session_items):
        """Instantiate cart items from session data.

        The value returned by this method is used to populate the
        cart's `items` attribute.

        Parameters
        ----------
        session_items : dict
            A dictionary of pk-quantity mappings (each pk is a string).
            For example: ``{'1': 5, '3': 2}``.

        Returns
        -------
        dict
            A map between the `session_items` keys and instances of
            :attr:`item_class`. For example::

                {'1': <CartItem: obj=foo, quantity=5>,
                 '3': <CartItem: obj=bar, quantity=2>}

        """
        pks = list(session_items.keys())
        items = {}
        item_class = self.item_class
        process_object = self.process_object
        for obj in self.get_queryset(pks):
            pk = str(obj.pk)
            obj = process_object(obj)
            items[pk] = item_class(obj, **session_items[pk])
        if len(items) < len(session_items):
            self._stale_pks = set(session_items).difference(items)
        return items

    def update(self):
        """Update the cart.

        First this method updates attributes dependent on the cart's
        `items`, such as `total_price` or `item_count`.
        After that, it saves the new cart state to the session.

        Generally, you'll need to call this method by yourself, only
        when implementing new methods that directly change the `items`
        attribute.

        """
        self.item_count = self.count_items()
        self.total_price = self.count_total_price()
        # Update the session
        session = self.request.session
        session_items = {}
        for pk, item in self.items.items():
            session_items[pk] = dict(quantity=item.quantity, **item._kwargs)
        session_data = session[session_key]
        session_data['items'] = session_items
        session_data['itemCount'] = self.item_count
        # The price can be of a type that can't be serialized to JSON
        session_data['totalPrice'] = str(self.total_price)
        session.modified = True

    def count_items(self, unique=True):
        """Count items in the cart.

        Parameters
        ----------
        unique : bool-convertible, optional

        Returns
        -------
        int
            If `unique` is truthy, then the result is the number of
            items in the cart. Otherwise, it's the sum of all item
            quantities.

        """
        if unique:
            return len(self.items)
        return sum([item.quantity for item in self.items.values()])

    def count_total_price(self):
        """Get the total price of all items in the cart."""
        return sum((item.total for item in self.items.values()))


def _clean_quantity(quantity, max_quantity=None):
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        raise NonConvertibleItemQuantity(quantity=quantity)
    if quantity == 0:
        raise ZeroItemQuantity()
    if quantity < 0:
        raise NegativeItemQuantity(quantity=quantity)
    if max_quantity and quantity > max_quantity:
        raise TooLargeItemQuantity(quantity=quantity, max_quantity=max_quantity)
    return quantity


class CartException(Exception):
    """Base class for cart exceptions."""
    msg_template = ''

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.msg = self.msg_template.format(**kwargs)

    def __str__(self):
        return self.msg


class InvalidItemQuantity(CartException):
    """Base class for exceptions related to invalid item quantity."""
    msg_template = "item quantity is invalid ({quantity})"


class NonConvertibleItemQuantity(InvalidItemQuantity):
    """Provided item quantity can't be converted to an integer."""
    msg_template = "can't convert quantity to an integer ({quantity})"


class NegativeItemQuantity(InvalidItemQuantity):
    """Provided item quantity is negative."""
    msg_template = 'item quantity is negative ({quantity})'


class ZeroItemQuantity(InvalidItemQuantity):
    """Provided item quantity is zero."""
    msg_template = 'item quantity must not be zero'


class TooLargeItemQuantity(InvalidItemQuantity):
    """Provided item quantity exceeds allowed limit."""
    msg_template = '{quantity} exceeds the allowed maximum of {max_quantity}'


class ItemNotInDatabase(CartException):
    """Database doesn't contain an item with the given primary key."""
    msg_template = "database doesn't have an item with pk {pk}"


class ItemNotInCart(CartException):
    """Item with the given pk is not in the cart."""
    msg_template = "cart doesn't contain an item with pk {pk}"
