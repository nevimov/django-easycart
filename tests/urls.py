from django.views.generic import TemplateView
from django.conf.urls import url

from easycart.urls import urlpatterns


urlpatterns += [
    url(r'^dummy/$', TemplateView.as_view(template_name='dummy.html'),
        name='dummy'),
]
