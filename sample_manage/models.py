from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.db import models


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.get_username()


class Project(models.Model):
    name = models.TextField(null=True, blank=True)

    period_day = models.IntegerField()

    def __str__(self):
        return self.name


class FamilyInfo(models.Model):
    proband = models.CharField(max_length=100)

    def __str__(self):
        return f"先证者：{self.proband}"


class SubjectInfo(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=(('male', '男'), ('female', '女')))
    age = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=20, default='汉族')
    native_place = models.CharField(max_length=10)
    diagnosis = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)

    family = models.ForeignKey(FamilyInfo)
    relation_ship = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']


class SampleType(models.Model):
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type


class SampleInfo(models.Model):
    name = models.CharField(max_length=20)
    barcode = models.CharField(max_length=50)

    type = models.ForeignKey(SampleType, blank=True, null=True)
    quantity = models.CharField(max_length=50, blank=True, null=True)

    project = models.ForeignKey(Project, blank=True, null=True)

    hospital = models.TextField(blank=True, null=True)
    subject = models.ForeignKey(SubjectInfo, blank=True, null=True)

    index1_seq = models.CharField(max_length=20, blank=True, null=True)
    index2_seq = models.CharField(max_length=20, blank=True, null=True)

    date_sampling = models.DateTimeField(blank=True, null=True)
    date_receive = models.DateTimeField(blank=True, null=True)
    date_deadline = models.DateTimeField(blank=True, null=True)

    has_request_note = models.BooleanField(default=True)
    has_informed_note = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_receive']

    def __str__(self):
        return self.name


class SamplePipe(models.Model):
    STATUS = (('sample_received', '收样'),
              ('DNA_extracted', 'DNA提取'),
              ('lib_build', '文库构建'),
              ('seq', '上机'),
              ('bioinfo', '生信分析'),
              ('report', '报告撰写'),)

    sample = models.ForeignKey(SampleInfo)
    latest = models.BooleanField(default=True)

    status = models.CharField(max_length=30, choices=STATUS, default='sample_received')

    date_dna_extract_begin = models.DateTimeField(blank=True, null=True)
    date_dna_extract_end = models.DateTimeField(blank=True, null=True)
    operator_dna_extract = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                             related_name='%(app_label)s_%(class)s_dna_extract')

    date_lib_build_begin = models.DateTimeField(blank=True, null=True)
    date_lib_build_end = models.DateTimeField(blank=True, null=True)
    operator_lib_build = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                           related_name='%(app_label)s_%(class)s_lib_build')

    date_sequencing_begin = models.DateTimeField(blank=True, null=True)
    date_sequencing_end = models.DateTimeField(blank=True, null=True)
    operator_sequencing = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                            related_name='%(app_label)s_%(class)s_sequencing')

    date_bioinfo_begin = models.DateTimeField(blank=True, null=True)
    date_bioinfo_end = models.DateTimeField(blank=True, null=True)
    operator_bioinfo = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                         related_name='%(app_label)s_%(class)s_bioinfo')

    date_report_begin = models.DateTimeField(blank=True, null=True)
    date_report_end = models.DateTimeField(blank=True, null=True)
    operator_report = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                        related_name='%(app_label)s_%(class)s_report')
