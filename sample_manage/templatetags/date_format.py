from datetime import datetime

from django import template

register = template.Library()


@register.filter(is_safe=True)
def date_format(d: datetime, format='%Y/%m/%d %H:%M:%S'):
    if d is None or d == 'None' or d == '':
        return d
    return d.strftime(format)
