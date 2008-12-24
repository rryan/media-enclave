# menclave/venclave/urls.py

from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',

    url(r'^$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'index.html'},
        name='venclave-home'),

    url(r'^$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'index.html'},
        name='venclave-search'),


    # Static content

    url(r'scripts/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': 'media/venclave/scripts/'},
        name='venclave-scripts'),

    url(r'^styles/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': 'media/venclave/styles/'},
        name='venclave-styles'),

    url(r'^images/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': 'media/venclave/images/'},
        name='venclave-images'),


)
