# menclave/aenclave/context_processor.py
#
# Audio-Enclave Specific Context Processors
#
#

from menclave.aenclave.channel import json_channel_info

def aenclave(request):
    # TODO(rnk): Sometimes this gets called more than we want.  We only want to
    # call it if we're populating a template derived from base.html.
    return {'dl': ('dl' in request.REQUEST),
            'playlist_info': json_channel_info()}
