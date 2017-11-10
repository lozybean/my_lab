from django import template
from sample_manage.models import SamplePipe

register = template.Library()


@register.filter(name='get_status')
def get_status(step_name):
    if step_name.endswith('_step'):
        step_name = step_name[:-5]
    for status in SamplePipe.STATUS:
        if status[0] == step_name:
            print(status[1])
            return status[1]
    return '未知'
