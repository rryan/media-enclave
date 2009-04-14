$(document).ready(function() {
    var init = function() {
        $('#facet-list .facet-options input:radio').change(update);
        checkbox.init()
        searchbar.init()
        slider.init()
    };

    var update = function() {
        var state = $.toJSON(get_state());
        $('#video-list > .list-body').load('/video/update_list/', {'f':state});
    };

    var get_state = function() {
        return $.extend(checkbox.get_state(),
                        searchbar.get_state(),
                        slider.get_state());
    };

    var checkbox = {
        init: function() {
            $('#facet-list .checkbox input:checkbox').change(update);
        },

        get_state: function() {
            var state = {};
            $('#facet-list > .checkbox').each(function(i, facet) {
                facet = $(facet);
                var name = facet.children('.facet-name').text();
                name = $.trim(name);
                var op = facet.find('.facet-options > input:checked').val();
                var selected = facet.find('.facet-choices > input:checked');
                selected = $.map(selected, function(e){return e.value;});
                state[name] = {op: op, selected: selected};
            });
            return state;
        }
    };

    var searchbar = {
        init: function() {
            $('#facet-list > .searchbar form').submit(searchbar.on_submit);
        },

        on_submit: function() {
            var form = $(this);
            var textfield = form.find('input:text');
            form.next('ul').append(searchbar.create_li(textfield.val()));
            textfield.val('');
            update();
            return false;
        },

        create_li: function(val) {
            var li = $('<li><span>'+val+'</span><a href="#">[x]</a></li>');
            li.find('a').click(searchbar.remove_li(li));
            return li;
        },

        remove_li: function(li) {
            return function() {
                li.remove();
                update();
            };
        },

        get_state: function() {
            var state = {};
            $('#facet-list > .searchbar').each(function(i, facet) {
                facet = $(facet);
                var name = facet.children('.facet-name').text();
                name = $.trim(name);
                var op = facet.find('.facet-options > input:checked').val();
                var selected = facet.find('.facet-choices li');
                selected = $.map(selected, function(li) {
                    return $(li).find('span').text();
                });
                state[name] = {op: op, selected: selected};
            });
            return state
        }
    };

    var slider = {
        init: function() {
            $('#facet-list .slider-div').each(function(i, div) {
                var div = $(div);
                var min = parseInt(div.attr('min'),10);
                var max = parseInt(div.attr('max'),10);
                var lo = div.prevAll('.slider-lo')
                var hi = div.prevAll('.slider-hi')
                div.slider({range: true,
                            min: min,
                            max: max,
                            values: [min, max],
                            slide: function(e, ui) {
                                lo.text(ui.values[0]);
                                hi.text(ui.values[1]);
                            },
                            change: function(e, ui) {
                                update();
                            }
                       });
            });
        },

        get_state: function() {
            var state = {};
            $('#facet-list > .slider').each(function(i, facet) {
                facet = $(facet);
                var name = facet.children('.facet-name').text();
                name = $.trim(name);
                var slider = facet.find('.slider-div');
                var lo = slider.slider('values', 0);
                var hi = slider.slider('values', 1);
                state[name] = {lo: lo, hi: hi}
            });
            return state;
        }
    };

    init();
});
