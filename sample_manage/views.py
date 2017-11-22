import datetime

from annoying.functions import get_object_or_None
from django.contrib import auth
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.urls import reverse_lazy
from django.utils.html import escape
from django.views import generic
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from sample_manage import models
from sample_manage.form import (LoginForm, SampleInfoForm, SubjectInfoForm, SampleTypeForm, ProjectForm,
                                FamilyInfoForm)
from sample_manage.models import SampleInfo, SubjectInfo, SamplePipe, Project, SampleType
from sample_manage.utils import (get_auth_user, get_user_profile, check_permission,
                                 get_primary_task, get_step_names, get_sample_from_lims,
                                 get_subject_from_lims)


# Create your views here.

class AuthCheckView(View):
    @staticmethod
    def is_auth(request):
        user = get_auth_user(request)
        if user and user.is_authenticated:
            return True


class Home(AuthCheckView):
    def get(self, request):
        if self.is_auth(request):
            primary_task = get_primary_task(request)
            return redirect('task', primary_task=primary_task, status='begin')
        else:
            return redirect('login')


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return self.render_to_response({'form': form})

    def form_valid(self, form, request):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return super().form_valid(form)
        else:
            return self.render_to_response({'form': form, 'password_is_wrong': True})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)


class LogoutView(AuthCheckView):
    def get(self, request):
        if self.is_auth(request):
            auth.logout(request)
        return redirect('login')


class MessageView(TemplateView):
    template_name = 'message.html'

    def get_context_data(self, **kwargs):
        return {'message': escape(kwargs['message_text'])}


class UserInfoView(TemplateView):
    template_name = 'user_profile.html'

    def get(self, request, *args, **kwargs):
        user_profile = get_user_profile(request)
        if not user_profile:
            return redirect('login')
        return super().get(request)


class SampleInfoView(TemplateView):
    template_name = 'sample_info.html'

    def get_context_data(self, sample_id, **kwargs):
        context = super(SampleInfoView, self).get_context_data(**kwargs)
        sample = get_object_or_404(SampleInfo, id=sample_id)
        projects = Project.objects.all()
        sample_types = SampleType.objects.all()
        context.update(**{'sample': sample, 'projects': projects,
                          'sample_types': sample_types})
        return context

    def post(self, request, **kwargs):
        barcode = request.POST.get('barcode')
        sample = get_object_or_None(SampleInfo, barcode=barcode)
        if sample is None:
            return redirect('message', message_text='不存在该样本')
        context = self.get_context_data(sample.id, **kwargs)
        return self.render_to_response(context)


class SampleListView(TemplateView):
    template_name = 'sample_list.html'
    query_type = None

    @staticmethod
    def get_sample_list_by_project(project_id):
        return {'sample_list': get_list_or_404(SampleInfo, project__id=project_id)}

    @staticmethod
    def get_sample_list_by_status(status):
        return {'sample_list': get_list_or_404(SampleInfo, sample_pipe__status=status)}

    @staticmethod
    def get_sample_list_by_date(step, year, month, day, status=None):
        query_date = datetime.date(int(year), int(month), int(day))
        if step == 'sample_receive':
            kwargs = {
                f'date_receive__date': query_date
            }
        else:
            kwargs = {
                f'sample_pipe__{step.lower()}__{status}__date': query_date
            }
        return {'sample_list': get_list_or_404(SampleInfo, **kwargs)}

    def get_context_data(self, **kwargs):
        if self.query_type == 'project':
            return self.get_sample_list_by_project(kwargs['project_id'])
        if self.query_type == 'status':
            return self.get_sample_list_by_status(kwargs['status'])
        if self.query_type == 'date':
            return self.get_sample_list_by_date(kwargs['step'], kwargs['year'], kwargs['month'],
                                                kwargs['day'], kwargs['status'])
        return {'sample_list': get_list_or_404(SampleInfo)}


class SubjectInfoView(TemplateView):
    template_name = 'subject_info.html'

    def get_context_data(self, subject_id, **kwargs):
        subject = get_object_or_404(SubjectInfo, id=subject_id)

        samples = SampleInfo.objects.filter(subject=subject)
        if subject.family:
            family = SubjectInfo.objects.filter(family=subject.family)
        else:
            family = None
        return {'subject': subject, 'sample_list': samples, 'family': family}

    def get(self, request, *args, **kwargs):
        if not check_permission(request, 'view_subject'):
            return redirect('message', message_text='你没有权限进行该操作')
        return super().get(request, *args, **kwargs)


class SubjectListView(TemplateView):
    template_name = 'subject_list.html'

    def get_context_data(self, **kwargs):
        subject_list = get_list_or_404(SubjectInfo)
        return {'subject_list': subject_list}


class AddFormView(FormView):
    template_name = 'form_input.html'
    permission = None
    success_message = '录入成功'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def model_name(self):
        raise NotImplementedError("must set model_name property!")

    @model_name.setter
    def model_name(self, value):
        self.__dict__['model_name'] = value

    def get_context_data(self, **kwargs):
        context = super(AddFormView, self).get_context_data(**kwargs)
        if 'pk' in kwargs:
            sample = get_object_or_None(self.model_name, id=kwargs['pk'])
            if sample is None:
                form = self.form_class()
            else:
                form = self.form_class(instance=sample)
        else:
            form = self.form_class()
        context.update(form=form)
        return context

    def form_valid(self, form):
        form.save()
        return redirect('message', message_text=self.success_message)

    def form_invalid(self, form):
        return redirect('message', message_text='录入失败')

    def get(self, request, *args, **kwargs):
        if self.permission and not check_permission(request, self.permission):
            return redirect('message', message_text='你没有权限进行该操作')
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        if self.permission and not check_permission(request, self.permission):
            return redirect('message', message_text='你没有权限进行该操作')
        return super().post(request, *args, **kwargs)


class AddSampleInfoView(AddFormView):
    form_class = SampleInfoForm
    model_name = SampleInfo
    permission = 'sample_receive'
    success_message = '样本登记成功'

    def get_context_data(self, **kwargs):
        context = super(AddSampleInfoView, self).get_context_data(**kwargs)
        context.update(lims_search=reverse_lazy('add_sample_info'))
        barcode = self.request.GET.get('barcode', None)
        if barcode:
            sample = get_sample_from_lims(barcode)
            form = self.form_class(instance=sample)
            context.update(form=form)
        return context

    def form_valid(self, form):
        sample_pipe = SamplePipe()
        sample_pipe.status = 'sample_receive'
        sample_pipe.save()
        sample = form.instance
        sample.sample_pipe = sample_pipe
        return super().form_valid(form)


class AddSubjectInfoView(AddFormView):
    form_class = SubjectInfoForm
    model_name = SubjectInfo
    permission = 'add_subject'
    success_message = '受检者登记成功'


class BaseAddFormView(CreatePopupMixin, generic.CreateView):
    template_name = 'form_popup.html'
    permission = None
    fields = None

    def get(self, request, *args, **kwargs):
        if self.permission and not check_permission(request, self.permission):
            return redirect('message', message_text='你没有权限进行该操作')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.permission and not check_permission(request, self.permission):
            return redirect('message', message_text='你没有权限进行该操作')
        return super().post(request, *args, **kwargs)


class BaseEditFormView(UpdatePopupMixin, generic.UpdateView):
    template_name = 'form_popup.html'
    permission = None
    fields = None

    def get(self, request, *args, **kwargs):
        if self.permission and not check_permission(request, self.permission):
            return redirect('message', message_text='你没有权限进行该操作')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.permission and not check_permission(request, self.permission):
            return redirect('message', message_text='你没有权限进行该操作')
        return super().post(request, *args, **kwargs)


class AddSampleTypePopupView(BaseAddFormView):
    form_class = SampleTypeForm
    permission = 'add_sample_type'


class EditSampleTypePopupView(BaseEditFormView):
    form_class = SampleTypeForm
    model = SampleType
    permission = 'add_sample_type'


class AddProjectPopupView(BaseAddFormView):
    form_class = ProjectForm
    permission = 'add_project'


class EditProjectPopupView(BaseEditFormView):
    form_class = ProjectForm
    model = Project
    permission = 'add_project'


class AddSubjectInfoPopupView(BaseAddFormView):
    form_class = SubjectInfoForm
    permission = 'add_subject'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(lims_search=reverse_lazy('add_subject_popup'))
        barcode = self.request.GET.get('barcode', None)
        if barcode:
            sample = get_subject_from_lims(barcode)
            form = self.form_class(instance=sample)
            context.update(form=form)
        return context


class EditSubjectInfoPopupView(BaseEditFormView):
    form_class = SubjectInfoForm
    model = SubjectInfo
    permission = 'add_subject'


class AddFamilyInfoPopupView(BaseAddFormView):
    form_class = FamilyInfoForm
    permission = 'add_subject'


class EditFamilyInfoPopupView(BaseEditFormView):
    form_class = FamilyInfoForm
    model = SubjectInfo
    permission = 'add_subject'


class TaskView(View):
    def get(self, request, primary_task, status):
        if not check_permission(request, primary_task):
            return redirect('message', message_text='你没有权限进行该操作')
        if primary_task == 'sample_receive':
            return redirect('add_sample_info')
        if not primary_task:
            return redirect('message', message_text='尚未设置主要任务')
        return redirect('sample_pipe', step_name=primary_task, status=status)

    def post(self, request, primary_task, status):
        return redirect('sample_pipe', step_name=primary_task, status=status)


class SamplePipeView(TemplateView):
    template_name = 'sample_pipe.html'

    @staticmethod
    def get_context_begin(step_name):
        previous_step_name, current_step_name = get_step_names(step_name)
        kwargs = {
            f'sample_pipe__{current_step_name}__begin__isnull': True,
        }
        if previous_step_name:
            kwargs[f'sample_pipe__{previous_step_name}__end__isnull'] = False
        samples = SampleInfo.objects.filter(**kwargs)
        if samples:
            return {'sample_list': samples, 'step_name': step_name, 'status': 'begin'}
        else:
            return {'sample_list': samples, 'step_name': step_name, 'status': 'begin',
                    'message': '没有相关任务'}

    @staticmethod
    def get_context_end(step_name):
        previous_step_name, current_step_name = get_step_names(step_name)
        kwargs = {
            f'sample_pipe__{current_step_name}__begin__isnull': False,
            f'sample_pipe__{current_step_name}__end__isnull': True,
        }
        samples = SampleInfo.objects.filter(**kwargs)
        if samples:
            return {'sample_list': samples, 'step_name': step_name, 'status': 'end'}
        else:
            return {'sample_list': samples, 'step_name': step_name, 'status': 'end',
                    'message': '没有进行中的样本'}

    def get_context_data(self, **kwargs):
        context = super(SamplePipeView, self).get_context_data(**kwargs)
        if self.status == 'begin':
            context_begin = self.get_context_begin(self.step_name)
            context.update(**context_begin)
        else:
            context_end = self.get_context_end(self.step_name)
            context.update(**context_end)
        return context

    def get(self, request, *args, step_name=None, status=None, **kwargs):
        if not check_permission(request, step_name):
            return redirect('message', message_text='你没有权限进行该操作')
        self.step_name = step_name
        self.status = status
        if self.status not in ['begin', 'end']:
            return redirect('message', message_text='状态错误，请重试！')
        return super().get(request, *args, **kwargs)

    def set_pipe_begin(self, samples, current_time, auth_user):
        current_step_name = f'{self.step_name}_step'
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
            sample_pipe.status = self.step_name
            sample_pipe.save()
            # 修改样本状态
            sample.sample_pipe = sample_pipe
            sample.save()
        # 重定向到任务中样本
        return redirect('sample_pipe', step_name=self.step_name, status='end')

    def set_pipe_end(self, samples, current_time, auth_user):
        current_step_name = f'{self.step_name}_step'
        for sample in samples:
            sample_pipe = sample.sample_pipe
            step = getattr(sample_pipe, current_step_name)
            # 修改步骤状态
            step.end = current_time
            if step.operator != auth_user:
                return redirect('message', message_text='操作人员不符合，请使用开始操作的账号登录')
            step.save()
        # 重定向到新的任务
        return redirect('sample_pipe', step_name=self.step_name, status='begin')

    def post(self, request, *args, step_name=None, status=None, **kwargs):
        if not check_permission(request, step_name):
            return redirect('message', message_text='你没有权限进行该操作')
        self.step_name = step_name
        self.status = status
        auth_user = get_auth_user(request)
        current_time = datetime.datetime.now()
        sample_id_list = request.POST.getlist('sample_list')
        samples = SampleInfo.objects.filter(id__in=sample_id_list)
        if self.status == 'begin':
            return self.set_pipe_begin(samples, current_time, auth_user)
        elif self.status == 'end' and not kwargs['success']:
            if self.step_name == 'dna_extract':
                request.session['sample_list'] = sample_id_list
                return redirect('dna_extract_info')
            if self.step_name == 'lib_build':
                request.session['sample_list'] = sample_id_list
                return redirect('lib_build_info')
            return self.set_pipe_end(samples, current_time, auth_user)
        elif kwargs['success']:
            return self.set_pipe_end(samples, current_time, auth_user)
        else:
            return redirect('message', message_text='状态错误，请重试！')


class BaseSamplePipeView(TemplateView):
    step_name = None
    template_name = None

    @staticmethod
    def get_samples(sample_id_list):
        return SampleInfo.objects.filter(id__in=sample_id_list)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if kwargs['sample_id']:
            context.update(sample_list=self.get_samples([kwargs['sample_id']]))
        else:
            context.update(sample_list=self.get_samples(self.request.session.get('sample_list')))
        return context

    def get(self, request, *args, **kwargs):
        if not check_permission(request, self.step_name):
            return redirect('message', message_text='你没有权限进行该操作')
        return super().get(request, *args, **kwargs)

    def post(self, request, **kwargs):
        if not check_permission(request, self.step_name):
            return redirect('message', message_text='你没有权限进行该操作')
        return self.finish_step(request, **kwargs)

    def finish_step(self, request, **kwargs):
        raise NotImplementedError("must implement finish_step")


class DnaExtractInfoView(BaseSamplePipeView):
    step_name = 'dna_extract'
    template_name = 'step_infos/dna_extract_info.html'

    def finish_step(self, request, **kwargs):
        auth_user = get_auth_user(request)
        current_time = datetime.datetime.now()
        store_place_list = request.POST.getlist('store_place_list')
        pass_qc_list = request.POST.getlist('pass_qc_list')
        sample_id_list = request.POST.getlist('sample_list')
        for ind, sample_id in enumerate(sample_id_list):
            sample = get_object_or_None(SampleInfo, id=sample_id)
            if sample is None:
                continue
            step = getattr(sample.sample_pipe, f'{self.step_name}_step')
            # 保存index序列
            step.end = current_time
            step.store_place = store_place_list[ind]
            step.pass_qc = pass_qc_list[ind]
            if step.operator != auth_user:
                return redirect('message', message_text='操作人员不符合，请使用开始操作的账号登录')
            step.save()

        # 重定向到新的任务
        return redirect('sample_pipe', step_name=self.step_name, status='begin')


class QuantifyInfoView(BaseSamplePipeView):
    step_name = 'quantify'
    template_name = 'step_infos/quantify_info.html'

    def finish_step(self, request, **kwargs):
        auth_user = get_auth_user(request)
        current_time = datetime.datetime.now()
        store_place_list = request.POST.getlist('store_place_list')
        pass_qc_list = request.POST.getlist('pass_qc_list')
        sample_id_list = request.POST.getlist('sample_list')
        for ind, sample_id in enumerate(sample_id_list):
            sample = get_object_or_None(SampleInfo, id=sample_id)
            if sample is None:
                continue
            step = getattr(sample.sample_pipe, f'{self.step_name}_step')
            # 保存index序列
            step.end = current_time
            step.store_place = store_place_list[ind]
            step.pass_qc = pass_qc_list[ind]
            if step.operator != auth_user:
                return redirect('message', message_text='操作人员不符合，请使用开始操作的账号登录')
            step.save()

        # 重定向到新的任务
        return redirect('sample_pipe', step_name=self.step_name, status='begin')


class LibBuildInfoView(BaseSamplePipeView):
    step_name = 'lib_build'
    template_name = 'step_infos/lib_build_info.html'

    def finish_step(self, request, **kwargs):
        auth_user = get_auth_user(request)
        current_time = datetime.datetime.now()
        index1_list = request.POST.getlist('index1_list')
        index2_list = request.POST.getlist('index2_list')
        store_place_list = request.POST.getlist('store_place_list')
        pass_qc_list = request.POST.getlist('pass_qc_list')
        sample_id_list = request.POST.getlist('sample_list')
        for ind, sample_id in enumerate(sample_id_list):
            sample = get_object_or_None(SampleInfo, id=sample_id)
            if sample is None:
                continue
            step = getattr(sample.sample_pipe, f'{self.step_name}_step')
            # 保存index序列
            step.end = current_time
            step.index1_seq = index1_list[ind]
            step.index2_seq = index2_list[ind]
            step.store_place = store_place_list[ind]
            step.pass_qc = pass_qc_list[ind]
            if step.operator != auth_user:
                return redirect('message', message_text='操作人员不符合，请使用开始操作的账号登录')
            step.save()

        # 重定向到新的任务
        return redirect('sample_pipe', step_name=self.step_name, status='begin')
