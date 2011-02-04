#!/usr/bin/python

import logging
import os
import urllib
import re

from django.conf import settings
from django.shortcuts import get_object_or_404

from menclave.venclave import models
from menclave.venclave.html import render_to_response


def main(request):
    q = models.ContentNode.with_metadata().order_by('-updated')
    recent_movies = q.filter(kind=models.KIND_MOVIE)[:10]
    recent_tv = q.filter(kind=models.KIND_TV)[:10]
    return render_to_response("venclave/browse.html", request,
                              {'recent_movies': recent_movies,
                               'recent_tv': recent_tv})


def movies(request):
    queryset = models.ContentNode.with_metadata().filter(kind=models.KIND_MOVIE)
    return render_to_response("venclave/simple_movies.html", request,
                              {'nodes': queryset})


def tv(request):
    queryset = models.ContentNode.objects.filter(kind=models.KIND_SERIES)
    return render_to_response("venclave/browse.html", request)


def other(request):
    # TODO
    queryset = models.ContentNode.objects.filter(kind=models.KIND_UNKNOWN)
    return render_to_response("venclave/browse.html", request)


def movie_detail(request, title):
    node = get_object_or_404(models.ContentNode, title=title,
                              kind=models.KIND_MOVIE)
    return generic_detail(request, node)


def generic_detail(request, node):
    return render_to_response("venclave/detail.html", request,
                              {'node': node})
