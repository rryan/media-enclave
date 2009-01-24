
from django.shortcuts import render_to_response
from django.template import RequestContext

def render_html_template(template, request, options=None, *args, **kwargs):
    """Render a template response with some extra parameters."""
    
    # {} is an unsafe default value, so use use None instead.
    if options is None:
        options = {}

    # The only reason this exists is so that if we need to, in the
    # future, we can hook all of our render_html_template calls very
    # easily. Right now, this is really no different than
    # render_to_response.

    return render_to_response(template, options, *args, **kwargs)

def html_error(request, message=None, title=None):
    return render_html_template('aenclave/error.html', request,
                                {'error_message':message, 'error_title':title},
                                context_instance=RequestContext(request))
