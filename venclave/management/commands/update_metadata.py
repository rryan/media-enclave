#!/usr/bin/env python

"""
A Django management command to update metadata for content in the database.

Run this command periodically to lookup metadata for new content and update
existing metadata.
"""
import logging
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from menclave.venclave import models
from menclave.venclave import metadata

class Command(BaseCommand):
    """Updates metadata for ContentNodes"""

    option_list = BaseCommand.option_list + (
        make_option('--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force update of all metadata sources.'),
        make_option('--force-imdb',
            action='store_true',
            dest='force_imdb',
            default=False,
            help='Force update of IMDb metadata.'),
        make_option('--force-rottentomatoes',
            action='store_true',
            dest='force_rt',
            default=False,
            help='Force update of RottenTomatoes metadata.'),
        make_option('--force-metacritic',
            action='store_true',
            dest='force_mc',
            default=False,
            help='Force update of metacritic metadata.'),
        make_option('--force-nyt',
            action='store_true',
            dest='force_nyt',
            default=False,
            help='Force update of NYT metadata.'),
        )

    def handle(self, *args, **options):
        # For now, only deal w/ movies.
        movies = models.ContentNode.objects.filter(kind=models.KIND_MOVIE)

        for node in movies:
            logging.info("Updating metadata for '%s'" % node)
            metadata.update_metadata(node,
                                     force=options['force'],
                                     force_imdb=options['force_imdb'],
                                     force_rt=options['force_rt'],
                                     force_mc=options['force_mc'],
                                     force_nyt=options['force_nyt'])


