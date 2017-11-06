from django.shortcuts import render, get_object_or_404
from sample_manage.models import SampleInfo


# Create your views here.

def sample_info(request, sample_id):
    sample = get_object_or_404(SampleInfo, id=sample_id)
    return render(request, 'sample_info.html', {'sample': sample})
