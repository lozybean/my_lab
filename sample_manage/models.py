from django.db import models


# Create your models here.

class Project(models.Model):
    name = models.TextField(null=True, blank=True)

    period_day = models.IntegerField()


class FamilyInfo(models.Model):
    proband = models.CharField(max_length=100)


class SubjectInfo(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=4, choices=[('male', '男'), ('female', '女')])
    age = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=20, default='汉族')
    native_place = models.CharField(max_length=10)
    hospital = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    history = models.TextField(blank=True, null=True)

    family = models.ForeignKey(FamilyInfo)
    relation_ship = models.CharField(max_length=50)


class SampleInfo(models.Model):
    name = models.CharField(max_length=20)
    barcode = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    quantity = models.CharField(max_length=50)

    # project = models.ForeignKey(Project)
    #
    # subject = models.ForeignKey(SubjectInfo)

    index1_seq = models.CharField(max_length=20)
    index2_seq = models.CharField(max_length=20)

    date_receive = models.DateTimeField(blank=True, null=True)
    date_sampling = models.DateTimeField(blank=True, null=True)
    date_deadline = models.DateTimeField(blank=True, null=True)

    date_dna_extract = models.DateTimeField(blank=True, null=True)
    date_lib_build = models.DateTimeField(blank=True, null=True)
    date_sequencing = models.DateTimeField(blank=True, null=True)
    date_bioinfo = models.DateTimeField(blank=True, null=True)
    date_report = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=10)

    has_request_note = models.BooleanField(default=True)
    has_informed_note = models.BooleanField(default=True)

    def __str__(self):
        return self.name
