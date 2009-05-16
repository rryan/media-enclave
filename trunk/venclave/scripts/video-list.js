venclave.videolist = {
    panes: [],

    title_onclick: function(a_elt) {
        var a = $(a_elt);
        var id = a.closest('tr').attr('id1');
        var that = this;
        if (!this.panes[id]) {
            $.get('/video/load_pane/',
                  {id: id},
                  function(html) {
                      that.toggle_style(a_elt.parentNode, 'background', '#CCC');
                      var pane = $(html);
                      that.panes[id] = pane;
                      a.closest('tr').after(pane);
		              var title = pane.find('.nytimes').attr('href').replace(/#/, '');
                      jQuery.getJSON("http://www.google.com/uds/GwebSearch?v=1.0&q=nytimes review "+encodeURIComponent(title)+"&callback=?",
                                     function(json) {
                                         pane.find('.nytimes').attr({'href' : json.responseData.results[0].url});
                                     });
                  });
        } else {
            this.panes[id].toggle();
            this.toggle_style(a_elt.parentNode, 'background', '#CCC');
        }
        return false;
    },

    toggle_style: function(elt, attr, value) {
        if (elt.style[attr]) {
            elt.style[attr] = '';
        } else {
            elt.style[attr] = value;
        }
    },
}
