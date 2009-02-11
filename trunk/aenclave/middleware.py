# menclave/aenclave/middleware.py

"""Aenclave middleware."""

import logging

from menclave.aenclave.models import Channel

class LoggingMiddleware(object):

    """Logs exceptions with tracebacks with the standard logging module."""

    def process_exception(self, request, exception):
        logging.exception('Logging request handler error.')


class ChannelMiddleware(object):

    """Stuffs channel snapshots into the request object for performance."""

    def process_request(self, request):
        request.channel_snapshots = dict()
        channels = Channel.objects.all()
        for channel in channels:
            snapshot = channel.controller().get_channel_snapshot()
            request.channel_snapshots[channel.id] = snapshot
