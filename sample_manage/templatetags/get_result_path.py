from django import template

register = template.Library()


@register.filter(is_safe=True)
def get_result_path(sequencing_step):
    if sequencing_step is None:
        return ''
    try:
        seq_date = sequencing_step.begin.strftime('%Y-%m-%d')
    except (AttributeError, TypeError):
        return ''
    return f'/mnt/analysis/{sequencing_step.sequencer}/{seq_date}'
