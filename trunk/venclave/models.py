# menclave/venclave/models.py

from calendar import timegm
import datetime

from django.db import models

#================================= UTILITIES =================================#

def datetime_string(dt):
    date, today = dt.date(), datetime.date.today()
    if date == today: return dt.strftime('Today %H:%M:%S')
    elif date == today - datetime.timedelta(1):
        return dt.strftime('Yesterday %H:%M:%S')
    else: return dt.strftime('%d %b %Y %H:%M:%S')

#================================== MODELS ===================================#

class Tag(models.Model):
    def __unicode__(self): return self.name

    name = models.CharField(max_length=50, primary_key=True)

    class Admin:
        list_display = ('name',)
        list_display_links = ('name',)
        search_fields = ('name',)

    class Meta:
        ordering = ('name',)

#-----------------------------------------------------------------------------#

class VisibleManager(models.Manager):
    """VisibleManager -- manager for getting only visible videos"""
    def get_query_set(self):
        return super(VisibleManager, self).get_query_set().filter(visible=True)

#-----------------------------------------------------------------------------#

class Producer(models.Model):
    name = models.TextField()

#-----------------------------------------------------------------------------#

class Genre(models.Model):
    name = models.TextField()

#-----------------------------------------------------------------------------#

class VideoMetadata(models.Model):
    """
    Video metadata holder
    """
    imdb = models.OneToOneField("IMDBMetadata", null=True)
    rotten_tomatoes = models.OneToOneField("RottenTomatoesMetadata", null=True)
    manual = models.OneToOneField("ManualMetadata", null=True)

class VideoMetadataSource(models.Model):
    """
    Abstract base class for storing metadata
    """
    def __unicode__(self): return "%s Metadata" % self.source_name()

    @classmethod
    def source_name(self):
        raise NotImplementedError("the source isn't properly defined")

    class Meta:
        abstract = True

class IMDBMetadata(VideoMetadataSource):
    """
    IMDB sourced metadata
    """
    
    @classmethod
    def source_name(cls):
        return "IMDB"
    
    

    genre = models.ManyToManyField("Genre")
    producers = models.ManyToManyField("Producer")
    plot_summary = models.TextField()
    rating = models.FloatField()

class RottenTomatoesMetadata(VideoMetadataSource):
    """
    RottenTomatoes metadata
    """

    @classmethod
    def source_name(cls):
        return "RottenTomatoes"

    percent_rating = models.IntegerField()
    average_rating = models.FloatField()

class ManualMetadata(VideoMetadataSource):
    """
    Manually entered metadata
    """

    @classmethod
    def source_name(cls):
        return "Manual"

    description = models.TextField()
    

#-----------------------------------------------------------------------------#

class Video(models.Model):
    def __unicode__(self): return self.title

    #--------------------------------- Title ---------------------------------#

    title = models.CharField(max_length=255)

    #--------------------------------- Time ----------------------------------#

    time = models.PositiveIntegerField(help_text="The duration of the video,"
                                       " in seconds.")
    def time_string(self):
        string = str(datetime.timedelta(0, self.time))
        if self.time < 600: return string[3:]
        elif self.time < 3600: return string[2:]
        else: return string
    time_string.short_description = 'time'

    #--------------------------------- Kind ----------------------------------#

    KIND_CHOICES = (('mo', 'movie'),
                    ('tv', 'TV episode'),
                    ('sh', 'short'),
                    ('tr', 'trailer'),
                    ('rc', 'random clip'))

    kind = models.CharField(max_length=2, choices=KIND_CHOICES)

    #------------------------------ Metadata ---------------------------------#
    
    metadata = models.OneToOneField("VideoMetadata")

    #------------------------------ Date Added -------------------------------#

    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    def date_added_string(self): return datetime_string(self.date_added)
    date_added_string.short_description = 'date added'

    #------------------------------ Last Queued ------------------------------#

    last_queued = models.DateTimeField(default=None, blank=True, null=True,
                                       editable=False)
    def last_queued_string(self): return datetime_string(self.last_queued)
    last_queued_string.short_description = 'last queued'

    #------------------------------ Play Count -------------------------------#
    
    play_count = models.IntegerField(editable=False)

    #------------------------------ Download Count ---------------------------#
    
    downloads = models.IntegerField(editable=False)

    #------------------------------ Video Path -------------------------------#

    video = models.FileField(upload_to='venclave/videos/%Y/%m/%d/')

    #------------------------------- Cover Art -------------------------------#

    cover_art = models.ImageField(upload_to='venclave/cover_art/%Y/%m/%d',
                                  blank=True, null=True)

    #--------------------------------- Tags ----------------------------------#

    tags = models.ManyToManyField(Tag, blank=True)

    #-------------------------------- Visible --------------------------------#

    visible = models.BooleanField(default=True, help_text="Non-visible videos"
                                  " do not appear in search results.")

    #------------------------------ Other Stuff ------------------------------#

    class Meta:
        get_latest_by = 'date_added'
        ordering = ('title',)

    @models.permalink
    def get_absolute_url(self):
        return ('django.views.generic.list_detail.object_detail',
                (str(self.id),), {'queryset': Video.objects,
                                  'template_name': 'video_detail.html'})

    def queue_touch(self):
        self.last_queued = datetime.datetime.now()
        self.save()

    objects = models.Manager()
    visibles = VisibleManager()

#-----------------------------------------------------------------------------#

class Chapter(models.Model):
    def __unicode__(self): return self.name

    video = models.ForeignKey(Video, related_name='chapters')

    name = models.CharField(max_length=50)

    time = models.PositiveIntegerField(help_text="The time from the"
                                       " start of the video at which the"
                                       " chapter starts, in seconds.")

    class Meta:
        ordering = ('video', 'time',)
        unique_together = (('video', 'name'),)

#-----------------------------------------------------------------------------#

class Channel(models.Model):
    def __unicode__(self): return self.name

    #-------------------------------- Fields ---------------------------------#

    # For channels, we want the id to be editable, because the channel with
    # id=1 is the default channel.
    id = models.PositiveSmallIntegerField('ID', primary_key=True, help_text=
                                          "The channel with ID=1 will be the"
                                          " default channel.")

    name = models.CharField(max_length=32, unique=True)

    pipe = models.FilePathField(path='/tmp', match="xmms.*", recursive=True,
                                help_text="The path to the XMMS2 control pipe"
                                " for this channel.")

    last_touched = models.DateTimeField(auto_now=True, editable=False)
    def last_touched_timestamp(self):
        return timegm(self.last_touched.timetuple())

    #------------------------------ Other Stuff ------------------------------#

    class Meta:
        get_latest_by = 'last_touched'
        ordering = ('id',)

    @models.permalink
    def get_absolute_url(self):
        return ('menclave.venclave.views.channel_detail', (str(self.id),))

    @classmethod
    def default(cls): return cls.objects.get(pk=1)

    def touch(self):
        self.save()  # `self.last_touched` will auto-update.

    def controller(self): return Controller(self)


# This import goes at the end to avoid circularity.
#from control import Controller

#=============================================================================#
