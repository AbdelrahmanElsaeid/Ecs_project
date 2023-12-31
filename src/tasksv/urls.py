
from django.urls import path, re_path

from src.tasksv import views
app_name = 'tasksv'




urlpatterns = [
    re_path(r'^list/(?:submission/(?P<submission_pk>\d+)/)?$', views.task_list, name="task_list"),
    re_path(r'^list/mine/(?:submission/(?P<submission_pk>\d+)/)?$', views.my_tasks, name="my_tasks"),
    re_path(r'^(?P<task_pk>\d+)/accept/$', views.accept_task, name='accept_task'),
    re_path(r'^(?P<task_pk>\d+)/accept/full/$', views.accept_task_full, name='accept_task_full_deatils'),
    re_path(r'^accept/$', views.accept_tasks, name='accept_tasks'),
    re_path(r'^accept/full/$', views.accept_tasks_full, name='accept_tasks_full'),
    re_path(r'^(?P<task_pk>\d+)/decline/$', views.decline_task, name='decline_task'),
    re_path(r'^(?P<task_pk>\d+)/decline/full/$', views.decline_task_full,name='decline_task_full'),
    re_path(r'^(?P<task_pk>\d+)/do/$', views.do_task, name='do_task'),
    re_path(r'^(?P<task_pk>\d+)/preview/$', views.preview_task, name='preview_task'),
]

