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
def reverse_name(name):
    """
    "Smith, John" => "John Smith"
    """
    last, first = name.split(', ')
    return first+' '+last

@register.simple_tag
def make_stars(rating):
    if rating >= 5.75:
        return ("<img src="+reverse('venclave-images', args=['star_green_full.png'])+"/>") * 5
    html = ("<img src="+reverse('venclave-images', args=['star_yellow_full.png'])+"/>") * int(rating)
    if .25 < (rating % 1 ) < .75:
        html += "<img src="+reverse('venclave-images', args=['star_yellow_half.png'])+"/>"
    return html

