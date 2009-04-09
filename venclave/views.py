# venclave/views.py

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.loader import select_template
from django.template import Context


from menclave.venclave.models import ContentNode, Director, Genre

def home(request):
    nodes = ContentNode.objects.all().order_by('release_date')
    nodes = nodes.values_list('release_date',flat=True).distinct()
    years = [x.year for x in nodes]

    return render_to_response("venclave/index.html",
                              {'genres': Genre.objects.all(),
                               'years': years})

def Qu(field, op, value):
    return Q(**{(str(field) + '__' + str(op)): str(value)})

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
    return render_to_response('venclave/browse.html',
                              {'list': create_video_list(trees),
                               'search_query': query_string})

def create_video_list(trees):
    html = []
    templates = {} # kind->template
    for node, children in trees:
        t = templates.setdefault(node.kind,
                                 select_template(['list_items/kind_%s.html' % node.kind,
                                                  'list_items/default.html']))
        c = Context({'node': node})
        if children:
            c['sublist'] = create_video_list(children)
        else:
            c['sublist'] = None
        html.append(t.render(c))
    return ''.join(html)

def upload(request):
    pass

def content_view(request, id):
    try:
        content = ContentNode.objects.get(pk=id)
    except ContentNode.DoesNotExist:
        raise Http404()

    return render_to_response("venclave/content_view.html",
                              {'content': content})

def genres_view(request, ids):
    ids = ids.split(',')
    try:
        genres = Genre.objects.in_bulk(ids)
    except Genre.DoesNotExist:
        raise Http404()

    return render_to_response("venclave/genres_view.html",
                              {'genres': genres})

def genre_view(request, id):
    try:
        genre = Genre.objects.get(pk=id)
    except Genre.DoesNotExist:
        raise Http404()

    return render_to_response("venclave/genre_view.html",
                              {'genre': genre})

def director_view(request, id):
    try:
        director = Director.objects.get(pk=id)
    except Director.DoesNotExist:
        raise Http404()

    return render_to_response("venclave/director_view.html",
                              {'director': director})
