# venclave/views.py

import cgi
import json
import logging
import re

from django import forms
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import Context, RequestContext
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _  # For the auth form.

from menclave.venclave.html import render_to_response
from menclave.venclave.models import ContentNode, KIND_MOVIE, KIND_SERIES, KIND_SEASON
from menclave.venclave.templatetags import venclave_tags


class VenclaveUserCreationForm(auth_forms.UserCreationForm):

    """We subclass the default user creation form to change the text labels."""

    username = forms.RegexField(label=_("username"), max_length=30,
                                regex=r'^\w+$',
                                help_text = _("Required. 30 characters or "
                                              "fewer. Alphanumeric characters "
                                              "only (letters, digits and "
                                              "underscores)."),
                                error_message = _("This value must contain "
                                                  "only letters, numbers and "
                                                  "underscores."))
    password1 = forms.CharField(label=_("password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("retype password"),
                                widget=forms.PasswordInput)


def Qu(field, op, value):
    return Q(**{(str(field) + '__' + str(op)): value})


def home(request):
    browse_redirect = HttpResponseRedirect(reverse('venclave-browse'))
    # If already authenticated, go right in.
    if request.user.is_authenticated():
        return browse_redirect

    ## If SSL auth works, go right in.
    #user = auth.authenticate(request=request)
    #if user:
        #auth.login(request, user)
        #logging.info("User %s logged in via SSL", user.username)
        #return browse_redirect

    reg_form = VenclaveUserCreationForm()
    if request.method == 'POST':
        # login
        if request.POST.get('f') == 'l':
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                logging.info("User %s logged in via password", user.username)
                return browse_redirect
        # register
        elif settings.VENCLAVE_ALLOW_REGISTRATION and request.POST['f'] == 'r':
            reg_form = VenclaveUserCreationForm(request.POST)
            if reg_form.is_valid():
                reg_form.save()
                username = reg_form.cleaned_data['username']
                password = reg_form.cleaned_data['password1']
                user = auth.authenticate(username=username, password=password)
                auth.login(request, user)
                return browse_redirect
    return render_to_response("venclave/index.html", request,
                              {'reg_form': reg_form, 'settings': settings})


def words_to_query(query_string):
    """Given a string of words, returns a query for matching each word."""
    full_query = Q()
    query_words = query_string.split()
    for word in query_words:
        word_query = Q()
        for field in ContentNode.SEARCHABLE_FIELDS:
            # Each word may appear in any field, so we use OR here.
            word_query |= Qu(field, 'icontains', word)
        # Each match must contain every word, so we use AND here.
        full_query &= word_query
    return full_query


def browse_and_update_vals(nodes, query_string):
    """Compute values common to browse and update_list.

    Returns a dict containing objects useful for browse and update_list.
    """
    nodes = nodes.select_related('metadata__imdb')
    video_list = create_video_list(nodes)
    video_count = ContentNode.objects.all().count()
    results_count = nodes.count()
    return {
        'videolist': video_list,
        'banner_msg': banner_msg(video_count, results_count, query_string),
    }


@login_required
def browse(request):
    # Process search query
    form = request.GET
    query_string = form.get('q', '')
    full_query = words_to_query(query_string)
    nodes = ContentNode.objects.filter(full_query)
    facet_attributes = ContentNode.attributes
    result = browse_and_update_vals(nodes, query_string)
    result.update({'attributes': facet_attributes,
                   'search_query': query_string})
    return render_to_response('venclave/browse.html', request, result,
                              context_instance=RequestContext(request))

def exhibit(request):
    result = {'settings': settings}
    return render_to_response('venclave/exhibit.html', request, result,
                              context_instance=RequestContext(request))

def exhibit_history(request):
    return HttpResponse('<html><body></body></html>')

def exhibit_content_dbg(request):
    """Handler for debugging the performance of the exhibit_content handler.

    The debug toolbar looks for the </body> to insert itself into, so we just
    wrap the JSON with html and body tags.  Kill this off once exhibit_content
    uses a constant number of queries.
    """
    content = exhibit_content(request).content
    return HttpResponse('<html><body>' + content + '</body></html>')

# TODO(rnk): Move the json mimetype stuff back up out of aenclave so we can
# reuse it for this request.
# TODO(rnk): select_related doesn't work for ManyToMany relationships.  We
# could really speed this query up if we didn't do ~6000 SQL queries for
# actors, directors, and genres.  Writing this in straight SQL may be too hard,
# so we may have to resort to just loading all role and genre models into
# memory, and building a dict mapping from movie id to lists of models.
def exhibit_content(request):
    content_nodes = ContentNode.with_metadata(
        ).filter(kind__in=[KIND_MOVIE, KIND_SERIES])
    kinds = {KIND_MOVIE: 'Movie',
             KIND_SERIES: 'TV Show',}
    items = []
    titleyearPattern = re.compile("^(.*) \((\d{4})\)$")

    # for i in range(15):
    #     items.append({'type': 'Season',
    #                   'label': ,
    #                   'Label': 'Season %d' % (i+1),
    #                   'href': '/tvseasons'})


    for node in content_nodes:
        name = node.simple_name()
        item = {'type': kinds.get(node.kind, 'Unknown'),
                'label': node.simple_name(),
                'DateAdded': str(node.created),
                'Title': node.simple_name(),
                'Year': '',
                }
        missing = []

        match = titleyearPattern.search(name)
        if match:
            item['Title'] = match.group(1)
            item['Year'] = match.group(2)


        is_tv_series = node.kind == KIND_SERIES
        is_movie = node.kind == KIND_MOVIE

        if is_tv_series:
            seasons = []

            for child in node.children.all():
                seasons.append({'type': 'Season',
                                'label': str(child.id),
                                'title': child.title,
                                'link': '<a href="%s">%s</a>' % ('/foolio', child.title),
                                'href': '/tvseasons/%d' % child.id})
            items.extend(seasons)

            item['Seasons'] = [str(child.id) for child in node.children.all() if child.kind == KIND_SEASON]
            # item['Seasons'] = [{'type': 'Season',
            #                     'label': child.title,
            #                     'href': '/tvseasons'}
            #                    for child in node.children.all() if child.kind == KIND_SEASON]

        item['DL'] = node.downloads

        metadata = node.metadata
        imdb = metadata.imdb if metadata else None
        rt = metadata.rotten_tomatoes if metadata else None
        mc = metadata.metacritic if metadata else None

        if metadata and metadata.nyt_review:
            item['NYTReviewURL'] = metadata.nyt_review
        else:
            missing.append('NYTReviewURL')

        if imdb:
            imdb = node.metadata.imdb
            item['IMDbURL'] = 'http://www.imdb.com/title/tt%s' % imdb.imdb_id
            item['IMDbGenres'] = [genre.name for genre in imdb.genres.all()]

            if imdb.rating is not None:
                item['IMDbRating'] = imdb.rating
            else:
                missing.append('IMDbRating')

            if imdb.length is not None:
                item['IMDbRuntime'] = imdb.length
            else:
                missing.append('IMDbRuntime')

            if imdb.plot_outline is not None:
                item['IMDbPlotOutline'] = imdb.plot_outline
            else:
                missing.append('IMDbPlotOutline')

            item['IMDbGenres'] = [genre.name for genre in imdb.genres.all()]
            item['IMDbDirectors'] = [director.name for director in imdb.directors.all()]

            # Limit to top 4

            item['IMDbActors'] = [actor.name for actor in imdb.actors.all()][:4]

            # Don't provide it if we don't have any. It's easier to check after
            # the query.
            if len(item['IMDbActors']) == 0:
                del item['IMDbActors']

            if imdb.thumb_image:
                item['ThumbURL'] = imdb.thumb_image.url

            # if imdb.thumb_uri is not None:
            #     item['ThumbURL'] = imdb.thumb_uri
            #     item['ThumbWidth'] = imdb.thumb_width
            #     item['ThumbHeight'] = imdb.thumb_height
        else:
            missing.append('IMDbURL')

        if rt:
            item['RTURL'] = rt.rt_uri

            # Prefer IMDb (local) thumbnails.
            if rt.thumb_uri and 'ThumbURL' not in item:
                item['ThumbURL'] = rt.thumb_uri
                # item['ThumbWidth'] = rt.thumb_width
                # item['ThumbHeight'] = rt.thumb_height

            if rt.top_critics_percent:
                item['RTRating'] = rt.top_critics_percent


                if rt.top_critics_fresh is None:
                    item['RTST'] = 'n'
                elif rt.top_critics_fresh is True:
                    item['RTST'] = 'f'
                else:
                    item['RTST'] = 'r'
            elif rt.all_critics_percent:
                item['RTRating'] = rt.all_critics_percent
                if rt.all_critics_fresh is None:
                    item['RTST'] = 'n'
                elif rt.all_critics_fresh is True:
                    item['RTST'] = 'f'
                else:
                    item['RTST'] = 'r'
            else:
                item['RTST'] = 'n'
                missing.append('RTRating')
        else:
            missing.append('RTURL')

        if mc:
            item['MCURL'] = 'http://www.metacritic.com%s' % mc.mc_uri
            if mc.score:
                item['MCRating'] = mc.score
            else:
                missing.append('MCRating')
            if mc.status:
                if mc.status == 'tbd':
                    item['MCST'] = 'n'
                elif mc.status in ['terrible', 'unfavorable']:
                    item['MCST'] = 'u'
                elif mc.status in ['mixed']:
                    item['MCST'] = 'm'
                elif mc.status in ['favorable', 'outstanding']:
                    item['MCST'] = 'f'
            else:
                item['MCST'] = 'n'
        else:
            missing.append('MCURL')

        item['Missing'] = missing
        items.append(item)

    properties = {
        'Title': { 'valueType': 'text' },
        'Year': { 'valueType': 'number' },
        'Seasons': { 'valueType': 'item' },
        'ThumbURL': { 'valueType': 'url' },
        'ThumbWidth': { 'valueType': 'number' },
        'ThumbHeight': { 'valueType': 'number' },
        'IMDbRating': { 'valueType': 'number', 'label': 'IMDb User Rating' },
        'IMDbURL': { 'valueType': 'url', 'label': 'IMDb URL' },
        'IMDbGenres': { 'valueType': 'text', 'label': 'Genres' },
        'IMDbDirectors': { 'valueType': 'text', 'label': 'Directors' },
        'IMDbActors': { 'valueType': 'text', 'label': 'Actors' },
        'IMDbRuntime': { 'valueType': 'number', 'label': 'Runtime' },
        'IMDbReleaseDate': { 'valueType': 'date', 'label': 'Release Date' },
        'IMDbAKA': { 'valueType': 'text', 'label': 'Alternate Titles' },
        'IMDbProduction': { 'valueType': 'text', 'label': 'Production Companies' },
        'IMDbPlotOutline': { 'valueType': 'text', 'label': 'Plot Outline' },
        'RTRating': { 'valueType': 'number', 'label': 'RottenTomatoes Rating' },
        'RTURL': { 'valueType': 'url', 'label': 'RottenTomatoes URL' },
        'RTActors': { 'valueType': 'text', 'label': 'Actors' },
        'RTDirectors': { 'valueType': 'text', 'label': 'Directors' },
        'RTWriters': { 'valueType': 'text', 'label': 'Writers' },
        'RTST': { 'valueType': 'text', 'label': 'RottenTomatoes Status'},
        'RTBoxOffice': { 'valueType': 'number', 'label': 'Box Office' },
        'MCURL': { 'valueType': 'url', 'label':' MetaCritic URL' },
        'MCRating': { 'valueType': 'number', 'label': 'Metacritic Rating' },
        'MCST': { 'valueType': 'text', 'label': 'Metacritic Status' },
        'MCNA': { 'valueType': 'boolean', 'label': 'MC No Rating' },
        'NYTReviewURL': { 'valueType': 'url', 'label': 'NYT Review URL' },
        'DateAdded': { 'valueType': 'date', 'label': 'Date Added' },
        'DL': { 'valueType': 'number', 'label': 'Downloads' },
        'Random': { 'valueType': 'number', 'label': 'Random' },
        'Missing': { 'valueType': 'text', 'label': 'Missing Fields' },
        }

    types = {
        'Movie': { 'pluralLabel': 'Movies' },
        'TV Show': { 'pluralLabel': 'TV Shows' },
        'Season': { 'pluralLabel': 'Seasons' },
    }

    result = {'types': types,
              'properties': properties,
              'items': items }

    return HttpResponse(json.dumps(result, indent=2))



@login_required
def update_list(request):
    facets = json.loads(request.POST['f'])
    query_string = request.POST.get('q', '')
    word_query = words_to_query(query_string)
    nodes = ContentNode.objects.filter(word_query)
    for facet in facets:
        # Don't apply this filter on reset
        if facet.get('reset', False):
            continue
        query = Q()
        attribute = ContentNode.attrs_by_name[facet['name']]
        type = attribute.facet_type
        if type == 'slider':
            lo = facet['lo']
            hi = facet['hi']
            query = Qu(attribute.path, 'range', (lo, hi))
            nodes = nodes.filter(query)
        elif facet['op'] == 'or':
            #kind = 'exact' if type == 'checkbox' else 'icontains'
            kind = 'contains'
            for value in facet['selected']:
                subquery = Qu(attribute.path, kind, value)
                query |= subquery
            nodes = nodes.filter(query)
        elif facet['op'] == 'and':
            # Build up a recursive 'IN' queryset.  This is the only way we
            # could figure out how to implement 'AND'ing.
            # TODO(rnk): Evaluate the performance of these queries.  The Django
            # docs recommend doing two queries instead of one for MySQL.
            kind = 'contains'
            # We do this whole dance with next_nodes to reduce the nesting
            # level of 'IN' filters on the 'nodes' queryset.
            next_nodes = nodes
            for value in facet['selected']:
                nodes = next_nodes
                subquery = Qu(attribute.path, kind, value)
                nodes = nodes.filter(subquery)
                pks = nodes.values('pk')
                next_nodes = ContentNode.objects.filter(pk__in=pks)
        else:
            raise ValueError("op must be 'slider', 'or', or 'and'")
    result = browse_and_update_vals(nodes, query_string)
    return HttpResponse(json.dumps(result))


def create_video_list(nodes):
    """Return the HTML table of the video list.

    We do not use Django templates here because they are *extremely* slow when
    rendered over and over again in a loop.  This optimization may become
    irrelevant when we enable paging, but for now it's a big help.
    """
    html_parts = [LIST_HEADER]
    for node in nodes:
        imdb = node.metadata and node.metadata.imdb
        html_parts.append(LIST_ITEM_TEMPLATE % {
            'id': node.id,
            'icon': reverse("venclave-images",
                            args=["%s_icon.png" % node.kind]),
            'kind': node.kind,
            'title': node.title,
            'length': imdb and venclave_tags.mins_to_hours(imdb.length) or '-',
            'year': imdb and imdb.release_year or '-',
            'rating': imdb and venclave_tags.make_stars(imdb.rating) or '-',
        })
    html_parts.append(LIST_FOOTER)
    return ''.join(html_parts)


LIST_HEADER = """\
<table id="video-list" cellspacing="0" cellpadding="0">
  <thead>
    <tr>
      <th class="item-icon"></th>
      <th class="item-arrow"></th>
      <th class="item-title">title</th>
      <th class="item-length">length</th>
      <th class="item-release">year</th>
      <th class="item-rating">rating</th>
    </tr>
  </thead>
  <tbody id="list-body" class="list-body">
"""


LIST_FOOTER = """\
  </tbody>
</table>
"""


LIST_ITEM_TEMPLATE = """\
<tr id1="%(id)s">
  <td class="item-icon">
    <img src="%(icon)s" alt="%(kind)s"/>
  </td>
  <td class="item-arrow">
  </td>
  <td class="item-title">
    <a href="#" class="leaf"
      onclick="return venclave.videolist.title_onclick(this)">%(title)s</a>
  </td>
  <td class="item-length">
    %(length)s
  </td>
  <td class="item-release">
    %(year)s
  </td>
  <td class="item-rating">
    %(rating)s
  </td>
</tr>
"""


def banner_msg(video_count, results_count, search_string):
    msg = ''
    if video_count != results_count:
        msg += '%s results in ' % results_count
    msg += '%s videos' % video_count
    if search_string:
        msg += ' for "%s"' % cgi.escape(search_string)
    return msg


@login_required
def get_pane(request):
    id = request.GET['id']
    node = ContentNode.objects.get(pk=id)
    t = select_template(['venclave/panes/%s_pane.html' % node.kind,
                         'venclave/panes/default.html'])
    return HttpResponse(t.render(Context({'node': node})))


@login_required
def upload(request):
    return render_to_response('venclave/upload.html', request,
                              context_instance=RequestContext(request))


def detail(request, id):
    node = get_object_or_404(ContentNode, pk=id)
    return render_to_response('venclave/detail.html', request,
                              {'node': node})
