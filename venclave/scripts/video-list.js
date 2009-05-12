$(document).ready(function() {
    $('#video-list').tablesorter()
    $('#video-list .item-title > a').each(function(i, a) {
        a = $(a);
        a.click(function(e) {
            tr.a.closest('tr').next();
            tr.toggle();
            return false;
        });
    });
});

videolist_onclick = function(e) {
    toggle_bg()
    if (!pane) {
        $.get('{% url venclave-pane %}',
              {id: id},
              function(html) {
                  pane = $(html);
                  a.closest('tr').after(pane);
		          var title = pane.find('.nytimes').attr('href').replace(/#/, '');
                  jQuery.getJSON("http://www.google.com/uds/GwebSearch?v=1.0&q=nytimes review "+encodeURIComponent(title)+"&callback=?",
                                 function(json) {
                                     pane.find('.nytimes').attr({'href' : json.responseData.results[0].url});
                                 });
              });
    } else {
        pane.toggle();
    }
    return false;
}