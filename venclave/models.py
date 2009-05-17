# menclave/venclave/models.py

import datetime

from django.db import models
from django.db.models import Min, Max
from django.db.models import Q

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

class TreeManager(models.Manager):

    def root_nodes(self):
        return super(TreeManager, self).get_query_set().filter(parent__isnull=True)

    def leaf_nodes(self):
        return super(TreeManager, self).get_query_set().filter(
            Q(kind='movie') | Q(kind='TV episode'))

    def fringe(self, tree):
        if not tree[1]:
            return [tree[0]]
        else:
            fringe = []
            for subtree in tree[1]:
                fringe += self.fringe(subtree)
            return fringe

    def treeify(self, query_set):
        roots = []
        trees = {} # root->tree

        for node in query_set:
            # Expand all descendants
            tree = self.expand(node)
            while node not in trees:
                trees[node] = tree
                # Is node a root?
                if not node.parent:
                    roots.append(tree)
                    break
                # Traverse up branch
                node = node.parent
                tree = (node, [tree])
            else:
                old_tree = trees[node]
                # Node is the same, update children
                old_tree[1] = tree[1]
        return roots

    # Todo: make more like order_by
    def sort_trees(self, trees, key=(lambda node: node.title), reverse=False):
        trees.sort(key=lambda tree: key(tree[0]), reverse=reverse)
        for tree in trees:
            self.sort_trees(tree[1], key, reverse)

    def expand(self, node):
        if node.kind == "movie":
            return [node, []]
        children = node.children.all()
        return [node, [self.expand(child) for child in children]]

    # Warning! Returns a list of trees, not a query
    def all(self):
        roots = self.root_nodes()
        return [self.expand(node) for node in roots]

    # Warning! Returns a list of trees, not a query
    def filter(self, *args, **kwargs):
        order_by = None
        if 'order_by' in kwargs:
            order_by = kwargs['order_by']
            del kwargs['order_by']
        query_set = super(TreeManager,self).filter(*args, **kwargs).select_related('metadata__imdb')
        trees = self.treeify(query_set)
        if order_by:
            trees = self.sort_trees(trees, order_by)
        return trees

class AttributesManager(models.Manager):
    def all(self):
        return [self.attributes[a] for a in self.attribute_order]

    class Attribute(object):
        def __init__(self, name, path, facet_type, get_choices):
            self.name = name
            self.path = path # string specifying field in querysets
                             # relative to ContentNode
            self.facet_type = facet_type
            self.get_choices = get_choices

    attribute_order = ('Type', 'Genre', 'Rating', 'Year', 'Director')

    attributes = {"Genre":
                  Attribute("Genre",
                            "metadata__imdb__genres__name",
                            "checkbox",
                            lambda: [(g.name,g.name) for g in Genre.objects.order_by('name')]),
                  "Actor":
                  Attribute("Actor",
                            "metadata__imdb__actors__name",
                            "searchbar",
                            lambda: Actor.objects.order_by('name')),
                  "Director":
                  Attribute("Director",
                            "metadata__imdb__directors__name",
                            "searchbar",
                            lambda: Director.objects.order_by('name')),
                  "Type":
                   Attribute("Type",
                             "kind",
                             "checkbox",
                             lambda: [('movie', 'Movie'), ('TV episode', 'TV')]),
                  "Year":
                  Attribute("Year",
                            "metadata__imdb__release_year",
                            "slider",
                            lambda: IMDBMetadata.objects.aggregate(min=Min('release_year'),
                                                                   max=Max('release_year'))),
                  "Rating":
                  Attribute("Rating",
                            "metadata__imdb__rating",
                            "slider",
                            lambda: {'min':0, 'max':5})
                  }


#-----------------------------------------------------------------------------#

class Director(models.Model):
    name = models.TextField(primary_key=True)

    def __unicode__(self):
        return self.name

#-----------------------------------------------------------------------------#

class Actor(models.Model):
    name = models.TextField(primary_key=True)

    def __unicode__(self):
        return self.name

#-----------------------------------------------------------------------------#

class Genre(models.Model):
    name = models.TextField(primary_key=True)

    def __unicode__(self):
        return self.name

#-----------------------------------------------------------------------------#

class ContentMetadata(models.Model):
    """
    Content metadata container
    """
    imdb = models.ForeignKey("IMDBMetadata", blank=True, null=True)
    rotten_tomatoes = models.ForeignKey("RottenTomatoesMetadata",
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

    #created = models.DateTimeField(auto_now_add=True, editable=False)
    #updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

class IMDBMetadata(ContentMetadataSource):
    """
    IMDB sourced metadata
    """

    @classmethod
    def source_name(cls):
        return "IMDB"

    imdb_id = models.CharField(max_length=255, null=True, blank=True)
    imdb_canonical_title = models.CharField(max_length=1024, null=True, primary_key = True)
    release_date = models.DateTimeField(blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    genres = models.ManyToManyField("Genre") # TODO - rename to genres
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
KIND_SEASON = 'sn'
KIND_TRAILER = 'tr'
KIND_RANDOMCLIP = 'rc'
KIND_UNKNOWN = 'uk'

class ContentNode(models.Model):

    owner = models.ForeignKey('auth.User')

    objects = models.Manager()
    trees = TreeManager()
    attributes = AttributesManager()

    def __unicode__(self): return self.compact_name()

    KIND_CHOICES = ((KIND_MOVIE, 'movie'),
                    (KIND_TV, 'TV episode'),
                    (KIND_SERIES, 'TV series'),
                    (KIND_SEASON, 'TV season'),
                    (KIND_TRAILER, 'trailer'),
                    (KIND_RANDOMCLIP, 'random clip'),
                    (KIND_UNKNOWN, 'unknown'))

    kind = models.CharField(default=KIND_UNKNOWN,
                            max_length=2,
                            choices=KIND_CHOICES)

    title = models.CharField(max_length=1024)

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

    parent = models.ForeignKey("self", related_name="children",
                               blank=True, null=True)

    metadata = models.OneToOneField("ContentMetadata")


    #--------------------------------- Content Path --------------------------#
    #TODO (jslocum) Path needs to be an absolute path.
    path = models.FilePathField(path='venclave/content/',
                                recursive=True,
                                blank=True,
                                max_length=512)

    #------------------------------- Cover Art -------------------------------#

    cover_art = models.ImageField(upload_to='venclave/cover_art/%Y/%m/%d',
                                  blank=True,
                                  null=True)

    #------------------------------ Download Count ---------------------------#

    downloads = models.IntegerField(default=0, editable=False)


    #--------------------------------- Tags ----------------------------------#

    tags = models.ManyToManyField(Tag, blank=True)

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
        return ('title', 'metadata__imdb__directors__name', 'metadata__imdb__actors__name')
