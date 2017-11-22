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

    url(r'^sample_pipe/(?P<step_name>\w+)/(?P<status>\w+)/(?P<success>\d)?$',
        views.SamplePipeView.as_view(), name='sample_pipe'),
    url(r'^task/(?P<primary_task>\w+)/(?P<status>\w+)/$', views.TaskView.as_view(), name='task'),

    url(r'^index_info/(?P<sample_id>\d+)?$', views.IndexInfoInputView.as_view(), name='input_index_info'),

    url(r'^add/sample_info/(?P<pk>\d+)?$', views.AddSampleInfoView.as_view(), name='add_sample_info'),
    url(r'^add/subject_info/(?P<pk>\d+)?$', views.AddSubjectInfoView.as_view(), name='add_subject_info'),

    url(r'^add/sample_type/popup/add$', views.AddSampleTypePopupView.as_view(), name='add_sample_type_popup'),
    url(r'^add/sample_type/popup/edit/(?P<pk>.*)/$', views.EditSampleTypePopupView.as_view(),
        name='edit_sample_type_popup'),

    url(r'^add/project/popup/add$', views.AddProjectPopupView.as_view(), name='add_project_popup'),
    url(r'^add/project/popup/edit/(?P<pk>.*)/$', views.EditProjectPopupView.as_view(),
        name='edit_project_popup'),

    url(r'^add/subject/popup/add$', views.AddSubjectInfoPopupView.as_view(), name='add_subject_popup'),
    url(r'^add/subject/popup/edit/(?P<pk>.*)/$', views.EditSubjectInfoPopupView.as_view(),
        name='edit_subject_popup'),

    url(r'^add/family/popup/add$', views.AddFamilyInfoPopupView.as_view(), name='add_family_popup'),
    url(r'^add/family/popup/edit/(?P<pk>.*)/$', views.EditFamilyInfoPopupView.as_view(),
        name='edit_family_popup'),
]
