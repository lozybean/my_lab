from django.contrib import admin
from sample_manage.models import SampleInfo


# Register your models here.

class SampleInfoAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.register(SampleInfo, SampleInfoAdmin)
# admin.register(SubjectInfo)
# admin.register(Project)
# admin.register(FamilyInfo)
