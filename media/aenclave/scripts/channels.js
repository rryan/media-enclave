// channels -- functions for the Channels page
// BTW This module assumes that the Prototype library has been loaded.  Refer
//     to www.prototypejs.org for documentation.

var channels = {

  /********************************* ACTIONS *********************************/

  dequeue: function() {
    var indices = songlist.gather_indices();
    if (indices.length > 0) {
      document.dequeueform.indices.value = indices;
      document.dequeueform.submit();
    }
  },

  askemail: function() {
    with (songlist) {
      start_subaction();
      add_subaction_label("Email a link to the current song to:");
      add_subaction_textbox("emailaddress", "username@example.com");
      add_subaction_button("ok", "channels.okemail();", "Send");
      add_subaction_cancel_button();
    }
  },

  okemail: function() {
    var params = {email: $("emailaddress").value, ids: $("currentsong").name}
    new Ajax.Request("/audio/json/email/",
                     {method: "post", parameters: params,
                      onFailure: function() {
                        songlist.error_message("Got no reponse from server.");
                      },
                      onSuccess: function(transport, json) {
                        if ("error" in json) {
			  songlist.error_message(json.error);
                        } else if ("success" in json) {
			  songlist.success_message(json.success);
			} else {
			  songlist.error_message(
			    "Unintelligible server response.");
			}
                      }});
  },

  recent: function() {
    songlist.error_message("This feature isn't done yet.");
  },

  /***************************** CONTROL BUTTONS *****************************/

  play: function() {
    channels._control_action("play");
  },

  pause: function() {
    channels._control_action("pause");
  },

  skip: function() {
    channels._control_action("skip");
  },

  shuffle: function() {
    channels._control_action("shuffle");
  },

  _control_action: function(action) {
    new Ajax.Request("/audio/json/control/",
		     {method:"post", parameters:{action:action},
		      onFailure: function() {
			error_message("Got no reponse from server.");
		      },
		      onSuccess: function(transport, json) {
			if ("error" in json) {
			  songlist.error_message(json.error);
			} else if ("success" in json) {
			  window.location.reload();
			} else {
			  songlist.error_message(
			    "Unintelligible server response.");
			}
		      }});
  },

  /******************************* AUTO-UPDATE *******************************/

  TIME_BAR_WIDTH: 160,

  init_time_bar: function(params) {
    var tbar = $('timebar');
    tbar.playing = params.playing;
    tbar.skipping = params.skipping;
    tbar.elapsed_time = params.elapsed_time;
    tbar.total_time = params.total_time;
    tbar.timestamp = params.timestamp;
    if (tbar.playing && !tbar.skipping) {
      // Increment the bar once per second.
      tbar.pe = new PeriodicalExecuter(function(pe) {
	channels.update_elapsed_time(1 + $('timebar').elapsed_time);
      }, 1);
    }
    // Sync with the server every few seconds.
    var delay = (tbar.skippping ? 5 : 10);
    setTimeout(function() {
      new Ajax.PeriodicalUpdater($('debugz'), 'update/',
				 {method: 'post', evalScripts: true,
				  frequency: delay,
				  parameters: {timestamp: tbar.timestamp}});
    }, delay * 1000);
  },

  update_elapsed_time: function(time) {
    var tbar = $('timebar');
    tbar.elapsed_time = time;
    var width = Math.min(channels.TIME_BAR_WIDTH, channels.TIME_BAR_WIDTH *
			 tbar.elapsed_time / tbar.total_time);
    tbar.style.width = width + "px";
  }

};

// var bar_timer = null;

// function start_bar() {
//   if (bar_playing && !bar_skipping) {
//     bar_timer = setTimeout("update_bar();", 1000);
//   }
//   if (bar_skipping) setTimeout("sync_bar();", 4500);
//   else setTimeout("sync_bar();", 9500);
// }

// function update_bar() {
//   if (!bar_playing) return;
//   var target = document.getElementById("bar");
//   bar_elapsed += 1;
//   var width = Math.min(160, 160 * bar_elapsed / bar_total);
//   target.style.width = width + "px";
//   bar_timer = setTimeout("update_bar();", 1000);
// }

// function sync_bar() {
//   if (bar_skipping) {
//     window.location.reload();
//     return;
//   }
//   // Build the request.
//   var params = "channel=" + bar_channel + "&timestamp=" + bar_timestamp;
//   var http = new XMLHttpRequest();
//   http.open("POST", "/audio/xml/update/", true);
//   http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
//   http.setRequestHeader("Content-length", params.length);
//   http.setRequestHeader("Connection", "close");
//   http.setRequestHeader("Cache-Control", "no-cache");
//   // Set the callback function.
//   http.onload = function(event) {
//     if (bar_timer) {
//       clearTimeout(bar_timer);
//       bar_timer = null;
//     }
//     var response = http.responseXML;
//     if (response) {
//       var element = response.documentElement;
//       if (element.tagName == "reload") window.location.reload();
//       else if (element.tagName == "update") {
//         var target = document.getElementById("bar");
//         new_elapsed = parseInt(element.getAttribute("elapsed"));
//         new_total = parseInt(element.getAttribute("total"));
//         if (new_total != bar_total || new_elapsed < bar_elapsed) {
//           window.location.reload();
//         } else {
//           bar_elapsed = new_elapsed;
//           var target = document.getElementById("bar");
//           var width = Math.min(160, 160 * bar_elapsed / bar_total);
//           target.style.width = width + "px";
//           if (bar_playing) bar_timer = setTimeout("update_bar();", 1000);
//           setTimeout("sync_bar();", 9500);
//         }
//       } else if (element.tagName == "continue") {
//         setTimeout("sync_bar();", 9500);
//       } else if (element.tagName == "error") {
//         error_message("ERROR:" + element.firstChild.nodeValue);
//       } else error_message("UNEXPECTED REPLY: " + element.tagName);
//     }
//   }
//   // Ship it!
//   http.send(params);
// }

/*****************************************************************************/
