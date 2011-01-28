#!/usr/bin/env python

from __future__ import division

from django.template import Library
from django.template import Context
from django.template.loader import get_template
from django.core.urlresolvers import reverse


register = Library()

@register.simple_tag
def facet(attribute):
    type = attribute.facet_type
    choices = attribute.get_choices()
    t = get_template('facets/%s.html' % type)
    return t.render(Context({'attribute': attribute}))


@register.simple_tag
def comma_separated(items, alt_text=""):
    items = list(items)
    if not items:
        return alt_text
    return ', '.join(str(item) for item in items)


@register.simple_tag
def make_stars(rating):
    if not rating:
        return ""
    if rating >= 4.75:
        url = reverse('venclave-images', args=['star_green_full.png'])
        return ('<img src="%s"/>' % url) * 5
    url = reverse('venclave-images', args=['star_yellow_full.png'])
    html = ('<img src="%s"/>' % url) * int(rating)
    if .25 < (rating % 1 ) < .75:
        url = reverse('venclave-images', args=['star_yellow_half.png'])
        html += '<img src="%s"/>' % url
    return html


@register.filter
def rating(rating):
    """Map None to the empty string."""
    if not rating:
        return "??"
    return rating


@register.filter
def mins_to_hours(mins):
    """Convert a number of minutes into hours:mins."""
    if not mins:
        return ""
    try:
        mins = int(mins)
    except (ValueError, TypeError):
        return ""
    hours = mins // 60
    mins = mins % 60
    return "%d:%02d" % (hours, mins)


@register.filter
def ex_braces(content):
    """Wrap text in braces for exhibit.

    Django has no way to escape braces in its template syntax, and Exhibit uses
    expressions like {{.label}} for its ex:*-subcontent attributes.  This
    is used to, for example, generate a URL from the item in the lens.

    See: http://simile.mit.edu/wiki/Exhibit/Dynamic_URLs

    This filter exists to wrap text in double curly braces that will make it
    past Django and be visible to Exhibit.  The official way to do this with
    django is to use {% templatetag openvariable %} to emit a literal {{.  This
    is less than ideal, so we use the filter approach.
    """
    return "{{" + content + "}}"
