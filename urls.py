from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    '',
    (r'^audio/', include('menclave.aenclave.urls')),
    (r'^video/', include('menclave.venclave.urls')),
    (r'^admin/', include('django.contrib.admin.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$',
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
