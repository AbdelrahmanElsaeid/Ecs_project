from django.urls import path, re_path

from src.tags import views

app_name='tags'




urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^new/$', views.edit, name='edit'),
    re_path(r'^(?P<pk>\d+)/edit/$', views.edit, name='edit'),
    re_path(r'^(?P<pk>\d+)/delete/$', views.delete, name='delete'),
    re_path(r'^assign/submission/(?P<submission_pk>\d+)$', views.assign, name='assign'),
]


