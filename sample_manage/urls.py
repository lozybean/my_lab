from django.conf.urls import url
from sample_manage import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^message/(?P<message_text>[\w《》，。？：！…—]+)/$', views.message, name='message'),
    url(r'^sample_list/$', views.sample_list, name='sample_list'),
    url(r'^sample_list/status/(?P<status>\w+)/$', views.query_sample_by_status, name='query_sample_by_status'),
    url(r'^sample_list/date/(?P<step>\w+)/(?P<status>\w+)?/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        views.query_sample_by_date, name='query_sample_by_date'),
    url(r'^sample_list/project/(?P<project_id>\d+)/$', views.query_sample_by_project, name='query_sample_by_project'),
    url(r'^subject_list/$', views.subject_list, name='subject_list'),
    url(r'^sample_info/(?P<sample_id>\d+)/$', views.sample_info, name='sample_info'),
    url(r'^sample_info/barcode/$', views.query_sample_by_barcode, name='query_sample_by_barcode'),
    url(r'^subject_info/(?P<subject_id>\d+)$', views.subject_info, name='subject_info'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^user_info/$', views.user_info, name='user_info'),
    url(r'^sample_pipe/(?P<step_name>\w+)/(?P<status>\w+)/$', views.sample_pipe_list, name='sample_pipe'),

    url(r'^sequencing_step_info/(?P<sample_id>\d+)?$', views.sequencing_step_info, name='sequencing_step_info'),

    url(r'^task/(?P<primary_task>\w+)/(?P<status>\w+)/$', views.task, name='task'),

    url(r'^add/sample_info/(?P<pk>\d+)?$', views.add_sample_info, name='add_sample_info'),
    url(r'^add/subject_info/(?P<pk>\d+)?$', views.add_subject_info, name='add_subject_info'),
    url(r'^add/sample_type/(?P<pk>\d+)?$', views.add_sample_type, name='add_sample_type'),
]
