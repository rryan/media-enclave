$(document).ready(function() {
    $('#video-list .item-title > a.parent').each(function(i, a) {
	a = $(a);
	a.click(function(e) {
	    a.closest('tr').next().toggle();
	    return false;
	});
    });
});