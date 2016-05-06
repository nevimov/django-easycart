from django.conf.urls import url

from easycart.views import (
    AddItem,
    RemoveItem,
    ChangeItemQuantity,
    EmptyCart,
)

urlpatterns = [
    url(r'^add/$', AddItem.as_view(), name='cart-add'),
    url(r'^remove/$', RemoveItem.as_view(), name='cart-remove'),
    url(r'^change-quantity/$', ChangeItemQuantity.as_view(),
        name='cart-change-quantity'),
    url(r'^empty/$', EmptyCart.as_view(), name='cart-empty'),
]
