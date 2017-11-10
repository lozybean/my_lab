import datetime

from annoying.functions import get_object_or_None
from django.contrib import auth
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.utils.html import escape
from sample_manage import models
from sample_manage.form import (LoginForm, SampleInfoForm, SubjectInfoForm)
from sample_manage.models import SampleInfo, SubjectInfo, SamplePipe, Project, SampleType, SequencingStep
from sample_manage.utils import get_auth_user, get_user_profile, check_permission, get_primary_task


# Create your views here.

def home(request):
    user = get_auth_user(request)
    if user and user.is_authenticated:
        primary_task = get_primary_task(request)
        return redirect(task, primary_task=primary_task, status='begin')
    else:
        return redirect(login)


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
                return redirect(home)
            else:
                return render(request, 'login.html', {'form': form, 'password_is_wrong': True})
        else:
            return render(request, 'login.html', {'form': form})


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect(login)


def message(request, message_text):
    return render(request, 'message.html', {'message': message_text, })


def user_info(request):
    user_profile = get_user_profile(request)
    if not user_profile:
        return redirect(login)
    return render(request, 'user_profile.html')


def sample_info(request, sample_id):
    sample = get_object_or_404(SampleInfo, id=sample_id)
    projects = Project.objects.all()
    sample_types = SampleType.objects.all()
    return render(request, 'sample_info.html', {'sample': sample, 'projects': projects,
                                                'sample_types': sample_types})


def sample_list(request):
    samples = get_list_or_404(SampleInfo)
    return render(request, 'sample_list.html', {'sample_list': samples})


def query_sample_by_project(request, project_id):
    samples = get_list_or_404(SampleInfo, project__id=project_id)
    return render(request, 'sample_list.html', {'sample_list': samples})


def query_sample_by_status(request, status):
    samples = get_list_or_404(SampleInfo, sample_pipe__status=status)
    return render(request, 'sample_list.html', {'sample_list': samples})


def query_sample_by_date(request, step, year, month, day, status=None):
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
    return render(request, 'sample_list.html', {'sample_list': samples})


def query_sample_by_barcode(request):
    print(request.method)
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        print(barcode)
        sample = get_object_or_None(SampleInfo, barcode=barcode)
        return redirect(sample_info, sample_id=sample.id)
    else:
        return redirect(home)


def subject_info(request, subject_id):
    if not check_permission(request, 'subject_view'):
        return redirect(message, message_text='你没有权限进行该操作')
    subject = get_object_or_404(SubjectInfo, id=subject_id)

    samples = SampleInfo.objects.filter(subject=subject)
    if subject.family:
        family = SubjectInfo.objects.filter(family=subject.family)
    else:
        family = None
    return render(request, 'subject_info.html', {'subject': subject,
                                                 'sample_list': samples, 'family': family})


def subject_list(request):
    subjects = get_list_or_404(SubjectInfo)
    return render(request, 'subject_list.html', {'subject_list': subjects})


def sample_input(request, sample_id=None):
    if not check_permission(request, 'sample_receive'):
        return redirect(message, message_text='你没有权限进行该操作')
    if request.method == 'GET':
        if sample_id is None:
            form = SampleInfoForm()
        else:
            sample = get_object_or_None(SampleInfo, id=sample_id)
            if sample is None:
                form = SampleInfoForm()
            else:
                form = SampleInfoForm(instance=sample)
        return render(request, 'form_input.html', {'form': form})
    else:
        form = SampleInfoForm(request.POST)
        if form.is_valid():
            sample_pipe = SamplePipe()
            sample_pipe.status = 'sample_receive'
            sample_pipe.save()
            sample = form.instance
            sample.sample_pipe = sample_pipe
            form.save()
            return redirect(message, message_text=escape('样本登记成功！'))

        else:
            return render(request, 'form_input.html', {'form': form})


def subject_input(request, subject_id=None):
    if not check_permission(request, 'subject_input'):
        return redirect(message, message_text='你没有权限进行该操作')
    if request.method == 'GET':
        if subject_id is None:
            form = SubjectInfoForm()
        else:
            subject = get_object_or_None(SubjectInfo, id=subject_id)
            if subject is None:
                form = SubjectInfoForm()
            else:
                form = SubjectInfoForm(instance=subject)
        return render(request, 'form_input.html', {'form': form})
    else:
        form = SubjectInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(message, message_text=escape('受检者登记成功！'))
        else:
            return render(request, 'form_input.html', {'form': form})


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
    previous_step_name, current_step_name = get_step_names(step_name)
    kwargs = {
        f'sample_pipe__{current_step_name}__begin__isnull': True,
    }
    if previous_step_name:
        kwargs[f'sample_pipe__{previous_step_name}__end__isnull'] = False
    samples = SampleInfo.objects.filter(**kwargs)
    if samples:
        return render(request, 'sample_pipe.html', {'sample_list': samples,
                                                    'step_name': step_name, 'status': 'begin'})
    else:
        return render(request, 'sample_pipe.html', {'sample_list': samples,
                                                    'step_name': step_name, 'status': 'begin',
                                                    'message': '没有相关任务'})


def get_sample_pipe_processing(request, step_name):
    previous_step_name, current_step_name = get_step_names(step_name)
    kwargs = {
        f'sample_pipe__{current_step_name}__begin__isnull': False,
        f'sample_pipe__{current_step_name}__end__isnull': True,
    }
    samples = SampleInfo.objects.filter(**kwargs)
    if samples:
        return render(request, 'sample_pipe.html', {'sample_list': samples,
                                                    'step_name': step_name, 'status': 'end'})
    else:
        return render(request, 'sample_pipe.html', {'sample_list': samples,
                                                    'step_name': step_name, 'status': 'end',
                                                    'message': '没有进行中的样本'})


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


def get_index_seq(request, sample_id_list):
    samples = SampleInfo.objects.filter(id__in=sample_id_list)
    return render(request, 'input_index_seq.html', {'sample_list': samples})


def set_index_seq(request):
    auth_user = get_auth_user(request)
    index1_list = request.POST.getlist('index1_list')
    index2_list = request.POST.getlist('index2_list')
    current_time = datetime.datetime.now()
    sample_id_list = request.POST.getlist('sample_list')
    for ind, sample_id in enumerate(sample_id_list):
        sample = get_object_or_None(SampleInfo, id=sample_id)
        if sample is None:
            continue
        sample_pipe = sample.sample_pipe
        # 保存index序列
        sequencing = SequencingStep()
        sequencing.index1_seq = index1_list[ind]
        sequencing.index2_seq = index2_list[ind]
        sequencing.operator = auth_user
        sequencing.begin = current_time
        sequencing.save()
        # 修改流程状态
        sample_pipe.sequencing_step = sequencing
        sample_pipe.status = 'sequencing'
        sample_pipe.save()
        # 修改样本状态
        sample.sample_pipe = sample_pipe
        sample.save()
    # 重定向到新的任务
    return get_sample_pipe(request, 'sequencing', 'end')


def sequencing_step_info(request, sample_id=None):
    if not check_permission(request, 'sequencing'):
        return redirect(message, message_text='你没有权限进行该操作')
    if request.method == 'GET':
        if sample_id is None:
            return redirect(home)
        else:
            return get_index_seq(request, [sample_id])
    else:
        set_pipe_info = request.POST.get('set_pipe_info', True)
        if set_pipe_info == '0' or set_pipe_info == 0:
            sample_id_list = request.POST.getlist('sample_list')
            return get_index_seq(request, sample_id_list)
        else:
            return set_index_seq(request)


def get_sample_pipe(request, step_name, status):
    if status == 'begin':
        return get_sample_pipe_tasks(request, step_name)
    elif status == 'end':
        return get_sample_pipe_processing(request, step_name)
    else:
        return redirect(message, message_text='状态错误，请重试！')


def set_sample_pipe(request, step_name, status):
    if status == 'begin':
        if step_name == 'sequencing':
            return sequencing_step_info(request)
        else:
            return start_sample_pipe(request, step_name)
    elif status == 'end':
        return finish_sample_pipe(request, step_name)
    else:
        return redirect(message, message_text='状态错误，请重试！')


def sample_pipe_list(request, step_name, status='begin'):
    if not check_permission(request, step_name):
        return redirect(message, message_text='你没有权限进行该操作')
    if request.method == 'GET':
        return get_sample_pipe(request, step_name, status)
    else:
        return set_sample_pipe(request, step_name, status)


def task(request, primary_task, status):
    if primary_task == 'sample_receive':
        return redirect(subject_input)
    if not primary_task:
        return message(request, '尚未设置主要任务')
    return sample_pipe_list(request, primary_task, status)
