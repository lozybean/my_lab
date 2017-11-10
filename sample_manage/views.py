import datetime

from django.contrib import auth
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.utils.html import escape
from sample_manage import models
from sample_manage.form import (LoginForm, SampleInfoForm, SubjectInfoForm)
from sample_manage.models import SampleInfo, SubjectInfo, UserProfile, SamplePipe
from sample_manage.utils import get_auth_user


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
    return render(request, 'sample_info.html', {'sample': sample, 'is_auth': auth_user})


def sample_list(request):
    auth_user = get_auth_user(request)
    samples = get_list_or_404(SampleInfo)
    return render(request, 'sample_list.html', {'sample_list': samples, 'is_auth': auth_user})


def query_sample_by_project(request, project_id):
    auth_user = get_auth_user(request)
    samples = get_list_or_404(SampleInfo, project__id=project_id)
    return render(request, 'sample_list.html', {'sample_list': samples, 'is_auth': auth_user})


def query_sample_by_status(request, status):
    auth_user = get_auth_user(request)
    samples = get_list_or_404(SampleInfo, sample_pipe__status=status)
    return render(request, 'sample_list.html', {'sample_list': samples, 'is_auth': auth_user})


def query_sample_by_date(request, step, year, month, day, status=None):
    auth_user = get_auth_user(request)
    query_date = datetime.date(int(year), int(month), int(day))
    if step == 'sample_received':
        kwargs = {
            f'date_receive__date': query_date
        }
    else:
        kwargs = {
            f'sample_pipe__{step.lower()}__{status}__date': query_date
        }
    samples = get_list_or_404(SampleInfo, **kwargs)
    return render(request, 'sample_list.html', {'sample_list': samples, 'is_auth': auth_user})


def subject_info(request, subject_id):
    subject = get_object_or_404(SubjectInfo, id=subject_id)
    samples = SampleInfo.objects.filter(subject=subject)
    if subject.family:
        family = SubjectInfo.objects.filter(family=subject.family)
    else:
        family = None
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
            sample_pipe = SamplePipe()
            sample_pipe.status = 'sample_received'
            sample_pipe.save()
            sample = form.instance
            sample.sample_pipe = sample_pipe
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


def get_step_names(step_name):
    step_list = SamplePipe.STEPS
    current_step_name = f'{step_name.lower()}_step'
    step_index = step_list.index(current_step_name)
    if step_index - 1 >= 0:
        previous_step_name = step_list[step_index - 1]
    else:
        previous_step_name = None
    return previous_step_name, current_step_name


def get_sample_pipe_tasks(request, step_name):
    auth_user = get_auth_user(request)
    previous_step_name, current_step_name = get_step_names(step_name)
    kwargs = {
        f'sample_pipe__{current_step_name}__begin__isnull': True,
    }
    if previous_step_name:
        kwargs[f'sample_pipe__{previous_step_name}__end__isnull'] = False
    samples = SampleInfo.objects.filter(**kwargs)
    if samples:
        return render(request, 'sample_pipe.html', {'sample_list': samples, 'is_auth': auth_user,
                                                    'step_name': step_name, 'status': 'begin'})
    else:
        return redirect(message, message_text='没有相关任务！')


def get_sample_pipe_processing(request, step_name):
    auth_user = get_auth_user(request)
    previous_step_name, current_step_name = get_step_names(step_name)
    kwargs = {
        f'sample_pipe__{current_step_name}__begin__isnull': False,
        f'sample_pipe__{current_step_name}__end__isnull': True,
    }
    samples = SampleInfo.objects.filter(**kwargs)
    if samples:
        return render(request, 'sample_pipe.html', {'sample_list': samples, 'is_auth': auth_user,
                                                    'step_name': step_name, 'status': 'end'})
    else:
        return redirect(message, message_text='没有进行中的样本！')


def start_sample_pipe(request, step_name):
    auth_user = get_auth_user(request)
    previous_step_name, current_step_name = get_step_names(step_name)

    current_time = datetime.datetime.now()
    sample_id_list = request.POST.getlist('sample_list')
    samples = SampleInfo.objects.filter(id__in=sample_id_list)
    for sample in samples:
        sample_pipe = sample.sample_pipe
        step = getattr(sample_pipe, current_step_name)
        if step is None:
            # 步骤尚未开始
            step_model_name = current_step_name.title().replace('_', '')
            step_model = getattr(models, step_model_name)
            step = step_model()
        # 修改步骤状态
        step.begin = current_time
        step.operator = auth_user
        step.save()
        # 修改流程状态
        setattr(sample_pipe, current_step_name, step)
        sample_pipe.status = step_name
        sample_pipe.save()
        # 修改样本状态
        sample.sample_pipe = sample_pipe
        sample.save()
    # 重定向到任务中样本
    return get_sample_pipe_processing(request, step_name)


def finish_sample_pipe(request, step_name):
    auth_user = get_auth_user(request)
    previous_step_name, current_step_name = get_step_names(step_name)

    current_time = datetime.datetime.now()
    sample_id_list = request.POST.getlist('sample_list')
    samples = SampleInfo.objects.filter(id__in=sample_id_list)
    for sample in samples:
        sample_pipe = sample.sample_pipe
        step = getattr(sample_pipe, current_step_name)
        # 修改步骤状态
        step.end = current_time
        if step.operator != auth_user:
            return redirect(message(request, '操作人员不符合，请使用开始操作的账号登录'))
        step.save()
        # 修改流程状态
        setattr(sample_pipe, current_step_name, step)
        sample_pipe.save()
        # 修改样本状态
        sample.sample_pipe = sample_pipe
        sample.save()
    # 重定向到新的任务
    return get_sample_pipe_tasks(request, step_name)


def sample_pipe_list(request, step_name, status='begin'):
    if request.method == 'GET':
        if status == 'begin':
            return get_sample_pipe_tasks(request, step_name)
        elif status == 'end':
            return get_sample_pipe_processing(request, step_name)
        else:
            redirect(message, message_text='状态错误，请重试！')
    else:
        if status == 'begin':
            return start_sample_pipe(request, step_name)
        elif status == 'end':
            return finish_sample_pipe(request, step_name)
        else:
            redirect(message, message_text='状态错误，请重试！')
