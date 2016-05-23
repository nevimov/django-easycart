Settings
========

Most of the Easycart behavior is customized by overriding and extending the
:class:`~cart.BaseCart` and :class:`~cart.BaseItem` classes, however, a few
things are controlled through the settings below:


.. _settings-cart-class:

.. option:: EASYCART_CART_CLASS

   A string pointing to :ref:`your cart class <quickstart-define-cart-class>`.

   Has no default value, must always be set, if you want to use
   :doc:`built-in views <easycart.views>`.


.. _settings-cart-var:

.. option:: EASYCART_CART_VAR

   **default**: 'cart'

   The name for the context variable providing
   :ref:`access to the cart from templates <quickstart-access-from-templates>`.


.. _settings-session-key:

.. option:: EASYCART_SESSION_KEY

   **default**: 'easycart'

   Key in ``request.session`` under which to store the cart data.
