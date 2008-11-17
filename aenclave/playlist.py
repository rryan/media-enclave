
from django.template import RequestContext
from django.db.models.query import Q
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from menclave.aenclave.login import permission_required
from menclave.aenclave.html import render_html_template, html_error
from menclave.aenclave.xml import render_xml_to_response
from menclave.aenclave.json import render_json_template, json_error, json_success
from menclave.aenclave.models import Playlist, PlaylistEntry
from menclave.aenclave.utils import get_integer, get_unicode, get_song_list

#----------------------------- Playlist Viewing ------------------------------#

def all_playlists(request):
    return render_html_template('playlist_list.html', request,
                                {'playlist_list': Playlist.objects.all()},
                                context_instance=RequestContext(request))

def playlist_detail(request, playlist_id):
    try: playlist = Playlist.objects.get(pk=playlist_id)
    except Playlist.DoesNotExist: raise Http404
    can_cede = playlist.can_cede(request.user)
    # This order_by uses PlaylistEntry's Meta ordering, which is position.
    songs = playlist.songs.order_by('playlistentry')
    return render_html_template('playlist_detail.html', request,
                                {'playlist': playlist,
                                 'song_list': songs,
                                 'force_actions_bar': can_cede,
                                 'allow_cede': can_cede,
                                 'allow_edit': playlist.can_edit(request.user)},
                                context_instance=RequestContext(request))

def user_playlists(request, username):
    plists = Playlist.objects.filter(owner__username=username)
    return render_html_template('playlist_list.html', request,
                                {'playlist_list': plists},
                                context_instance=RequestContext(request))

def xml_user_playlists(request):
    if request.user.is_authenticated():
        query = Q(owner=request.user) | Q(group__in=request.user.groups.all())
        playlists = Playlist.objects.filter(query)
    else: playlists = Playlist.objects.none()
    return render_xml_to_response('playlist_list.xml',
                                  {'playlist_list':playlists})

def json_user_playlists(request):
    if request.user.is_authenticated():
        query = Q(owner=request.user) | Q(group__in=request.user.groups.all())
        playlists = Playlist.objects.filter(query)
    else: playlists = Playlist.objects.none()
    return render_json_template('playlist_list.json',
                                {'playlist_list':playlists})



#----------------------------- Playlist Editing ------------------------------#

@permission_required('aenclave.add_playlist', 'Make Playlist')
def create_playlist(request):
    form = request.POST
    name = get_unicode(form, 'name')
    if not name:
        return html_error(request,'No name provided.')  # TODO better feedback
    # Make sure that we can create the playlist.
    # WTF In fact, we can't use playlist.songs until playlist has been saved.
    playlist = Playlist(name=name, owner=request.user)
    try:
        playlist.save()  # BTW This will fail if (name,owner) is not unique.
    except:
        return html_error(request, 'A playlist of that name already exists.')
    #    return error(request,'Nonunique name/owner.')  # TODO better feedback
    # Add the specified songs to the playlist.
    songs = get_song_list(form)
    playlist.set_songs(songs)
    playlist.save()
    # Redirect to the detail page for the newly created playlist.
    return HttpResponseRedirect(playlist.get_absolute_url())

@permission_required('aenclave.change_playlist', 'Add Songs')
def add_to_playlist(request):
    # Get the playlist to be added to.
    form = request.POST
    try: playlist = Playlist.objects.get(pk=get_integer(form, 'pid'))
    except Playlist.DoesNotExist:
        return html_error(request, 'That playlist does not exist.',
                          'Add Songs')
    # Make sure the user is allowed to edit this playlist.
    if not playlist.can_edit(request.user):
        return html_error(request, 'You lack permission to edit this'
                          ' playlist.', 'Add Songs')
    # Add the songs and redirect to the detail page for this playlist.
    songs = get_song_list(form)
    playlist.append_songs(songs)
    return HttpResponseRedirect(playlist.get_absolute_url())

@permission_required('aenclave.change_playlist', 'Remove Songs')
def remove_from_playlist(request):
    # Get the playlist to be removed from.
    form = request.POST
    try: playlist = Playlist.objects.get(pk=get_integer(form, 'pid'))
    except Playlist.DoesNotExist:
        return html_error(request, 'That playlist does not exist.',
                          'Remove Songs')
    # Make sure the user is allowed to edit this playlist.
    if not playlist.can_edit(request.user):
        return html_error(request, 'You lack permission to edit this'
                          ' playlist.', 'Remove Songs')
    # Remove the songs and redirect to the detail page for this playlist.
    songs = get_song_list(form)
    PlaylistEntry.objects.filter(song__in=songs).delete()
    return HttpResponseRedirect(playlist.get_absolute_url())

@permission_required('aenclave.delete_playlist', 'Delete Playlist')
def delete_playlist(request):
    # Get the playlist to be deleted.
    form = request.POST
    try: playlist = Playlist.objects.get(pk=get_integer(form, 'pid'))
    except Playlist.DoesNotExist:
        return html_error(request, 'That playlist does not exist.',
                          'Delete Playlist')
    # Make sure the user is allowed to delete the playlist.
    if not playlist.can_cede(request.user):
        return html_error(request, 'You may only delete your own playlists.',
                          'Delete Playlist')
    # Delete the playlist and redirect to the user's playlists page.
    playlist.delete()
    return HttpResponseRedirect(reverse('aenclave-user-playlist',
                                        args=[request.user.username]))

@permission_required('aenclave.change_playlist', 'Edit Playlist')
def edit_playlist(request, playlist_id):
    # Get the playlist.
    form = request.POST
    try: playlist = Playlist.objects.get(pk=playlist_id)
    except Playlist.DoesNotExist:
        return json_error('That playlist does not exist.')
    # Check that they can edit it.
    if not playlist.can_edit(request.user):
        return json_error('You are not authorized to edit this playlist.')
    songs = get_song_list(form)
    if songs:
        playlist.set_songs(songs)
        playlist.save()
    return json_success('Successfully edited "%s".' % playlist.name)

