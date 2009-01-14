# menclave/aenclave/control.py

"""Aenclave middleware."""

import logging


class LoggingMiddleware(object):

    """Logs exceptions with tracebacks with the standard logging module."""

    def process_exception(self, request, exception):
        logging.exception(exception.message)
