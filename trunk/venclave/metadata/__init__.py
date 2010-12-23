from common import *
from imdb import *
from rottentomatoes import *
from metacritic import *
from nyt import *

def update_contentnodes_metadata(nodes, force=False, force_imdb=False,
                                 force_rt=False, force_mc=False, force_nyt=False):
    imdb_nodes = nodes.filter(metadata__imdb__imdb_id=None) \
        if not force and not force_imdb else nodes
    rt_nodes = nodes.filter(metadata__rotten_tomatoes__rt_id=None) \
        if not force and not force_rt else nodes
    mc_nodes = nodes.filter(metadata__metacritic__mc_id=None) \
        if not force and not force_mc else nodes
    nyt_nodes = nodes.filter(metadata__nyt_review=None) \
        if not force and not force_nyt else nodes

    for node in imdb_nodes:
        update_imdb_metadata(node, force=force or force_imdb)
    for node in rt_nodes:
        update_rottentomatoes_metadata(node, force=force or force_rt)
    for node in mc_nodes:
        update_metacritic_metadata(node, force=force or force_mc)
    for node in nyt_nodes:
        update_nyt_metadata(node, force=force or force_nyt)


def update_metadata(node, force=False, force_imdb=False, force_rt=False, force_mc=False, force_nyt=False):
    update_imdb_metadata(node, force=force or force_imdb)
    update_rottentomatoes_metadata(node, force=force or force_rt)
    update_metacritic_metadata(node, force=force or force_mc)
    update_nyt_metadata(node, force=force or force_nyt)
