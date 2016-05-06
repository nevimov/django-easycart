"""Tests for cart.context_processors."""
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from tests.common import Cart, fill_db, set_up_session


@override_settings(
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'easycart.context_processors.cart',
            ],
        },
    }],
)
class TestContextProcessors(TestCase):

    def setUp(self):
        fill_db()
        set_up_session(self.client.session)

    def test_context_has_cart_variable(self):
        url = reverse('dummy')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cart', response.context)
        cart = response.context['cart']
        self.assertTrue(isinstance(cart, Cart))
        # Ensure the cart instance has been correctly initialized
        self.assertEqual(len(cart.items), 4)
