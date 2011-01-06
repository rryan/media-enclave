from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
    # TODO(rnk): This redirect to /audio/ should be eliminated.  If only one
    # menclave app is installed, we could pick the right one automatically, and
    # give a lame picker index if more than one is installed.
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/audio'}),
    (r'^log/', include('menclave.log.urls')),
    (r'^admin/(.*)', admin.site.root),
)

if 'menclave.aenclave' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^audio/', include('menclave.aenclave.urls')))

if 'menclave.venclave' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^video/', include('menclave.venclave.urls')))

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$',
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
