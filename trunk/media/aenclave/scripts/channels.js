// channels -- functions for the Channels page

var channels = {

  /********************************* ACTIONS *********************************/

  dequeue: function() {
    var indices = songlist.gather_indices();
    if (indices.length > 0) {
      document.forms.dequeueform.indices.value = indices;
      document.forms.dequeueform.submit();
    }
  },

  askemail: function() {
    with (songlist) {
      start_subaction();
      add_subaction_label("Email a link to the current song to:");
      add_subaction_textbox("emailaddress", "username@example.com",
                            channels.okemail);
      add_subaction_button("ok", "channels.okemail();", "Send");
      add_subaction_cancel_button();
    }
  },

  okemail: function() {
    var params = {email: $("emailaddress").value, ids: $("currentsong").name}
    var options = {
      url: "/audio/json/email/",
      type: "post",
      data: params,
      dataType: 'json',
      error: function() {
        songlist.error_message("Got no reponse from server.");
      },
      success: function(json) {
        if ("error" in json) {
          songlist.error_message(json.error);
        } else if ("success" in json) {
          songlist.success_message(json.success);
        } else {
          songlist.error_message("Unintelligible server response.");
        }
      }
    };
    jQuery.ajax(options);
  },

  recent: function() {
    songlist.error_message("This feature isn't done yet.");
  }

};
