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
    barcode = models.CharField(max_length=50, unique=True)

    type = models.ForeignKey(SampleType, blank=True, null=True)
    quantity = models.CharField(max_length=50, blank=True, null=True)

    project = models.ForeignKey(Project, blank=True, null=True)

    hospital = models.TextField(blank=True, null=True)
    subject = models.ForeignKey(SubjectInfo, blank=True, null=True)

    date_sampling = models.DateTimeField(blank=True, null=True)
    date_receive = models.DateTimeField(blank=True, null=True)
    date_deadline = models.DateTimeField(blank=True, null=True)

    has_request_note = models.BooleanField(default=True)
    has_informed_note = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_receive']

    def __str__(self):
        return f'{self.barcode}({self.name})'


class DNAExtractStep(models.Model):
    STATUS = 'DNA_extracted'

    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    def __str__(self):
        return f'操作人: {self.operator}'


class LibBuildStep(models.Model):
    STATUS = 'lib_build'

    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    def __str__(self):
        return f'操作人: {self.operator}'


class SequencingStep(models.Model):
    STATUS = 'seq'

    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    index1_seq = models.CharField(max_length=20, blank=True, null=True)
    index2_seq = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'操作人: {self.operator}'


class BioInfoStep(models.Model):
    STATUS = 'bioinfo'

    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    def __str__(self):
        return f'操作人: {self.operator}'


class ReportStep(models.Model):
    STATUS = 'report'

    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    def __str__(self):
        return f'操作人: {self.operator}'


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

    dna_extract_step = models.ForeignKey(DNAExtractStep, blank=True, null=True)

    lib_build_step = models.ForeignKey(LibBuildStep, blank=True, null=True)

    sequencing_step = models.ForeignKey(SequencingStep, blank=True, null=True)

    bioinfo_step = models.ForeignKey(BioInfoStep, blank=True, null=True)

    report_step = models.ForeignKey(ReportStep, blank=True, null=True)
