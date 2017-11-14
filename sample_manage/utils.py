from django.contrib import auth
from sample_manage.models import UserProfile,SamplePipe

def get_auth_user(request):
    if request.user.is_authenticated():
        auth_user = auth.get_user(request)
    else:
        auth_user = False
    return auth_user


def get_user_profile(request):
    user = get_auth_user(request)
    if not user:
        return False
    return UserProfile.objects.filter(user=user).first()


def check_permission(request, operation):
    user_profile = get_user_profile(request)
    if not user_profile:
        return False
    return getattr(user_profile, operation)


def get_primary_task(request):
    user_profile = get_user_profile(request)
    if not user_profile:
        return None
    return user_profile.primary_task


def get_step_names(step_name):
    step_list = SamplePipe.STEPS
    current_step_name = f'{step_name.lower()}_step'
    step_index = step_list.index(current_step_name)
    if step_index - 1 >= 0:
        previous_step_name = step_list[step_index - 1]
    else:
        previous_step_name = None
    return previous_step_name, current_step_name