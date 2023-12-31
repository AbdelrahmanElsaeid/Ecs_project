from django.urls import path, re_path

from src.boilerplate import views
app_name='boilerplate'


urlpatterns = [
    path('list/', views.list_boilerplate, name='list_boilerplate'),
    path('new/', views.edit_boilerplate, name='edit_boilerplate'),
    re_path(r'^(?P<text_pk>\d+)/edit/$', views.edit_boilerplate, name='edit_boilerplate'),
    re_path(r'^(?P<text_pk>\d+)/delete/$', views.delete_boilerplate, name='delete_boilerplate'),
    path('select/', views.select_boilerplate, name='select_boilerplate'),
]
