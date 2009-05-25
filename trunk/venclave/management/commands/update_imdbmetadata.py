#!/usr/bin/env python

"""
A Django management command to load IMDB metadata into the database.

Run this command after downloading new IMDB metadata.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from menclave.venclave import imdb


class Command(BaseCommand):

    """Updates and creates IMDBMetadata nodes."""

    def handle(self, *args, **options):
        if args:
            assert len(args) == 1
            (imdb_path,) = args
        elif hasattr(settings, 'IMDB_PATH'):
            imdb_path = settings.IMDB_PATH
        else:
            raise CommandError("Unable to find path to video files.  Either "
                               "set IMDB_PATH in settings.py or pass it on "
                               "the command line.")
        imdb.create_imdb_metadata(imdb_path)
