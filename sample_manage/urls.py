from django.conf.urls import url
from sample_manage import views

urlpatterns = [
    url(r'^sample_list/$', views.sample_list, name='sample_list'),
    url(r'^subject_list/$', views.subject_list, name='subject_list'),
    url(r'^sample_info/(?P<sample_id>\d+)/$', views.sample_info, name='sample_info'),
    url(r'^subject_info/(?P<subject_id>\d+)$', views.subject_info, name='subject_info'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^user_info/$', views.user_info, name='user_info'),
]
