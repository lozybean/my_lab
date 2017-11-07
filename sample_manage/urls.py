from django.conf.urls import url
from sample_manage import views

urlpatterns = [
    url(r'^sample_list/$', views.sample_list, name='sample_list'),
    url(r'^sample_info/(?P<sample_id>\d+)/$', views.sample_info, name='sample_info'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
]
