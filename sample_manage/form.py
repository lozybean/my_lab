import datetime

from datetimewidget.widgets import DateTimeWidget
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from sample_manage.models import (SampleInfo, SampleType, Project, SubjectInfo,
                                  FamilyInfo)
from sample_manage.widget import AddAnotherEditSelectedWidgetWrapper


class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label='用户名',
        error_messages={'required': '请输入用户名'},
        widget=forms.TextInput(
            attrs={
                'placeholder': '用户名',
            }
        ),
    )
    password = forms.CharField(
        required=True,
        label='密码',
        error_messages={'required': '请输入密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '请输入密码',
            }
        ),
    )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError('请输入正确的用户名和密码')
        else:
            super().clean()


class SampleInfoForm(forms.ModelForm):
    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode', '')
        if SampleInfo.objects.filter(barcode=barcode).exists():
            raise ValidationError("该样本条码已经存在，请核对或者修改已有样本！")
        return barcode

    type = forms.ModelChoiceField(
        label='样本类型',
        queryset=SampleType.objects,
        widget=AddAnotherEditSelectedWidgetWrapper(
            widget=forms.Select,
            add_related_url=reverse_lazy('add_sample_type_popup'),
            edit_related_url=reverse_lazy('edit_sample_type_popup', args=['__fk__']),
        )
    )
    project = forms.ModelChoiceField(
        label='项目类型',
        queryset=Project.objects,
        widget=AddAnotherEditSelectedWidgetWrapper(
            widget=forms.Select,
            add_related_url=reverse_lazy('add_project_popup'),
            edit_related_url=reverse_lazy('edit_project_popup', args=['__fk__']),
        )
    )
    hospital = forms.CharField(
        label='送检医院',
        widget=forms.TextInput(
            attrs={
                'placeholder': '送检医院/单位',
            }
        )
    )
    subject = forms.ModelChoiceField(
        label='受检者',
        queryset=SubjectInfo.objects,
        widget=AddAnotherEditSelectedWidgetWrapper(
            widget=forms.Select,
            add_related_url=reverse_lazy('add_subject_popup'),
            edit_related_url=reverse_lazy('edit_subject_popup', args=['__fk__']),
        )
    )
    date_sampling = forms.DateTimeField(
        required=True,
        label='采样时间',
        widget=DateTimeWidget(
            usel10n=True,
            bootstrap_version=3,
        )
    )
    date_receive = forms.DateTimeField(
        initial=datetime.datetime.now(),
        required=True,
        label='样本接收时间',
        widget=DateTimeWidget(
            usel10n=True,
            bootstrap_version=3,
        )
    )
    date_deadline = forms.DateTimeField(
        label='报告截止时间',
        required=False,
        widget=DateTimeWidget(
            usel10n=True,
            bootstrap_version=3,
        )
    )

    class Meta:
        model = SampleInfo
        fields = ['name', 'barcode', 'type', 'quantity', 'project',
                  'hospital', 'subject', 'date_receive', 'date_sampling', 'date_deadline',
                  'has_request_note', 'has_informed_note']


class SubjectInfoForm(forms.ModelForm):
    family = forms.ModelChoiceField(
        label='家系',
        required=False,
        queryset=FamilyInfo.objects,
        widget=AddAnotherEditSelectedWidgetWrapper(
            widget=forms.Select,
            add_related_url=reverse_lazy('add_family_popup'),
            edit_related_url=reverse_lazy('edit_family_popup', args=['__fk__']),
        )
    )

    class Meta:
        model = SubjectInfo
        fields = '__all__'


class FamilyInfoForm(forms.ModelForm):
    class Meta:
        model = FamilyInfo
        fields = '__all__'


class SampleTypeForm(forms.ModelForm):
    class Meta:
        model = SampleType
        fields = '__all__'


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
