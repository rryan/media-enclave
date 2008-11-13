from models import Song
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from math import ceil as ceiling
from menclave.settings import SUPPORTED_AUDIO

class BadContent(Exception):
    def __init__(self, extension):
        self.extension = extension

def valid_song(name):
    """
    Tests whether a song is supported or not based on extension
    and the configuration settings in menclave.settings
    """
    ext = name.lower()[len(name)-3:]
    return ext in SUPPORTED_AUDIO

def process_song(name, content):
    """
    Processes a song upload: saving it and reading the meta information
    returns the song object and mutagen audio object
    """
    # Save the song into the database -- we'll fix the tags in a moment.
    song = Song(track=0, time=0)
    
    song.audio.save(name, content)
    
    info = {}
    
    audio = None

    if not valid_song(name):
        raise BadContent(name)
    
    ext = name.lower()[len(name)-3:]

    if ext == "mp3":
        # Now, open up the MP3 file and save the tag data into the database.
        audio = MP3(song.audio.path, ID3=EasyID3)
        try: info['title'] = audio['title'][0]
        except (KeyError, IndexError): info['title'] = 'Unnamed Song'
        try: info['album'] = audio['album'][0]
        except (KeyError, IndexError): info['album'] = ''
        try: info['artist'] = audio['artist'][0]
        except (KeyError, IndexError): info['artist'] = ''
        try: info['track'] = int(audio['tracknumber'][0].split('/')[0])
        except (KeyError, IndexError, ValueError): info['track'] = 0
        info['time'] = int(ceiling(audio.info.length))

    # omfg: iTunes tags... hate. hate. hate.
    # http://atomicparsley.sourceforge.net/mpeg-4files.html
    elif ext == "m4a":
        # Now, open up the MP3 file and save the tag data into the database.
        audio = MP4(song.audio.path)
        try: 
            info['title'] = audio['\xa9nam'][0]
        except (KeyError, IndexError): 
            try: 
                info['title'] = audio['\xa9NAM'][0]
            except (KeyError, IndexError):
                info['title'] = 'Unnamed Song'
        try: 
            info['album'] = audio['\xa9alb'][0]
        except (KeyError, IndexError):
            try: 
                info['album'] = audio['\xa9ALB'][0]
            except (KeyError, IndexError): 
                info['album'] = ''
        try: 
            info['artist'] = audio['\xa9art'][0]
        except (KeyError, IndexError): 
            try: 
                info['artist'] = audio['\xa9ART'][0]
            except (KeyError, IndexError):
                info['artist'] = ''
        try: info['track'] = int(audio['trkn'][0][0])
        except (KeyError, IndexError, ValueError, TypeError): 
            info['track'] = 0
        info['time'] = int(ceiling(audio.info.length))
    else:
        raise BadContent(ext)

    song.title = info['title']
    song.album = info['album']
    song.artist = info['artist']
    song.track = info['track']
    song.time = info['time']
    song.save()

    if not hasattr(audio.info, 'sketchy'):
        # Mutagen only checks mp3s for sketchiness
        audio.info.sketchy = False
    
    return (song, audio)
