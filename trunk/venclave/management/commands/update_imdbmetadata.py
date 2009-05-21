#!/usr/bin/env python

"""
A Django management command to load IMDB metadata into the database.

Run this command after downloading new IMDB metadata.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from menclave.venclave.models import ContentNode
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
        titles = [node.title for node in ContentNode.objects.all()]
        #imdb.amnesia_import(titles, imdb_path)
        imdb.create_imdb_nodes(imdb_path)
