// songlist -- functions for all pages with a songlist on them
// BTW This module assumes that both the Prototype and the jQuery library have
//     been loaded.  Refer to www.prototypejs.org and www.jquery.com for
//     documentation.

// Setup TableDnD on page load.
jQuery(document).ready(function() {
  jQuery('#songlist').tableDnD({
      onDrop: function(table, row) {
        // Fix row colors.
        songlist.recolor_rows();
        // Tell the server that we've reordered the songs if it makes sense.
        var path = window.location.pathname;
        var match;
        if (match = path.match(/^\/audio\/playlists\/normal\/(\d+)/)) {
          songlist.update_songlist('/playlists/update/' + match[1]);
        }
      },
      dragHandle: 'drag-handle'
  });
  jQuery('#songlist tr').hover(function() {
    jQuery('.drag-handle', this).addClass('drag-handle-dragging');
  }, function() {
    jQuery('.drag-handle', this).removeClass('drag-handle-dragging');
  });
});

var songlist = {

  /*************************** SUBACTION UTILITIES ***************************/

  // Start a new subaction, ending any previous subaction.
  start_subaction: function() {
    songlist.end_subaction();
    // Hide the action tray (thus uncovering the subaction tray).
    $("actions").style.display = "none";
  },

  // End the current subaction (if any).
  end_subaction: function() {
    // Unhide the action tray (thus covering the subaction tray).
    $("actions").style.display = "block";
    // Remove all children from the subaction tray.
    var tray = $("subactions");
    while (tray.childNodes.length > 0) tray.removeChild(tray.lastChild);
  },

  // Cancel the current subaction (if any).
  cancel: function() {
    songlist.end_subaction();
  },

  add_subaction_item: function(item) {
    $("subactions").appendChild(item);
  },

  add_subaction_span: function(item) {
    var span = document.createElement("span");
    span.appendChild(item);
    songlist.add_subaction_item(span);
  },

  // Add a text label to the subaction tray.
  //   text: the text of the label (e.g. "Select a foobar to bazify:")
  add_subaction_label: function(text) {
    var label = document.createElement("span");
    label.appendChild(document.createTextNode(text));
    songlist.add_subaction_item(label);
  },

  // Add a textbox to the subaction tray.
  //   ID: the ID of the textbox element, (e.g. "email")
  //   value: the initial contents of the textbox (e.g. "username@example.com")
  //   opt_callback: called with no args when the user hits enter.
  add_subaction_textbox: function(ID, value, opt_callback) {
    var box = document.createElement("input");
    box.type = "text";
    box.size = 30;
    box.id = ID;
    box.value = value;
    songlist.add_subaction_span(box);
    if (opt_callback) {
      Event.observe(box, 'keyup', function(evt) {
        if (evt.keyCode == Event.KEY_RETURN) {
          opt_callback();
        }
      });
    }
  },

  // Add a button to the subaction tray.
  //   klass: the CSS class of the button element, (e.g. "ok" or "cancel")
  //   action: code to execute when the button is pressed (e.g. "bazify();")
  //   text: the displayed text on the button (e.g. "Click to bazify!")
  add_subaction_button: function(klass, action, text) {
    var button = document.createElement("a");
    button.className = klass;
    button.setAttribute("href", "javascript:" + action);
    button.appendChild(document.createTextNode(text));
    songlist.add_subaction_item(button);
  },

  // Add a cancel button for the subaction tray; the button will call cancel()
  // when pressed.
  add_subaction_cancel_button: function() {
    songlist.add_subaction_button("cancel", "songlist.cancel();", "Cancel");
  },

  // End the current subaction (if any), and display a success message using
  // the subaction tray.
  //   text: the text to display (e.g. "The thingy was successfully bazified.")
  success_message: function(text) {
    songlist.start_subaction();
    songlist.add_subaction_label(text);
    songlist.add_subaction_button("ok", "songlist.end_subaction();", "Yay!");
  },

  // Cancel the current subaction (if any), and display an error message using
  // the subaction tray.
  //   text: the error text to display (e.g. "The system is down!")
  error_message: function(text) {
    songlist.start_subaction();
    songlist.add_subaction_label(text);
    songlist.add_subaction_button("cancel", "songlist.cancel();", "Phooey!");
  },

  /*************************** CHECKBOX FUNCTIONS ****************************/

  // Sets the checked state of all checkboxes in the songlist to be the same as
  // the checkbox given as an argument.
  select_all: function(box) {
    var boxen = $("songlist").getElementsByTagName("input");
    // WTF What if there are non-checkbox inputs in the songlist?  Who cares,
    //     those inputs will ignore the `checked` attribute anyway.
    for (var i = 0; i < boxen.length; i++) boxen[i].checked = box.checked;
  },

  // Returns a space-separated string of the IDs of all selected songs.
  //  empty: if true, nothing selected -> empty return value
  //         if false, nothing selected is equivalent to everything selected
  gather_ids: function(empty) {
    var boxen = $("songlist").getElementsByTagName("input");
    var selected = "";
    var all = "";
    // WTF We start with i=1 to skip the checkbox in the table head.
    for (var i = 1; i < boxen.length; i++) {
      var box = boxen[i];
      var next = box.name + " ";
      all += next;
      if (box.checked == true) selected += next;
    }
    if (empty || selected.length > 0) return selected;
    else return all;
  },

  gather_indices: function() {
    var boxen = $("songlist").getElementsByTagName("input");
    var selected = "";
    // WTF We start with i=1 to skip the checkbox in the table head.
    for (var i = 1; i < boxen.length; i++) {
      var box = boxen[i];
      if (box.checked == true) selected += (i-1) + " ";
    }
    return selected;
  },

  /********************************* ACTIONS *********************************/

  // Queues a single song with an XHR.
  queue_click: function(link) {
    // Add a paragraph after the link giving the status of the request.
    var para = document.createElement('p');
    var control_div = $('controls');
    control_div.appendChild(para);
    para.innerHTML = 'queueing...';
    // Set the cursor over the link to wait.
    link.style.cursor = 'wait';
    para.style.cursor = 'wait';
    var options = {
      method: 'get',
      onFailure: function(transport) {
        para.innerHTML = 'failed to queue.';
      },
      onSuccess: function(transport, response_json) {
        if (response_json.error) {
          para.innerHTML = 'failed to queue.';
        } else {
          para.innerHTML = 'queued successfully.';
          controls.update_playlist_info(response_json);
        }
      },
      onComplete: function(transport) {
        // Undo the waiting cursor.
        link.style.cursor = '';
        para.style.cursor = '';
        // Remove the paragraph after five seconds.
        window.setTimeout(function() {
          control_div.removeChild(para);
        }, 3000);
      }
    };
    new Ajax.Request(link.href + '&getupdate=1', options);
    return false;
  },

  // Queues all selected songs.
  queue: function() {
    var ids = songlist.gather_ids(true); // true -> queue nothing if nothing
    if (ids.length > 0) {                //         is selected
      document.forms.queueform.ids.value = ids;
      document.forms.queueform.submit();
    } else {
      songlist.error_message("You haven't selected any songs.");
    }
  },

  // DLs all selected songs.
  dl: function() {
    var ids = songlist.gather_ids(true);
    if (ids.length > 0) {
      document.forms.dlform.ids.value = ids;
      document.forms.dlform.submit();
    } else {
      songlist.error_message("You haven't selected any songs.");
    }
  },

  askcreate: function() {
    with (songlist) {
      start_subaction();
      add_subaction_label("Put songs into a playlist called:");
      add_subaction_textbox("playlistname", "Rockin' Out", songlist.okcreate);
      add_subaction_button("ok", "songlist.okcreate();", "Create playlist");
      add_subaction_cancel_button();
    }
  },

  okcreate: function() {
    var name = document.getElementById("playlistname").value;
    // WTF createform is the name of a form, not something that creates forms.
    document.forms.createform.name.value = name;
    document.forms.createform.ids.value = songlist.gather_ids(false);
    songlist.end_subaction();
    document.forms.createform.submit();
  },

  askdelete: function() {
    with (songlist) {
      start_subaction();
      add_subaction_label("Submit a delete request for the selected songs?");
      add_subaction_button("ok", "songlist.okdelete();", "Yes");
      add_subaction_cancel_button();
    }
  },

  delete: function() {
    with (songlist) {
      start_subaction();
      add_subaction_label("Really DELETE the selected songs?");
      add_subaction_button("ok", "songlist.okdelete();", "Yes, those tunes suck!");
      add_subaction_cancel_button();
    }
  },

  okdelete: function() {
    // WTF deleteform is the name of a hidden delete form on the page
    document.forms.deleteform.ids.value = songlist.gather_ids(false);
    songlist.end_subaction();
    document.forms.deleteform.submit();
  },

  askadd: function() {
    // We need to figure out which playlists the user is allowed to add to so
    // that we can list those in a dropdown menu.  Let's ask the server.
    new Ajax.Request("/audio/json/playlists/user/",
                     {method: "get",
                      onFailure: function() {
                        songlist.error_message("Got no reponse from server.");
                      },
                      onSuccess: function(transport, json) {
                        if ("error" in json) {
                          songlist.error_message(json.error);
                        } else songlist._make_askadd_tray(json);
                      }});
  },

  // Called only by askadd().  Create a subaction tray with a dropdown list of
  // the user's playlists.
  _make_askadd_tray: function(json) {
    // Create a menu of playlist choices.
    var select = document.createElement("select");
    select.id = "playlistid"
    for (var i = 0; i < json.length; i++) {
      var item = json[i];
      var option = document.createElement("option");
      option.value = item.pid;
      option.appendChild(document.createTextNode(item.name));
      select.appendChild(option);
    }
    // If there are any choices, make a subaction.
    if (select.childNodes.length > 0) {
      with (songlist) {
        start_subaction();
        add_subaction_label("Add songs to playlist:");
        add_subaction_span(select);
        add_subaction_button("ok", "songlist.okadd();", "Add songs");
        add_subaction_cancel_button();
      }
    } else songlist.error_message("No playlists exist that you may edit.");
  },

  okadd: function() {
    var select = document.getElementById("playlistid");
    var addform = document.forms.addform;
    addform.pid.value = select.value;
    addform.ids.value = songlist.gather_ids(false);
    songlist.end_subaction();
    addform.submit();
  },

  update_songlist: function(url, table) {
    // Collect all the song ids in order and send them to the server.
    var song_ids = [];
    var boxen = $('songlist').getElementsByTagName("input");
    for (var i = 0; i < boxen.length; i++) {
      song_ids.push(boxen.name);
    }
    var options = {
      method: 'post',
      parameters: {song_ids: song_ids.join(',')}
    };
    new Ajax.Request(url, options);
  },

  /******************************* TAG EDITING *******************************/

  // This is called when the user clicks the edit button next to a song to edit
  // the song tags.
  edit_song: function(target) {
    // Replace text with text boxes.
    var row = target.parentNode;
    var tds = row.getElementsByTagName("TD");
    for (var i = 1; i <= 4; i++) {
      var td = tds[i];
      var box = document.createElement("INPUT");
      var text;
      var links = td.getElementsByTagName('A');
      // This was used to use .innerHTML, which isn't what we want.
      // That would put &amp; in the text box.
      // We want .innerText, but FF doesn't support it,
      // so the cross browser way is .innerText || .textContent
      if (links.length > 0) {
        text = links[0].innerText || td.textContent;
      } else {
        text = td.innerText || td.textContent;
      }
      text = text.strip();
      box.type = "text";
      box.className = "text";
      box.value = text;
      // Clear the cell and replace it with the input box.
      td.innerHTML = '';
      td.appendChild(box);
    }
    // Replace the edit button with a done button.
    target.className = "done";
    target.setAttribute("onclick", "songlist.done_editing(this);");
  },

  done_editing: function(target) {
    // Collect the parameters from the text boxes.
    var tds = target.parentNode.getElementsByTagName("TD");
    var params = {id: tds[0].firstChild.name};
    for (var i = 1; i <= 4; i++) {
      var td = tds[i];
      params[td.getAttribute("name")] = td.lastChild.value;
    }
    // Send the request.
    var options = {
      method: "post",
      parameters: params,
      onFailure: function() {
        target.className = "error";
        target.setAttribute("onclick", "");
        songlist.error_message("Got no reponse from server.");
      },
      onSuccess: function(transport, json) {
        if ("error" in json) {
          songlist.error_message(json.error);
        } else {
          songlist._update_edited_song(target, json);
        }
      }
    };
    new Ajax.Request("/audio/json/edit/", options);
  },

  // Called only by done_editing().  Update the row in the table based on the
  // data sent back by the server.
  _update_edited_song: function(target, json) {
    target.className = "edit";
    target.setAttribute("onclick", "songlist.edit_song(this);");
    var tds = target.parentNode.getElementsByTagName("TD");
    for (var i = 1; i <= 4; i++) {
      var td = tds[i];
      td.removeChild(td.lastChild);
      var info = json[i-1];
      if (info.href) {
        var link = document.createElement("A");
        if (info.klass) link.className = info.klass;
        link.setAttribute("href", info.href);
        link.appendChild(document.createTextNode(info.text));
        td.appendChild(link);
      } else {
        td.appendChild(document.createTextNode(info.text));
      }
    }
  },

  /***************************** SORTABLE TABLES *****************************/

  // WTF These functions may not work properly for the songlist on the Channels
  //     page.  That's okay -- that songlist doesn't need to be sortable.

  // Return the head of the songlist table.
  table_head: function() {
    return $('songlist').getElementsByTagName('thead')[0];
  },

  // Return the body of the songlist table.
  table_body: function() {
    // WTF This next line should be `return $('songlist').tbody;` but Safari
    //     doesn't support the tbody attribute.
    // $#!* Browser compatibility issues suck.
    return $('songlist').getElementsByTagName('tbody')[0];
  },

  // Recolor the rows of the songlist table so that they alternate properly.
  // This should be called at the end of functions that reorder the rows.
  recolor_rows: function() {
    var tbody = songlist.table_body();
    var a = true;
    var i = 0;
    var firstRow = tbody.rows[0];
    // If the first row has the current song, leave it with the class 'c'.
    if (firstRow && firstRow.hasClassName('c')) i++;
    for (; i < tbody.rows.length; i++) {
      var row = tbody.rows[i];
      if (a) row.className = 'a';
      else row.className = 'b';
      a = !a;
    }
  },

  // Reverse the rows in the songlist.
  reverse_rows: function() {
    var tbody = songlist.table_body();
    for (var i = tbody.rows.length - 1; i >= 0; i--) {
      var row = tbody.rows[i];
      tbody.removeChild(row);
      tbody.appendChild(row);
    }
    songlist.recolor_rows();
  },

  // Get and return the text of a table cell.  This tries to be smart about
  // links and textboxes.
  get_cell_text: function(cell) {
    var text = "";
    for (var i = 0; i < cell.childNodes.length; i++) {
      var child = cell.childNodes[i];
      if (child.nodeType == Node.TEXT_NODE) {
        text = child.nodeValue.strip();
      } else if (child.nodeType == Node.ELEMENT_NODE) {
        if (child.tagName == "INPUT") {
          return String(child.value).strip();
        } else return songlist.get_cell_text(child);
      }
    }
    return text;
  },

  sort_rows_by: function(col, type, reversed) {
    // Step 1: Pick a key function.
    var key;
    if (type == "int") {
      key = function(text) {
        var value = parseInt(text, 10);
        if (isNaN(value)) return "";
        else return value;
      };
    } else if (type == "date") {
      key = function(text) {
        var date = new Date();
        var dateparts = text.split(" ");
        var timeparts;
        if (dateparts.length == 2) {
          timeparts = dateparts[1].split(":");
          date.setHours(parseInt(timeparts[0], 10));
          date.setMinutes(parseInt(timeparts[1], 10));
          date.setSeconds(parseInt(timeparts[2], 10));
          if (dateparts[0] == "Today");
          else if (dateparts[0] == "Yesterday") {
            date = new Date(date - 24 * 60 * 60 * 1000);
          }
        } else {
          date.setDate(parseInt(dateparts[0], 10));
          date.setMonth({Jan:0, Feb:1, Mar:2, Apr:3, May:4, Jun:5, Jul:6,
                         Aug:7, Sep:8, Oct:9, Nov:10, Dec:11}[dateparts[1]]);
          date.setYear(parseInt(dateparts[2], 10));
          timeparts = dateparts[3].split(":");
        }
        date.setHours(parseInt(timeparts[0], 10));
        date.setMinutes(parseInt(timeparts[1], 10));
        date.setSeconds(parseInt(timeparts[2], 10));
        return date;
      };
    } else if (type == "time") {
      key = function(text) {
        var parts = text.split(":");
        var total = 0;
        for (var i = 0; i < parts.length; i++) {
          total = 60 * total + parseInt(parts[i], 10);
        }
        return total;
      };
    } else {
      key = function(text) { return text; };
    }
    // Step 2: Pull all the rows out of the table body.
    var tbody = songlist.table_body();
    var rows = [];
    for (var i = tbody.rows.length - 1; i >= 0; i--) {
      var row = tbody.rows[i];
      tbody.removeChild(row);
      var text = songlist.get_cell_text(row.getElementsByTagName('td')[col]);
      // Sort first by key, then by index (to force sorting stability), then
      // include the row itself so we can pull it out later.
      rows.push([key(text), i, row]);
    }
    // Step 3: Sort the rows.
    if (reversed) {
      rows.sort(function(a, b) {
        if (a[0] == "") return 1;
        else if (b[0] == "") return -1;
        else if (a[0] < b[0]) return 1;
        else if (a[0] > b[0]) return -1;
        else return a[1] - b[1];
      });
    } else {
      rows.sort(function(a, b) {
        if (a[0] == "") return 1;
        else if (b[0] == "") return -1;
        else if (a[0] < b[0]) return -1;
        else if (a[0] > b[0]) return 1;
        else return a[1] - b[1];
      });
    }
    // Step 4: Put the rows back into the table body and recolor the rows.
    for (var i = 0; i < rows.length; i++) tbody.appendChild(rows[i][2]);
    songlist.recolor_rows();
  },

  sorta: function(cell) {
    var headers = songlist.table_head().getElementsByTagName('th');
    var type = cell.getAttribute("sorttype");
    var col = 0;
    for (var i = 0; i < headers.length; i++) {
      var child = headers[i];
      if (child == cell) {
        col = i;
        child.setAttribute("onclick", "songlist.sortd(this);");
        child.className = "sorta";
      } else if (child.className == "sorta" || child.className == "sortd") {
        child.setAttribute("onclick", "songlist.sorta(this);");
        child.className = "sort";
      }
    }
    songlist.sort_rows_by(col, type, false);
  },

  sortd: function(cell) {
    var headers = songlist.table_head().getElementsByTagName('th');
    var type = cell.getAttribute("sorttype");
    var col = 0;
    for (var i = 0; i < headers.length; i++) {
      var child = headers[i];
      if (child == cell) {
        col = i;
        child.setAttribute("onclick", "songlist.sorta(this);");
        child.className = "sortd";
      } else if (child.className == "sorta" || child.className == "sortd") {
        child.setAttribute("onclick", "songlist.sorta(this);");
        child.className = "sort";
      }
    }
    songlist.sort_rows_by(col, type, true);
  }

};

/*****************************************************************************/
