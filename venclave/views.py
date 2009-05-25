# venclave/views.py

import cjson
import cgi

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _  # For the auth form.
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import select_template
from django.template import Context, RequestContext

from menclave.venclave.models import ContentNode
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
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('venclave-browse'))
    reg_form = VenclaveUserCreationForm()
    if request.method == 'POST':
        # login
        if request.POST['f'] == 'l':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect(reverse('venclave-browse'))
        # register
        elif request.POST['f'] == 'r':
            reg_form = VenclaveUserCreationForm(request.POST)
            if reg_form.is_valid():
                reg_form.save()
                username = reg_form.cleaned_data['username']
                password = reg_form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                login(request, user)
                return HttpResponseRedirect(reverse('venclave-browse'))
    return render_to_response("venclave/index.html",
                              {'reg_form': reg_form})


def words_to_query(query_string):
    """Given a string of words, returns a query for matching each word."""
    full_query = Q()
    query_words = query_string.split()
    for word in query_words:
        word_query = Q()
        for field in ContentNode.searchable_fields():
            # Each word may appear in any field, so we use OR here.
            word_query |= Qu(field, 'icontains', word)
        # Each match must contain every word, so we use AND here.
        full_query &= word_query
    return full_query


def browse_and_update_vals(query, query_string):
    """Compute values common to browse and update_list.

    Returns a dict containing objects useful for browse and update_list.
    """
    nodes = ContentNode.objects.filter(query)
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
    facet_attributes = ContentNode.attributes
    result = browse_and_update_vals(full_query, query_string)
    result.update({'attributes': facet_attributes,
                   'search_query': query_string})
    return render_to_response('venclave/browse.html', result,
                              context_instance=RequestContext(request))


@login_required
def update_list(request):
    facets = cjson.decode(request.POST['f'])
    query_string = request.POST.get('q', '')
    full_query = words_to_query(query_string)
    for facet in facets:
        # Don't apply this filter on reset
        if ('reset' in facet) and facet['reset']:
            continue
        query = Q()
        attribute = ContentNode.attrs_by_name[facet['name']]
        type = attribute.facet_type
        if type == 'slider':
            lo = facet['lo']
            hi = facet['hi']
            query = Qu(attribute.path, 'range', (lo, hi))
        else:
            #kind = 'exact' if type == 'checkbox' else 'icontains'
            kind = 'contains'
            for value in facet['selected']:
                subquery = Qu(attribute.path, kind, value)
                if facet['op'] == "or":
                    query |= subquery
                elif facet['op'] == "and":
                    query &= subquery
                else:
                    raise ValueError, "op must be 'or' or 'and'"
        full_query &= query
    result = browse_and_update_vals(full_query, query_string)
    return HttpResponse(cjson.encode(result))


def create_video_list(nodes):
    """Return the HTML table of the video list.

    We do not use Django templates here because they are *extremely* slow when
    rendered over and over again in a loop.  This optimization may become
    irrelevant when we enable paging, but for now it's a big help.
    """
    html_parts = [LIST_HEADER]
    for node in nodes:
        imdb = node.metadata.imdb
        html_parts.append(LIST_ITEM_TEMPLATE % {
            'id': node.id,
            'icon': reverse("venclave-images",
                            args=["%s_icon.png" % node.kind]),
            'kind': node.kind,
            'title': node.title,
            'length': venclave_tags.mins_to_hours(imdb.length) or '-',
            'year': imdb.release_year or '-',
            'rating': venclave_tags.make_stars(imdb.rating) or '-',
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
    node = ContentNode.objects.get(pk=id);
    t = select_template(['venclave/panes/%s_pane.html' % node.kind,
                         'venclave/panes/default.html'])
    return HttpResponse(t.render(Context({'node': node})))


@login_required
def upload(request):
    return render_to_response('venclave/upload.html',
                              context_instance=RequestContext(request))


def detail(request, id):
    node = get_object_or_404(ContentNode, pk=id)
    return render_to_response('venclave/detail.html',
                              {'node': node})
