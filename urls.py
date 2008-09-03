from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
#    (r'^', include('menclave.aenclave.urls')),
    (r'^audio/', include('menclave.aenclave.urls')),
#    (r'^games/', include('menclave.genclave.urls')),
#    (r'^video/', include('menclave.venclave.urls')),
    (r'^admin/(.*)', admin.site.root),
#    (r'^$', include('menclave.aenclave.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$',
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
