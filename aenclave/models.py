# menclave/aenclave/models.py

from calendar import timegm
import datetime
from math import exp

from django.db import models
from django.contrib.auth.models import Group, User

#================================= UTILITIES =================================#

def datetime_string(dt):
    date, today = dt.date(), datetime.date.today()
    if date == today: return dt.strftime('Today %H:%M:%S')
    elif date == today - datetime.timedelta(1):
        return dt.strftime('Yesterday %H:%M:%S')
    else: return dt.strftime('%d %b %Y %H:%M:%S')

#================================== MODELS ===================================#

class VisibleManager(models.Manager):
    """VisibleManager -- manager for getting only visible songs"""
    def get_query_set(self):
        return super(VisibleManager, self).get_query_set().filter(visible=True)


class Song(models.Model):
    def __unicode__(self): return self.title

    #--------------------------------- Title ---------------------------------#

    title = models.CharField(maxlength=255)

    #--------------------------------- Album ---------------------------------#

    album = models.CharField(maxlength=255)

    #-------------------------------- Artist ---------------------------------#

    artist = models.CharField(maxlength=255)

    #--------------------------------- Track ---------------------------------#

    track = models.PositiveSmallIntegerField()
    def track_string(self):
        if self.track == 0: return ''
        else: return str(self.track)
    track_string.short_description = 'track'

    #--------------------------------- Time ----------------------------------#

    time = models.PositiveIntegerField(help_text="The duration of the song,"
                                       " in seconds.")
    def time_string(self):
        string = str(datetime.timedelta(0, self.time))
        if self.time < 600: return string[3:]
        elif self.time < 3600: return string[2:]
        else: return string
    time_string.short_description = 'time'

    #------------------------------ Date Added -------------------------------#

    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    def date_added_string(self): return datetime_string(self.date_added)
    date_added_string.short_description = 'date added'

    #------------------------------ Last Queued ------------------------------#

    last_queued = models.DateTimeField(default=None, blank=True, null=True,
                                       editable=False)
    def last_queued_string(self): return datetime_string(self.last_queued)
    last_queued_string.short_description = 'last queued'

    #------------------------------ Audio Path -------------------------------#

    audio = models.FileField(upload_to='aenclave/songs/%Y/%m/%d/')

    #------------------------------- Album Art -------------------------------#

    album_art = models.ImageField(upload_to='aenclave/songs/%Y/%m/%d/',
                                  blank=True, null=True)

    #--------------------------------- Score ---------------------------------#

    score = models.PositiveIntegerField(default=0, editable=False)
    def adjusted_score(self):
        if self.last_queued is None: return 0
        delta = datetime.datetime.now() - self.last_queued
        # 1.1574074074074073e-05 == 1.0 / (60 * 60 * 24)
        days = delta.days + delta.seconds * 1.1574074074074073e-05
        return int(self.score * exp(-0.05 * days))
    adjusted_score.short_description = 'score'

    #-------------------------------- Visible --------------------------------#

    visible = models.BooleanField(default=True, help_text="Non-visible songs"
                                  " do not appear in search results.")

    #------------------------------ Other Stuff ------------------------------#

    class Admin:
        date_hierarchy = 'date_added'
        list_display = ('track','title', 'time_string', 'album', 'artist',
                        'date_added', 'adjusted_score', 'visible')
        list_display_links = ('title',)
        list_filter = ('visible', 'date_added')
        search_fields = ('title', 'album', 'artist')

    class Meta:
        get_latest_by = 'date_added'
        ordering = ('artist', 'album', 'track')

    @models.permalink
    def get_absolute_url(self):
        return ('aenclave-song', (str(self.id),))

    def queue_touch(self):
        self.last_queued = datetime.datetime.now()
        self.score = self.adjusted_score() + 100
        self.save()

    objects = models.Manager()
    visibles = VisibleManager()

#-----------------------------------------------------------------------------#

class Playlist(models.Model):
    def __unicode__(self): return self.name

    #-------------------------------- Fields ---------------------------------#

    name = models.CharField(maxlength=255)

    owner = models.ForeignKey(User)

    group = models.ForeignKey(Group, blank=True, null=True)

    songs = models.ManyToManyField(Song, blank=True,
                                   filter_interface=models.HORIZONTAL)

    last_modified = models.DateTimeField(auto_now=True, editable=False)
    def last_modified_string(self): return datetime_string(self.last_modified)
    last_modified_string.short_description = 'Last modified'

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    def date_created_string(self): return datetime_string(self.date_created)
    date_created_string.short_description = 'Date created'

    #------------------------------ Other Stuff ------------------------------#

    class Admin:
        date_hierarchy = 'date_created'
        list_display = ('name', 'owner', 'group', 'last_modified',
                        'date_created')
        list_filter = ('owner', 'last_modified', 'date_created')
        search_fields = ('name',)

    class Meta:
        get_latest_by = 'last_modified'
        ordering = ('owner', 'name')
        unique_together = (('name', 'owner'),)

    @models.permalink
    def get_absolute_url(self):
        return ('aenclave-playlist', (str(self.id),))

    def can_cede(self, user):
        return (user == self.owner)

    def can_edit(self, user):
        if self.group is None: return (user == self.owner)
        try: self.group.user_set.get(id=user.id)
        except User.DoesNotExist: return (user == self.owner)
        else: return True

#-----------------------------------------------------------------------------#

class Channel(models.Model):
    def __unicode__(self): return self.name

    #-------------------------------- Fields ---------------------------------#

    # For channels, we want the id to be editable, because the channel with
    # id=1 is the default channel.
    id = models.PositiveSmallIntegerField('ID', primary_key=True, help_text=
                                          "The channel with ID=1 will be the"
                                          " default channel.")

    name = models.CharField(maxlength=32, unique=True)

    pipe = models.FilePathField(path='/tmp', match="xmms.*", recursive=True,
                                help_text="The path to the XMMS2 control pipe"
                                " for this channel.")

    last_touched = models.DateTimeField(auto_now=True, editable=False)
    def last_touched_timestamp(self):
        return timegm(self.last_touched.timetuple())

    #------------------------------ Other Stuff ------------------------------#

    class Admin:
        list_display = ('id', 'name', 'pipe', 'last_touched')
        list_display_links = ('name',)

    class Meta:
        get_latest_by = 'last_touched'
        ordering = ('id',)

    @models.permalink
    def get_absolute_url(self):
        return ('aenclave-channel', (str(self.id),))

    @classmethod
    def default(cls): return cls.objects.get(pk=1)

    def touch(self):
        self.save()  # `self.last_touched` will auto-update.

    def controller(self): return Controller(self)


# This import goes at the end to avoid circularity.
from control import Controller

#=============================================================================#
