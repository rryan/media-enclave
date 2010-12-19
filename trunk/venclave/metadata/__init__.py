from common import *
from imdb import *
from rottentomatoes import *
from metacritic import *
from nyt import *

def update_metadata(node, force=False, force_imdb=False, force_rt=False, force_mc=False, force_nyt=False):
    update_imdb_metadata(node, force=force or force_imdb)
    update_rottentomatoes_metadata(node, force=force or force_rt)
    update_metacritic_metadata(node, force=force or force_mc)
    update_nyt_metadata(node, force=force or force_nyt)
