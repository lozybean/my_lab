from django.db import models


# Create your models here.

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
    hospital = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)

    family = models.ForeignKey(FamilyInfo)
    relation_ship = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']


class SampleInfo(models.Model):
    STATUS = (('sample_received', '收样'),
              ('DNA_extracted', 'DNA提取'),
              ('lib_build', '文库构建'),
              ('seq', '上机'),
              ('bioinfo', '生信分析'),
              ('report', '报告撰写'),)
    name = models.CharField(max_length=20)
    barcode = models.CharField(max_length=50)
    type = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.CharField(max_length=50, blank=True, null=True)

    project = models.ForeignKey(Project, blank=True, null=True)

    subject = models.ForeignKey(SubjectInfo, blank=True, null=True)

    index1_seq = models.CharField(max_length=20, blank=True, null=True)
    index2_seq = models.CharField(max_length=20, blank=True, null=True)

    date_sampling = models.DateTimeField(blank=True, null=True)
    date_receive = models.DateTimeField(blank=True, null=True)
    date_deadline = models.DateTimeField(blank=True, null=True)

    date_dna_extract_begin = models.DateTimeField(blank=True, null=True)
    date_dna_extract_end = models.DateTimeField(blank=True, null=True)
    date_lib_build_begin = models.DateTimeField(blank=True, null=True)
    date_lib_build_end = models.DateTimeField(blank=True, null=True)
    date_sequencing_begin = models.DateTimeField(blank=True, null=True)
    date_sequencing_end = models.DateTimeField(blank=True, null=True)
    date_bioinfo_begin = models.DateTimeField(blank=True, null=True)
    date_bioinfo_end = models.DateTimeField(blank=True, null=True)
    date_report_begin = models.DateTimeField(blank=True, null=True)
    date_report_end = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS)

    has_request_note = models.BooleanField(default=True)
    has_informed_note = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_receive']

    def __str__(self):
        return self.name
