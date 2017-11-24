import re
from datetime import datetime

import simplejson as json
from annoying.functions import get_object_or_None
from django.contrib import auth
from lxml import objectify
from sample_manage.form import SubjectInfoForm
from sample_manage.models import UserProfile, SamplePipe, SampleInfo, SampleType, Project
from suds.client import Client


class objectJSONEncoder(json.JSONEncoder):
    """A specialized JSON encoder that can handle simple lxml objectify types
        >>> from lxml import objectify
        >>> obj = objectify.fromstring("<Book><price>1.50</price><author>W. Shakespeare</author></Book>")
        >>> objectJSONEncoder().encode(obj)
        '{"price": 1.5, "author": "W. Shakespeare"}'
   """

    def default(self, o):
        if isinstance(o, objectify.IntElement):
            return int(o)
        if isinstance(o, objectify.NumberElement) or isinstance(o, objectify.FloatElement):
            return float(o)
        if isinstance(o, objectify.ObjectifiedDataElement):
            return str(o)
        if hasattr(o, '__dict__'):
            # For objects with a __dict__, return the encoding of the __dict__
            return o.__dict__
        return json.JSONEncoder.default(self, o)


class LimsClient(object):
    ClientID = 'SAMSUNG GENOMICS'
    ClientGUID = '1D2FBD86-3AC7-4EB9-B2FA-0F4D45C5CF11'
    client = Client('http://report.dalabs.cn/RasClientDetail.asmx?wsdl')

    def get_info_by_barcode(self, barcode):
        response = self.client.service.GetCheckPData(self.ClientID, self.ClientGUID, barcode)
        response = f'<result>{response}</result>'
        xml_object = objectify.fromstring(response)
        if not hasattr(xml_object.ResultsDataSet, 'Table'):
            return None
        json_object = objectJSONEncoder().encode(xml_object.ResultsDataSet.Table)
        return json.loads(json_object)


lims_client = LimsClient()


def get_sample_type_or_create(type_name):
    sample_type = get_object_or_None(SampleType, type=type_name)
    if sample_type is None:
        sample_type = SampleType()
        sample_type.type = type_name
        sample_type.save()
    return sample_type


def get_project_or_create(project_name):
    project = get_object_or_None(Project, name=project_name)
    if project is None:
        project = Project()
        project.name = project_name
        project.save()
    return project


def translate_gender(gender_in_chinese):
    gender_translator = {'男': 'male', '女': 'female'}
    return gender_translator.get(gender_in_chinese, '')


def get_age_num(age_description):
    age_num = re.search('(\d+)', age_description).group(1)
    return int(age_num)


def get_sample_from_lims(barcode: str):
    lims_info = lims_client.get_info_by_barcode(barcode)
    if lims_info is None:
        return None
    lims_info_custom = json.loads(lims_info['CUSTOM_FIELD'])

    sample = SampleInfo()

    sample.name = ''
    sample.barcode = barcode
    sample.hospital = lims_info['ORD_INST_NM']
    sample.type = get_sample_type_or_create(lims_info['SPCM_TY'])
    sample.quantity = lims_info_custom['样本量']
    sample.project = get_project_or_create(lims_info['ORD_NM'])

    sample.date_sampling = datetime.strptime(lims_info['SPCM_REG_DT'], '%Y-%m-%d')
    sample.date_receive = datetime.now()

    return sample


def get_subject_from_lims(barcode: str):
    lims_info = lims_client.get_info_by_barcode(barcode)
    if lims_info is None:
        return None
    lims_info_custom = json.loads(lims_info['CUSTOM_FIELD'])

    subject_form = SubjectInfoForm()
    subject = subject_form.save(commit=False)
    subject.name = lims_info['PTNT_NM']
    subject.gender = translate_gender(lims_info['PTNT_SEX'])
    subject.age = get_age_num(lims_info['PTNT_AGE'])
    subject.diagnosis = lims_info_custom['病理诊断']
    subject.family_history = lims_info_custom['家族史']
    subject.nationality = lims_info['NATION'].strip()
    return subject


def get_auth_user(request):
    if request.user.is_authenticated():
        auth_user = auth.get_user(request)
    else:
        auth_user = False
    return auth_user


def get_user_profile(request):
    user = get_auth_user(request)
    if not user:
        return False
    return UserProfile.objects.filter(user=user).first()


def check_permission(request, operation):
    user_profile = get_user_profile(request)
    if not user_profile:
        return False
    return getattr(user_profile, operation)


def get_primary_task(request):
    user_profile = get_user_profile(request)
    if not user_profile:
        return None
    return user_profile.primary_task


def get_step_names(step_name):
    step_list = SamplePipe.STEPS
    current_step_name = f'{step_name.lower()}_step'
    step_index = step_list.index(current_step_name)
    if step_index - 1 >= 0:
        previous_step_name = step_list[step_index - 1]
    else:
        previous_step_name = None
    return previous_step_name, current_step_name
