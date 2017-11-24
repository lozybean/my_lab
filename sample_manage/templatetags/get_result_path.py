from django import template

register = template.Library()


@register.filter(is_safe=True)
def get_result_path(sequencing_step):
    print(sequencing_step)
    seq_date = sequencing_step.begin.strftime('%Y-%m-%d')
    print(seq_date)
    return f'/mnt/analysis/{sequencing_step.sequencer}/{seq_date}'
