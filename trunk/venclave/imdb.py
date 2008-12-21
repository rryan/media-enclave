#!/usr/bin/python
# -*- coding: utf-8 -*-
# imdb.py
#
# In general, IMDB parsing crap.
#
from __future__ import with_statement
import re
import sys

from django.conf import settings

from menclave.venclave import models

IMDB_RESOURCE_PATH="data/imdb"

# General rating format:
#'      2..222...2       5   5.2  "#1 College Sports Show, The" (2004)'

#RATINGS_RE = "^\s+([.*0-9]{10})\s+(\d+)\s+(\d+\.\d)\s+(.*)$"
RATINGS_RE = r"""(?x)                          # turn on verbose mode
                 ^                             # grab from start
                 \s+                           #
                 (?P<distribution>[.*1-9]{10}) # distribution chars, 10 times
                 \s+                           #
                 (?P<votes>\d+)                # number of votes
                 \s+                           #
                 (?P<rating>\d+\.\d+)          # the rating 0-10.x
                 \s+                           #
                 (?P<title>.*)                 # the title
                 $                             # end of string
                 """

# Various title formats:
# TODO - fold these into a tests
#'"'Allo 'Allo!" (1982)'
#'"$treet, The" (2000) {Closet Cases (#1.4)}'
#'"'Drehscheibe, Die'" (1964) {(1970-02-01)}'
#'"10 Years Younger" (2004/II)'
#'"106 & Park Top 10 Live" (2000) {The Pursuit of Happyness Preview}'
#'"24" (2001) {9:00 p.m.-10:00 p.m. (#1.22)}'
#'100 Sexiest Artists (2002) (TV)'
#'100 Kilos (2001) (V)'
#'110% Natural 3 (2002) (V)'
#'110° in Tucson (2005) (V)'
#'American Rhapsody, An (2001)'
#'American Ruling Class, The (2005)'
#"Ami de Vincent, L' (1983)"
#'Vampiric Love Story, A (????)'
#'"Zomergasten" (1988) {(#19.4)}'

# Movie Title/Series Title (year) (V) (TV) {Episode Title (release date) (#season.episode)}
# 

# This bastard will parse the above examples.
TITLE_RE = r"""(?x)                         # turn on verbose
                ^                           # grab from start
                (?:                         # get the title (nongreedy) either:
                "(?P<series>.*?)"           #   quoted series title
                |                           #     OR
                (?P<movie>.*?)              #   movie name
                )                           # 
                \s+                         # needs to be at least 1
                \(                          # in parens
                (?P<year>(?:\d{4}|\?{4}))   # grab the year
                (?P<yearextra>.*?)          # and maybe other crap (non-greedy)
                \)                          #
                \s*                         # could be nothing more, so *
                (?:{                        # optionally the curly brace part
                (?P<episodetitle>.*?)       # non-greedy grab episode title
#                \s+                         #
                (?:\((?:                    # optionally, in parens - EITHER
                \#(?P<season>\d+)\.         # hash, season number, dot
                (?P<episode>\d+)            # episode number
                |                           #   OR
                (?P<date>\d{4}-\d{2}-\d{2}) # release date
                )\)){0,1}                   # the paren statement is optional
                }){0,1}                     # zero or one of the curly brace
                (?P<extras>\s*\(.*?\))*     # any extra crap (TV), (V), etc.
                $                           # end of string
                """

def parse_title(title):
    """
    Makes a good effort at parsing an IMDB title string.

    If successful, returns a dict of various stuff:
          series : the title of the TV series, if it's a TV series
           movie : the title of the movie, if it's a movie
            year : the year of the title's release
       yearextra : umm...
    episodetitle : episode title, if it's a TV series
          season : season number (TV)
         episode : episode number (TV)
            date : specific release date (maybe air date?)
          extras : extra crap hanging off the end of the title

          TODO(rryan)
            kind : a guess at the 'kind' of the title 
    Otherwise, returns None
    
    """
    m = re.compile(TITLE_RE).match(title)
    if m:
        title = m.groupdict()

        # A bug in TITLE_RE causes episodetitle to possibly chomp
        # extra whitespace. Strip it manually here.
        episode_title = title.get('episodetitle', None)
        if episode_title:
            title['episodetitle'] = episode_title.rstrip()

        return title
    return None

def parse_ratings(filename):
    """
    Parses ratings out of IMDB's ratings.list
    """
    matcher = re.compile(RATINGS_RE)
    title_matcher = re.compile(TITLE_RE)
    ratings_index = {}
    succeed = 0
    fail = 0
    
    with open(filename,"r") as f:
        for line in f:
            match = matcher.match(line)
            if match:
                groups = match.groupdict()
                title = parse_title(groups.get('title'))
                if not title:
                    print "Failed on %s" % line
                    fail = fail + 1
                    continue
                rating = groups.get('rating')

                if title.get('movie',None):
                    movie = title.get('movie')
                    year = title.get('year')
                    ratings_index[(movie, year)] = title
                elif title.get('series',None):
                    series = title.get('series')
                    year = title.get('year')
                    season = title.get('season')
                    episode = title.get('episode')
                    ratings_index[(series,year,season,episode)] = title
                succeed = succeed + 1
    print "%d title parse failures out of %d" % (fail, fail+succeed)
    return ratings_index

def merge_ratings(ratings,contents):
    """
    Takes ratings that have been parsed out of ratings.list, and
    merges them with the various ContentNodes in the database.
    """
    
    for content in contents:
        meta = content.metadata
        imdb = meta.imdb
        if imdb is None:
            imdb = models.IMDBMetadata()
            imdb.save()
            meta.imdb = imdb
            meta.save()
            
        imdb = meta.imdb

        # see if we have imdb ratings for this title
        # update them in imdb
        # save imdb

if __name__ == "__main__":
    from sys import argv
    print argv
    ratings = parse_ratings(argv[1])
    import pdb
    pdb.set_trace()
