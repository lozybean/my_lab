from django.db import models


# Create your models here.

class Project(models.Model):
    name = models.TextField()


class SampleType(models.Model):
    type = models.TextField()


class SampleInfo(models.Model):
    barcode = models.CharField(max_length=50)

    subject = models.ForeignKey(SubjectInfo)


class FamilyInfo(models.Model):
    proband = models.CharField(max_length=100)


class SubjectInfo(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=4, choices=['男', '女'])
    age = models.IntegerField()
    nationality = models.CharField(max_length=20, default='汉族')
    native_place = models.CharField(max_length=10)
    hospital = models.TextField()
    diagnosis = models.TextField()
    history = models.TextField()

    project = models.ForeignKey(Project)

    family = models.ForeignKey(FamilyInfo)
    relation_ship = models.CharField(max_length=50)


class SamplePipe(models.Model):
    date_sampling = models.DateTimeField()
    date_receive = models.DateTimeField()
