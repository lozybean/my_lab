from django.contrib import admin
from sample_manage.models import SampleInfo, SubjectInfo, Project, FamilyInfo

# Register your models here.


admin.site.register(SampleInfo)
admin.site.register(SubjectInfo)
admin.site.register(Project)
admin.site.register(FamilyInfo)
