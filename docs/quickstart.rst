Quickstart
==========

This document demonstrates how you can use Easycart to implement the shopping
cart functionality in your django project.


Install the app
---------------

Before you do anything else, ensure that Django Session Framework is
`enabled and configured`_.

Use pip_ to install Easycart::

    $ pip install django-easycart

Add the app to your INSTALLED_APPS setting::

    INSTALLED_APPS = [
        ...
        'easycart',
    ]


.. _enabled and configured: https://docs.djangoproject.com/en/dev/topics/http/sessions/
.. _pip: https://pip.pypa.io/en/stable/


.. _quickstart-define-cart-class:

Define your cart class
----------------------

First, create a new django application::

    $ python manage.py startapp cart

It will contain things not provided by Easycart, such as templates and static
files. Those are unique to each project, so it's your responsibility to provide
them.

Next, we need to create a customized cart class. Don't worry, it's really easy,
just subclass :class:`~cart.BaseCart` and override its
:meth:`~cart.BaseCart.get_queryset()` method::

    # cart/views.py
    from easycart import BaseCart

    # We assume here that you've already defined your item model
    # in a separate app named "catalog".
    from catalog.models import Item


    class Cart(BaseCart):

        def get_queryset(self, pks):
            return Item.objects.filter(pk__in=pks)

Now, our class knows how to communicate with the item model.

.. note::

   For simplicity's sake, the example above supposes that a single model is
   used to access all database information about items. If you use `multi-table
   inheritance`_, see :ref:`this link <cookbook-multiple-item-models>`.

There are many more customizations you can make to the cart class, check out
:doc:`cookbook` and :doc:`reference`, after you complete this tutorial.


.. _multi-table inheritance: https://docs.djangoproject.com/en/dev/topics/db/models/#multi-table-inheritance


Plug in ready-to-use views
--------------------------

Every cart needs to perform tasks like adding/removing items, changing the
quantity associated with an item or emptying the whole cart at once. You can
write your own views for that purpose, using the cart class we've created
above, but what's the point in reinventing the wheel? Just use :doc:`the ones
<easycart.views>` shipped with Easycart.

Add the following to your project settings::

    EASYCART_CART_CLASS = 'cart.views.Cart'

Create ``cart/urls.py``::

    from django.conf.urls import url

    urlpatterns = [
        # This pattern must always be the last
        url('', include('easycart.urls'))
    ]

Include it in the root URLconf::

    url(r'^cart/', include('cart.urls')),

Now, the cart can be operated by sending POST-requests to Easycart urls:

    +----------------------+---------------------------------------------+
    | URL name             | View                                        |
    +======================+=============================================+
    | cart-add             | :class:`~views.AddItem`                     |
    +----------------------+---------------------------------------------+
    | cart-remove          | :class:`~views.RemoveItem`                  |
    +----------------------+---------------------------------------------+
    | cart-change-quantity | :class:`~views.ChangeItemQuantity`          |
    +----------------------+---------------------------------------------+
    | cart-empty           | :class:`~views.EmptyCart`                   |
    +----------------------+---------------------------------------------+

.. tip::

    It would be wise to create a javascript API to handle these requests.
    Here's an oversimplified example of such an API that can serve as a
    starting point. It uses `a bit of jQuery`_ and assumes that
    CSRF-protection_ has already been `taken care of`_.

    .. code-block:: javascript


       var cart = {
           add: function (pk, quantity) {
             quantity = quantity || 1
             return $.post(URLS.addItem, {pk: pk, quantity: quantity}, 'json')
           }

           remove: function (itemPK) {
             return $.post(URLS.removeItem, {pk: itemPK}, 'json')
           }

           changeQuantity: function (pk, quantity) {
             return $.post(URLS.changeQuantity, {pk: pk, quantity: quantity}, 'json')
           }

           empty: function () {
             $.post(URLS.emptyCart, 'json')
           }
       }

    Inline a script similar to the one below in your base template, so you
    don't have to hardcode the urls.

     .. code-block:: htmldjango

         <script>
         var URLS = {
           addItem:        '{% url "cart-add" %}',
           removeItem:     '{% url "cart-remove" %}',
           changeQuantity: '{% url "cart-change-quantity" %}',
           emptyCart:      '{% url "cart-empty" %}',
         }
         </script>


.. _a bit of jQuery: https://api.jquery.com/jquery.post/
.. _CSRF-protection: https://docs.djangoproject.com/en/dev/ref/csrf/
.. _taken care of: https://docs.djangoproject.com/en/dev/ref/csrf/#ajax


.. _quickstart-access-from-templates:

Access the cart from templates
------------------------------

To enable the built-in cart `context processor`_, add
``context_processors.cart`` to your project settings::

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    # other context processors
                    'easycart.context_processors.cart',
                ],
            },
        },
    ]

Now, the cart can be accessed in any template through context variable
``cart`` like this:

.. code-block:: htmldjango

    {{ cart.item_count }}
    {{ cart.total_price }}

    {% for item in cart.list_items %}
    <div>
        {# Access the item's model instance using its "obj" attribute #}
        {{ item.obj.name }}
        <img src="{{ item.obj.picture.url }}">
        {{ item.price }}
        {{ item.quantity }}
        {{ item.total }}
    </div>
    {% endfor %}

The name of the variable can be changed using the :ref:`EASYCART_CART_VAR
<settings-cart-var>` setting.

----

Well, that's all. Of course, you still need to write some front-end scripts and
create additional views (for instance, for order processing), but all of this
is far beyond the scope of this document.

.. _context processor: https://docs.djangoproject.com/en/dev/ref/templates/api/#writing-your-own-context-processors
