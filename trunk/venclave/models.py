# menclave/venclave/models.py

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

class RootNodesManager(models.Manager):
    """
    Manager to access only root nodes (i.e. those that should be
    initially displayed -- movies, tv shows (not episodes), etc.)
    """
    def get_query_set(self):
        return super(VideosManager, self).get_query_set().filter(parent__isnull=True)

#-----------------------------------------------------------------------------#

class Director(models.Model):
    name = models.TextField()

#-----------------------------------------------------------------------------#

class Genre(models.Model):
    name = models.TextField()

#-----------------------------------------------------------------------------#

class Actor(models.Model):
    name = models.TextField()

#-----------------------------------------------------------------------------#

class ContentMetadata(models.Model):
    """
    Content metadata container
    """
    imdb = models.OneToOneField("IMDBMetadata", blank=True, null=True)
    rotten_tomatoes = models.OneToOneField("RottenTomatoesMetadata",
                                           blank=True, null=True)
    manual = models.OneToOneField("ManualMetadata", blank=True, null=True)
    file = models.OneToOneField("FileMetadata", blank=True, null=True)

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
    release_date = models.DateTimeField(blank=True, null=True)
    genre = models.ManyToManyField("Genre") # TODO - rename to genres
    directors = models.ManyToManyField("Director")
    actors = models.ManyToManyField("Actor")
    plot_summary = models.TextField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)

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

class ManualMetadata(ContentMetadataSource):
    """
    Manually entered metadata
    """

    @classmethod
    def source_name(cls):
        return "Manual"

    description = models.TextField()

class VideoFile(models.Model):
    
    file = models.FileField(upload_to='venclave/content')
    parent = models.ForeignKey('ContentNode')


KIND_TV = 'tv'
KIND_MOVIE = 'mo'
KIND_SERIES = 'se'
KIND_TRAILER = 'tr'
KIND_RANDOMCLIP = 'rc'
KIND_UNKNOWN = 'uk'

class ContentNode(models.Model):

    owner = models.ForeignKey('auth.User')

    objects = models.Manager()
    root_nodes = RootNodesManager()

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
    season = models.IntegerField(blank=True, null=True)
    episode = models.IntegerField(blank=True, null=True)

    def simple_name(self):
        return self.title

    def compact_name(self):
        if self.kind == 'tv':
            return "%s S%2dE%2d" % (self.title, self.season, self.episode)
        return self.title

    def full_name(self):
        if self.kind == KIND_TV:
            return ("%s Season %2d Episode %2d" %
                    (self.title, self.season, self.episode))
        elif self.kind == KIND_MOVIE:
            return "%s (%d)" % (self.title, self.release_date.year)
        return self.title

    def fully_qualified_name(self):
        if self.parent:
            return "%s > %s" % (self.parent.fully_qualified_name(),
                                self.compact_name())
        else:
            return self.compact_name()

    #--------------------------------- Parent Node ---------------------------#

    parent = models.ForeignKey("ContentNode", related_name="children",
                               blank=True, null=True)

    #--------------------------------- Content Metadata ----------------------#

    metadata = models.OneToOneField("ContentMetadata")

    #--------------------------------- Tags ----------------------------------#

    tags = models.ManyToManyField(Tag, blank=True)

    #--------------------------------- Timestamps ----------------------------#

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    def date_added_string(self): return datetime_string(self.created)
    date_added_string.short_description = 'date added'

    #------------------------------ Other Stuff ------------------------------#

    class Meta:
        get_latest_by = 'created'
        ordering = ('title',)

    @models.permalink
    def get_absolute_url(self):
        return ('django.views.generic.list_detail.object_detail',
                (str(self.id),), {'queryset': ContentNode.objects,
                                  'template_name': 'content_detail.html'})

    @classmethod
    def searchable_fields(cls):
        # TODO(rnk): Expand this to include the rest of the metadata.
        return ('title', 'season', 'episode')


