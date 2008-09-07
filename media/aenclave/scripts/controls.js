// controls -- functions for the omni-present control widget
// BTW This module assumes that the Prototype library has been loaded.  Refer
//     to www.prototypejs.org for documentation.

Array.prototype.equals = function(other) {
  if (this.length != other.length) {
    return false;
  }
  for (var i = 0; i < this.length; i++) {
    if (this[i] != other[i]) {
      return false;
    }
  }
  return true;
}

function pluralize(num, opt_plural, opt_singular) {
  var plural = opt_plural || 's';
  var singular = opt_singular || '';
  if (num > 1) {
    return plural;
  } else {
    return singular;
  }
}

// This is PeriodicalExecuter that does not start on construction, but can be
// started and restarted with calls to start() and stop().
var MyPeriodicalExecuter = Class.create(PeriodicalExecuter, {

  // Override the constructor so that we don't start executing on construction.
  initialize: function(callback, frequency) {
    // The below is cargo-culted from the original PeriodicalExecuter
    // constructor.
    this.callback = callback;
    this.frequency = frequency;
    // currentlyExecuting is true if the callback is executing, and false
    // otherwise.
    this.currentlyExecuting = false;
    // timer is null when we are stopped, and a setInterval timer value
    // otherwise.
    this.timer = null;
  },

  // Start periodic execution of our callback.
  start: function() {
    if (!this.timer) {
      this.registerCallback();
      // Do a callback now, since setInterval waits.
      // WTF Yes, wait one millisecond so we don't block.
      // TODO(rnk): Properly bind the 'this' value for the callback.
      window.setTimeout(this.callback, 1);
    }
  },

  stop: function() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

});

var controls = {

  // The number of seconds between requests to update the controls.
  DELAY: 5,

  // The PeriodicalExecuter that calls controls.update().
  updater: null,

  // The PeriodicalExecuter that moves the progress bar.
  timestepper: null,

  // The JSON object that we get back from the server with the playlist info.
  // We keep this reference with an eye towards using this state for other
  // purposes later.
  playlist_info: null,

  initialize: function(playlist_info) {
    controls.updater = new MyPeriodicalExecuter(controls.update,
                                                controls.DELAY);
    controls.timestepper = new MyPeriodicalExecuter(function() {
      if (controls.playlist_info) {
        // TODO(rnk): Use the browser's clock to avoid drift better.
        controls.update_elapsed_time(1 + controls.playlist_info.elapsed_time);
      }
    }, 1);
    // WTF Don't delete the next line, or we'll reload the channels page a lot
    //     because we'll think that the playlist has changed.
    controls.playlist_info = playlist_info;
    controls.update_playlist_info(playlist_info);
    if (Boolean(cookies.read('controls_minimized'))) {
      controls.minimize();
    } else {
      controls.updater.start();
    }
  },

  // Fires an xhr that will get new info from the server.
  update: function(opt_action) {
    var url = '/audio/json/controls_update/';
    var parameters = null;
    // We do this typeof check to avoid some weird bug.
    if (typeof opt_action == 'string') {
      url = '/audio/json/control/';
      parameters = {'action': opt_action}
    }
    var options = {
      method: 'post',
      onFailure: function(transport) {
        controls.error(String(transport.status));
      },
      onSuccess: function(transport, response_json) {
        // Update the control panel with the response JSON.
        if (response_json.error) {
          controls.error(response_json.error);
        } else {
          controls.update_playlist_info(response_json);
        }
      }
    };
    if (parameters) {
      options['parameters'] = parameters;
    }
    new Ajax.Request(url, options);
  },

  _playlist_empty: function(playlist_info) {
    return !Boolean(playlist_info &&
                    playlist_info.songs &&
                    playlist_info.songs.length > 0);
  },

  playlist_changed: function(playlist_info) {
    // Ugh, this boolean logic is complicated.
    var old_plist_empty = controls._playlist_empty(controls.playlist_info);
    var new_plist_empty = controls._playlist_empty(playlist_info);
    // If we're on channels, and the playlist changed, reload the page.
    if (!(old_plist_empty || new_plist_empty)) {
      return (controls.playlist_info.playlist_length ==
                playlist_info.playlist_length &&
              !controls.playlist_info.songs.equals(playlist_info.songs));
    } else {
      return old_plist_empty != new_plist_empty;
    }
  },

  // Updates the controls widget with new playlist information.
  update_playlist_info: function(playlist_info) {
    var on_channels = window.location.pathname.indexOf('channels/') > -1;
    if (on_channels && controls.playlist_changed(playlist_info)) {
      window.location.reload();
      return;
    }
    controls.playlist_info = playlist_info;
    if (controls._playlist_empty(playlist_info)) {
      controls.clear_controls();
    } else {
      // We have some songs, display them.
      controls.update_elapsed_time(playlist_info.elapsed_time);
      if (playlist_info.playing) {
        controls.timestepper.start();
        $('pause').show();
        $('play').hide();
      } else {
        $('pause').hide();
        $('play').show();
      }
      $('current-song').innerHTML = playlist_info.songs[0];
      var song_list = $('song-list');
      song_list.innerHTML = '';
      for (var i = 1; i < playlist_info.songs.length; i++) {
        var li = document.createElement('li');
        song_list.appendChild(li);
        li.innerHTML = playlist_info.songs[i];
      }
      var length = playlist_info.playlist_length;
      var duration = playlist_info.playlist_duration;
      var msg = length + ' song' + pluralize(length) + ' total, ';
      msg += duration + ' playing time.';
      if (playlist_info.playlist_length > 3) {
        msg = '... ' + msg;
      }
      $('control-trailer').innerHTML = msg;
    }
  },

  // BTW This must stay consistent with base.css.
  TIME_BAR_WIDTH: 160,

  update_elapsed_time: function(time) {
    var tbar = $('timebar');
    if (!tbar) return;
    controls.playlist_info.elapsed_time = time;
    var width = Math.min(controls.TIME_BAR_WIDTH, controls.TIME_BAR_WIDTH *
                         time / controls.playlist_info.song_duration);
    tbar.style.width = width + 'px';
  },

  error: function(msg) {
    controls.clear_controls();
    $('current-song').innerHTML = 'ERROR: ' + msg;
  },

  clear_controls: function() {
    // Leave -- in the current song spot and stop the progress bar.
    controls.timestepper.stop();
    controls.update_elapsed_time(0);
    // In case another callback gets executed, still set the bar to 0.
    setTimeout(function() {
      controls.update_elapsed_time(0);
    }, 1000);
    $('current-song').innerHTML = '--';
    // Clear the song list and the other info.
    $('song-list').innerHTML = '';
    $('control-trailer').innerHTML = '';
  },

  /***************************** CONTROL BUTTONS *****************************/

  minimize: function() {
    $('controls').hide();
    $('controls-restore').show();
    controls.updater.stop();
    cookies.save('controls_minimized', '1', 365);
  },

  restore: function() {
    $('controls-restore').hide();
    $('controls').show();
    controls.updater.start();
    cookies.delete_('controls_minimized');
  },

  play: function() {
    controls._control_action('play');
  },

  pause: function() {
    controls._control_action('pause');
    controls.timestepper.stop();
    $('pause').hide();
    $('play').show();
  },

  skip: function() {
    controls._control_action('skip');
  },

  shuffle: function() {
    controls._control_action('shuffle');
  },

  _control_action: function(action) {
    controls.update(action);
  }

};
