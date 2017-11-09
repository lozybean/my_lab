from datetime import date

from annoying.functions import get_object_or_None
from django.contrib import auth
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.utils.html import escape
from sample_manage.form import (LoginForm, SampleInfoForm, SubjectInfoForm)
from sample_manage.models import SampleInfo, SubjectInfo, UserProfile, SamplePipe
from sample_manage.utils import get_samples_with_pipe, get_auth_user


# Create your views here.

def login(request):
    if request.method == 'GET':
        form = LoginForm()

        return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return redirect(sample_list)
            else:
                return render(request, 'login.html', {'form': form, 'password_is_wrong': True})
        else:
            return render(request, 'login.html', {'form': form})


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect(login)


def message(request, message_text):
    user = get_auth_user(request)
    return render(request, 'message.html', {'message': message_text, 'is_auth': user})


def user_info(request):
    user = get_auth_user(request)
    if not user:
        return redirect(login)
    user_profile = UserProfile.objects.filter(user=user)
    return render(request, 'user_profile.html', {'user_profile': user_profile,
                                                 'user': user, 'is_auth': user})


def sample_info(request, sample_id):
    sample = get_object_or_404(SampleInfo, id=sample_id)
    auth_user = get_auth_user(request)
    sample_pipe = get_object_or_None(SamplePipe, sample=sample, latest=True)
    print(dir(sample_pipe))
    print(sample_pipe.STEPS)
    step = getattr(sample_pipe, sample_pipe.STEPS[0])
    print(step.LABEL)
    return render(request, 'sample_info.html', {'sample': sample, 'is_auth': auth_user,
                                                'sample_pipe': sample_pipe})


def sample_list(request):
    auth_user = get_auth_user(request)
    samples = get_samples_with_pipe()
    return render(request, 'sample_list.html', {'sample_list': samples, 'is_auth': auth_user})


def query_sample_by_status(request, status):
    auth_user = get_auth_user(request)
    samples = get_samples_with_pipe(can_be_none=False, status=status)
    return render(request, 'sample_list.html', {'sample_list': samples, 'is_auth': auth_user})


def query_sample_by_date(request, step, status, year, month, day):
    auth_user = get_auth_user(request)
    kwargs = {
        f'{step.lower()}__{status}__date': date(int(year), int(month), int(day))
    }
    samples = get_samples_with_pipe(can_be_none=False, **kwargs)
    return render(request, 'sample_list.html', {'sample_list': samples, 'is_auth': auth_user})


def subject_info(request, subject_id):
    subject = get_object_or_404(SubjectInfo, id=subject_id)
    samples = SampleInfo.objects.filter(subject=subject)
    family = SubjectInfo.objects.filter(family=subject.family)
    auth_user = get_auth_user(request)
    return render(request, 'subject_info.html', {'subject': subject, 'is_auth': auth_user,
                                                 'sample_list': samples, 'family': family})


def subject_list(request):
    subjects = get_list_or_404(SubjectInfo)
    auth_user = get_auth_user(request)
    return render(request, 'subject_list.html', {'subject_list': subjects, 'is_auth': auth_user})


def sample_input(request):
    auth_user = get_auth_user(request)
    if request.method == 'GET':
        form = SampleInfoForm()
        return render(request, 'form_input.html', {'form': form, 'is_auth': auth_user})
    else:
        form = SampleInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(message, message_text=escape('样本登记成功！'))

        else:
            return render(request, 'form_input.html', {'form': form, 'is_auth': auth_user})


def subject_input(request):
    auth_user = get_auth_user(request)
    if request.method == 'GET':
        form = SubjectInfoForm()
        return render(request, 'form_input.html', {'form': form, 'is_auth': auth_user})
    else:
        form = SubjectInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(message, message_text=escape('受检者登记成功！'))
        else:
            return render(request, 'form_input.html', {'form': form, 'is_auth': auth_user})
