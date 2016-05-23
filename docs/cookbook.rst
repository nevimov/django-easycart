Cookbook
========

.. _cookbook-multiple-item-models:

Adapting to multiple item models
--------------------------------

If you use `multi-table inheritance`_ in your item models, then you will likely
want that cart items were associated with instances of their respective child
models. This can be achieved by overriding the
:meth:`~cart.BaseCart.process_object` method  of the :class:`~cart.BaseCart`
class.

Let's assume we have the following models::

    # catalog/models.py
    from django.db import models

    class Item(models.Model):
        name = models.CharField(max_length=40)
        price = models.PositiveIntegerField()

    class Book(Item):
        author = models.CharField(max_length=40)

    class Magazine(Item):
        issue = models.CharField(max_length=40)


Instances of ``Item`` can access their respective child model through
attributes *book* and *magazine*. The problem is, we don't know in advance
which one to use. The easiest way to circumvent it is to use a try‑except block
to access each attribute one by one::

    from django.core.exceptions import ObjectDoesNotExist
    from easycart import BaseCart

    CATEGORIES = ('book', 'magazine')


    class Cart(BaseCart):

        def get_queryset(self, pks):
            return Item.objects.filter(pk__in=pks).select_related(*CATEGORIES)

        def process_object(self, obj):
            for category in CATEGORIES:
                try:
                    return getattr(obj, category)
                except ObjectDoesNotExist:
                    pass

Alternatively, just store the name of the right attribute in a separate field
on ``Item``::

    class Item(models.Model):
        name = models.CharField(max_length=40)
        price = models.PositiveIntegerField()
        category = models.CharField(max_length=50, editable=False)

        def save(self, *args, **kwargs):
            if not self.category:
                self.category = self.__class__.__name__.lower()
            super().save(*args, **kwargs)

In this case, your cart class may look something like this::

    class Cart(BaseCart):

        def get_queryset(self, pks):
            return Item.objects.filter(pk__in=pks).select_related(*CATEGORIES)

        def process_object(self, obj):
            return getattr(obj, obj.category)

.. attention::

   Whatever technique you choose, be sure to use `select_related()`_ to avoid
   redundant queries to the database.


.. _select_related(): https://docs.djangoproject.com/en/dev/ref/models/querysets/#select-related


Associating arbitrary data with cart items
------------------------------------------

You can associate arbitrary data with items by passing extra keyword arguments
to the cart's method :meth:`~cart.BaseCart.add`.

As an example, we will save the date and time the item is added to the cart.
Having a timestamp may be handy in quite a few scenarios. For example, many
e-commerce sites have a widget displaying a list of items recently added to the
cart.

To implement such functionality, create a cart class similar to the one below::

    import time
    from easycart import BaseCart

    class Cart(BaseCart):

        def add(self, pk, quantity=1):
            super(Cart, self).add(pk, quantity, timestamp=time.time())

        def list_items_by_timestamp(self):
            return self.list_items(sort_key=lambda item: item.timestamp, reverse=True)

Now, in your templates, do something like:

.. code-block:: htmldjango

    {% for item in cart.list_items_by_timestamp|slice:":6" %}
        {{ item.name }}
        {{ item.price }}
    {% endfor %}


Adding per item discounts and taxes
-----------------------------------

To change the way the individual item prices are calculated, you need to
override the :meth:`~cart.BaseItem.total` method of the :class:`~cart.BaseItem`
class.

Assume we have the following models.py::

    from django.db import models

    class Item(models.Model):
        price = models.DecimalField(decimal_places=2, max_digits=8)
        # Suppose discounts and taxes are stored as percentages
        discount = models.IntegerField(default=0)
        tax = models.IntegerField(default=0)

In this case, your item class may look like this::

    class CartItem(BaseItem):

        @property
        def total(self):
            discount_mod = 1 - self.obj.discount/100
            tax_mod = 1 + self.obj.tax/100
            return self.price * discount_mod * tax_mod


    class Cart(BaseCart):
        # Point the cart to the new item class
        item_class = CartItem


Limiting the maximum quantity allowed per item
----------------------------------------------

You may want to limit the maximum quantity allowed per item, for example, to
ensure that the user can't put more items in his cart than you have in stock.

See the :attr:`~cart.BaseItem.max_quantity` attribute of the
:class:`~cart.BaseCart` class.
