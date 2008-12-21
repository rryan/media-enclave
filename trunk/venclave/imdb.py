# imdb.py
#
# In general, IMDB parsing crap.
#
import re

from django.conf import settings

from menclave.venclave import models

IMDB_RESOURCE_PATH="data/imdb"

# General rating format:
#'      2..222...2       5   5.2  "#1 College Sports Show, The" (2004)'
RATINGS_RE = "^\s+([.*0-9]{10})\s+(\d+)\s+(\d+\.\d)\s+(.*)$"

# Various title formats:
# TODO - fold these into a tests
#'"'Allo 'Allo!" (1982)'
#'"$treet, The" (2000) {Closet Cases (#1.4)}'
#'"'Drehscheibe, Die'" (1964) {(1970-02-01)}'
#'"10 Years Younger" (2004/II)'
#'"106 & Park Top 10 Live" (2000) {The Pursuit of Happyness Preview}'
#'"24" (2001) {9:00 p.m.-10:00 p.m. (#1.22)}'

# this isn't done yet
TITLE_RE = '^"(.*)" \((\d{4})\) ({(.*)\s*\(#(\d+)\.(\d+)\)})*'

def parse_ratings(filename):
    """
    Parses ratings out of IMDB's ratings.list
    """
    matcher = re.compile(RATINGS_RE)
    title_matcher = re.compile(TITLE_RE)
    with open(filename,"r") as f:
        for line in f:
            match = matcher.match(line)
            if match:
                distribution,votes,rank,title = match.groups()
                



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
