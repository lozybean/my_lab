from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from sample_manage.models import (SampleInfo, SubjectInfo, Project, FamilyInfo,
                                  UserProfile, SampleType, SamplePipe,
                                  DNAExtractStep, LibBuildStep, BioInfoStep, ReportStep)


# Register your models here.

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user_profile'


class MyUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

admin.site.register(SampleType)
admin.site.register(SampleInfo)
admin.site.register(SubjectInfo)
admin.site.register(Project)
admin.site.register(FamilyInfo)

admin.site.register(DNAExtractStep)
admin.site.register(LibBuildStep)
admin.site.register(BioInfoStep)
admin.site.register(ReportStep)
admin.site.register(SamplePipe)
