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

    url(r'^search/$',
        'menclave.venclave.views.simple_search',
        name='venclave-search'),

    # Genre -- just ids for now, support names when we know more about
    # how genres will work
    
    url(r'^genre/(?P<ids>[0-9,]+)$',
        'menclave.venclave.views.genres_view',
        name='venclave-genre'),

    # Content -- slugs in the future -- ids for now
    
    url(r'^content/(?P<id>\d+)$',
        'menclave.venclave.views.content_view',
        name='venclave-content'),

    # People -- is it too generic? maybe just directors? 

    url(r'^director/(?P<id>\d+)$',
        'menclave.venclave.views.director_view',
        name='venclave-director'),

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

    url(r'^data/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': 'media/venclave/content/'},
        name='venclave-data'),

)
