# menclave/aenclave/views.py

import re

from django.core.mail import send_mail
from django.template import RequestContext

from menclave import settings
from menclave.aenclave.json import json_error, json_success
from menclave.aenclave.html import render_html_template
from menclave.aenclave.models import Song
from menclave.aenclave.utils import get_song_list

#--------------------------------- Roulette ----------------------------------#

def roulette(request):
    # Choose six songs randomly.
    queryset = Song.visibles.order_by('?')[:6]
    return render_html_template('roulette.html', request,
                                {'song_list': queryset},
                                context_instance=RequestContext(request))

#--------------------------------- Misc --------------------------------------#

def json_email_song_link(request):
    form = request.POST
    email_address = form.get('email', '')
    if not re.match("^[-_a-zA-Z0-9.]+@[-_a-zA-Z0-9.]+$", email_address):
        return json_error("Invalid email address.")
    songs = get_song_list(form)
    if songs:
        message = ["From: Audio Enclave <%s>\r\n" %
                   settings.DEFAULT_FROM_EMAIL,
                   "To: %s\r\n\r\n" % email_address,
                   "Someone sent you a link to the following "]
        if len(songs) == 1:
            message.append("song:\n\n")
            subject = songs[0].title
        else:
            message.append("songs:\n\n")
            subject = "%d songs" % len(songs)
        for song in songs:
            message.extend((song.title, "\n",
                            song.artist, "\n",
                            song.album, "\n",
                            settings.HOST_NAME +
                            song.get_absolute_url(), "\n\n"))
        # Ship it!
        send_mail("Link to " + subject, "".join(message),
                  settings.DEFAULT_FROM_EMAIL, (email_address,))
        return json_success("An email has been sent to %s." % email_address)
    else: return json_error("No matching songs were found.")

#=============================================================================#
