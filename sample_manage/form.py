import datetime

from datetimewidget.widgets import DateTimeWidget
from django import forms
from sample_manage.models import (SampleInfo, SampleType, Project, SubjectInfo,
                                  FamilyInfo)


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
    name = forms.CharField(
        required=True,
        label='样本名称',
        error_messages={'required': '必须输入样本名称'},
        widget=forms.TextInput(
            attrs={
                'placeholder': '请输入样本名称(检测名称)',
            }
        )
    )
    barcode = forms.CharField(
        required=True,
        label='样本条码',
        error_messages={'required': '必须输入样本条码',
                        'unique': '该样本条码已经存在，请核对或者修改已有样本'},
        widget=forms.TextInput(
            attrs={
                'placeholder': '请输入样本条码号',
            }
        )
    )
    type = forms.ModelChoiceField(
        label='样本类型',
        queryset=SampleType.objects
    )
    quantity = forms.CharField(
        label='样本量',
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects,
        label='项目类型',
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
    )
    date_sampling = forms.DateTimeField(
        label='采样时间',
        widget=DateTimeWidget(
            usel10n=True,
            bootstrap_version=3,
        )
    )
    date_receive = forms.DateTimeField(
        initial=datetime.datetime.now(),
        label='样本接收时间',
        widget=DateTimeWidget(
            usel10n=True,
            bootstrap_version=3,
        )
    )
    date_deadline = forms.DateTimeField(
        label='报告截止时间',
        widget=DateTimeWidget(
            usel10n=True,
            bootstrap_version=3,
        )
    )
    has_request_note = forms.BooleanField(
        label='是否有检测申请单',
        initial=True,
    )
    has_informed_note = forms.BooleanField(
        label='是否有知情同意书',
        initial=True,
    )

    class Meta:
        model = SampleInfo
        fields = ['name', 'barcode', 'type', 'quantity', 'project',
                  'hospital', 'subject', 'date_receive', 'date_sampling', 'date_deadline',
                  'has_request_note', 'has_informed_note']


class SubjectInfoForm(forms.ModelForm):
    name = forms.CharField(
        label='受检者姓名'
    )
    gender = forms.ChoiceField(
        label='性别',
        choices=(('male', '男'), ('female', '女')),
    )
    age = forms.IntegerField(
        label='年龄',
    )
    nationality = forms.CharField(
        label='名族',
        initial='汉族',
    )
    native_place = forms.CharField(
        label='籍贯',
    )
    diagnosis = forms.CharField(
        label='临床诊断',
        required=False,
        widget=forms.Textarea()
    )
    family_history = forms.CharField(
        label='家族史',
        required=False,
        widget=forms.Textarea()
    )
    family = forms.ModelChoiceField(
        label='家系',
        required=False,
        queryset=FamilyInfo.objects,
    )
    relation_ship = forms.CharField(
        label='家系关系',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': '和家系中先证者的关系',
            }
        )
    )

    class Meta:
        model = SubjectInfo
        fields = '__all__'
