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
