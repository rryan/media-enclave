# menclave/aenclave/urls.py

from django.conf.urls.defaults import *

from menclave.aenclave.models import Song

urlpatterns = patterns(
    '',

    url(r'^$',
        'menclave.aenclave.views.direct_to_template',
        {'template': 'index.html',
         'extra_context': {'total_song_count': Song.visibles.count}},
        name='aenclave-home'),

    # Login/logout

    url(r'^login/$',
        'menclave.aenclave.views.login',
        name='aenclave-login'),

    url(r'^logout/$',
        'menclave.aenclave.views.logout',
        name='aenclave-logout'),

    url(r'^user/$',  # DEBUG remove this eventually
        'menclave.aenclave.views.user_debug',
        name="aenclave-user-debug"),

    # Queuing

    url(r'^queue/$',
        'menclave.aenclave.views.queue_songs',
        name='aenclave-queue-songs'),

    url(r'^dequeue/$',
        'menclave.aenclave.views.dequeue_songs',
        name='aenclave-dequeue-songs'),

    # Searching

    url(r'^search/$',
        'menclave.aenclave.views.normal_search',
        name='aenclave-normal-search'),

    url(r'^filter/$',
        'menclave.aenclave.views.direct_to_template',
        {'template': 'filter.html'},
        name='aenclave-filter-home'),

    (r'^filter/search/$',
     'menclave.aenclave.views.filter_search'),

    # Browsing

    url(r'^browse/$',
        'menclave.aenclave.views.browse_index',
        name='aenclave-browse-index'),

    (r'^browse/albums/(?P<letter>[a-zA-Z~#@])/$',
     'menclave.aenclave.views.browse_albums'),

    (r'^browse/artists/(?P<letter>[a-zA-Z~#@])/$',
     'menclave.aenclave.views.browse_artists'),

    url(r'^songs/(?P<object_id>\d+)/$',
        'django.views.generic.list_detail.object_detail',
        {'queryset': Song.objects, 'template_name': 'song_detail.html'},
        name='aenclave-song'),

    url(r'^albums/(?P<album_name>.+)/$',
        'menclave.aenclave.views.view_album',
        name='aenclave-album'),

    url(r'^artists/(?P<artist_name>.+)/$',
        'menclave.aenclave.views.view_artist',
        name='aenclave-artist'),

    url(r'^songs/$',
        'menclave.aenclave.views.list_songs',
        name='aenclave-list'),

    # Channels

    url(r'^channels/$',
        'menclave.aenclave.views.channel_detail',
        name='aenclave-default-channel'),

    url(r'^channels/(?P<channel_id>\d+)/$',
        'menclave.aenclave.views.channel_detail',
        name='aenclave-channel'),

    # Playlists

    url(r'^playlists/$',
        'menclave.aenclave.views.all_playlists',
        name='aenclave-playlists-home'),

    url(r'^playlists/normal/(?P<playlist_id>\d+)/$',
        'menclave.aenclave.views.playlist_detail',
        name='aenclave-playlist'),

    url(r'^playlists/user/(?P<username>.+)/$',
        'menclave.aenclave.views.user_playlists',
        name='aenclave-user-playlist'),

    url(r'^playlists/create/$',
        'menclave.aenclave.views.create_playlist',
        name='aenclave-playlist-create'),

    url(r'^playlists/add/$',
        'menclave.aenclave.views.add_to_playlist',
        name='aenclave-playlist-add'),

    url(r'^playlists/remove/$',
        'menclave.aenclave.views.remove_from_playlist',
        name='aenclave-playlist-remove'),

    url(r'^playlists/delete/$',
        'menclave.aenclave.views.delete_playlist',
        name='aenclave-playlist-delete'),

    # Uploading

    url(r'^upload/$',
        'menclave.aenclave.views.direct_to_template',
        {'template': 'upload.html'},
        name='aenclave-upload-home'),

    url(r'^upload/http/$',
        'menclave.aenclave.views.upload_http',
        name='aenclave-http-upload'),

    url(r'^upload/fancy/$',
        'menclave.aenclave.views.upload_http_fancy',
        name='aenclave-http-upload-fancy'),

    url(r'^upload/fancy/receive/$',
        'menclave.aenclave.views.upload_http_fancy_receiver',
            name='aenclave-http-upload-fancy-receiver'),


    url(r'^upload/sftp/$',
        'menclave.aenclave.views.upload_sftp',
        name='aenclave-sftp-upload'),

    url(r'^upload/sftp-info/$',
        'menclave.aenclave.views.direct_to_template',
        {'template': 'sftp_info.html'},
        name='aenclave-sftp-info'),

    # DL

    url(r'^dl/$',
        'menclave.aenclave.views.dl',
        name='aenclave-dl'),

    # Roulette

    url(r'^roulette/$',
        'menclave.aenclave.views.roulette',
        name='aenclave-roulette'),

    # Delete Requests

    url(r'^delete-songs/$',
        'menclave.aenclave.views.delete_songs',
        name='aenclave-delete-songs'),

    # XML hooks

    (r'^xml/queue/$',
     'menclave.aenclave.views.xml_queue'),

    (r'^xml/dequeue/$',
     'menclave.aenclave.views.xml_dequeue'),

    (r'^xml/control/$',
     'menclave.aenclave.views.xml_control'),

    (r'^xml/update/$',
     'menclave.aenclave.views.xml_update'),

    (r'^xml/edit/$',
     'menclave.aenclave.views.xml_edit'),

    (r'^xml/playlists/user/$',
     'menclave.aenclave.views.xml_user_playlists'),

    # JSON hooks

    (r'^json/control/$',
     'menclave.aenclave.views.json_control'),

    (r'^json/edit/$',
     'menclave.aenclave.views.json_edit'),

    (r'^json/playlists/user/$',
     'menclave.aenclave.views.json_user_playlists'),

    (r'^json/email/$',
     'menclave.aenclave.views.json_email_song_link'),

    (r'^json/controls_update/$',
     'menclave.aenclave.views.json_control_update'),

    (r'^json/controls_update/(?P<channel_id>\d+)/$',
     'menclave.aenclave.views.json_control_update'),

)
