# menclave/aenclave/control.py

"""menclave.aenclave.control -- music player control functions"""

import os
import random
import logging
import traceback

from xmmsclient import XMMSError
from xmmsclient import PLAYBACK_STATUS_PLAY as PLAY
from xmmsclient import PLAYBACK_STATUS_PAUSE as PAUSE
from xmmsclient import PLAYBACK_STATUS_STOP as STOP

from menclave.settings import AENCLAVE_DEQUEUE_NOISES_DIR
from menclave.aenclave.connection import CONNECTION_MANAGER
from menclave.aenclave.models import Channel, Song

__all__ = ('ControlError', 'Controller')

#=============================================================================#

class ControlError(Exception):
    """The exception class for music control-related errors."""
    pass

def _catch():
    """Call from within an except-block to record the error."""
    logging.error(traceback.format_exc())

#=============================================================================#

class Controller(object):
    """Controller([channel]) -- class for controlling music channels

    Creates a controller object for the given channel, or for the default
    channel if no Channel object is given."""
    def __init__(self, channel=None):
        if channel is None: channel = Channel.default()

# WTF (rryan): This code is broken by Apache, because it spawns so
# many damn workers, that so many connections to the music daemon are
# made that it hits the unix file descriptor limit. For now, we just
# use one connection, and pray there aren't race conditions (hah)

#         client = XMMSSync()
#         try: client.connect(channel.pipe)
#         except IOError:
#             logging.error("XMMS2 daemon is apparently dead. Running xmms2-launcher.")
#             os.spawnlp(os.P_WAIT, 'xmms2-launcher', 'xmms2-launcher')
#             try:
#                 client.connect(channel.pipe)
#             except IOError:
#                 _catch()
#                 raise ControlError("The music daemon is not responding.")
#        self.client = client

        self.client = CONNECTION_MANAGER.connection_for_channel(channel)
        self.channel = channel

    def _xmms2_url(self, path):
        # XMMS2 will quote the URL for us -- all we have to do is provide file:// + path
        return 'file://' + path

    #---------------------------- STATUS METHODS -----------------------------#

    def get_status(self):
        """controller.get_status() -> status of channel

        Returns control.PLAY, control.PAUSE, or control.STOP, depending on the
        status of the channel."""
        try: return self.client.playback_status()
        except XMMSError:
            _catch()
            return STOP  # not worth raising an error

    def is_playing(self):
        """controller.is_playing() -> True iff the channel is playing"""
        return self.get_status() == PLAY

    def is_paused(self):
        """controller.is_paused() -> True iff the channel is paused"""
        return self.get_status() == PAUSE

    def is_stopped(self):
        """controller.is_stopped() -> True iff the channel is stopped"""
        return self.get_status() == STOP

    def get_elapsed_time(self):
        """controller.get_elapsed_time() -> elapsed time of song, in seconds"""
        # BTW playback_playtime() returns the elapsed time in milliseconds, so
        #     we divide by 1000 to convert to seconds.
        try: return self.client.playback_playtime() // 1000
        except XMMSError:
            _catch()
            return 0  # not worth raising an error

    def get_current_song(self):
        """controller.get_current_song() -> currently playing song"""
        if self.is_stopped(): return None
        try:
            # Get the XMMS2 medialib ID of the currently playing song.
            current = self.client.playback_current_id()
            # WTF Probably due to a bug, playback_current_id sometimes returns
            #     zero if called right after starting playback, but this
            #     back-up code seems to work in that situation.
            if current == 0:
                plist = self.client.playlist_list_entries()
                current = plist[self._get_current_position()]
            # Get the primary database key of the corresponding song object.
            info = self.client.medialib_get_info(current)
            pk_string = info['aenclave', 'pk']
            if pk_string == 'DQ': return 'DQ'
            else: pk = int(pk_string)
            # Return the proper song object.
            return Song.objects.get(pk=pk)
        except Exception:
            _catch()
            raise ControlError("Couldn't get the current song.")

    def _get_current_position(self):
        """controller.get_current_position() -> position of song in playlist"""
        # Different versions of XMMS treat this API call differently.
        # It either returns:
        #  - the integer position
        #  - a dict with the integer position under the key 'position'
        value = self.client.playlist_current_pos()
        if type(value) is type({}):
            return value['position']
        return value

    def get_queue_songs(self):
        """controller.get_queue_songs() -> list of songs in queue"""
        # If the queue is stopped, return the empty list.
        if self.is_stopped(): return []
        try:
            # Get the list of songs in the playlist.
            plist = self.client.playlist_list_entries()
            # If the list is empty, return the empty list.
            if len(plist) == 0: return []
            # Otherwise, chop off everything up through the current song.
            plist = plist[self._get_current_position()+1:]
            # Get the primary database keys.
            pks = [int(self.client.medialib_get_info(ID)['aenclave','pk'])
                   for ID in plist]
            # Return the database entries.
            songs = Song.objects.in_bulk(pks)
            return [songs[pk] for pk in pks]
        except (XMMSError, KeyError, ValueError, Song.DoesNotExist):
            _catch()
            raise ControlError("The queue couldn't be read.")

    def get_queue_length(self):
        """controller.get_queue_length() -> number of songs in queue"""
        # If the queue is stopped, return zero.
        if self.is_stopped(): return 0
        try:
            # Get the length of the playlist.
            length = len(self.client.playlist_list_entries())
            # If the playlist is empty, return zero.
            if length == 0: return 0
            # Otherwise, return the length not counting the current song.
            return length - self._get_current_position() - 1
        except XMMSError:
            _catch()
            return 0  # not worth raising an error

    def get_queue_duration(self):
        """controller.get_queue_duration() -> total remaining time, in seconds

        Returns the total time left on the queue, in seconds, including
        remaining time on the current song and the total duration of all
        remaining songs."""
        try:
            # If the queue is stopped, then it's empty.
            if self.is_stopped(): return 0
            # Figure out which songs haven't finished playing yet, including
            # the song that is currently playing.
            plist = self.client.playlist_list_entries()
            if len(plist) == 0: return 0
            plist = plist[self._get_current_position():]
        except XMMSError:
            _catch()
            return 0  # not worth raising an error
        # Sum the durations of the current song and the songs in the queue.
        total = 0
        for ID in plist:
            # Due to bugs in early releases of XMMS2, the duration entry is
            # occasionally absent.  To be safe, we allow it to default to zero.
            try: total += self.client.medialib_get_info(ID).get('duration', 0)
            except XMMSError: _catch()
        # Subtract the time that has already elapsed in the current song.
        try: total -= self.client.playback_playtime()
        except XMMSError: _catch()
        # The playtimes used by XMMS2 are in milliseconds, so divide by 1000.
        return total // 1000

    #--------------------------- PLAYBACK CONTROL ----------------------------#

    def stop(self):
        """controller.stop() -- stops the music and clears the queue"""
        # If the queue is already stopped, then do nothing.
        if self.is_stopped(): return
        try:
            self.client.playback_stop()
            self.client.playlist_clear()
        except XMMSError:
            _catch()
            raise ControlError("The queue could not be stopped.")
        else: self.channel.touch()

    def pause(self):
        """controller.pause() -- pauses the music"""
        if self.is_playing():
            try: self.client.playback_pause()
            except XMMSError:
                _catch()
                raise ControlError("The song could not be paused.")
            else: self.channel.touch()

    def unpause(self):
        """controller.unpause() -- unpauses the music"""
        if self.is_paused():
            try: self.client.playback_start()
            except XMMSError:
                _catch()
                raise ControlError("The song could not be unpaused.")
            else: self.channel.touch()

    def skip(self):
        """controller.skip() -- skips the current song"""
        # If the queue is already stopped, then do nothing.
        if self.is_stopped(): return
        # Play a dequeue noise.
        try:
            # Pick a random dequeue noise and get its path.
            dir_list = os.listdir(AENCLAVE_DEQUEUE_NOISES_DIR)
            if(len(dir_list) == 0):
                raise OSError("No deque files")
            deq = random.choice(dir_list)
            deq = self._xmms2_url(os.path.join(AENCLAVE_DEQUEUE_NOISES_DIR,
                                               deq))
        except OSError:
            # We can't find the files for some reason.
            _catch()
        else:
            try:
                # Have XMMS2 import the dequeue noise data.
                self.client.medialib_add_entry(deq)
                # Have XMMS2 remember that this is a dequeue noise.
                ID = self.client.medialib_get_id(deq)
                self.client.medialib_property_set(ID, 'pk', 'DQ', 'aenclave')
                # Insert the dequeue noise just after the current song.  We
                # can't insert a song beyond the length of the playlist, so if
                # we're at the end of the playlist, we have to use
                # playlist_add() instead of playlist_insert().
                nextpos = self._get_current_position() + 1
                if nextpos >= len(self.client.playlist_list_entries()):
                    self.client.playlist_add_id(ID)
                else: self.client.playlist_insert_id(nextpos, ID)
            except XMMSError:
                # XMMS2 couldn't queue the song for some reason, just let it
                # slide.
                _catch()
        # Now skip the current song, thus going on to play the dequeue noise.
        # This is done by telling the playlist to prepare to move one song
        # forward relative to the current song, and then "tickling" the
        # playback.
        try:
            nextpos = self._get_current_position() + 1
            if nextpos >= len(self.client.playlist_list_entries()):
                # If there's no next track, we can't go to the next song, we
                # have to stop playback.
                self.client.playback_stop()
            else:
                self.client.playlist_set_next_rel(1)
                self.client.playback_tickle()
        except XMMSError:
            _catch()
            raise ControlError("The song could not be dequeued.")
        else: self.channel.touch()

    def shuffle(self):
        """controller.shuffle() -- shuffles the songs in the queue"""
        # If the queue is stopped, do nothing.
        if self.is_stopped(): return
        try:
            # Get the list of songs in the playlist.
            plist = self.client.playlist_list_entries()
            # If the list is empty, do nothing.
            if len(plist) == 0: return
            # Get the current position.
            pos = self._get_current_position()
            # Dequeue all upcoming songs.
            for index in xrange(len(plist)-1, pos, -1):
                self.client.playlist_remove_entry(index)
            # Chop off everything up through the current song.
            plist = plist[pos+1:]
            # Shuffle it up!
            random.shuffle(plist)
            # Requeue the shuffled songs.
            for ID in plist: self.client.playlist_add_id(ID)
        except XMMSError:
            _catch()
            raise ControlError("The queue couldn't be shuffled.")
        else: self.channel.touch()

    #----------------------------- QUEUE CONTROL -----------------------------#

    def add_song(self, song):
        """controller.add_song(song) -- adds the song to the queue"""
        self.add_songs([song])

    def add_songs(self, songs):
        """controller.add_songs(songs) -- adds the songs to the queue"""
        # If the queue is stopped, clear it, so that when we start it below,
        # songs that have already played won't be played again.  Eventually, we
        # want to set up XMMS2 to remove songs when they finish, but even when
        # we do, this is a useful safety check to have.
        try:
            stopped = self.is_stopped()
            if stopped: self.client.playlist_clear()
        except XMMSError:
            _catch()
            raise ControlError("The queue could not be cleaned.")
        # Add the songs to the end of the queue.
        for song in songs:
            # The XMMS2 client expects URLs rather than paths
            url = self._xmms2_url(song.audio.path)
            try:
                # Have XMMS2 import the song data.
                retval = self.client.medialib_add_entry(url)

                # Get ID of the song in the media library
                ID = self.client.medialib_get_id(url)

                # Sometimes medialib_get_id returns 0 directly after
                # we add an item to the media library. To account for this
                # if we get a 0, then loop a few times trying again.
                if ID == 0:
                    logging.debug("Attempting to recover from medialib_get_id==0 for '%s'." % url)
                    for i in range(10):
                        ID = self.client.medialib_get_id(url)

                # Under no circumstances should you provide a 0 to xmmsclient. A bug in xmms2 will cause the server
                # to start ignoring future requests.
                if ID == 0:
                    logging.debug("Tried to recover from medialib_get_id==0 for '%s' but could not. Dropping the song on the floor." % url)
                    continue

                # Have XMMS2 remember the primary key of the database entry.
                self.client.medialib_property_set(ID, 'pk', str(song.id), 'aenclave')

                # Add the song to the queue.
                self.client.playlist_add_id(ID)

            except XMMSError:
                _catch()
                logging.error("Couldn't add song to the queue.")
                raise ControlError("The song could not be added to the queue.")
            # Update the song's last_played date.
            else: song.queue_touch()
        # Start the queue playing if it's not already.
        if stopped:
            try: self.client.playback_start()
            except XMMSError:
                _catch()
                raise ControlError("The queue could not be started.")
        # Remember that this channel has been touched.
        self.channel.touch()

    def remove_song(self, index):
        self.remove_songs([index])

    def remove_songs(self, indices):
        # We want to add each index to the XMMS2 playlist position so as to
        # ignore songs that have finished playing, and then we add 1 so as to
        # ignore the currently playing song.  Then we need to check if that
        # index is valid.
        try:
            base = self._get_current_position() + 1
            length = len(self.client.playlist_list_entries())
        except XMMSError:
            _catch()
            raise ControlError("The contents of the queue could not be read.")
        # We'll be polite and not edit the input list, so make a copy first.
        indices = indices[:]
        # Sort the list in reverse order, so that we delete later songs first.
        indices.sort(reverse=True)
        # Remove each song in the list.
        for index in indices:
            index += base
            # If the index is not valid, log an error and punt.
            if not 0 <= index < length:
                logging.error('ERROR', "can't remove song index %i from list of"
                              " length %i" % (index, length))
                return
            # Remove the song from the playlist.
            try: self.client.playlist_remove_entry(index)
            except XMMSError, e:
                _catch()
                raise ControlError("The song could not be dequeued.")
        # Remember that this channel has been touched.
        self.channel.touch()

    def clear_queued_songs(self):
        self.remove_songs(range(0, self.get_queue_length()))

    def move_song(self, frm, to):
        self.move_songs([frm], to)

    def move_songs(self, frms, to):
        # We want to add each index to the XMMS2 playlist position so as to
        # ignore songs that have finished playing, and then we add 1 so as to
        # ignore the currently playing song.  Then we need to check if that
        # index is valid.
        try:
            base = self._get_current_position() + 1
            length = len(self.client.playlist_list_entries())
        except XMMSError:
            _catch()
            raise ControlError("The contents of the queue could not be read.")
        # We'll be polite and not edit the input list, so make a copy first.
        frms = frms[:]
        # Sort the list in reverse order, so that we move later songs first.
        frms.sort(reverse=True)
        # Move each song in the list.
        to += base
        for frm in frms:
            frm += base
            # If the index is not valid, log an error and punt.
            if not 0 <= frm < length:
                logging.error('ERROR', "can't move song index %i in list of length %i" %
                          (frm, length))
                return
            # Move the song.
            try: self.client.playlist_move(frm, to)
            except XMMSError:
                _catch()
                raise ControlError("The song could not be moved.")
        # Remember that this channel has been touched.
        self.channel.touch()

#=============================================================================#
