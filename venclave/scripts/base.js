// TODO(rnk): I think Skye meant to commit something here, but I need this in
// order for shit to work.
var venclave = {

    bound_func: function(f, this_) {
        return function() {
            return f.apply(this_, arguments);
        };
    }

};
