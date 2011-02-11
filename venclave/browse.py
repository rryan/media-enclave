#!/usr/bin/python

import logging
import os
import urllib
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from menclave.venclave import models
from menclave.venclave.html import render_to_response


@login_required
def browse(request):
    q = models.ContentNode.with_metadata().order_by('-created')
    recent_movies = q.filter(kind=models.KIND_MOVIE)[:10]
    recent_tv = q.filter(kind=models.KIND_TV)[:10]
    return render_to_response("venclave/browse.html", request,
                              {'recent_movies': recent_movies,
                               'recent_tv': recent_tv})


@login_required
def movies(request):
    q = models.ContentNode.with_metadata().filter(kind=models.KIND_MOVIE)
    return render_to_response("venclave/simple_movies.html", request,
                              {'nodes': q})


@login_required
def tv(request):
    q = models.ContentNode.with_metadata()
    q = q.filter(kind=models.KIND_SERIES)
    return render_to_response("venclave/simple.html", request,
                              {'nodes': q})


@login_required
def other(request):
    q = models.ContentNode.with_metadata()
    q = q.exclude(kind__in=(models.KIND_MOVIE, models.KIND_SERIES,
                            models.KIND_TV, models.KIND_SEASON))
    return render_to_response("venclave/simple.html", request,
                              {'nodes': q})


@login_required
def movie_detail(request, title):
    node = get_object_or_404(models.ContentNode, title=title,
                             kind=models.KIND_MOVIE)
    return generic_detail(request, node)


@login_required
def detail(request, id):
    node = get_object_or_404(models.ContentNode, pk=id)
    return generic_detail(request, node)


def generic_detail(request, node):
    return render_to_response("venclave/detail.html", request, {'node': node})
