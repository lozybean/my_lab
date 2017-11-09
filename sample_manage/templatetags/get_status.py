from django import template

register = template.Library()


@register.filter(name='get_status')
def get_status(pipe, step_name):
    for status in pipe.STATUS:
        if f'{status[0]}_step' == step_name:
            return status[1]
    return '未知'
