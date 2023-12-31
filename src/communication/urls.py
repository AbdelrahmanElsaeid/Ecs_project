
from django.urls import path, re_path

from src.communication import views

app_name = 'communication'



urlpatterns = [
    re_path(r'^list/(?:(?P<submission_pk>\d+)/)?$', views.list_threads, name='list_threads'),
    re_path(r'^widget/$', views.dashboard_widget, name='dashboard_widget'),
    re_path(r'^widget/overview/(?P<submission_pk>\d+)/$', views.communication_overview_widget, name='communication_overview_widget'),
    re_path(r'^new/(?:(?P<submission_pk>\d+)/)?(?:(?P<to_user_pk>\d+)/)?$', views.new_thread, name='new_thread'),
    re_path(r'^(?P<thread_pk>\d+)/read/$', views.read_thread, name='read_thread'),
    re_path(r'^(?P<thread_pk>\d+)/mark_read/$', views.mark_read, name='mark_read'),
    re_path(r'^(?P<thread_pk>\d+)/star/$', views.star, name='star'),
    re_path(r'^(?P<thread_pk>\d+)/unstar/$', views.unstar, name='unstar'),
]