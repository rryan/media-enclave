# menclave/aenclave/context_processor.py
#
# Audio-Enclave Specific Context Processors
#
#

from views import playlist_info_json

def aenclave(request):
    return {'dl': ('dl' in request.REQUEST),
            'playlist_info': playlist_info_json()}
