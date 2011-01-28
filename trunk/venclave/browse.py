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
    return render_to_response("venclave/browse.html", request)


def movies(request):
    queryset = models.ContentNode.with_metadata().filter(kind=models.KIND_MOVIE)
    return render_to_response("venclave/simple_movies.html", request,
                              {'nodes': queryset})

def tv(request):
    # TODO
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
