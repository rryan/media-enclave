# menclave/venclave/urls.py

from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',

    url(r'^$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'index.html'},
        name='venclave-home'),

)