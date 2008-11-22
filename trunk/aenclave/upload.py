import os

from django.core.files import File
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext

from menclave.aenclave.login import permission_required_redirect
from menclave.aenclave.html import html_error, render_html_template
from menclave.aenclave import processing
from django.conf import settings

#---------------------------------- Upload -----------------------------------#

@permission_required_redirect('aenclave.add_song', 'goto')
def upload_http(request):
    # Nab the file and make sure it's legit.
    audio = request.FILES.get('audio', None)
    if audio is None:
        return html_error(request, 'No file was uploaded.', 'HTTP Upload')

    try:
        song, audio = processing.process_song(audio.name, audio)
    except processing.BadContent:
        return html_error(request, "You may only upload audio files.",
                          "HTTP Upload")

    return render_html_template('upload_http.html', request,
                                {'song_list': [song],
                                 'sketchy_upload': audio.info.sketchy},
                                context_instance=RequestContext(request))

@permission_required_redirect('aenclave.add_song', 'goto')
def upload_sftp(request):
    song_list = []
    sketchy = False
    sftp_upload_dir = settings.AENCLAVE_SFTP_UPLOAD_DIR

    # Figure out available MP3's in SFTP upload DIR
    for root, dirs, files in os.walk(sftp_upload_dir):
        for filename in files:
            if processing.valid_song(filename):
                full_path = root + '/' + filename

                content = File(open(full_path, 'r'))
    
                song, audio = processing.process_song(full_path, content)
                
                song_list.append(song)

                if audio.info.sketchy:
                    sketchy = True

                #remove the file from the sftp-upload directory
                os.unlink(full_path)

    return render_html_template('upload_sftp.html', request,
                                {'song_list': song_list,
                                 'sketchy_upload': sketchy},
                                context_instance=RequestContext(request))

@permission_required_redirect('aenclave.add_song', 'goto')
def upload_http_fancy(request):

    # HTTPS is way slowed down..
    if request.is_secure():
        return HttpResponseRedirect("http://" + request.get_host() +
                                    reverse("aenclave-http-upload-fancy"))

    file_types = map(lambda s: "*.%s" % s, settings.SUPPORTED_AUDIO)
    return render_html_template('upload_http_fancy.html', request,
                                {'song_list': [],
                                 'show_songlist': True,
                                 'file_types': file_types,
                                 'force_actions_bar':True},
                                context_instance=RequestContext(request))

def upload_http_fancy_receiver(request):

    # Centipedes, in my request headers?
    # Yes! This view receives its session key in the POST, because
    # the multiple-file-uploader uses Flash to send the request,
    # and the best Flash can do is grab our cookies from javascript
    # and send them in the POST.

    session_key = request.REQUEST.get(settings.SESSION_COOKIE_NAME,None)
    if not session_key:
        raise Http404()

    # This is how SessionMiddleware does it.
    session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    try:
        request.session = session_engine.SessionStore(session_key)
    except Exception, e:
        return html_error(e)

    # SWFUpload will show an error to the user if this happens.
    if not request.user.is_authenticated():
        return HttpResponseForbidden()

    audio = None
    # The key is generally 'Filedata' but this is just easier.
    for k,f in request.FILES.items():
        audio = f

    # SWFUpload does not properly fill out the song's mimetype, so
    # just use the extension.
    if audio is None:
        return html_error(request, 'No file was uploaded.', 'HTTP Upload')
    elif not processing.valid_song(audio.name):
        return html_error(request, 'You may only upload MP3 files.',
                              'HTTP Upload')
    # Save the song into the database -- we'll fix the tags in a moment.
    song, audio = processing.process_song(audio.name, audio)
    
    return render_html_template('songlist_song_row.html', request,
                                {'song': song},
                                context_instance=RequestContext(request))
