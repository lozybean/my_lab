from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def display_none(v, default='空'):
    if v is None or v == 'None':
        return mark_safe(default)
    else:
        return mark_safe(v)

