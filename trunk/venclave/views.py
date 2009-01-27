# venclave/views.py

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render_to_response

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

def simple_search(request):
    form = request.GET
    # Get the query.
    query_string = form.get('q','')
    query_words = query_string.split()
    if not query_words:
        queryset = ()
        query_string = ''
    else:
        full_query = Q()
        for word in query_words:
            word_query = Q()
            for field in ContentNode.searchable_fields():
                # WTF Each word may appear in any field, so we use OR here.
                word_query |= Qu(field, 'icontains', word)
            # WTF Each match must contain every word, so we use AND here.
            full_query &= word_query
        queryset = ContentNode.visibles.filter(full_query)
    return render_to_response('venclave/search_results.html',
                              {'videos':queryset,
                               'search_query':query_string})


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
