from datetimewidget.widgets import DateTimeWidget
from django import forms
from sample_manage.models import SampleInfo, SampleType, Project, SubjectInfo


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
                'field_class': 'col-md-2'
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

    class Meta:
        model = SampleInfo
        fields = ['name', 'barcode', 'type', 'quantity', 'project',
                  'hospital', 'subject', 'date_receive', 'date_sampling', 'date_deadline']
