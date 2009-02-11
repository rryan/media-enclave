# menclave/aenclave/control.py

"""Music player control functions."""

import logging

import Pyro.core

from menclave import settings
from menclave.aenclave.models import Channel, Song

#=============================================================================#

class ControlError(Exception):

    """The exception class for music control-related errors."""

    pass

def delegate_rpc(method):
    """Delegate a method to the instance player proxy, and then call it."""
    def new_method(self, *args, **kwargs):
        try:
            retval = getattr(self.player, method.__name__)(*args, **kwargs)
        except Exception, e:
            # This will be a pyro remote error.  Log the remote trace.
            logging.exception('RPC raised exception; remote traceback:\n' +
                              ''.join(Pyro.util.getPyroTraceback(e)))
            raise ControlError(e.message)
        else:
            kwargs['rpc_val'] = retval
            return method(self, *args, **kwargs)
    return new_method

#=============================================================================#

class Controller(object):

    """
    Class for remotely controlling the playback of a channel.

    channel -- The id of the controlled channel.
    player -- The Pyro remote player object.

    This class wraps a RemotePlayer object does extra client-side steps as
    necessary.  All multi-step player logic belongs in the base GstPlayer object
    to avoid multiple RPCs.  The player is also synchronized, so we avoid race
    conditions by doing computation in the player.
    """

    def __init__(self, channel=None):
        """
        Create a controller for the given channel or the default channel, 1.
        """
        if channel is None: channel = Channel.default()
        self.channel = channel
        # TODO(rnk): Change the naming to make one remote object per channel.
        #subs = (settings.HOST_NAME, settings.GST_PLAYER_PORT, channel.id)
        #uri = "PYROLOC://%s:%i/gst_player/%i" % subs
        uri = "PYROLOC://%s:%i/gst_player" % (settings.GST_PLAYER_HOST,
                                              settings.GST_PLAYER_PORT)
        self.player = Pyro.core.getProxyForURI(uri)

    #---------------------------- STATUS METHODS -----------------------------#

    def _refresh_songs(self, songs, user=None):
        """
        Refresh song models, preserving the player-added attributes.

        We do this so that we can have the most up-to-date tags if the user
        editted the tags while the song was on the queue.
        """
        pks = [song.pk for song in songs]
        pk_dict = dict((song.pk, (i, song)) for (i, song) in enumerate(songs))
        fresh_songs = Song.objects.filter(pk__in=pks)
        # It would be nice to not have to iterate this queryset, but we have to
        # annotate the models with playid and the noise.  We have to get the
        # user passed all the way into here in order to do this annotation if
        # the caller wants it before we force query evaluation.
        if user is not None:
            fresh_songs = Song.annotate_favorited(fresh_songs, user)
        final_songs = []
        for song in fresh_songs:
            (i, stale_song) = pk_dict[song.pk]
            song.noise = stale_song.noise
            song.playid = stale_song.playid
            final_songs.append([i, song])
        final_songs.sort()
        return [song for (_, song) in final_songs]

    @delegate_rpc
    def get_channel_snapshot(self, user=None, rpc_val=None):
        """Return a snapshot of the current channel state."""
        rpc_val.song_queue = self._refresh_songs(rpc_val.song_queue, user=user)
        rpc_val.song_history = self._refresh_songs(rpc_val.song_history,
                                                   user=user)
        return rpc_val

    #--------------------------- PLAYBACK CONTROL ----------------------------#

    @delegate_rpc
    def stop(self, rpc_val=None):
        """Stops the music and clears the queue."""
        self.channel.touch()

    @delegate_rpc
    def pause(self, rpc_val=None):
        """Pause the music."""
        self.channel.touch()

    @delegate_rpc
    def unpause(self, rpc_val=None):
        """Unpause the music."""
        self.channel.touch()

    @delegate_rpc
    def skip(self, rpc_val=None):
        """Skip the current song and play a dequeue noise."""
        self.channel.touch()

    #----------------------------- QUEUE CONTROL -----------------------------#

    def add_song(self, song, rpc_val=None):
        """Add a song to the queue."""
        self.add_songs([song])

    @delegate_rpc
    def add_songs(self, songs, rpc_val=None):
        """Add some songs to the queue."""
        self.channel.touch()

    def remove_song(self, playid, rpc_val=None):
        """Remove the song with playid from the queue."""
        self.remove_songs([playid])

    @delegate_rpc
    def remove_songs(self, playids, rpc_val=None):
        """Remove the songs with playids in playids from the queue."""
        self.channel.touch()

    @delegate_rpc
    def move_song(self, playid, after_playid, rpc_val=None):
        """Move the first song to after the second song in the queue."""
        self.channel.touch()

    @delegate_rpc
    def shuffle(self, rpc_val=None):
        """Shuffle the songs in the queue."""
        self.channel.touch()

#=============================================================================#
