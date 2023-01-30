from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(needs_autoescape=False)
@stringfilter
def format_err(error, autoescape=False):

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    result = error.replace('рассылки', '').replace('Название', 'названием')
    return mark_safe(esc(result))

@register.filter(needs_autoescape=True)
@stringfilter
def cutlastchar(text, autoescape=True):

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    result = text[:-1]
    return mark_safe(esc(result))