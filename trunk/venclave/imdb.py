#!/usr/bin/python
# -*- coding: utf-8 -*-
# imdb.py
#
# In general, IMDB parsing crap.
#
from __future__ import with_statement

import re
import sys
import cPickle

from django.contrib.auth.models import User
from django.conf import settings

from menclave.venclave import models

#============================== MOVIES =======================================#

# parses a movies.list

MOVIE_RE = "^(?P<title>.+?)\t+(?P<startyear>(?:\d{4}|\?{4}))(?:-(?P<endyear>(?:\d{4}|\?{4}))){0,1}$"

def parse_movies(filename):
    """
    Parse an IMDB movies.list file and spit out a giant list of titles
    in standard format.
    """
    movie_matcher = re.compile(MOVIE_RE)
    movie_index = []

    with open(filename,"r") as f:
        for line in f:
            line = line.decode('latin1').encode('utf-8')
            match = movie_matcher.match(line)

            if match:
                title = match.group('title').strip()
                movie_index.append(title)

 #    pick = open(filename + '.pickle', 'wr')
#     cPickle.dump(movie_index, pick)
    print "parse_movies done: #movies is " + str(len(movie_index))
    return movie_index

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
                line = f.next().decode('latin1').encode('utf-8')

                title_match = re_title.match(line)
                plot_match = re_plot.match(line)
                author_match = re_author.match(line)

                if title_match:
                    title = title_match.group('title').strip()
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

    print "parse_plots done"
 #    pick = open(filename + ".pickle", 'wr')
#     cPickle.dump(plot_index, pick)
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
    all_genres = set()
    valid = False

    with open(filename,"r") as f:
        for line in f:
            line = line.decode('latin1').encode('utf-8')
            if not valid:
                # HACK(rryan): There is noise at the beginning of
                # the file which hits our filter. So I skip everything
                # until we hit this.
                if line == "8: THE GENRES LIST\n":
                    valid = True
                continue
            match = genre_matcher.match(line)

            if match:
                title = match.group('title').strip()
                genre = match.group('genre')
                all_genres.add(genre)
                genre_index.setdefault(title,[]).append(genre)

#     pick = open(filename + ".pickle",'wr')
#     cPickle.dump(genre_index, pick)
    print "parse_genres done"
    return genre_index, all_genres


#TODO: add actor parsing and support



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
    """
    Parses directors.list and spits out a map of director names to
    list of titles they directed.
    """
    start = re.compile(DIRECTOR_START_RE)
    continue_ = re.compile(DIRECTOR_CONTINUE_RE)
    directors_index = {}
    all_directors = set()

    with open(filename,"r") as f:
        finished = False
        valid = False
        while not finished:
            try:
                line = f.next().decode('latin1').encode('utf-8')
                start_match = start.match(line)

                if start_match:
                    # this line is the start of a director
                    director = start_match.group('director').strip()
                    title = start_match.group('title').strip()
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
                    
                    #add directr's name to list of directors
                    all_directors.add(director)

                    # grab all extra titles following this line
                    while True:
                        line = f.next()
                        continue_match = continue_.match(line)

                        if not continue_match:
                            break

                        titles.append(continue_match.group('title'))

                    # add the director to each title
                    for title in titles:
                        directors_index.setdefault(title,[]).append(director)

            except StopIteration:
                finished = True
 #    pick = open(filename + ".pickle",'wr')
#     tup = directors_index, all_directors
#     cPickle.dump(tup, pick)
    print "parse_directors done"
    return directors_index, all_directors


#=============================== ACTORS ======================================#

#The code for this is essentially copied from the code for directors, as the
#.list files are in a very similar format.
#TODO (jslocum) figure out what to do with roles.
ACTOR_START_RE="^(?P<actor>.+?)\t+(?P<title>.+)$"
ACTOR_CONTINUE_RE = "^\t+(?P<title>.+)$"
ACOTR_ROLE_RE = "^\t+(?P<title>.+)\[(?P<role>.+)\].+$"
def parse_actors(filename):
    """
    Parses actors.list and spits out a map of actor names to
    list of titles they played in.
    """
    start = re.compile(ACTOR_START_RE)
    continue_ = re.compile(ACTOR_CONTINUE_RE)
    actors_index = {}
    all_actors = set()

    with open(filename,"r") as f:
        finished = False
        valid = False
        while not finished:
            try:
                line = f.next().decode('latin1').encode('utf-8')
                start_match = start.match(line)

                if start_match:
                    # this line is the start of a actor
                    actor = start_match.group('actor').strip()
                    title = start_match.group('title').strip()
                    titles = [title]
                    

                    # HACK(rryan): There is noise at the beginning of
                    # the file which hits our filter. So I skip everything
                    # until we get Name\t+Titles
                    if not valid:
                        if actor.strip() == "Name" and title.strip() == "Titles":
                            valid = True
                            # eat the "----\t+------" line
                            f.next()
                        continue
                    
                    #print actor + '\n\n\n\n\n\n\n' + title + '\n\n\n\n\n\n\n*******************************'
                    #add actor's name to actor list
                    all_actors.add(actor)

                    # grab all extra titles following this line
                    while True:
                        line = f.next()
                        continue_match = continue_.match(line)

                        if not continue_match:
                            break

                        titles.append(continue_match.group('title'))

                    # add the actor to each title
                    for title in titles:
                        actors_index.setdefault(title,[]).append(actor)

            except StopIteration:
                finished = True
 #    pick = open(filename + ".pickle",'wr')
#     tup = actors_index, all_actors
#     cPickle.dump(tup, pick)
    print "parse_actors done: #actors is:" + str(len(all_actors))
    return actors_index, all_actors



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
#(VG)           = video game

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
            year : the year of the title's release, possibly ????
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

        #guess the kind
        kind = None
        # if it has movie, then it is a movie
        if title['movie']:
            kind = models.KIND_MOVIE
        # if it has series, then it is a tv episode or tv series
        elif title['series']:
            # if it has an episode and season, then it is a tv episode
            if not title['episode'] is None and not title['season'] is None:
                kind = models.KIND_TV
            else: # otherwise it is probably a series
                kind = models.KIND_SERIES
        if kind is None:
            kind = models.KIND_UNKNOWN
        title['kind'] = kind

        return title
    return None


#============================== RATINGS ======================================#

# General rating format:
#'      2..222...2       5   5.2  "#1 College Sports Show, The" (2004)'

#RATINGS_RE = "^\s+([.*0-9]{10})\s+(\d+)\s+(\d+\.\d)\s+(.*)$"



#This regular expression DOES NOT WORK ON ALL MOVIES. I have no clue why.
#Example of failure: the movie 21 (made in 2008), is not matched.
# RATINGS_RE = r"""(?x)                          # turn on verbose mode
#                  ^                             # grab from start
#                  \s+                           #
#                  (?P<distribution>[.*1-9]{10}) # distribution chars, 10 times
#                  \s+                           #
#                  (?P<votes>\d+)                # number of votes
#                  \s+                           #
#                  (?P<rating>\d+\.\d+)          # the rating 0-10.x
#                  \s+                           #
#                  (?P<title>.*)                 # the title
#                  $                             # end of string
#                  """


#Somehow this works though? WTF?
RATINGS_RE = """^\s+([.*0-9]{10})\s+(\d+)\s+(?P<rating>\d+\.\d)\s+(?P<title>.*)$"""


def parse_ratings(filename):
    """
    Parses ratings out of IMDB's ratings.list. Returns a map of IMDB
    titles to ratings.
    """
    matcher = re.compile(RATINGS_RE)
    title_matcher = re.compile(TITLE_RE)
    ratings_index = {}

    with open(filename,"r") as f:
        for line in f:
            line = line.decode('latin1').encode('utf-8')
            match = matcher.match(line)
            if match:
                title = match.group('title').strip()
                rating = match.group('rating')
                ratings_index[title] = rating
            


#     pick = open(filename + '.pickle','wr')
    print "parse_ratings done"
    return ratings_index


#This is just quick thing I whipped up to match running times. It doesn't work 
#for TV shows, but it seems to work for movies.


RUNNING_RE = """^(?P<title>.+\))\s+[^\d]*(?P<time>\d+).*$"""


#I don't think this is necessary
RUNNING_RE_2 = """^(?P<title>.+\).+\))\s+[^\d]*(?P<time>\d+).*$"""

def parse_runnings(filename):
    """
    Parses runnings out of IMDB's running-times.list. Returns a map of IMDB
    titles to times.
    """
    matcher = re.compile(RUNNING_RE)
    matcher2 = re.compile(RUNNING_RE_2)
    title_matcher = re.compile(TITLE_RE)
    ratings_index = {}

    with open(filename,"r") as f:
        for line in f:
            line = line.decode('latin1').encode('utf-8')
            match = matcher.match(line)
            if match:
                title = match.group('title').strip()
                time = match.group('time')
                ratings_index[title] = time
            else:
                match = matcher2.match(line)
                if match:
                    title = match.group('title').strip()
                    time = match.group('time')
                    ratings_index[title] = time
            


#     pick = open(filename + '.pickle','wr')
    print "parse_runnings done"
    return ratings_index





def create_imdb_database_pickles(imdb_path):
    movies_file = "%s/movies.list" % imdb_path
    ratings_file = "%s/ratings.list" % imdb_path
    directors_file = "%s/directors.list" % imdb_path
    actors_file = "%s/actors.list" % imdb_path
    actresses_file = "%s/actresses.list" % imdb_path
    genres_file = "%s/genres.list" % imdb_path
    plots_file = "%s/plot.list" % imdb_path

    field_lists = {}

    movies = parse_movies(movies_file)
    ratings = parse_ratings(ratings_file)
    

    #parse_directors, actors and genres all return a duple containting a 
    #title->field dictionary, and a list of all field values (i.e. all actors)
    directors = parse_directors(directors_file)
    field_lists['directors'] = directors[1]
    directors = directors[0]
    
    actors = parse_actors(actors_file)
    field_lists['actors'] = actors[1]
    actors = actors[0]
    
    actresses = parse_actors(actresses_file)
    field_lists['actresses'] = actresses[1]
    actresses = actresses[0]

    genres = parse_genres(genres_file)
    field_lists['genres'] = genres[1]
    genres = genres[0]
    
    plots = parse_plots(plots_file)

    titles = []
    title_index = {}

    index = 0
    print "number of movies is: " + str(len(movies))
    movies.sort()
    print "movies sorted"
    for title in movies:
        if index % 25000 == 24999:
            print "working on movie " + str(index)
            pick = open(imdb_path + "dictionary__" + str(index/25000) + ".pickle", 'wr')
            cPickle.dump(title_index, pick)
            pick.close()
            title_index = {}
        title_dict = {}

        rating = ratings.get(title,None)
        if not rating is None:
            title_dict['rating'] = rating

        genres_list = genres.get(title,None)
        if not genres_list is None:
            title_dict['genres'] = genres_list

        plots_list = plots.get(title,None)
        if not plots_list is None:
            title_dict['plots'] = plots_list

        directors_list = directors.get(title,None)
        if not directors_list is None:
            title_dict['directors'] = directors_list

        actors_list = actors.get(title,None)
        if not actors_list is None:
            title_dict['actors'] = actors_list

        actresses_list = actresses.get(title, None)
        if not actresses_list is None:
            title_dict['actresses'] = actresses_list

        title_dict['title'] = title
        title_dict['title_parse'] = parse_title(title)

#        titles.append(title_dict)
        title_index[title] = title_dict

        index +=1

  #   imdb = {'titles': titles,
#             'index': title_index,
#             'lists': field_lists}
    
#     pic = os.open(imdb_path + "pickled_IMDB", 'wr');
#     cPickle.dump(imdb, pic)
#     print "Successfully loaded IMDB text files!"
    
#    return imdb



def load_imdb_database(imdb_path):
    movies_file = "%s/movies.list" % imdb_path
    ratings_file = "%s/ratings.list" % imdb_path
    directors_file = "%s/directors.list" % imdb_path
    actors_file = "%s/actors.list" % imdb_path
    actresses_file = "%s/actresses.list" % imdb_path
    genres_file = "%s/genres.list" % imdb_path
    plots_file = "%s/plot.list" % imdb_path

    field_lists = {}

    movies = parse_movies(movies_file)
    ratings = parse_ratings(ratings_file)
    

    #parse_directors, actors and genres all return a duple containting a 
    #title->field dictionary, and a list of all field values (i.e. all actors)
    directors = parse_directors(directors_file)
    field_lists['directors'] = directors[1]
    directors = directors[0]
    
    actors = parse_actors(actors_file)
    field_lists['actors'] = actors[1]
    actors = actors[0]
    
    actresses = parse_actors(actresses_file)
    field_lists['actresses'] = actresses[1]
    actresses = actresses[0]

    genres = parse_genres(genres_file)
    field_lists['genres'] = genres[1]
    genres = genres[0]
    
    plots = parse_plots(plots_file)

    titles = []
    title_index = {}

    index = 0
    print "number of movies is: " + str(len(movies))
    for title in movies:
        if index % 25000 == 0:
            print "working on movie " + str(index)
        title_dict = {}

        rating = ratings.get(title,None)
        if not rating is None:
            title_dict['rating'] = rating

        genres_list = genres.get(title,None)
        if not genres_list is None:
            title_dict['genres'] = genres_list

        plots_list = plots.get(title,None)
        if not plots_list is None:
            title_dict['plots'] = plots_list

        directors_list = directors.get(title,None)
        if not directors_list is None:
            title_dict['directors'] = directors_list

        actors_list = actors.get(title,None)
        if not actors_list is None:
            title_dict['actors'] = actors_list

        actresses_list = actresses.get(title, None)
        if not actresses_list is None:
            title_dict['actresses'] = actresses_list

        title_dict['title'] = title
        title_dict['title_parse'] = parse_title(title)

        titles.append(title_dict)
        title_index[title] = title_dict

        index +=1

    imdb = {'titles': titles,
            'index': title_index,
            'lists': field_lists}
    
    #pic = os.open(imdb_path + "pickled_IMDB", 'wr');
    #cPickle.dump(imdb, pic)
    print "Successfully loaded IMDB text files!"
    
    return imdb

def update_imdb_metadata(imdb_path):

    imdb = load_imdb_database(imdb_path)

    contents = IMDBNode.objects.all()

    for content in contents:
        update_IMDB_nodes(content, imdb)

def find_content_title(content, imdb):

    kind = content.kind
    titles = imdb['titles']

    to_match = None

    if kind == models.KIND_MOVIE:
        title = utils.canonicalTitle(content.title)
        year = content.release_date.year if content.release_date else None

        to_match = {'movie': title,
                    'kind': models.KIND_MOVIE}

        if not year is None:
            to_match['year'] = year

    elif kind == models.KIND_SERIES:
        title = utils.canonicalTitle(content.title)
        year = content.release_date.year if content.release_date else None

        to_match = {'series': title,
                    'kind': models.KIND_SERIES,
                    'episodetitle': None,
                    'season': None,
                    'episode': None,
                    'date': None}

        if not year is None:
            to_match['year'] = year

    elif kind == models.KIND_TV:
        series = utils.canonicalTitle(content.parent.title)
        episode_title = content.title
        season = content.season
        episode = content.episode
        year = content.release_date.year if content.release_date else None

        to_match = {'series': series,
                    'kind': models.KIND_TV}

        if not year is None:
            to_match['year'] = year

        if season is None and episode is None:
            to_match['episodetitle'] = episode_title

        if not season is None:
            to_match['season'] = season

        if not episode is None:
            to_match['episode'] = episode

    print "Searching for a match for %s" % to_match

    found = None
    for title in titles:
        from_match = title['title_parse']

        all_match = True
        for key in to_match.keys():
            m1 = from_match[key]
            m2 = to_match[key]

            if from_match['movie'] == 'Coffee':
                print "'%s' versus '%s'" % (m1,m2)

            # so fug. replace!
            if not str(m1).lower() == str(m2).lower():
                all_match = False
                break
        if all_match:
            found = title
            break

    return found['title']

def update_imdb_node(node, imdb):
    
    canonical_title = node.imdb_canonical_title
    
    title_dict = imdb['index'].get(canonical_title, None)
    parse = title_dict['title_parse']

    # can't happen?
    if not title_dict:
        print "No dict for title %s" % canonical_title
        return

    year = node.release_date.year if node.release_date else None
    if not year:
        node.release_date = datetime.datetime(parse['year'],1,1)

    # rating
    if 'rating' in title_dict:
        imdb.rating = title_dict['rating']

    # genres
    if 'genres' in title_dict:
        pass

    # plots
    if 'plots' in title_dict:
        pass

    # directors
    if 'directors' in title_dict:
        pass

    if kind == models.KIND_MOVIE:
        pass # nothing to do here
    elif kind == models.KIND_SERIES:
        pass # nothing to do here
    elif kind == models.KIND_TV:
        # tv episode

        # merge missing data
        if content.title is None and not parse['episodetitle'] is None:
            content.title = parse['episodetitle']
        if content.episode is None and not parse['episode'] is None:
            content.episode = int(parse['episode'])
        if content.season is None and not parse['season'] is None:
            content.season = int(parse['season'])

    # save changes
    imdb.save()
    content.metadata.imdb = imdb
    content.save()




def create_movie_nodes(imdb_path):
    movies_file = "%s/movies.list" % imdb_path
    ratings_file = "%s/ratings.list" % imdb_path
    plots_file = "%s/plot.list" % imdb_path
    

    titles = parse_movies(movies_file)
    plots = parse_plots(plots_file)
    ratings = parse_ratings(ratings_file)
    i=0
    for title in titles:
        i+=1
        if i%25000==0:
            print i
        title_parse = parse_title(title)
        #print 'movie: ' + title
        meta = models.IMDBMetadata(imdb_canonical_title = title)
        meta.save()
        if title_parse['year'] != '????':
            try:
                meta.release_year = int(title_parse['year'])
            except ValueError:
                foo=1

        plots_list = plots.get(title,None)
        if not plots_list is None:
            if len(plots_list)>0:
                meta.plot_summary=plots_list[0]['plot']

        rating = ratings.get(title,None)
        if not rating is None:
            try:
                meta.rating = float(rating)
            except ValueError:
                foo=2
        meta.save()



def create_genre_nodes(imdb_path):
    genres_file = "%s/genres.list" % imdb_path
    
    genes = parse_genres(genres_file)
    genres = genes[1]
    for genre in genres:
        gnode = models.Genre(name = genre)
        gnode.save()
        print "created genre:" + genre

    genre_dict = genes[0]
    i = 0
    for key in genre_dict.keys():
        i+=1
        if i%50000 ==0:
            print i
        meta = list(models.IMDBMetadata.objects.filter(imdb_canonical_title__exact = key))
        if len(meta) > 0:
            meta = meta[0]
            for genre in genre_dict[key]:
                meta.genres.add(list(models.Genre.objects.filter(name__iexact=genre))[0])


def create_director_nodes(imdb_path):
    directors_file = "%s/directors.list" % imdb_path
    

    directs = parse_directors(directors_file)
    directors = directs[1]
    # print 'creating ' + str(len(directors)) + ' director nodes'
#     i=0
#     for director in directors:
#         i+=1
#         if i%15000 ==0:
#             print i
#         dnode = models.Director(name = director)
#         dnode.save()
#         #print "created director:" + director
        
    director_dict = directs[0]
    i=0
    for key in director_dict.keys():
        i+=1
        if i%15000 ==0:
            print i
#        try:
        key = key.decode('latin1')
        meta = list(models.IMDBMetadata.objects.filter(imdb_canonical_title__exact = key))
        if len(meta) > 0:
            meta = meta[0]
            for director in director_dict[key]:
                dnode = models.Director(name = director)
                dnode.save()
                meta.directors.add(list(models.Director.objects.filter(name__iexact=director))[0])
            meta.save()
#         except UnicodeError:
#             print "unicode error!"


def create_actor_nodes(imdb_path):
    actors_file = "%s/actors.list" % imdb_path

    acts = parse_actors(actors_file)
#     actors = acts[1]
#     print 'creating ' + str(len(actors)) + ' actor nodes'
#     i=0
#     for actor in actors:
#         i+=1
#         if i%15000 ==0:
#             print i
#         dnode = models.Actor(name = actor)
#         dnode.save()
#         #print "created actor:" + actor
    

    actor_dict = acts[0]
    i=0
    print len(actor_dict.keys())
    for key in actor_dict.keys():
        key = key.decode('latin1')
        i+=1
        if i%15000 ==0:
            print i
        meta = list(models.IMDBMetadata.objects.filter(imdb_canonical_title__exact = key))
        if len(meta) > 0:
            meta = meta[0]
            for actor in actor_dict[key]:
                dnode = models.Actor(name = actor)
                dnode.save()
                meta.actors.add(list(models.Actor.objects.filter(name__iexact=actor))[0])



def create_actress_nodes(imdb_path):
    actresses_file = "%s/actresses.list" % imdb_path
    
    actressi = parse_actors(actresses_file)
#     actresses = actressi[1]
#     print 'creating ' + str(len(actresses)) + ' actress nodes'
#     i=0
#     for actress in actresses:
#         i+=1
#         if i%15000 ==0:
#             print i
#         dnode = models.Actor(name = actress)
#         dnode.save()
#         #print "created actress:" + actress
                
    i=0
    actor_dict = actressi[0]
    print len(actor_dict.keys())
    for key in actor_dict.keys()[3000000:]:
        key = key.decode('latin1')
        i+=1
        if i%15000 ==0:
            print i
        meta = list(models.IMDBMetadata.objects.filter(imdb_canonical_title__exact = key))
        if len(meta) > 0:
            meta = meta[0]
            for actor in actor_dict[key]:
                dnode = models.Actor(name = actor)
                dnode.save()
                meta.actors.add(list(models.Actor.objects.filter(name__iexact=actor))[0])






def create_imdb_nodes(imdb_path):
    imdb = load_imdb_database(imdb_path)

    print 'creating genre nodes'
    for genre in imdb['lists']['genres']:
        gnode = models.Genre(name = genre)
        gnode.save()
        #print "created genre:" + genre

    print 'creating ' + str(len(imdb['lists']['directors'])) + ' director nodes'
    for director in imdb['lists']['directors']:
        dnode = models.Director(name = director)
        dnode.save()
        #print "created director:" + director

    print 'creating ' + str(len(imdb['lists']['actors'])) + ' actor nodes'
    for actor in imdb['lists']['actors']:
        anode = models.Actor(name = actor)
        anode.save()
        #print "created actor:" + actor

    print 'creating ' + str(len(imdb['lists']['actresses'])) + ' actress nodes'
    for actress in imdb['lists']['actresses']:
        asnode = models.Actor(name = actress)
        asnode.save()
        #print "created actress:" + actress


    for title in imdb['index'].keys():
        movie_data = imdb['index'][title]
        #TODO: add other fields
        meta = models.IMDBMetadata(imdb_canonical_title = title)
        if 'plots' in movie_data.keys():
            meta.plot_summary = movie_data['plots'][0]['plot']
        if 'title_parse' in movie_data.keys():
            if 'year' in movie_data['title_parse']:
                if movie_data['title_parse']['year'] != "????":
                    meta.release_year = int(movie_data['title_parse']['year'])
        meta.save()
        genres = movie_data['genres']
        for genre in genres:
            meta.genres.add(list(models.Genre.objects.filter(name__iexact=genre))[0])

        directors = movie_data['directors']
        for director in directors:
            meta.genres.add(list(models.Director.objects.filter(name__iexact=director))[0])

        actors = movie_data['actors'].append(movie_data['actresses'])
        for actor in actorss:
            meta.actors.add(list(models.Actor.objects.filter(name__iexact=actor))[0])

        meta.save()
        print "made movie node for movie" + title

        


#this is just a ginormous hack. If you use this for real, you are dumb
def amnesia_import(path, imdb_path):
    movies_file = "%s/movies.list" % imdb_path
    ratings_file = "%s/ratings.list" % imdb_path
    plots_file = "%s/plot.list" % imdb_path
    runnings_file = "%s/running-times.list" % imdb_path

    movie_list = parse_movies(movies_file)
    movies = []
    amnesia = open(path)
    for line in amnesia:
        name = line[0:len(line)-7].strip()
        for movie in movie_list:
            if name in movie:
                movies.append(name)
                break
    
    print "Done getting names"

    titles = movies
    plots = parse_plots(plots_file)
    ratings = parse_ratings(ratings_file)
    runnings = parse_runnings(runnings_file)
    i=0
    for title in titles:
        i+=1
        if i%25==0:
            print i
        title_parse = parse_title(title)
        #print 'movie: ' + title
        meta = models.IMDBMetadata(imdb_canonical_title = title)
        meta.save()
        if not title_parse is None:
            if not title_parse['year'] is None:
                try:
                    meta.release_year = int(title_parse['year'])
                except ValueError:
                    foo=1

        plots_list = plots.get(title,None)
        if not plots_list is None:
            if len(plots_list)>0:
                meta.plot_summary=plots_list[0]['plot']

        rating = ratings.get(title,None)
        if not rating is None:
            try:
                meta.rating = float(rating)
            except ValueError:
                print "rating failed for: " + rating + "  " + title

        running = runnings.get(title,None)
        if not running is None:
            try:
                meta.length = float(running)
            except ValueError:
                print "running failed for: " + running + "  " + title

        
        meta.save()


#makes a content node for every IMDBMetadata instance, and gives it to the user
def make_content_nodes(user):
    for x in models.IMDBMetadata.objects.all():
        met = models.ContentMetadata(imdb = x)
        met.save()
        name = x.imdb_canonical_title.strip()
        if name[-1] == ')':
            name = name[0:-4].strip()
        name = name[0:-6].strip()
        content = models.ContentNode(owner = user, metadata=met,downloads=0,title=name, kind='movie')
        content.save()
        







# if __name__ == "__main__":
#     from sys import argv
#     imdb_root = argv[1]

#     #ratings_file = "%s/ratings.list" % imdb_root
#     #directors_file = "%s/directors.list" % imdb_root
#     #genres_file = "%s/genres.list" % imdb_root
#     #plots_file = "%s/plot.list" % imdb_root
#     #ratings = parse_ratings(ratings_file)
#     #directors = parse_directors(directors_file)
#     #genres = parse_genres(genres_file)
#     #plots = parse_plots(plots_file)

#     imdb = load_imdb_database(imdb_root)
#     from menclave.venclave import models
#     cn = models.ContentNode()
#     cn.title = 'Coffee'
#     import datetime
#     cn.release_date = datetime.datetime(1999,1,1)
#     cn.kind = models.KIND_MOVIE

#     find_content_title(cn, imdb)

#     import pdb
#     pdb.set_trace()
