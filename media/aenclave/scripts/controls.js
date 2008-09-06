// controls -- functions for the omni-present control widget
// BTW This module assumes that the Prototype library has been loaded.  Refer
//     to www.prototypejs.org for documentation.

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
    this.currentlyExecuting = false;
  },

  // Start periodic execution of our callback.
  start: function() {
    if (!this.timer) {
      this.registerCallback();
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
        controls.update_elapsed_time(1 + controls.playlist_info.elapsed_time);
      }
    }, 1);
    controls.update_playlist_info(playlist_info);
    controls.updater.start();
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

  // Updates the controls widget with new playlist information.
  update_playlist_info: function(playlist_info) {
    if (!playlist_info) return;
    controls.playlist_info = playlist_info;
    if (playlist_info.songs && playlist_info.songs.length > 0) {
      // We have some songs, display them.
      controls.update_elapsed_time(playlist_info.elapsed_time);
      controls.timestepper.start();
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
    } else {
      controls.clear_controls();
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
    }, 500);
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
  },

  restore: function() {
    $('controls-restore').hide();
    $('controls').show();
    controls.updater.start();
  },

  play: function() {
    controls._control_action('play');
  },

  pause: function() {
    controls._control_action('pause');
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
