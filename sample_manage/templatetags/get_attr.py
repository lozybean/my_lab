import re
import sys

from django import template

numeric_test = re.compile("^\d+$")
register = template.Library()


@register.filter(is_safe=True)
def get_attr(value, arg):
    """Gets an attribute of an object dynamically from a string name"""

    if hasattr(value, str(arg)):
        print('in get_attr', getattr(value, arg), file=sys.stdout)
        return getattr(value, arg)
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        raise AttributeError(f"{value} do not have such a attr: {arg}")
