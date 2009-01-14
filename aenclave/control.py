# menclave/aenclave/control.py

"""Music player control functions."""

import logging
import traceback

import Pyro.core

from menclave import settings  # TODO(rnk): Switch to the below.
#from aenclave import settings
from menclave.aenclave.models import Channel

#=============================================================================#

# TODO(rnk): Wrap all RPCs (in a nice way) to rethrow errors as ControlErrors.

class ControlError(Exception):

    """The exception class for music control-related errors."""

    pass

def _catch():
    """Call from within an except-block to record the error."""
    logging.error(traceback.format_exc())

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
        uri = "PYROLOC://localhost:%i/gst_player" % (settings.GST_PLAYER_PORT)
        self.player = Pyro.core.getProxyForURI(uri)

    #---------------------------- STATUS METHODS -----------------------------#

    def get_channel_snapshot(self):
        """Return a snapshot of the current channel state."""
        return self.player.get_channel_snapshot()

    #--------------------------- PLAYBACK CONTROL ----------------------------#

    def stop(self):
        """Stops the music and clears the queue."""
        self.player.stop()
        self.channel.touch()

    def pause(self):
        """Pause the music."""
        self.player.pause()
        self.channel.touch()

    def unpause(self):
        """Unpause the music."""
        self.player.unpause()
        self.channel.touch()

    def skip(self):
        """Skip the current song and play a dequeue noise."""
        self.player.skip()
        self.channel.touch()

    #----------------------------- QUEUE CONTROL -----------------------------#

    def add_song(self, song):
        """Add a song to the queue."""
        self.add_songs([song])

    def add_songs(self, songs):
        """Add songs to the queue."""
        self.player.add_songs(songs)
        self.channel.touch()

    def remove_song(self, playid):
        self.remove_songs([playid])

    def remove_songs(self, playids):
        self.player.remove_songs(playids)
        self.channel.touch()

    def move_song(self, playid, after_playid):
        self.player.move_song(playid, after_playid)
        self.channel.touch()

    def shuffle(self):
        """Shuffle the songs in the queue."""
        self.player.shuffle()
        self.channel.touch()

#=============================================================================#
