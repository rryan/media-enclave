#!/usr/bin/python

import logging
import os
import urllib
import re

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404

from menclave.venclave import models
from menclave.venclave import views


def main(request):
    return render_to_response("venclave/browse.html",
                              {'request': request,
                               'settings': settings})


def movies(request):
    queryset = models.ContentNode.with_metadata().filter(kind=models.KIND_MOVIE)
    return render_to_response("venclave/simple_movies.html",
                              {'request': request,
                               'nodes': queryset,
                               'settings': settings})


def tv(request):
    queryset = models.ContentNode.objects.filter(kind=models.KIND_SERIES)
    return render_to_response("venclave/browse.html",
                              {'request': request,
                               'settings': settings})


def other(request):
    queryset = models.ContentNode.objects.filter(kind=models.KIND_UNKNOWN)
    return render_to_response("venclave/browse.html",
                              {'request': request,
                               'settings': settings})


def movie_detail(request, title):
    node = get_object_or_404(models.ContentNode, title=title,
                              kind=models.KIND_MOVIE)
    return generic_detail(request, node)


def generic_detail(request, node):
    return render_to_response("venclave/detail.html",
                              {'node': node})
