# venclave/views.py

from django.http import Http404
from django.shortcuts import render_to_response

from menclave.venclave.models import ContentNode, Director, Genre

def home(request):
    years = [x.year for x in ContentNode.objects.all().order_by('release_date').values_list('release_date',flat=True).distinct()]

    return render_to_response("index.html",
                              {'genres': Genre.objects.all(),
                               'years': years})



def simple_search(request):
    raise Http404()

def content_view(request, id):
    try:
        content = ContentNode.objects.get(pk=id)
    except ContentNode.DoesNotExist:
        raise Http404()

    return render_to_response("content_view.html",
                              {'content': content})

def genres_view(request, ids):
    ids = ids.split(',')
    try:
        genres = Genre.objects.in_bulk(ids)
    except Genre.DoesNotExist:
        raise Http404()

    return render_to_response("genres_view.html",
                              {'genres': genres})

def genre_view(request, id):
    try:
        genre = Genre.objects.get(pk=id)
    except Genre.DoesNotExist:
        raise Http404()

    return render_to_response("genre_view.html",
                              {'genre': genre})

def director_view(request, id):
    try:
        director = Director.objects.get(pk=id)
    except Director.DoesNotExist:
        raise Http404()

    return render_to_response("director_view.html",
                              {'director': director})
