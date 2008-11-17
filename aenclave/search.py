import datetime
import itertools

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db.models import Q

from menclave.aenclave.control import Controller
from menclave.aenclave.models import Song
from menclave.aenclave.utils import parse_date, parse_time, parse_integer, get_unicode
from menclave.aenclave.html import render_html_template, html_error

def Qu(field, op, value):
    return Q(**{(str(field) + '__' + str(op)): str(value)})

#------------------------------- Normal Search -------------------------------#

def normal_search(request):
    form = request.GET
    # Get the query.
    query_string = form.get('q','')
    query_words = query_string.split()
    # If no query was provided, then yield no results.
    if not query_words: queryset,query_string = (),''
    # Otherwise, get matching songs.
    else:
        full_query = Q()
        for word in query_words:
            word_query = Q()
            for field in ('title', 'album', 'artist'):
                # WTF Each word may appear in any field, so we use OR here.
                word_query |= Qu(field, 'icontains', word)
            # WTF Each match must contain every word, so we use AND here.
            full_query &= word_query
        queryset = Song.visibles.filter(full_query)
    # If we're feeling lucky, queue a random result.
    if form.get('lucky', False):
        if queryset is ():
            queryset = Song.visibles
        song = queryset.order_by('?')[0]
        Controller().add_song(song)
        # Redirect to the channels page.
        return HttpResponseRedirect(reverse('aenclave-default-channel'))
    # Otherwise, display the search results.
    return render_html_template('search_results.html', request,
                                {'song_list':queryset,
                                 'search_query':query_string},
                                context_instance=RequestContext(request))

#------------------------------- Filter Search -------------------------------#

def _build_filter_tree(form, prefix):
    """_build_filter_tree(form, prefix) -- returns (tree,total,errors)

    Builds the subtree rooted at the prefix from the form.
      tree -- filter tree structure
      total -- total number of criteria
      errors -- list of errors
    Returns (None,0,None) if there is no subtree rooted at the prefix.  Raises
    a KeyError if the tree is malformed."""
    try: kind = form[prefix]
    except KeyError: return None, 0, None
    if kind in ('or','and','nor','nand'):
        prefix += '_'
        subtrees, total, errors = [], 0, []
        for i in itertools.count():
            subprefix = prefix + str(i)
            subtree, subtotal, suberr = _build_filter_tree(form, subprefix)
            if subtree is None: break  # There are no more subtrees.
            elif subtotal == 0: continue  # Skip this empty subtree.
            subtrees.append(subtree)
            total += subtotal
            errors.extend(suberr)
        return ('sub', kind, subtrees), total, errors
    else:
        rule = form[prefix+'_r']
        if kind in ('title','album','artist'):
            string = get_unicode(form, prefix+'_f0')
            # If the kind is blank, then ignore the criterion.
            if not string: return (), 0, ()
            # Validate the rule.
            if rule not in ('in','notin','start','notstart','end','notend',
                            'is','notis'):
                raise KeyError('bad string rule: %r' % rule)
            return (kind, rule, string), 1, ()
        elif kind in ('time','track','play_count'):
            errors = []
            # Get f0 and, if needed, f1.
            try:
                if kind == 'time': f0 = parse_time(form[prefix+'_f0'])
                else: f0 = parse_integer(form[prefix+'_f0'])
            except ValueError, err: errors.append(str(err))
            if rule in ('inside','outside'):
                try:
                    if kind == 'time': f1 = parse_time(form[prefix+'_f1'])
                    else: f1 = parse_integer(form[prefix+'_f1'])
                except ValueError, err: errors.append(str(err))
            # Validate the rule.
            if errors: return (), 1, errors
            elif rule in ('inside', 'outside'):
                return (kind, rule, (f0, f1)), 1, ()
            elif rule in ('is','notis','lte','gte'):
                return (kind, rule, f0), 1, ()
            else: raise KeyError('bad integer rule: %r' % rule)
        elif kind in ('date_added','last_queued'):
            if rule in ('last','nolast'):
                # Validate the number.  This is human provided, so give an
                # error string if it's bad.
                try: number = parse_integer(form[prefix+'_f0'])
                except ValueError, err: return (), 1, (str(err),)
                # Validate the unit.  This is provided by the form, so raise
                # a KeyError if it's bad.
                unit = form[prefix+'_f1']
                if unit not in ('hour','day','week','month','year'):
                    raise KeyError('bad date unit: %r' % unit)
                return (kind, rule, (number, unit)), 1, ()
            else:
                errors = []
                # Get f0 and, if needed, f1.
                try: f0 = parse_date(form[prefix+'_f0'])
                except ValueError, err: errors.append(str(err))
                if rule in ('inside','outside'):
                    try: f1 = parse_date(form[prefix+'_f1'])
                    except ValueError, err: errors.append(str(err))
                # Validate the rule.
                if errors: return (), 1, errors
                elif rule in ('before','after'):
                    return (kind, rule, f0), 1, ()
                elif rule in ('inside','outside'):
                    return (kind, rule, (f0, f1)), 1, ()
                else: raise KeyError('bad date rule: %r' % rule)
        else: raise KeyError('bad kind: %r' % kind)

def _build_filter_query(tree):
    kind, rule, data = tree
    if kind == 'sub':
        is_or = rule in ('or','nor')
        query = Q()
        for subtree in data:
            subquery = _build_filter_query(subtree)
            if is_or: query |= subquery
            else: query &= subquery
        if rule in ('nor','nand'): query = ~Q(query)
        return query
    elif kind in ('title','album','artist'):
        negate = rule.startswith('not')
        if negate: rule = rule[3:]
        if rule == 'in': query = Qu(kind, 'icontains', data)
        elif rule == 'start': query = Qu(kind, 'istartswith', data)
        elif rule == 'end': query = Qu(kind, 'iendswith', data)
        elif rule == 'is': query = Qu(kind, 'iexact', data)
        if negate: return ~Q(query)
        else: return query
    elif kind in ('time','track','play_count'):
        if rule in ('lte','gte'): return Qu(kind, rule, data)
        elif rule == 'is': return Qu(kind, 'exact', data)
        elif rule == 'notis': return ~Q(Qu(kind, 'exact', data))
        elif rule == 'inside': return Qu(kind, 'range', data)
        elif rule == 'outside':
            return Qu(kind, 'lt', data[0]) | Qu(kind, 'gt', data[1])
    elif kind in ('date_added','last_queued'):
        if rule in ('last','nolast'):
            number, unit = data
            if unit == 'hour': delta = datetime.timedelta(0,3600)
            elif unit == 'day': delta = datetime.timedelta(1)
            elif unit == 'week': delta = datetime.timedelta(7)
            elif unit == 'month': delta = datetime.timedelta(30.43685)
            elif unit == 'year': delta = datetime.timedelta(365.24220)
            date = datetime.datetime.now() - number * delta
            if rule == 'last': return Qu(kind, 'gte', date)
            else: return Qu(kind, 'lt', date)
        else:
            if rule == 'before': return Qu(kind, 'lt', data)
            elif rule == 'after': return Qu(kind, 'gt', data)
            elif rule == 'inside': return Qu(kind, 'range', data)
            elif rule == 'outside':
                return Qu(kind, 'lt', data[0]) | Qu(kind, 'gt', data[1])

def filter_search(request):
    try: tree,total,errors = _build_filter_tree(request.GET, 'k')
    except KeyError, err: return html_error(request, message=str(errors))
    if errors: return html_error(request, message=str(errors)) #raise Http404  # TODO error (human's fault)
    if total == 0: queryset = ()
    else: queryset = Song.visibles.filter(_build_filter_query(tree))
    return render_html_template('filter_results.html', request,
                                {'song_list':queryset,
                                 'criterion_count':total},
                              context_instance=RequestContext(request))
