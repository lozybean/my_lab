from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.db import models

# Create your models here.

STATUS = (('sample_receive', '样本接收'),
          ('dna_extract', 'DNA提取'),
          ('lib_build', '文库构建'),
          ('quantify', '上机前定量'),
          ('sequencing', '上机测序'),
          ('bioinfo', '生信分析'),
          ('report', '报告撰写'),
          ('finish', '完成检测'),)


class UserProfile(models.Model):
    TASK_NAMES = STATUS[:-1]
    PERMISSIONS = [('add_subject', '受检者录入'),
                   ('view_subject', '受检者信息查询'),
                   ('add_sample_type', '添加样本类型'),
                   ('add_project', '增加检测项目'),
                   ('sample_delete', '样本删除'),
                   ] + list(TASK_NAMES)
    user = models.OneToOneField(User, verbose_name='用户名', on_delete=models.CASCADE)

    primary_task = models.CharField(blank=True, max_length=30,
                                    choices=TASK_NAMES, verbose_name='主要任务')

    # permissions:
    add_subject = models.BooleanField(default=False, verbose_name='受检者录入')
    view_subject = models.BooleanField(default=False, verbose_name='受检者信息查询')

    add_sample_type = models.BooleanField(default=False, verbose_name='添加样本类型')
    add_project = models.BooleanField(default=False, verbose_name='增加检测项目')

    sample_receive = models.BooleanField(default=False, verbose_name='样本接收')
    sample_delete = models.BooleanField(default=False, verbose_name='样本删除')

    dna_extract = models.BooleanField(default=False, verbose_name='DNA提取')
    lib_build = models.BooleanField(default=False, verbose_name='文库构建')
    quantify = models.BooleanField(default=False, verbose_name='上机前定量')
    sequencing = models.BooleanField(default=False, verbose_name='上机测序')

    bioinfo = models.BooleanField(default=False, verbose_name='生信分析')
    report = models.BooleanField(default=False, verbose_name='报告撰写')

    def __str__(self):
        return self.user.get_username()


class Project(models.Model):
    name = models.TextField(null=True, blank=True, verbose_name='项目名称')

    period_day = models.IntegerField(verbose_name='项目周期/工作日', default=0)

    def __str__(self):
        return self.name


class FamilyInfo(models.Model):
    proband = models.CharField(max_length=100, verbose_name='家系/先证者')

    def __str__(self):
        return f"先证者：{self.proband}"


class SubjectInfo(models.Model):
    name = models.CharField(max_length=100, verbose_name='姓名')
    gender = models.CharField(max_length=10, choices=(('male', '男'), ('female', '女')),
                              verbose_name='性别')
    age = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    nationality = models.CharField(max_length=20, default='汉族', verbose_name='名族',
                                   blank=True)
    native_place = models.CharField(max_length=10, verbose_name='籍贯', blank=True)
    diagnosis = models.TextField(blank=True, null=True, verbose_name='临床诊断')
    family_history = models.TextField(blank=True, null=True, verbose_name='家族史')

    family = models.ForeignKey(FamilyInfo, blank=True, null=True, verbose_name='家系')
    relation_ship = models.CharField(max_length=50, blank=True, null=True, verbose_name='与先证者的关系')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']


class SampleType(models.Model):
    type = models.CharField(max_length=100, verbose_name='样本类型')

    def __str__(self):
        return self.type


class SampleInfo(models.Model):
    name = models.CharField(max_length=20, verbose_name='样本名称')
    barcode = models.CharField(max_length=50, unique=True, verbose_name='样本条码号')

    type = models.ForeignKey(SampleType, blank=True, null=True, verbose_name='样本类型')
    quantity = models.CharField(max_length=50, blank=True, null=True, verbose_name='样本量')

    project = models.ForeignKey(Project, blank=True, null=True, verbose_name='项目类型')

    hospital = models.TextField(blank=True, null=True, verbose_name='送检医院/单位')
    subject = models.ForeignKey(SubjectInfo, blank=True, null=True, verbose_name='受检者')

    date_sampling = models.DateTimeField(blank=True, null=True, verbose_name='采样时间')
    date_receive = models.DateTimeField(blank=True, null=True, verbose_name='收样时间')
    date_deadline = models.DateTimeField(blank=True, null=True, verbose_name='截止时间')
    date_submit = models.DateTimeField(blank=True, null=True, verbose_name='送检时间')

    has_request_note = models.BooleanField(default=True, verbose_name='是否有检测申请单')
    has_informed_note = models.BooleanField(default=True, verbose_name='是否有知情同意书')

    class Meta:
        ordering = ['-date_receive']

    def __str__(self):
        return f'{self.barcode}({self.name})'


class SamplePipe(models.Model):
    STATUS = STATUS
    sample = models.OneToOneField(SampleInfo, verbose_name='样本信息', on_delete=models.CASCADE,
                                  related_name='sample_pipe')

    # 实际操作的步骤
    STEPS = [f'{i[0]}_step' for i in STATUS][1:-1]

    status = models.CharField(max_length=30, choices=STATUS, verbose_name='当前状态')

    def set_steps(self):
        """
        make sure every step has an initial active step
        :return:
        """
        for step_name in self.STEPS:
            getattr(self, step_name)

    def get_status_display(self):
        status_name = dict(STATUS)[self.status]
        step = getattr(self, f'{self.status}_step', None)
        if not step:
            return status_name
        if step.begin and not step.end:
            return f'{status_name}:进行中'
        elif step.begin and step.end:
            return f'{status_name}:已完成'
        else:
            return status_name

    @property
    def dna_extract_step(self):
        first_active = self.dnaextractstep_set.filter(active=True).first()
        if not first_active:
            first_active = DnaExtractStep()
            first_active.sample_pipe = self
            first_active.save()
        return first_active

    @property
    def lib_build_step(self):
        first_active = self.libbuildstep_set.filter(active=True).first()
        if not first_active:
            first_active = LibBuildStep()
            first_active.sample_pipe = self
            first_active.save()
        return first_active

    @property
    def quantify_step(self):
        first_active = self.quantifystep_set.filter(active=True).first()
        if not first_active:
            first_active = QuantifyStep()
            first_active.sample_pipe = self
            first_active.save()
        return first_active

    @property
    def sequencing_step(self):
        first_active = self.sequencingstep_set.filter(active=True).first()
        if not first_active:
            first_active = SequencingStep()
            first_active.sample_pipe = self
            first_active.save()
        return first_active

    @property
    def bioinfo_step(self):
        first_active = self.bioinfostep_set.filter(active=True).first()
        if not first_active:
            first_active = BioinfoStep()
            first_active.sample_pipe = self
            first_active.save()
        return first_active

    @property
    def report_step(self):
        first_active = self.reportstep_set.filter(active=True).first()
        if not first_active:
            first_active = ReportStep()
            first_active.sample_pipe = self
            first_active.save()
        return first_active

    def __str__(self):
        return f"<SamplePipe: {self.sample.name}>"


class DnaExtractStep(models.Model):
    sample_pipe = models.ForeignKey(SamplePipe, blank=True, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, verbose_name='活动状态')

    begin = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    end = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract',
                                 verbose_name='操作人员')

    store_place = models.CharField(max_length=50, blank=True, null=True, verbose_name='存储位置')
    pass_qc = models.BooleanField(default=True, verbose_name='通过质控')

    def __str__(self):
        return f'操作人: {self.operator}'

    class Meta:
        ordering = ['-begin', '-end']


class LibBuildStep(models.Model):
    sample_pipe = models.ForeignKey(SamplePipe, blank=True, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, verbose_name='活动状态')

    begin = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    end = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract',
                                 verbose_name='操作人员')

    index1_seq = models.CharField(max_length=20, blank=True, null=True, verbose_name='INDEX1')
    index2_seq = models.CharField(max_length=20, blank=True, null=True, verbose_name='INDEX2')
    store_place = models.CharField(max_length=50, blank=True, null=True, verbose_name='存储位置')
    pass_qc = models.BooleanField(default=True, verbose_name='通过质控')

    def __str__(self):
        return f'操作人: {self.operator}'

    class Meta:
        ordering = ['-begin', '-end']


class QuantifyStep(models.Model):
    sample_pipe = models.ForeignKey(SamplePipe, blank=True, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, verbose_name='活动状态')

    begin = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    end = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_quantify',
                                 verbose_name='操作人员')

    store_place = models.CharField(max_length=50, blank=True, null=True, verbose_name='存储位置')
    pass_qc = models.BooleanField(default=True, verbose_name='通过质控')

    def __str__(self):
        return f'操作人: {self.operator}'

    class Meta:
        ordering = ['-begin', '-end']


class SequencingStep(models.Model):
    SEQUENCER = (('MiSeq-M03074', 'MiSeq-M03074'),
                 ('MiSeq-M05418', 'MiSeq(研发)'),
                 ('NextSeq-CN500', 'NextSeq-CN500'),
                 ('NextSeq-NS500', 'NextSeq-NS500'),
                 ('MiniSeq-MN00531', 'MiniSeq(邵逸夫)'),
                 )

    sample_pipe = models.ForeignKey(SamplePipe, blank=True, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, verbose_name='活动状态')

    begin = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    end = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract',
                                 verbose_name='操作人员')

    index1_seq = models.CharField(max_length=20, blank=True, null=True, verbose_name='INDEX1')
    index2_seq = models.CharField(max_length=20, blank=True, null=True, verbose_name='INDEX2')

    sequencer = models.CharField(choices=SEQUENCER, blank=True,
                                 null=True, verbose_name='测序仪器',
                                 max_length=30)
    pass_qc = models.BooleanField(default=True, verbose_name='通过质控')

    def __str__(self):
        return f'操作人: {self.operator}'

    class Meta:
        ordering = ['-begin', '-end']


class BioinfoStep(models.Model):
    sample_pipe = models.ForeignKey(SamplePipe, blank=True, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, verbose_name='活动状态')

    begin = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    end = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract',
                                 verbose_name='操作人员')

    project_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='使用流程')
    result_path = models.CharField(max_length=200, blank=True, null=True, verbose_name='结果路径')
    pass_qc = models.BooleanField(default=True, verbose_name='通过质控')

    def __str__(self):
        return f'操作人: {self.operator}'

    class Meta:
        ordering = ['-begin', '-end']


class ReportStep(models.Model):
    sample_pipe = models.ForeignKey(SamplePipe, blank=True, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, verbose_name='活动状态')

    begin = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    end = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                 related_name='%(app_label)s_%(class)s_dna_extract',
                                 verbose_name='操作人员')

    def __str__(self):
        return f'操作人: {self.operator}'

    class Meta:
        ordering = ['-begin', '-end']
