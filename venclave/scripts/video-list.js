$(document).ready(function() {
    $('#video-list').tablesorter()
    $('#video-list .item-title > a').each(function(i, a) {
        a = $(a);
        a.click(function(e) {
            a.closest('tr').next().toggle();
            return false;
        });
    });
});
