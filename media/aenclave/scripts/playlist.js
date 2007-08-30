// playlist -- functions for viewing a playlist in Audio Enclave

var playlist = {

  edit: function() {
    
  },

  remove: function() {
    var ids = songlist.gather_ids(true); // true -> remove nothing if nothing
    if (ids.length > 0) {                //         is selected
      document.removeform.ids.value = ids;
      document.removeform.submit();
    }
  },

  askdel: function() {
    with (songlist) {
      start_subaction();
      add_subaction_label("Um, are you sure about that?");
      add_subaction_button("ok", "playlist.okdel();", "Delete it!");
      add_subaction_cancel_button();
    }
  },

  okdel: function() {
    songlist.end_subaction();
    document.deleteform.submit();
  }

};
