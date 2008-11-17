import cjson


from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext

from menclave.aenclave.login import permission_required_json, permission_required, permission_required_xml
from menclave.aenclave.utils import get_int_list, get_song_list, get_integer
from menclave.aenclave.xml import simple_xml_response, xml_error, render_xml_to_response
from menclave.aenclave.json import render_json_response, json_success, json_error
from menclave.aenclave.html import render_html_template
from menclave.aenclave.control import Controller, ControlError
from menclave.aenclave.models import Channel

#--------------------------------- Channels ----------------------------------#

def channel_detail(request, channel_id=1):
    try: channel = Channel.objects.get(pk=channel_id)
    except Channel.DoesNotExist: raise Http404
    ctrl = channel.controller()
    current_song = ctrl.get_current_song()
    return render_html_template('channels.html', request,
                                {'channel': channel,
                                 'current_song': current_song,
                                 'song_list': ctrl.get_queue_songs(),
                                 'force_actions_bar': True,
                                 'elapsed_time': ctrl.get_elapsed_time(),
                                 'skipping': (current_song == 'DQ'),
                                 'playing': ctrl.is_playing(),
                                 'no_queuing': True},
                                context_instance=RequestContext(request))

def channel_reorder(request, channel_id=1):
    try: channel = Channel.objects.get(pk=channel_id)
    except Channel.DoesNotExist: raise Http404
    ctrl = channel.controller()
    form = request.POST
    songs = get_song_list(form)
    # FIXME(rnk): This is the stupidest, most non-threadsafe way possible to do
    #             this.  I should probably be shot for it.  Please, for the
    #             love of all that is holy, consider fixing this.
    ctrl.clear_queued_songs()
    ctrl.add_songs(songs)
    return json_success('Successfully reordered channel.')

def json_channel_info(channel_id=1):
    channel = Channel.objects.get(pk=channel_id)
    data = {}
    ctrl = channel.controller()
    songs = ctrl.get_queue_songs()
    current_song = ctrl.get_current_song()
    if current_song:
        songs.insert(0, current_song)
    # Provide data for the first three songs.
    data['songs'] = []
    for song in songs:
        if len(data['songs']) >= 3:
            break
        if song is 'DQ':
            # Skip dequeue noises.
            continue
        # Strip the metadata of extra spaces, or we'll truncate too much.
        info_str = '%s - %s' % (song.title.strip(), song.artist.strip())
        if len(info_str) > 30:
            info_str = info_str[:27] + '...'
        data['songs'].append(info_str)
    data['elapsed_time'] = ctrl.get_elapsed_time()
    data['song_duration'] = songs[0].time if (songs and songs[0] != 'DQ') else 0
    data['playlist_length'] = len(songs)
    data['playlist_duration'] = ctrl.get_queue_duration()
    data['playing'] = ctrl.is_playing()
    return cjson.encode(data)

def xml_update(request):
    form = request.POST
    channel_id = get_integer(form, 'channel', 1)
    try: channel = Channel.objects.get(pk=channel_id)
    except Channel.DoesNotExist:
        return xml_error('invalid channel id: ' + repr(channel_id))
    timestamp = get_integer(form, 'timestamp', None)
    if timestamp is None: return xml_error('invalid timestamp')
    elif timestamp >= channel.last_touched_timestamp():  # up-to-date timestamp
        try:
            ctrl = channel.controller()
            if not ctrl.is_playing: return simple_xml_response('continue')
            elapsed_time = ctrl.get_elapsed_time()
            total_time = ctrl.get_current_song().time
            return render_xml_to_response('update.xml',
                                          {'elapsed_time':elapsed_time,
                                           'total_time':total_time})
        except ControlError, err: return xml_error(str(err))
    else: return simple_xml_response('reload')  # old timestamp


#---------------------------------- Queuing ----------------------------------#

@permission_required_json('aenclave.can_control')
def json_control(request):
    action = request.POST.get('action','')
    try:
        if action == 'play': Controller().unpause()
        elif action == 'pause': Controller().pause()
        elif action == 'skip': Controller().skip()
        elif action == 'shuffle': Controller().shuffle()
        else: return json_error('invalid action: ' + action)
    except ControlError, err:
        return json_error(str(err))
    else:
        # Control succeeded, get the current playlist state and send that back.
        return json_control_update(request)

def json_control_update(request, channel_id=1):
    try:
        channel_info = json_channel_info(channel_id)
    except ControlError, err:
        return json_error(str(err))
    else:
        return render_json_response(channel_info)

@permission_required('aenclave.can_queue', 'Queue Song')
def queue_songs(request):
    form = request.REQUEST
    # Get the selected songs.
    songs = get_song_list(form)
    # Queue the songs.
    Controller().add_songs(songs)
    if 'getupdate' in form:
        # Send back an updated playlist status.
        return json_control_update(request)
    else:
        # Redirect to the channels page.
        return HttpResponseRedirect(reverse('aenclave-default-channel'))

@permission_required('aenclave.can_queue', 'Dequeue Song')
def dequeue_songs(request):
    form = request.POST
    # Get the selected indices.
    indices = get_int_list(form, 'indices')
    # Dequeue the songs.
    Controller().remove_songs(indices)
    # Redirect to the channels page.
    return HttpResponseRedirect(reverse('aenclave-default-channel'))

@permission_required_xml('aenclave.can_queue')
def xml_queue(request):
    form = request.POST
    # Get the selected songs.
    songs = get_song_list(form)
    # Queue the songs.
    try: Controller().add_songs(songs)
    except ControlError, err: return xml_error(str(err))
    else: return simple_xml_response('success')

@permission_required_xml('aenclave.can_queue')
def xml_dequeue(request):
    form = request.POST
    # Get the selected songs.
    indices = get_int_list(form, 'indices')
    # Dequeue the songs.
    try: Controller().remove_songs(indices)
    except ControlError, err: return xml_error(str(err))
    else: return simple_xml_response('success')

@permission_required_xml('aenclave.can_control')
def xml_control(request):
    form = request.POST
    action = form.get('action','')
    try:
        if action == 'play': Controller().unpause()
        elif action == 'pause': Controller().pause()
        elif action == 'skip': Controller().skip()
        elif action == 'shuffle': Controller().shuffle()
        else: return xml_error('invalid action: ' + action)
    except ControlError, err: return xml_error(str(err))
    else: return simple_xml_response('success')

    
