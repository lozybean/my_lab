from django.contrib import auth
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from sample_manage.form import LoginForm
from sample_manage.models import SampleInfo, SubjectInfo, UserProfile


# Create your views here.

def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return redirect(sample_list)
            else:
                return render(request, 'login.html', {'form': form, 'password_is_wrong': True})
        else:
            return render(request, 'login.html', {'form': form})


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect(login)


def user_info(request):
    user = get_auth_user(request)
    if not user:
        return redirect(login)
    user_profile = UserProfile.objects.filter(user=user)
    return render(request, 'user_profile.html', {'user_profile': user_profile,
                                                 'user': user, 'is_auth': user})


def get_auth_user(request):
    if request.user.is_authenticated():
        auth_user = auth.get_user(request)
    else:
        auth_user = False
    return auth_user


def sample_info(request, sample_id):
    sample = get_object_or_404(SampleInfo, id=sample_id)
    auth_user = get_auth_user(request)
    return render(request, 'sample_info.html', {'sample': sample, 'is_auth': auth_user})


def sample_list(request):
    samples = get_list_or_404(SampleInfo)
    auth_user = get_auth_user(request)
    return render(request, 'sample_list.html', {'sample_list': samples, 'is_auth': auth_user})


def subject_info(request, subject_id):
    subject = get_object_or_404(SubjectInfo, id=subject_id)
    samples = SampleInfo.objects.filter(subject=subject)
    family = SubjectInfo.objects.filter(family=subject.family)
    auth_user = get_auth_user(request)
    return render(request, 'subject_info.html', {'subject': subject, 'is_auth': auth_user,
                                                 'sample_list': samples, 'family': family})


def subject_list(request):
    subjects = get_list_or_404(SubjectInfo)
    auth_user = get_auth_user(request)
    return render(request, 'subject_list.html', {'subject_list': subjects, 'is_auth': auth_user})
