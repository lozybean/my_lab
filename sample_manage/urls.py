from django.conf.urls import url
from sample_manage import views

urlpatterns = [
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^user_info/$', views.UserInfoView.as_view(), name='user_info'),
    url(r'^message/(?P<message_text>[\w《》，。？：！…—]+)/$', views.MessageView.as_view(), name='message'),

    url(r'^sample_info/(?P<sample_id>\d+)/$', views.SampleInfoView.as_view(), name='sample_info'),
    url(r'^sample_info/barcode/$', views.SampleInfoView.as_view(), name='query_sample_by_barcode'),


    # sample list and queries
    url(r'^sample_list/$', views.SampleListView.as_view(), name='sample_list'),
    url(r'^sample_list/project/(?P<project_id>\d+)/$',
        views.SampleListView.as_view(query_type='project'), name='query_sample_by_project'),
    url(r'^sample_list/status/(?P<status>\w+)/$',
        views.SampleListView.as_view(query_type='status'), name='query_sample_by_status'),
    url(r'^sample_list/date/(?P<step>\w+)/(?P<status>\w+)?/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        views.SampleListView.as_view(query_type='date'), name='query_sample_by_date'),

    url(r'^subject_info/(?P<subject_id>\d+)$', views.SubjectInfoView.as_view(), name='subject_info'),
    url(r'^subject_list/$', views.SubjectListView.as_view(), name='subject_list'),

    url(r'^sample_pipe/(?P<step_name>\w+)/(?P<status>\w+)/$', views.SamplePipeView.as_view(), name='sample_pipe'),
    url(r'^sequencing_step_info/(?P<sample_id>\d+)?$',
        views.SequencingStepInfoView.as_view(), name='sequencing_step_info'),
    url(r'^task/(?P<primary_task>\w+)/(?P<status>\w+)/$', views.TaskView.as_view(), name='task'),

    url(r'^add/sample_info/(?P<pk>\d+)?$', views.AddSampleInfoView.as_view(), name='add_sample_info'),
    url(r'^add/subject_info/(?P<pk>\d+)?$', views.AddSubjectInfoView.as_view(), name='add_subject_info'),
    url(r'^add/sample_type/(?P<pk>\d+)?$', views.AddSampleTypeView.as_view(), name='add_sample_type'),
]
