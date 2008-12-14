from django.template import RequestContext

from menclave.aenclave.models import Song
from menclave.aenclave.utils import get_song_list
from menclave.aenclave.html import render_html_template


#--------------------------------- Browsing ----------------------------------#

def browse_index(request):
    total_albums = Song.visibles.values('album').distinct().count()
    total_artists = Song.visibles.values('artist').distinct().count()
    return render_html_template('browse_index.html', request,
                                {'total_albums': total_albums,
                                 'total_artists': total_artists},
                                context_instance=RequestContext(request))

def browse_albums(request, letter):
    if not letter.isalpha():
        letter = '#'
        matches = Song.visibles.filter(album__regex=r'^[^a-zA-Z]').order_by()
    else:
        letter = letter.upper()
        matches = Song.visibles.filter(album__istartswith=letter).order_by()
    albums = [item['album'] for item in matches.values('album').distinct()]
    return render_html_template('browse_albums.html', request,
                                {'letter': letter, 'albums': albums},
                                context_instance=RequestContext(request))

def browse_artists(request, letter):
    if not letter.isalpha():
        letter = '#'
        matches = Song.visibles.filter(artist__regex=r'^[^a-zA-Z]').order_by()
    else:
        letter = letter.upper()
        matches = Song.visibles.filter(artist__istartswith=letter).order_by()
    artists = [item['artist'] for item in matches.values('artist').distinct()]
    return render_html_template('browse_artists.html', request,
                                {'letter': letter, 'artists': artists},
                                context_instance=RequestContext(request))

def view_album(request, album_name):
    album_songs = Song.visibles.filter(album__iexact=album_name)
    return render_html_template('album_detail.html', request,
                                {'album_name': album_name,
                                 'song_list': album_songs},
                                context_instance=RequestContext(request))

def view_artist(request, artist_name):
    artist_songs = Song.visibles.filter(artist__iexact=artist_name)
    return render_html_template('artist_detail.html', request,
                                {'artist_name': artist_name,
                                 'song_list': artist_songs},
                                context_instance=RequestContext(request))

def list_songs(request):
    songs = get_song_list(request.REQUEST)
    return render_html_template('list_songs.html', request,
                                {'song_list': songs},
                                context_instance=RequestContext(request))
