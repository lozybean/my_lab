from django.contrib import auth
from sample_manage.models import UserProfile


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


def check_permission(user, operation):
    return getattr(user, operation)
