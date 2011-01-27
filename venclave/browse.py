#!/usr/bin/python

import logging
import os
import urllib
import re

from django.conf import settings
from django.shortcuts import render_to_response

from menclave.venclave import models


def main(request):
    return render_to_response("venclave/browse.html",
                              {'request': request,
                               'settings': settings})


def movies(request):
    queryset = models.ContentNode.objects.filter(kind=models.KIND_MOVIE)
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


def detail(request, path):
    return render_to_response("venclave/browse.html")


def IconFor(path):
    if item.endswith('/'):
        return 'folder'

    ext = name.split('.')[-1].lower()
    if ext in ('avi', 'mov', 'mp4', 'mpg', 'ogm', 'ogv', 'mkv'):
        return 'movie'
    if ext in ('jpg', 'gif'):
        return 'image3'
    if ext in ('mp3'):
        return 'sound2'
    if ext in ('pdf'):
        return 'pdf'
    if ext in ('rar', 'zip'):
        return 'compressed'
    if ext in ('srt', 'txt', 'sub', 'idx', 'nfo', 'torrent'):
        return 'text'

    return 'unknown'

def PrettyDate(d):
    return d.strftime('%B %d, %Y %H:%M %Z')

def PrettySize(b):
    """Returns a string which represents b bytes, e.g. 735051776 --> 701 MB

    We want to avoid using more than four digits, so we prefer "1.0 GB" over "1011 MB",
    which is why the tests below are for <= 1000 instead of <= 1024.

    This displays hundredths of terabytes and tenths of gigabytes,
    but integers for anything smaller.
    """
    if b <= 1000:
        return "%d&nbsp;B"%b
    kb = float(b)/1024
    if kb <= 1000:
        return "%d&nbsp;KB"%kb
    mb = kb/1024
    if mb <= 1000:
        return "%d&nbsp;MB"%mb
    gb = mb/1024
    if gb <= 1000:
        return "%.1f&nbsp;GB"%gb
    tb = gb/1024
    return "%.2f&nbsp;TB"%tb

    
def SISize(b):
    if b <= 1000:
        return "%d B"%b
    kb = float(b)/1000
    if kb <= 1000:
        return "%d KB"%kb
    mb = kb/1000
    if mb <= 1000:
        return "%d MB"%mb
    gb = mb/1000
    if gb <= 1000:
        return "%.1f GB"%gb
    tb = gb/1000
    return "%.2f TB"%tb

def Extension(name):
    
    extensions = {'sub': 'Subtitle file',
                  'idx': 'Subtitle index file'}

    ext = name.split('.')[-1].lower()

    if ext in extensions:
        return extensions[ext]
    return None

def FindTags(name):

    if not name:
        return None
    
    tags = {'PROPER': 'Fixes a problem with the previous version',
            'REPACK': 'Fixes a problem with the previous version',
            'RERIP': 'Fixes a problem with the previous version',
            'INTERNAL': 'Release is not intended for general distribution',
            'CAMERA': 'Video was recorded in a theater',
            'CAM': 'Video was recorded in a theater',
            'TELESYNC': 'Video was recorded in a theater, with line audio',
            'TS': '(Telesync) Video was recorded in a theater, with line audio',
            'TELECINE': 'Video was digitally copied from film reels',
            'TC': '(Telecine) Video was digitally copied from film reels',
            'WORKPRINT': 'An unfinished version of the film',
            'SCREENER': 'Video was ripped from a review copy',
            'PREAIR': 'Video was available before it aired',
            'SCREENER': 'Video was ripped from a review VHS',
            'DVDSCR': 'Video was ripped from a review DVD',
			'BDSCR': 'Video was ripped from a review Blu-Ray Disc',
            'R5': 'Video was ripped from a Region 5 DVD',
            'DVDRip': 'Video was ripped from the retail DVD',
            'BDRip': 'Video was ripped from the retail Blu-ray disc',
            'BRRip': 'Video was ripped from the retail Blu-ray disc',
            'HDTVRip': 'Video was recorded from an HDTV broadcast',
            'LIMITED': 'Video had a limited run in theaters',
            'FESTIVAL': 'Video was screened at a film festival',
            'DOCU': 'Video is a documentary',
            'XviD': 'Video is encoded with the XviD codec',
            'DivX': 'Video is encoded with the DivX codec',
            'AC3': 'Audio is encoded with the AC3 codec',
            'MP3': 'Audio is encoded as MP3'}


    out = []

    # This preserves the order from the filename
    # and the capitalization from the list of tags
    for word in re.findall('\w+',name):
        for tag in tags:
            if word.lower() == tag.lower():
                out.append(tag + ' &mdash; ' + tags[tag])

    if not out:
        return None

    return '<br>\n'.join(out)


def Request():

    if "REQUEST_URI" in os.environ:
        request = os.environ["REQUEST_URI"]
    else:
        request = "/oblivious/Movies/"

    request = request.lstrip('/').rstrip('/')
    request = re.sub('/+','/',request)

    section = None
    if request.startswith('forgetful'):
        request = request[10:]
        section = 'forgetful'
    elif request.startswith('oblivious'):
        request = request[10:]
        section = 'oblivious'
    else:
        # Not good!
        return (None, None)

    request = Unquote(request)

    if request.startswith('Search'):
        (request,search) = request.split('?',1)
    else:
        search = None

    if request.endswith('/index.html'):
        request = request[0:-10]


    return (section,request,search)

def Quote(string):
    return urllib.quote(string)

def Unquote(string):
    return urllib.unquote(string)
