# menclave/venclave/urls.py

from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',

    url(r'^$',
        'menclave.venclave.views.home',
        name='venclave-home'),

    # Static content -- These exist only for the test server.  In production,
    # they should not be served using Django, but with appropriate server
    # voodoo.

    url(r'^scripts/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': 'venclave/scripts/'},
        name='venclave-scripts'),

    url(r'^styles/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': 'venclave/styles/'},
        name='venclave-styles'),

    url(r'^images/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': 'venclave/images/'},
        name='venclave-images'),

    # Search

   url(r'^browse/$',
        'menclave.venclave.views.browse',
        name='venclave-browse'),

    url(r'^upload/$',
        'menclave.venclave.views.upload',
        name='venclave-upload'),

   url(r'^test/$',
       'menclave.venclave.views.test',
       name='venclave-test')

)
