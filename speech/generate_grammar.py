#!/usr/bin/python

import os
os.environ["DJANGO_SETTINGS_MODULE"] = 'menclave.settings'
import menclave
import menclave.settings
from menclave.aenclave.models import Song
import re

# start of grammar

print '''#JSGF V1.0;
grammar NiceRack;

public <top> = <msg> ;

<msg> = <queuecmd> {[command=queue]} | <dequeuecmd> {[command=dequeue]}  |
 <dequeueall> {[command=dequeueall]} | <pausecmd> {[command=pause]} | 
 <resumecmd> {[command=resume]} | <playlist> {[command=playlist]} ;

<dequeuecmd> = dequeue this song ;

<dequeueall> = dequeue everything ;

<queuecmd> = [computer] <queueword> [me] <request> ;

<queueword> = queue | play ;

<pausecmd> = pause | pause this song ;

<resumecmd> = resume this song | play this song | play | resume ; 

<playlist> = [computer] <queueword> [me] the playlist <playlistname> ;

<playlistname> = three songs {[pid=1]} | ten songs {[pid=2]} ;

<request> = '''

# TODO automate playlistname generation


# clean up a request:
# - lowercase
# - remove punctuation
# - put a . after single letters
# - let 'a' and 'the' be optional
def cleanup(s):
    s = s.lower()
    s = re.sub("[^a-z ']+", ' ', s) 
    s = re.sub('^a ', ' [a] ', s)
    s = re.sub('^the ', ' [the] ', s)
    return s

# load song info and print it as a grammar.
# ways you can queue a song:
# - songname
# - songname by artistname
# - songname from albumtitle
i = 0
l = len(Song.objects.all())
for song in Song.objects.all():
    i += 1
    
    title = cleanup(song.title)
    artist = cleanup(song.artist)
    album = cleanup(song.album)
    id = str(song.id)

    title_only = title +  ' {[id=' + id + ']} | ' 
    title_by_artist = title + ' by ' + artist + ' {[id=' + id + ']} | '
    title_from_album = title + ' from [the album] ' + album + ' {[id=' + id + ']} '

    print title_only
    print title_by_artist
    if i != l:
        title_from_album += ' | '
    print title_from_album

print ' ; '
