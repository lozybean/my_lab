from annoying.functions import get_object_or_None
from django.contrib import auth
from django.shortcuts import get_list_or_404
from sample_manage.models import SampleInfo, SamplePipe


def get_auth_user(request):
    if request.user.is_authenticated():
        auth_user = auth.get_user(request)
    else:
        auth_user = False
    return auth_user


def get_samples_with_pipe(can_be_none=True, **kwargs):
    def pipe_filter(pipe):
        if can_be_none:
            return True
        elif pipe is not None:
            return True
        else:
            return False

    samples = get_list_or_404(SampleInfo)
    sample_pipes = [get_object_or_None(SamplePipe, sample=sample, latest=True, **kwargs) for sample in samples]
    samples = [(sample, sample_pipe) for sample, sample_pipe in zip(samples, sample_pipes)
               if pipe_filter(sample_pipe)]
    return samples
