from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect

admin.autodiscover()

def audio_redirect(req):
    return HttpResponseRedirect('/audio/')


urlpatterns = patterns(
    '',
    (r'^$', audio_redirect),
    (r'^audio/', include('menclave.aenclave.urls')),
#    (r'^games/', include('menclave.genclave.urls')),
#    (r'^video/', include('menclave.venclave.urls')),
    (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$',
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
