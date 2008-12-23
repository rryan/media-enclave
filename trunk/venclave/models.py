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

# TODO(rryan) Should we replace this with django-tagging?
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
    """VisibleManager -- manager for getting only visible content"""
    def get_query_set(self):
        return super(VisibleManager, self).get_query_set().filter(visible=True)

#-----------------------------------------------------------------------------#

class Director(models.Model):
    name = models.TextField()

#-----------------------------------------------------------------------------#

class Genre(models.Model):
    name = models.TextField()

#-----------------------------------------------------------------------------#

class ContentMetadata(models.Model):
    """
    Content metadata container
    """
    imdb = models.OneToOneField("IMDBMetadata", null=True)
    rotten_tomatoes = models.OneToOneField("RottenTomatoesMetadata", null=True)
    manual = models.OneToOneField("ManualMetadata", null=True)
    file = models.OneToOneField("FileMetadata", null=True)

#-----------------------------------------------------------------------------#

class ContentMetadataSource(models.Model):
    """
    Abstract base class for storing metadata
    """
    def __unicode__(self): return "%s Metadata" % self.source_name()

    @classmethod
    def source_name(cls):
        raise NotImplementedError("the source isn't properly defined")

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

class IMDBMetadata(ContentMetadataSource):
    """
    IMDB sourced metadata
    """
    
    @classmethod
    def source_name(cls):
        return "IMDB"

    imdb_id = models.CharField(max_length=255, null=True)
    imdb_canonical_title = models.CharField(max_length=1024, null=True)
    genre = models.ManyToManyField("Genre")
    directors = models.ManyToManyField("Director")
    plot_summary = models.TextField()
    rating = models.FloatField()

class RottenTomatoesMetadata(ContentMetadataSource):
    """
    RottenTomatoes metadata
    """

    @classmethod
    def source_name(cls):
        return "RottenTomatoes"

    percent_rating = models.IntegerField()
    average_rating = models.FloatField()

class FileMetadata(ContentMetadataSource):
    """
    File-based metadata
    """

    @classmethod
    def source_name(cls):
        return "File"

    #--------------------------------- Time ----------------------------------#

    time = models.PositiveIntegerField(help_text="The duration of the video,"
                                       " in seconds.")
    def time_string(self):
        string = str(datetime.timedelta(0, self.time))
        if self.time < 600: return string[3:]
        elif self.time < 3600: return string[2:]
        else: return string
    time_string.short_description = 'time'


class ManualMetadata(ContentMetadataSource):
    """
    Manually entered metadata
    """

    @classmethod
    def source_name(cls):
        return "Manual"

    description = models.TextField()
    
#-----------------------------------------------------------------------------#


KIND_TV = 'tv'
KIND_MOVIE = 'mo'
KIND_SERIES = 'se'
KIND_TRAILER = 'tr'
KIND_RANDOMCLIP = 'rc'
KIND_UNKNOWN = 'uk'

class ContentNode(models.Model):
    def __unicode__(self): return self.full_name()

    #--------------------------------- Kind ----------------------------------#
    
    # Nodes can have different kinds.
    KIND_CHOICES = ((KIND_MOVIE, 'movie'),
                    (KIND_TV, 'TV episode'),
                    (KIND_SERIES, 'TV series'),
                    (KIND_TRAILER, 'trailer'),
                    (KIND_RANDOMCLIP, 'random clip'),
                    (KIND_UNKNOWN, 'unknown'))

    kind = models.CharField(max_length=2, choices=KIND_CHOICES)

    #--------------------------------- Title ---------------------------------#

    title = models.CharField(max_length=1024, null=True)

    # only applicable for kind=='tv', null if not applicable
    season = models.IntegerField(null=True)
    episode = models.IntegerField(null=True)

    def simple_name(self):
        return self.title

    def compact_name(self):
        if self.kind == 'tv':
            return "%s S%2dE%2d" % (self.title, self.season, self.episode)
        return self.title

    def full_name(self):
        if self.kind == 'tv':
            return "%s Season %2d Episode %2d" % (self.title, self.season, self.episode)
        return self.title

    def fully_qualified_name(self):
        if self.parent:
            return "%s > %s" % (self.parent.fully_qualified_name(), self.compact_name())
        else:
            return self.compact_name()


    #--------------------------------- Release Date --------------------------#

    release_date = models.DateTimeField(null=True)

    #--------------------------------- Parent Node ---------------------------#

    parent = models.ForeignKey("ContentNode", null=True)

    #--------------------------------- Content Metadata ----------------------#

    metadata = models.OneToOneField("ContentMetadata")

    #--------------------------------- Content Path --------------------------#

    path = models.FilePathField(path='venclave/content/',
                                recursive=True,
                                blank=True,
                                max_length=512)

    #------------------------------ Content File------------------------------#
        
    content = models.FileField(upload_to='venclave/content/')

    #------------------------------- Cover Art -------------------------------#

    cover_art = models.ImageField(upload_to='venclave/cover_art/%Y/%m/%d',
                                  blank=True, null=True)

    #------------------------------ Download Count ---------------------------#
    
    downloads = models.IntegerField(editable=False)

    #--------------------------------- Tags ----------------------------------#

    tags = models.ManyToManyField(Tag, blank=True)

    #--------------------------------- Timestamps ----------------------------#

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    def date_added_string(self): return datetime_string(self.created)
    date_added_string.short_description = 'date added'

    #-------------------------------- Visible --------------------------------#

    visible = models.BooleanField(default=True, help_text="Non-visible content"
                                  " does not appear in search results.")

    objects = models.Manager()
    visibles = VisibleManager()

    #------------------------------ Other Stuff ------------------------------#

    class Meta:
        get_latest_by = 'created'
        ordering = ('title',)

    @models.permalink
    def get_absolute_url(self):
        return ('django.views.generic.list_detail.object_detail',
                (str(self.id),), {'queryset': ContentNode.objects,
                                  'template_name': 'content_detail.html'})


#-----------------------------------------------------------------------------#

class Chapter(models.Model):
    def __unicode__(self): return self.name

    content = models.ForeignKey("ContentNode", related_name='chapters')

    name = models.CharField(max_length=50)

    time = models.PositiveIntegerField(help_text="The time from the"
                                       " start of the video at which the"
                                       " chapter starts, in seconds.")

    class Meta:
        ordering = ('content', 'time',)
        unique_together = (('content', 'name'),)

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

#=============================================================================#
