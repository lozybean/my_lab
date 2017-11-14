from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.db import models

# Create your models here.

STATUS = (('sample_receive', '样本接收'),
          ('dna_extract', 'DNA提取'),
          ('lib_build', '文库构建'),
          ('sequencing', '上机测序'),
          ('bioinfo', '生信分析'),
          ('report', '报告撰写'),
          ('finish', '完成检测'),)


class UserProfile(models.Model):
    TASK_NAMES = STATUS[:-1]
    PERMISSIONS = [('add_subject', '受检者输入'),
                   ('view_subject', '患者信息查看'),
                   ] + list(TASK_NAMES)
    user = models.OneToOneField(User)

    primary_task = models.CharField(blank=True, max_length=30, choices=TASK_NAMES)

    # permissions:
    add_subject = models.BooleanField(default=False)
    view_subject = models.BooleanField(default=False)

    add_sample_type = models.BooleanField(default=False)

    sample_receive = models.BooleanField(default=False)
    dna_extract = models.BooleanField(default=False)
    lib_build = models.BooleanField(default=False)
    sequencing = models.BooleanField(default=False)
    bioinfo = models.BooleanField(default=False)
    report = models.BooleanField(default=False)

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

    family = models.ForeignKey(FamilyInfo, blank=True, null=True)
    relation_ship = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']


class SampleType(models.Model):
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type


class DnaExtractStep(models.Model):
    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    def __str__(self):
        return f'操作人: {self.operator}'


class LibBuildStep(models.Model):
    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    def __str__(self):
        return f'操作人: {self.operator}'


class SequencingStep(models.Model):
    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    index1_seq = models.CharField(max_length=20, blank=True, null=True)
    index2_seq = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'操作人: {self.operator}'


class BioinfoStep(models.Model):
    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    def __str__(self):
        return f'操作人: {self.operator}'


class ReportStep(models.Model):
    begin = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract')

    def __str__(self):
        return f'操作人: {self.operator}'


class SamplePipe(models.Model):
    STATUS = STATUS

    # 实际操作的步骤
    STEPS = [f'{i[0]}_step' for i in STATUS][1:-1]

    status = models.CharField(max_length=30, choices=STATUS)

    dna_extract_step = models.ForeignKey(DnaExtractStep, blank=True, null=True)

    lib_build_step = models.ForeignKey(LibBuildStep, blank=True, null=True)

    sequencing_step = models.ForeignKey(SequencingStep, blank=True, null=True)

    bioinfo_step = models.ForeignKey(BioinfoStep, blank=True, null=True)

    report_step = models.ForeignKey(ReportStep, blank=True, null=True)


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

    sample_pipe = models.ForeignKey(SamplePipe, blank=True, null=True)

    class Meta:
        ordering = ['-date_receive']

    def __str__(self):
        return f'{self.barcode}({self.name})'
