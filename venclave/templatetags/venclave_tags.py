from django.template import Library
from django.template import Context
from django.template.loader import get_template

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
