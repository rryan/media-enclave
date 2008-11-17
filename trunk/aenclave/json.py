import cjson

from django.template import loader
from django.http import HttpResponse

from django.conf import settings

def render_json_template(*args, **kwargs):
    """Renders a JSON template, and then calls render_json_response()."""
    data = loader.render_to_string(*args, **kwargs)
    return render_json_response(data)

def render_json_response(data):
    """Sends an HttpResponse with the X-JSON header and the right mimetype."""
    resp = HttpResponse(data, mimetype=("application/json; charset=" +
                                        settings.DEFAULT_CHARSET))
    return resp

def json_success(message=""):
    return render_json_response(cjson.encode({'success': message}))

def json_error(message):
    return render_json_response(cjson.encode({'error': message}))
