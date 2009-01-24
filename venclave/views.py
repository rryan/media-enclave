# venclave/views.py

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

def simple_search(request):
    raise Http404()

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
