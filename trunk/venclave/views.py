# venclave/views.py
import cjson
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import get_template, select_template
from django.template import Context, RequestContext


from menclave.venclave.models import ContentNode, Director, Genre

def home(request):
    reg_form = UserCreationForm()
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
            reg_form = UserCreationForm(request.POST)
            if reg_form.is_valid():
                reg_form.save()
                username = reg_form.cleaned_data['username']
                password = reg_form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                login(request,user)
                return HttpResponseRedirect(reverse('venclave-browse'))
    return render_to_response("venclave/index.html",
                              {'reg_form': reg_form})

def Qu(field, op, value):
    return Q(**{(str(field) + '__' + str(op)): str(value)})

@login_required
def browse(request):
    # Process search query
    form = request.GET
    query_string = form.get('q', '')
    query_words = query_string.split()
    full_query = Q()
    for word in query_words:
        word_query = Q()
        for field in ContentNode.searchable_fields():
            # WTF Each word may appear in any field, so we use OR here.
            word_query |= Qu(field, 'icontains', word)
        # WTF Each match must contain every word, so we use AND here.
        full_query &= word_query
    trees = ContentNode.trees.filter(full_query)
    facet_attributes = ContentNode.attributes.all()
    return render_to_response('venclave/browse.html',
                              {'attributes': facet_attributes,
                               'list': create_video_list(trees),
                               'search_query': query_string},
                              context_instance=RequestContext(request))

@login_required
def update_list(request):
    facets = cjson.decode(request.POST['f'])
    full_query = Q()
    for name in facets:
        facet = facets[name]
        attribute = ContentNode.attributes.attributes[name]
        type = attribute.facet_type
        query = Q()
        if type == 'slider':
            lo = str(datetime(facet['lo'],1,1))+"00:00"
            hi = str(datetime(facet['hi'],12,31))+"00:00"
            query = Qu(attribute.path, 'range', (lo, hi))
        else:
            kind = 'exact' if type == 'checkbox' else 'icontains'
            for value in facet['selected']:
                subquery = Qu(attribute.path, kind, value)
                if facet['op'] == "or":
                    query |= subquery
                elif facet['op'] == "and":
                    query &= subquery
                else:
                    raise ValueException, "op must be 'or' or 'and'"
        full_query &= query
    trees = ContentNode.trees.filter(full_query)
    return HttpResponse(create_video_list(trees))

def create_video_list(trees):
    html = create_video_list_lp(trees)
    t = get_template('venclave/list_event_binding.html')
    html += t.render(Context())
    return html

def create_video_list_lp(trees):
    html = []
    templates = {} # kind->template
    for node, children in trees:
        t = templates.setdefault(node.kind,
                                 select_template(['list_items/kind_%s.html' % node.kind,
                                                  'list_items/default.html']))
        c = Context({'node': node})
        if children:
            c['sublist'] = create_video_list_lp(children)
        else:
            c['sublist'] = None
        html.append(t.render(c))
    return ''.join(html)

@login_required
def get_pane(request):
    id = request.GET['id']
    node = ContentNode.objects.get(pk=id);
    t = select_template(['venclave/panes/%s_pane.html' % node.kind,
                         'venclave/panes/default.html'])
    return HttpResponse(t.render(Context({'node': node})))

@login_required
def upload(request):
    return render_to_response('venclave/upload.html')
