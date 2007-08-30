# menclave/aenclave/dl.py

def context_processor(request):
    return {'dl': ('dl' in request.REQUEST)}

class Middleware(object):
    pass
