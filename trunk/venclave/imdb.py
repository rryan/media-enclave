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

#============================== PLOT =========================================#

# On IMDB multiple plot summaries can be contributed by different
# authors. Plot summaries for a title are started with a line like:

# MV: <title>

# With <title> in standard IMDB format.
# A plot summary is given by
# PL: ...Line 1...
# PL: ...Line 2...
# PL: ...
# PL: ...Line n...

# BY: <author>

# And multiple PL/BY groups can exist for the same MV. Different MV
# entries are offset by:

#-------------------------------------------------------------------------------

PLOT_TITLE_RE = "^MV:\s(?P<title>.+)$"
PLOT_PLOT_RE = "^PL:\s(?P<plot>.+)$"
PLOT_AUTHOR_RE = "^BY:\s(?P<author>.+)$"

def parse_plots(filename):
    """
    Parses an IMDB plots.list and returns a map of IMDB standard title
    names to a list of dicts, each with keys 'plot' and 'author'.
    """
    re_title = re.compile(PLOT_TITLE_RE)
    re_plot = re.compile(PLOT_PLOT_RE)
    re_author = re.compile(PLOT_AUTHOR_RE)

    plot_index = {}
    
    with open(filename,"r") as f:
        current_title = None
        current_plot = []
        current_plots = []
        while True:
            try:
                line = f.next()

                title_match = re_title.match(line)
                plot_match = re_plot.match(line)
                author_match = re_author.match(line)

                if title_match:
                    title = title_match.group('title')
                    if current_title:
                        plot_index[current_title] = current_plots
                        current_plots = []
                    current_title = title
                elif plot_match:
                    plot = plot_match.group('plot')
                    current_plot.append(plot.strip())
                elif author_match:
                    author = author_match.group('author')
                    plot = {'author': author, 'plot': ' '.join(current_plot)}
                    current_plot = []
                    current_plots.append(plot)
                
            except StopIteration:
                break
    return plot_index

#============================== GENRES =======================================#

# The genres file is a list of title and genre pairs. A title that has
# multiple genres is simply listed twice. The title name is in
# standard IMDB format and is separated from the genre by tabs.

# As usual there is tons of !@#$ noise at the beginning of the file,
# just to screw up people like us who try to parse it. The genres list
# starts off with these lines:

#8: THE GENRES LIST
#==================

GENRE_RE = "^(?P<title>.+?)\t+(?P<genre>.+)$"

def parse_genres(filename):
    """
    Parses an IMDB genres.list file and spits out a map of title names
    to list of genres. Title names are just an IMDB standard title
    formatted string.
    """
    genre_matcher = re.compile(GENRE_RE)
    genre_index = {}
    valid = False
    
    with open(filename,"r") as f:
        for line in f:
            if not valid:
                # HACK(rryan): There is noise at the beginning of
                # the file which hits our filter. So I skip everything
                # until we hit this. 
                if line == "8: THE GENRES LIST\n":
                    valid = True
                continue
            match = genre_matcher.match(line)

            if match:
                title = match.group('title')
                genre = match.group('genre')
                genre_index.setdefault(title,[]).append(genre)

    return genre_index

#============================== DIRECTORS ====================================#

# In general the directors file is formatted like so:

# "Director 1\t+Title 1"
# "\t+Title2"
# "\t+Title3"
# ""
# "Director 2\t+Title 1"
# ""
# etc

# The file has a lot of noise at the beginning which is not part of
# the list. The list itself is kicked off by the following lines:

#Name			Titles
#----			------

# To skip the noise, I temporarily hack it by detecting this line.

# For grabbing the director's name max length (variable column size)
DIRECTOR_START_RE="^(?P<director>.+?)\t+(?P<title>.+)$"
DIRECTOR_CONTINUE_RE = "^\t+(?P<title>.+)$"

def parse_directors(filename):
    start = re.compile(DIRECTOR_START_RE)
    continue_ = re.compile(DIRECTOR_CONTINUE_RE)
    directors = []
    
    with open(filename,"r") as f:
        finished = False
        valid = False
        while not finished:
            try:
                line = f.next()
                start_match = start.match(line)

                if start_match:
                    # this line is the start of a director
                    director = start_match.group('director')
                    title = start_match.group('title')
                    titles = [title]

                    # HACK(rryan): There is noise at the beginning of
                    # the file which hits our filter. So I skip everything
                    # until we get Name\t+Titles
                    if not valid:
                        if director == "Name" and title == "Titles":
                            valid = True
                            # eat the "----\t+------" line
                            f.next()
                        continue

                    # grab all extra titles following this line
                    while True:
                        line = f.next()
                        continue_match = continue_.match(line)
                        
                        if not continue_match:
                            break
                        
                        titles.append(continue_match.group('title'))

                    # add the director to the list
                    directors.append({'director': director, 'titles': titles})
            except StopIteration:
                finished = True
    return directors

#============================== RATINGS ======================================#

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

# from directors.list -- stupid docs are littered everywhere
#"xxxxx"        = a television series
#"xxxxx" (mini) = a television mini-series
#(TV)           = TV movie, or made for cable movie
#(V)            = made for video movie (this category does NOT include TV 
#                 episodes repackaged for video, guest appearances in 
#                 variety/comedy specials released on video, or 
#                 self-help/physical fitness videos)
#(VG)           = videro game

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
#                \s+                         # WTF(rryan) leave commented
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
    
    with open(filename,"r") as f:
        for line in f:
            match = matcher.match(line)
            if match:
                title = match.group('title')
                rating = match.group('rating')
                ratings_index[title] = rating
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
    imdb_root = argv[1]
    ratings_file = "%s/ratings.list" % imdb_root
    directors_file = "%s/directors.list" % imdb_root
    genres_file = "%s/genres.list" % imdb_root
    plots_file = "%s/plot.list" % imdb_root
    #ratings = parse_ratings(ratings_file)
    #directors = parse_directors(directors_file)
    #genres = parse_genres(genres_file)
    plots = parse_plots(plots_file)
    import pdb
    pdb.set_trace()
